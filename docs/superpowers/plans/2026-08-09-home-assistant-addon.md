# Home Assistant Add-on Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship CatLabel as a Home Assistant add-on whose UI is served through ingress and which prints to a Phomemo M02S over the host's shared Bluetooth adapter.

**Architecture:** The application keeps running as a single FastAPI process. Container-specific behaviour is switched on by environment variables, so the desktop path is unchanged when they are absent: the data directory becomes `/data`, the browser launch is suppressed, and requests are restricted to the Supervisor ingress proxy. The frontend resolves absolute paths against the document base so it survives being served under `/api/hassio_ingress/<token>/`. Add-on packaging lives in this repository and Supervisor builds the image on the Home Assistant machine.

**Tech Stack:** Python 3.11, FastAPI/uvicorn, bleak over host BlueZ (D-Bus), React 19 + Vite, unittest (backend), vitest (frontend), Docker.

**Spec:** `docs/superpowers/specs/2026-08-09-home-assistant-addon-design.md`

## Global Constraints

- Backwards compatibility: with none of the `CATLABEL_*` environment variables set, behaviour must be identical to today's desktop behaviour. Every new switch defaults to off.
- Environment variables and their add-on values: `CATLABEL_PORT=8099`, `CATLABEL_DATA_DIR=/data`, `CATLABEL_NO_BROWSER=1`, `CATLABEL_INGRESS_ONLY=1`.
- Ingress proxy address that must be allowed: `172.30.32.2`. Loopback (`127.0.0.1`, `::1`) also allowed. Everything else gets HTTP 403.
- Add-on architecture: `amd64` only. Ingress port `8099` must equal `CATLABEL_PORT`.
- No new Python or npm dependencies. Backend tests use `unittest`, frontend tests use `vitest`.
- Backend tests must not import `catlabel.api.main` (it pulls in `litellm` and performs filesystem work at import time). Test pure helpers instead.
- Run backend tests with `python -m unittest discover -s tests -v`, frontend tests with `npm test` inside `frontend/`.
- Git commits: this repository has no `user.email` configured. Commit with `git -c user.name="Krzysztof Błachowicz" -c user.email="krzysztof.blachowicz@gmail.com" commit ...`.
- Repository remote, used by the add-on Dockerfile: `https://github.com/ChrisB85/catlabel`.

## File Structure

**Created:**
- `catlabel/core/paths.py` — resolves the data and fonts directories from the environment. Two functions, no state.
- `catlabel/api/ingress.py` — pure predicate deciding whether a client address may reach the API.
- `frontend/src/utils/ingress.js` — resolves root-absolute URLs against the document base. Standalone so both `apiClient.js` and `apiErrors.js` can import it without a cycle (`apiClient.js` already imports `apiErrors.js`).
- `frontend/src/utils/ingress.test.js` — vitest coverage for the above.
- `tests/test_addon_runtime.py` — backend coverage for paths, the ingress predicate, and the browser switch.
- `tests/test_addon_manifest.py` — guards against drift between `config.yaml` and the `Dockerfile`.
- `repository.yaml` — add-on repository metadata at the repo root.
- `catlabel_addon/config.yaml`, `catlabel_addon/Dockerfile`, `catlabel_addon/README.md` — the add-on itself.

**Modified:**
- `catlabel/core/database.py` — database path from `paths`.
- `catlabel/api/main.py` — fonts path from `paths`, ingress middleware registration.
- `catlabel/__main__.py` — skip the browser launch when asked.
- `frontend/src/utils/apiClient.js` — resolve URLs inside `apiFetch`.
- `frontend/src/utils/apiErrors.js` — resolve the health probe URL.
- `frontend/src/store.js` — resolve the generated `@font-face` URL.
- `frontend/src/components/Sidebar.jsx`, `frontend/src/components/OnboardingWizard.jsx` — resolve the logo URL.
- `frontend/vite.config.js` — relative asset base.
- `frontend/dist/**` — rebuilt bundle, committed.
- `README.md` — add-on installation section.

---

### Task 1: Configurable data directory

Today `data/` is hardcoded and relative to the working directory, so nothing would persist across add-on updates.

**Files:**
- Create: `catlabel/core/paths.py`
- Create: `tests/test_addon_runtime.py`
- Modify: `catlabel/core/database.py:1-7`
- Modify: `catlabel/api/main.py:50`, `:56`, `:61`, `:84-85`, `:220`, `:222`, `:235`, `:238`

**Interfaces:**
- Consumes: nothing.
- Produces: `catlabel.core.paths.data_dir() -> str` and `catlabel.core.paths.fonts_dir() -> str`. Both read the environment on every call, so tests need no module reloading. `fonts_dir()` is always `os.path.join(data_dir(), "fonts")`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_addon_runtime.py`:

```python
from __future__ import annotations

import os
import unittest
from unittest import mock

from catlabel.core.paths import data_dir, fonts_dir


class DataDirectoryTests(unittest.TestCase):
    def test_defaults_to_relative_data_directory(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(data_dir(), "data")
            self.assertEqual(fonts_dir(), os.path.join("data", "fonts"))

    def test_follows_environment_override(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_DATA_DIR": "/data"}, clear=True):
            self.assertEqual(data_dir(), "/data")
            self.assertEqual(fonts_dir(), os.path.join("/data", "fonts"))

    def test_blank_override_is_ignored(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_DATA_DIR": ""}, clear=True):
            self.assertEqual(data_dir(), "data")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_addon_runtime -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catlabel.core.paths'`

- [ ] **Step 3: Write minimal implementation**

Create `catlabel/core/paths.py`:

```python
from __future__ import annotations

import os

DEFAULT_DATA_DIR = "data"


def data_dir() -> str:
    """Directory holding the database, fonts and imported assets."""
    return os.environ.get("CATLABEL_DATA_DIR") or DEFAULT_DATA_DIR


def fonts_dir() -> str:
    """Directory holding font files served under /fonts."""
    return os.path.join(data_dir(), "fonts")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_addon_runtime -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Use the helpers in the database module**

Replace the top of `catlabel/core/database.py` (currently lines 1-7):

```python
from sqlmodel import SQLModel, create_engine
import os

from .paths import data_dir

os.makedirs(data_dir(), exist_ok=True)
sqlite_file_name = os.path.join(data_dir(), "catlabel.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})
```

- [ ] **Step 6: Use the helpers in the API module**

In `catlabel/api/main.py`, add the import next to the other relative imports (near line 15, beside `from ..core.database import ...`):

```python
from ..core.paths import fonts_dir
```

Then replace every hardcoded fonts path. Line 50 and lines 56, 61 inside `download_default_fonts`:

```python
    os.makedirs(fonts_dir(), exist_ok=True)
```
```python
                dst = os.path.join(fonts_dir(), filename)
```
```python
        target = os.path.join(fonts_dir(), filename)
```

Lines 84-85, the module-level mount:

```python
os.makedirs(fonts_dir(), exist_ok=True)
app.mount("/fonts", StaticFiles(directory=fonts_dir()), name="fonts")
```

Lines 220-222 in `upload_font`:

```python
    os.makedirs(fonts_dir(), exist_ok=True)
    safe_filename = os.path.basename(file.filename)
    file_path = os.path.join(fonts_dir(), safe_filename)
```

Lines 235-238 in `list_fonts`:

```python
    os.makedirs(fonts_dir(), exist_ok=True)
    with Session(engine) as session:
        db_fonts = {f.name: f for f in session.exec(select(Font)).all()}
        disk_fonts = [f for f in os.listdir(fonts_dir()) if f.lower().endswith((".ttf", ".otf"))]
```

Leave the `Font.file_path` values as `f"fonts/{filename}"` — that is the URL path under the `/fonts` mount, not a filesystem path.

- [ ] **Step 7: Verify no hardcoded data paths remain**

Run: `grep -rn '"data/\|data/fonts' --include=*.py catlabel/`
Expected: no output.

- [ ] **Step 8: Run the whole backend suite**

Run: `python -m unittest discover -s tests -v`
Expected: PASS, no regressions.

- [ ] **Step 9: Commit**

```bash
git add catlabel/core/paths.py catlabel/core/database.py catlabel/api/main.py tests/test_addon_runtime.py
git -c user.name="Krzysztof Błachowicz" -c user.email="krzysztof.blachowicz@gmail.com" \
  commit -m "Resolve the data directory from the environment"
```

---

### Task 2: Suppress the browser launch

In a container there is no browser, and `webbrowser.open` would run for nothing on every start.

**Files:**
- Modify: `catlabel/__main__.py:29-45`
- Test: `tests/test_addon_runtime.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `catlabel.__main__.browser_launch_enabled() -> bool`, returning `False` when `CATLABEL_NO_BROWSER` is set to a non-empty value. `open_browser_when_ready` keeps its current signature.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_addon_runtime.py`:

```python
from catlabel.__main__ import browser_launch_enabled


class BrowserLaunchTests(unittest.TestCase):
    def test_enabled_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertTrue(browser_launch_enabled())

    def test_disabled_by_environment(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_NO_BROWSER": "1"}, clear=True):
            self.assertFalse(browser_launch_enabled())

    def test_blank_value_leaves_it_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_NO_BROWSER": ""}, clear=True):
            self.assertTrue(browser_launch_enabled())
```

Keep the `if __name__ == "__main__": unittest.main()` block at the very bottom of the file, and place the new import beside the existing ones at the top.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_addon_runtime -v`
Expected: FAIL with `ImportError: cannot import name 'browser_launch_enabled'`

- [ ] **Step 3: Write minimal implementation**

In `catlabel/__main__.py`, add the helper above `main()`:

```python
def browser_launch_enabled() -> bool:
    """The add-on runs headless, so the browser launch is switched off there."""
    return not os.environ.get("CATLABEL_NO_BROWSER")
```

Then guard the thread inside `main()`:

```python
    server = uvicorn.Server(config)
    if browser_launch_enabled():
        threading.Thread(
            target=open_browser_when_ready,
            args=(server, port),
            daemon=True,
        ).start()
    server.run()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_addon_runtime -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add catlabel/__main__.py tests/test_addon_runtime.py
git -c user.name="Krzysztof Błachowicz" -c user.email="krzysztof.blachowicz@gmail.com" \
  commit -m "Allow starting the server without opening a browser"
```

---

### Task 3: Restrict requests to the ingress proxy

Add-ons share an internal Docker network. Even with no published port, any other add-on could reach the API, so the container build closes that door.

**Files:**
- Create: `catlabel/api/ingress.py`
- Modify: `catlabel/api/main.py:87-93` (next to the existing `CORSMiddleware` registration)
- Test: `tests/test_addon_runtime.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `catlabel.api.ingress.ingress_only_enabled() -> bool` and `catlabel.api.ingress.is_allowed_client(host: str | None) -> bool`. `INGRESS_PROXY_HOST` is the string `"172.30.32.2"`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_addon_runtime.py` (import beside the others at the top):

```python
from catlabel.api.ingress import INGRESS_PROXY_HOST, ingress_only_enabled, is_allowed_client


class IngressAccessTests(unittest.TestCase):
    def test_supervisor_proxy_is_allowed(self) -> None:
        self.assertTrue(is_allowed_client(INGRESS_PROXY_HOST))

    def test_loopback_is_allowed(self) -> None:
        self.assertTrue(is_allowed_client("127.0.0.1"))
        self.assertTrue(is_allowed_client("::1"))

    def test_other_addons_are_rejected(self) -> None:
        self.assertFalse(is_allowed_client("172.30.33.7"))
        self.assertFalse(is_allowed_client("192.168.1.50"))

    def test_missing_client_address_is_rejected(self) -> None:
        self.assertFalse(is_allowed_client(None))
        self.assertFalse(is_allowed_client(""))

    def test_switch_is_off_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(ingress_only_enabled())

    def test_switch_follows_environment(self) -> None:
        with mock.patch.dict(os.environ, {"CATLABEL_INGRESS_ONLY": "1"}, clear=True):
            self.assertTrue(ingress_only_enabled())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_addon_runtime -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'catlabel.api.ingress'`

- [ ] **Step 3: Write minimal implementation**

Create `catlabel/api/ingress.py`:

```python
from __future__ import annotations

import os
from typing import Optional

INGRESS_PROXY_HOST = "172.30.32.2"
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1"})


def ingress_only_enabled() -> bool:
    """True when the server must answer only the Supervisor ingress proxy."""
    return bool(os.environ.get("CATLABEL_INGRESS_ONLY"))


def is_allowed_client(host: Optional[str]) -> bool:
    """Add-ons share a network, so anything but the ingress proxy is refused."""
    if not host:
        return False
    return host == INGRESS_PROXY_HOST or host in LOOPBACK_HOSTS
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_addon_runtime -v`
Expected: PASS (12 tests)

- [ ] **Step 5: Register the middleware**

In `catlabel/api/main.py`, extend the imports:

```python
from fastapi.responses import JSONResponse
```

and next to the other relative imports:

```python
from .ingress import ingress_only_enabled, is_allowed_client
```

Then, immediately after the existing `app.add_middleware(CORSMiddleware, ...)` call (line 87-93), add:

```python
if ingress_only_enabled():
    @app.middleware("http")
    async def restrict_to_ingress(request, call_next):
        client_host = request.client.host if request.client else None
        if not is_allowed_client(client_host):
            return JSONResponse({"detail": "Forbidden"}, status_code=403)
        return await call_next(request)
```

- [ ] **Step 6: Run the whole backend suite**

Run: `python -m unittest discover -s tests -v`
Expected: PASS, no regressions.

- [ ] **Step 7: Commit**

```bash
git add catlabel/api/ingress.py catlabel/api/main.py tests/test_addon_runtime.py
git -c user.name="Krzysztof Błachowicz" -c user.email="krzysztof.blachowicz@gmail.com" \
  commit -m "Refuse non-ingress clients when running as an add-on"
```

---

### Task 4: Serve the frontend under the ingress path

Ingress serves the app from `/api/hassio_ingress/<token>/` and strips that prefix before the request reaches the add-on, so the backend needs no routing change. The browser is the problem: today the frontend requests root-absolute paths such as `/api/printers/scan`, which under ingress would hit Home Assistant itself.

The fix resolves those paths against `document.baseURI` — the browser's own relative-URL machinery — rather than hand-rolled string math.

**Files:**
- Create: `frontend/src/utils/ingress.js`
- Create: `frontend/src/utils/ingress.test.js`
- Modify: `frontend/src/utils/apiClient.js:1`, `:27`
- Modify: `frontend/src/utils/apiErrors.js:56`
- Modify: `frontend/src/store.js:1069`
- Modify: `frontend/src/components/Sidebar.jsx:115`
- Modify: `frontend/src/components/OnboardingWizard.jsx:153`
- Modify: `frontend/vite.config.js:44`
- Modify: `frontend/dist/**` (rebuilt)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `resolveUrl(input)` exported from `frontend/src/utils/ingress.js`. It takes any value; root-absolute path strings (`/api/health`) come back as an absolute URL resolved against the document base, and everything else — protocol-relative strings, full URLs, `Request` objects — is returned untouched.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/utils/ingress.test.js`:

```js
import { describe, expect, it, vi } from 'vitest';
import { resolveUrl } from './ingress';

const withBase = (baseURI, run) => {
  vi.stubGlobal('document', { baseURI });
  try {
    return run();
  } finally {
    vi.unstubAllGlobals();
  }
};

describe('resolveUrl', () => {
  it('keeps root-absolute paths at the root when served from the root', () => {
    withBase('http://homeassistant.local:8000/', () => {
      expect(resolveUrl('/api/health')).toBe('http://homeassistant.local:8000/api/health');
    });
  });

  it('rebases root-absolute paths onto the ingress prefix', () => {
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl('/api/printers/scan'))
        .toBe('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/api/printers/scan');
    });
  });

  it('preserves the query string', () => {
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl('/api/fonts?refresh=1'))
        .toBe('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/api/fonts?refresh=1');
    });
  });

  it('leaves absolute and protocol-relative URLs alone', () => {
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl('https://example.com/a')).toBe('https://example.com/a');
      expect(resolveUrl('//example.com/a')).toBe('//example.com/a');
    });
  });

  it('leaves non-string inputs alone', () => {
    const request = new Request('http://example.com/a');
    withBase('http://homeassistant.local:8123/api/hassio_ingress/TOKEN/', () => {
      expect(resolveUrl(request)).toBe(request);
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/utils/ingress.test.js`
Expected: FAIL with a resolution error for `./ingress`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/src/utils/ingress.js`:

```js
// Home Assistant ingress serves the app under /api/hassio_ingress/<token>/ and
// strips that prefix before the request reaches the server, so only the browser
// needs to know about it. Resolving against the document base covers both the
// desktop build (served from /) and the add-on.
const documentBase = () => globalThis.document?.baseURI
  || globalThis.location?.href
  || 'http://localhost/';

export const resolveUrl = (input) => (
  typeof input === 'string' && input.startsWith('/') && !input.startsWith('//')
    ? new URL(input.slice(1), documentBase()).href
    : input
);
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/utils/ingress.test.js`
Expected: PASS (5 tests)

- [ ] **Step 5: Route every API call through it**

In `frontend/src/utils/apiClient.js`, add the import below the existing one on line 1:

```js
import { resolveUrl } from './ingress';
```

and change the `fetch` call inside `apiFetch` (line 27):

```js
    const response = await fetch(resolveUrl(input), { ...init, signal: controller.signal });
```

`apiClient.js` already imports from `apiErrors.js`, which is why `resolveUrl` lives in its own module — importing it from `apiClient.js` in the next step would create a cycle.

In `frontend/src/utils/apiErrors.js`, add the import at the top:

```js
import { resolveUrl } from './ingress';
```

and change the health probe (line 56):

```js
    const response = await fetch(resolveUrl('/api/health'), {
```

- [ ] **Step 6: Fix the remaining absolute URLs**

In `frontend/src/store.js`, add the import beside the other util imports at the top of the file:

```js
import { resolveUrl } from './utils/ingress';
```

and change the generated font rule (line 1069):

```js
        css += `@font-face { font-family: '${fontName}'; src: url('${resolveUrl('/' + encodeURI(filePath))}'); }\n`;
```

In `frontend/src/components/Sidebar.jsx`, add `import { resolveUrl } from '../utils/ingress';` beside the other imports and change line 115:

```jsx
              src={resolveUrl('/logo.webp')}
```

In `frontend/src/components/OnboardingWizard.jsx`, add the same import and change line 153:

```jsx
                    <img src={resolveUrl('/logo.webp')} alt="CatLabel" className="w-16 h-16 drop-shadow-md" draggable={false} />
```

- [ ] **Step 7: Make bundle assets relative**

In `frontend/vite.config.js`, add `base` to the exported config, directly above `plugins` (line 44):

```js
export default defineConfig({
  base: './',
  plugins: [react(), rootLogoAsset()],
```

This turns the `/assets/...` references in `dist/index.html` into `./assets/...`, which resolve correctly under both the root and the ingress prefix.

- [ ] **Step 8: Verify no root-absolute URLs are left in source**

Run: `cd frontend && grep -rn "src=\"/\|url('/\|fetch('/" src --include=*.jsx --include=*.js | grep -v test`
Expected: no output.

- [ ] **Step 9: Run the frontend suite and rebuild**

Run: `cd frontend && npm run check`
Expected: lint clean, all vitest suites pass, build succeeds.

Then confirm the built entry point uses relative assets:

Run: `grep -o 'src="[^"]*"' frontend/dist/index.html`
Expected: paths starting with `./assets/`.

- [ ] **Step 10: Commit**

```bash
git add frontend/src frontend/vite.config.js frontend/dist
git -c user.name="Krzysztof Błachowicz" -c user.email="krzysztof.blachowicz@gmail.com" \
  commit -m "Resolve frontend URLs against the document base for ingress"
```

---

### Task 5: Add-on packaging

Supervisor clones the add-on repository and builds the image on the Home Assistant machine. The Docker build context is the add-on directory only, so the Dockerfile cannot copy the application from the repository root — it clones the same repository from GitHub at a pinned ref instead.

**Consequence worth knowing before testing:** the add-on builds from what is pushed to GitHub, not from the local working copy. Push first, then install or rebuild.

**Files:**
- Create: `repository.yaml`
- Create: `catlabel_addon/config.yaml`
- Create: `catlabel_addon/Dockerfile`
- Create: `catlabel_addon/README.md`
- Create: `tests/test_addon_manifest.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: the environment switches from Tasks 1-3 (`CATLABEL_DATA_DIR`, `CATLABEL_NO_BROWSER`, `CATLABEL_INGRESS_ONLY`) and the existing `CATLABEL_PORT`.
- Produces: an installable add-on with slug `catlabel`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_addon_manifest.py`. It parses both files with regular expressions, so it needs no YAML dependency:

```python
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "catlabel_addon"


def _config_value(key: str) -> str:
    text = (ADDON / "config.yaml").read_text(encoding="utf-8")
    match = re.search(rf"^{key}:\s*\"?([^\"\n]+)\"?\s*$", text, re.MULTILINE)
    assert match, f"{key} missing from config.yaml"
    return match.group(1).strip()


class AddonManifestTests(unittest.TestCase):
    def test_ingress_port_matches_the_port_the_server_listens_on(self) -> None:
        dockerfile = (ADDON / "Dockerfile").read_text(encoding="utf-8")
        match = re.search(r"CATLABEL_PORT=(\d+)", dockerfile)
        self.assertIsNotNone(match, "CATLABEL_PORT missing from Dockerfile")
        self.assertEqual(_config_value("ingress_port"), match.group(1))

    def test_ingress_is_enabled_and_no_port_is_published(self) -> None:
        text = (ADDON / "config.yaml").read_text(encoding="utf-8")
        self.assertEqual(_config_value("ingress"), "true")
        self.assertNotRegex(text, r"(?m)^ports:")

    def test_bluetooth_access_is_declared(self) -> None:
        self.assertEqual(_config_value("host_dbus"), "true")

    def test_container_writes_to_the_persistent_volume(self) -> None:
        dockerfile = (ADDON / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("CATLABEL_DATA_DIR=/data", dockerfile)
        self.assertIn("CATLABEL_NO_BROWSER=1", dockerfile)
        self.assertIn("CATLABEL_INGRESS_ONLY=1", dockerfile)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_addon_manifest -v`
Expected: FAIL with `FileNotFoundError` for `catlabel_addon/config.yaml`

- [ ] **Step 3: Write the repository metadata**

Create `repository.yaml`:

```yaml
name: CatLabel
url: https://github.com/ChrisB85/catlabel
maintainer: Krzysztof Błachowicz <krzysztof.blachowicz@gmail.com>
```

- [ ] **Step 4: Write the add-on configuration**

Create `catlabel_addon/config.yaml`:

```yaml
name: CatLabel Studio
version: "0.1.0"
slug: catlabel
description: Design and print labels on Bluetooth thermal printers
url: https://github.com/ChrisB85/catlabel
arch:
  - amd64
init: false
startup: application
boot: manual
ingress: true
ingress_port: 8099
panel_icon: mdi:tag-text
panel_title: CatLabel
host_dbus: true
udev: true
```

No `ports:` key: the UI is reachable only through ingress, so Home Assistant authentication applies and nothing is published on the LAN. `/data` is mounted by Supervisor automatically.

- [ ] **Step 5: Write the Dockerfile**

Create `catlabel_addon/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Supervisor passes this to every add-on build; unused here because the base
# image is pinned rather than derived from the Home Assistant base images.
ARG BUILD_FROM

# Bump to build from a tag or branch other than the default.
ARG CATLABEL_REF=master

ENV PYTHONUNBUFFERED=1 \
    CATLABEL_PORT=8099 \
    CATLABEL_DATA_DIR=/data \
    CATLABEL_NO_BROWSER=1 \
    CATLABEL_INGRESS_ONLY=1

# The add-on build context is this directory only, so the application is
# fetched from the repository rather than copied from the parent directory.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && git clone --depth 1 --branch "${CATLABEL_REF}" \
        https://github.com/ChrisB85/catlabel.git /app \
    && apt-get purge -y --auto-remove git \
    && rm -rf /var/lib/apt/lists/* /app/.git

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "catlabel"]
```

`bleak` reaches the host's BlueZ over the system D-Bus socket that `host_dbus: true` maps in; no extra system packages are needed for BLE.

- [ ] **Step 6: Write the add-on README**

Create `catlabel_addon/README.md`:

```markdown
# CatLabel Studio add-on

Design and print labels on Bluetooth thermal printers from the Home Assistant UI.

## Install

1. Settings → Add-ons → Add-on store → ⋮ → Repositories.
2. Add `https://github.com/ChrisB85/catlabel`.
3. Install **CatLabel Studio**, then start it. The first build takes a few
   minutes and produces a large image, because the AI assistant dependencies
   are included.
4. Open it from the sidebar.

## Bluetooth

The add-on talks to the host's BlueZ over D-Bus and shares the adapter with the
Home Assistant Bluetooth integration. Connecting to a printer occasionally
fails on the first attempt while the adapter is busy with Home Assistant's
scan; the connection is retried automatically.

## Data

Projects, presets, fonts and the database live in `/data` and survive add-on
updates.

## Updating

The image is built from the repository on GitHub, not from a local copy. Push
your changes, bump `version` in `config.yaml`, then rebuild the add-on.
```

- [ ] **Step 7: Run test to verify it passes**

Run: `python -m unittest tests.test_addon_manifest -v`
Expected: PASS (4 tests)

- [ ] **Step 8: Document the add-on in the main README**

In `README.md`, add a `### Home Assistant` subsection immediately after the existing `### macOS & Linux` block:

```markdown
### Home Assistant
CatLabel can run as a Home Assistant add-on, printing over the Bluetooth adapter attached to your Home Assistant machine.

1. In Home Assistant, go to Settings → Add-ons → Add-on store → ⋮ → Repositories.
2. Add this repository's URL.
3. Install **CatLabel Studio** and start it. The interface appears in the sidebar.

The add-on requires Home Assistant OS or Supervised on `amd64`, and shares the Bluetooth adapter with the Home Assistant Bluetooth integration. See `catlabel_addon/README.md` for details.
```

- [ ] **Step 9: Run the whole backend suite**

Run: `python -m unittest discover -s tests -v`
Expected: PASS, no regressions.

- [ ] **Step 10: Commit and push**

```bash
git add repository.yaml catlabel_addon README.md tests/test_addon_manifest.py
git -c user.name="Krzysztof Błachowicz" -c user.email="krzysztof.blachowicz@gmail.com" \
  commit -m "Add Home Assistant add-on packaging"
git push origin master
```

The push is part of this task: the add-on build clones from GitHub, so nothing can be installed until the branch is published.

---

### Task 6: Verify on the Home Assistant machine

Manual, because nothing here can be exercised without the real Supervisor, the real BlueZ and the real printer.

**Files:** none.

**Interfaces:**
- Consumes: the installable add-on from Task 5.
- Produces: a verified installation, or defects to feed back into Tasks 1-5.

- [ ] **Step 1: Add the repository and install**

In Home Assistant: Settings → Add-ons → Add-on store → ⋮ → Repositories → add `https://github.com/ChrisB85/catlabel`. Install **CatLabel Studio**.
Expected: the build completes; the add-on log shows uvicorn listening on `0.0.0.0:8099`.

- [ ] **Step 2: Open the panel**

Start the add-on, then open CatLabel from the sidebar.
Expected: the editor loads with no console errors, the logo renders, and no request 404s. If assets or `/api/...` calls fail, Task 4 is at fault.

- [ ] **Step 3: Confirm the ingress restriction**

From a terminal on the Home Assistant host, with the add-on running:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://homeassistant.local:8099/api/health
```

Expected: connection refused or a timeout — the port is not published. The panel in the sidebar keeps working.

- [ ] **Step 4: Find the printer**

Turn the Phomemo M02S on, then run a printer scan in the sidebar.
Expected: the M02S is listed. If the first attempt finds nothing, run it again — the adapter is shared with the Home Assistant Bluetooth integration.

- [ ] **Step 5: Print**

Select the M02S, choose a continuous preset, place a text element, print.
Expected: the label comes out. If the connection fails repeatedly, check the add-on log for the retry attempts from `SppBackend.connect_attempts` and consider the `bt_adapter` option and a second dongle described in the spec.

- [ ] **Step 6: Confirm persistence**

Save a project, then restart the add-on and reload the panel.
Expected: the project, presets and fonts are still there. If not, Task 1 is at fault.

---

## Notes on deviations from the spec

- The spec sketched `paths.py` as the module constants `DATA_DIR` and `FONTS_DIR`. The plan uses the functions `data_dir()` and `fonts_dir()` instead, because constants captured at import time would force module reloading in tests.
- The spec did not settle how the application source reaches the image. The Docker build context is the add-on directory only, so the Dockerfile clones the repository from GitHub at `CATLABEL_REF`. That is why Task 5 ends with a push.
