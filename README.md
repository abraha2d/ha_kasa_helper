# Home Assistant Kasa Helper

A set of helper actions to use with TP-Link Kasa devices.

## Usage

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=abraha2d&repository=ha_kasa_helper)

### Manual install

1. Upload the contents of `custom_components/kasa_helper/` in this repository to
   `/config/custom_components/kasa_helper/`.

2. Add the following to `/config/configuration.yaml`:

   ```yml
   kasa_helper:
   ```

3. Restart Home Assistant

## Helpers

### set_brightness

Sets the brightness of a Kasa dimmer without turning it on.
