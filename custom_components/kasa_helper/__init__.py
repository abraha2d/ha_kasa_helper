"""The Kasa Helper integration."""

from asyncio import gather
from functools import partial

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import area_registry, device_registry, entity_registry
from homeassistant.config_entries import ConfigEntry

from kasa import (
    DeviceConnectionParameters,
    DeviceConfig,
    Device,
)
from kasa.iot import IotDimmer
from kasa.smart import SmartDevice

from .const import DOMAIN


async def handle_set_brightness(hass: HomeAssistant, call: ServiceCall):
    """Handle the set_brightness service action call."""

    ar = area_registry.async_get(hass)
    dr = device_registry.async_get(hass)
    er = entity_registry.async_get(hass)

    # Targets
    label_ids = call.data.get("label_id", [])
    floor_ids = call.data.get("floor_id", [])
    area_ids = call.data.get("area_id", [])
    device_ids = call.data.get("device_id", [])
    entity_ids = call.data.get("entity_id", [])

    # Get all targeted areas, including those targeted by floor/label
    label_areas = (
        area
        for areas in (
            area_registry.async_entries_for_label(ar, label_id)
            for label_id in label_ids
        )
        for area in areas
    )

    floor_areas = (
        area
        for areas in (
            area_registry.async_entries_for_floor(ar, floor_id)
            for floor_id in floor_ids
        )
        for area in areas
    )

    areas = (
        *label_areas,
        *floor_areas,
        *(a for area_id in area_ids if (a := ar.async_get_area(area_id)) is not None),
    )

    # Get all targeted devices, including those targeted by area/floor/label
    label_devices = (
        device
        for devices in (
            device_registry.async_entries_for_label(dr, label_id)
            for label_id in label_ids
        )
        for device in devices
    )

    area_devices = (
        device
        for devices in (
            device_registry.async_entries_for_area(dr, area.id) for area in areas
        )
        for device in devices
    )

    devices = (
        *label_devices,
        *area_devices,
        *[d for device_id in device_ids if (d := dr.async_get(device_id)) is not None],
    )

    # Get all targeted entities, including those targeted by device/area/floor/label
    label_entities = (
        entity
        for entities in (
            entity_registry.async_entries_for_label(er, label_id)
            for label_id in label_ids
        )
        for entity in entities
    )

    area_entities = (
        entity
        for entities in (
            entity_registry.async_entries_for_area(er, area.id) for area in areas
        )
        for entity in entities
    )

    device_entities = (
        entity
        for entities in (
            entity_registry.async_entries_for_device(er, device.id)
            for device in devices
        )
        for entity in entities
    )

    entities = (
        *label_entities,
        *area_entities,
        *device_entities,
        *(e for entity_id in entity_ids if (e := er.async_get(entity_id)) is not None),
    )

    # Filter targeted entities down to only TP-Link dimmers
    targets = {
        entity.id: entity
        for entity in entities
        if entity.domain == "light"
        and entity.platform == "tplink"
        and entity.capabilities is not None
        and "brightness" in entity.capabilities.get("supported_color_modes", [])
    }

    config_entries = (
        entry
        for target in targets.values()
        if (entry_id := target.config_entry_id) is not None
        and (entry := hass.config_entries.async_get_entry(entry_id)) is not None
    )

    # Use python-kasa to set brightness without turning the dimmers on
    brightness = call.data.get("brightness", 100)

    async def _set_brightness(config_entry: ConfigEntry):
        connection_parameters = config_entry.data.get("connection_parameters", {})
        connection_type = DeviceConnectionParameters.from_dict(connection_parameters)  # type: ignore

        config = DeviceConfig(
            host=config_entry.data.get("host", None),
            credentials_hash=config_entry.data.get("credentials_hash", None),
            connection_type=connection_type,
        )

        device = await Device.connect(config=config)

        if isinstance(device, IotDimmer):
            await device._set_brightness(brightness)  # type: ignore

        elif isinstance(device, SmartDevice) and "Brightness" in device.modules:
            device_info = (await device._query_helper("get_device_info"))["get_device_info"]  # type: ignore

            await device._query_helper(  # type: ignore
                "set_device_info", {
                    "brightness": int(brightness),
                    "device_on": device_info["device_on"],
                },
            )

        else:
            assert False, f"{device} is not a supported dimmer"

    await gather(*(_set_brightness(config_entry) for config_entry in config_entries))


def setup(hass: HomeAssistant, config: ConfigEntry):
    """Set up is called when Home Assistant is loading our component."""

    hass.services.register(
        DOMAIN,
        "set_brightness",
        partial(handle_set_brightness, hass),
    )

    # Return boolean to indicate that initialization was successful.
    return True
