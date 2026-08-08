# CatLabel as a Home Assistant Add-on

Date: 2026-08-09
Status: approved design, not yet implemented

## Goal

Run CatLabel as a Home Assistant add-on so labels can be designed and printed
from the Home Assistant UI, using the Bluetooth adapter attached to the Home
Assistant host.

## Target environment

- Home Assistant Supervised in a Proxmox VM, `amd64`.
- One USB Bluetooth dongle, already used by the Home Assistant Bluetooth
  integration.
- Printer: Phomemo M02S (FCC ID `2ASRB-M02S`). Already supported by
  `catlabel/vendors/phomemo/manifest.py:35` — 384 px, 48 mm, 203 dpi,
  protocol family `phomemo_m02`, transport BLE
  (`catlabel/vendors/phomemo/client.py:31`).

## Scope

In scope: the add-on packaging, a sidebar UI served through ingress, and the
code changes required for the app to run inside a container.

Out of scope: MQTT discovery, Home Assistant entities, printing from
automations, reading entity state into labels, `aarch64` and multi-arch images
published to GHCR, the Playwright headless renderer, and trimming the AI
dependencies.

## Architecture

### Add-on repository

The add-on lives in this repository, so Home Assistant installs it by adding
the repository URL and Supervisor builds the image on the machine. No CI, no
container registry.

```
repository.yaml           # name, url, maintainer
catlabel_addon/
  config.yaml
  Dockerfile
  README.md
  logo.png                # converted from logo.webp
  icon.png                # converted from logo.webp
```

### Add-on configuration

`catlabel_addon/config.yaml`, essential keys:

```yaml
arch: [amd64]
init: false                # plain python image, no s6 supervision
ingress: true
ingress_port: 8099
panel_icon: mdi:tag-text
host_dbus: true            # host BlueZ over the system D-Bus socket
udev: true
boot: manual
```

No `ports:` key. The UI is reachable only through ingress, which means Home
Assistant authentication applies and nothing is published on the LAN.

Supervisor mounts `/data` automatically; it survives add-on updates.

### Container image

`python:3.11-slim` base, `pip install -r requirements.txt`, then copy
`catlabel/` and `frontend/dist/`. Entry point `python -m catlabel`.

Environment set by the add-on:

| Variable | Value | Effect |
| --- | --- | --- |
| `CATLABEL_PORT` | `8099` | Matches `ingress_port`; already read by `catlabel/__main__.py`. |
| `CATLABEL_DATA_DIR` | `/data` | Database, fonts and projects on the persistent volume. |
| `CATLABEL_NO_BROWSER` | `1` | Suppresses the browser launch. |
| `CATLABEL_INGRESS_ONLY` | `1` | Enables the request source check. |

Without these variables the desktop behaviour is unchanged.

### Bluetooth on a shared adapter

`host_dbus: true` exposes the host system D-Bus socket, where BlueZ lives.
Home Assistant and the add-on are then two clients of the same `org.bluez`.
BlueZ reference-counts discovery per client, so both can scan. The printer is
not a Home Assistant device, so nothing competes for the connection itself.

The practical symptom of sharing is an occasional rejected first `connect`
while the adapter is busy with Home Assistant's active scan. The existing
retry path covers this — `SppBackend.connect_attempts`, called from
`catlabel/vendors/phomemo/client.py:39`. No new logic. If retries prove
insufficient in practice, add a `bt_adapter` add-on option (for example
`hci1`) and a second dongle.

Classic Bluetooth (RFCOMM/SPP) is not addressed. The M02S uses BLE, and
RFCOMM inside a container would need `NET_ADMIN` plus host-side pairing.

## Code changes

All changes are backwards compatible: with no environment variables set, the
desktop application behaves exactly as it does today.

### 1. Configurable data directory

Today the data directory is a hardcoded relative path, which breaks
persistence in a container. New module `catlabel/core/paths.py`:

```python
DATA_DIR = os.environ.get("CATLABEL_DATA_DIR", "data")
FONTS_DIR = os.path.join(DATA_DIR, "fonts")
```

Call sites to update: `catlabel/core/database.py:4-6`, and
`catlabel/api/main.py` lines 50, 56, 61, 84, 85, 220, 222, 235, 238.

### 2. Skip the browser launch

`catlabel/__main__.py` skips `open_browser_when_ready` when
`CATLABEL_NO_BROWSER` is set.

### 3. Ingress base path

Ingress serves the application under `/api/hassio_ingress/<token>/` and strips
that prefix before the request reaches the add-on, so the backend needs no
routing change. Only the browser is affected, because the frontend requests
absolute paths such as `/api/printers/scan`.

- `frontend/vite.config.js`: set `base: './'` so `dist/index.html` references
  `assets/` relatively.
- `frontend/src/utils/apiClient.js`: resolve absolute paths against the
  current document directory, inside `apiFetch`, leaving all call sites
  untouched:

```js
const ingressBase = () => {
  const path = globalThis.location?.pathname || '/';
  return path.endsWith('/') ? path : path.slice(0, path.lastIndexOf('/') + 1);
};
export const resolveUrl = (input) =>
  typeof input === 'string' && input.startsWith('/') ? ingressBase() + input.slice(1) : input;
```

  On the desktop `pathname` is `/`, so URLs are unchanged.

- Three places bypass `apiFetch` and need the same helper:
  `frontend/src/utils/apiErrors.js:56` (`fetch('/api/health')`),
  `frontend/src/store.js:1069` (the generated `@font-face` `src` URL), and the
  logo in `frontend/src/components/Sidebar.jsx:115` and
  `frontend/src/components/OnboardingWizard.jsx:153`.
- Rebuild the frontend and commit `frontend/dist`.

Rejected alternative: injecting `<base href>` from the `X-Ingress-Path` header.
It would require relaxing `base-uri 'none'` in the `dist/index.html` CSP and
editing every call site.

### 4. Request source check

Add-ons share an internal Docker network, so other add-ons can reach the API
even though no port is published. A middleware in `catlabel/api/main.py`,
active only when `CATLABEL_INGRESS_ONLY=1`, allows `172.30.32.2` (the
Supervisor ingress proxy) and loopback, and returns 403 for anything else.

## Testing

Automated:

- `tests/test_addon_runtime.py`: `DATA_DIR` follows the environment variable;
  the middleware rejects a foreign client address and accepts `172.30.32.2`;
  `main()` does not open a browser when `CATLABEL_NO_BROWSER` is set.
- `frontend/src/utils/apiClient.test.js`: `resolveUrl` for a root path and for
  an ingress path.

Manual, on the target machine: install the add-on from the repository URL,
open the sidebar panel, scan for printers and confirm the M02S is found, print
a test label, then restart the add-on and confirm projects and fonts survived.

## Risks

- Image size is roughly 1.5 GB because `litellm` and `google-cloud-aiplatform`
  are kept for parity with the desktop build. Removing them would require
  disabling `catlabel/api/routes_ai.py` and hiding the assistant panel, so the
  dependencies stay until size becomes a problem.
- The default fonts are downloaded on first start and need internet access.
  `download_default_fonts` already catches failures, so a start without
  network still succeeds, just without those fonts.
