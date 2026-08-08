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
