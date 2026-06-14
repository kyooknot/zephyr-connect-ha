"""Binary sensor platform for the Zephyr Hood integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ZephyrEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []
    for thing in coordinator.devices:
        entities.append(ZephyrOnline(coordinator, thing))
        entities.append(ZephyrGreaseFilterAlarm(coordinator, thing))
        entities.append(ZephyrCharcoalFilterAlarm(coordinator, thing))
    async_add_entities(entities)


class ZephyrOnline(ZephyrEntity, BinarySensorEntity):
    """Cloud connectivity of the hood (reported by the device shadow)."""

    _attr_name = "Online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, thing: str) -> None:
        super().__init__(coordinator, thing)
        self._attr_unique_id = f"{thing}_online"

    @property
    def available(self) -> bool:
        # This sensor reports online/offline, so it must not gate on isOnline.
        return super(ZephyrEntity, self).available

    @property
    def is_on(self) -> bool:
        return self._reported.get("isOnline", 0) not in (0, "0", False, None)


class ZephyrGreaseFilterAlarm(ZephyrEntity, BinarySensorEntity):
    """Grease filter needs cleaning."""

    _attr_name = "Grease filter"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator, thing: str) -> None:
        super().__init__(coordinator, thing)
        self._attr_unique_id = f"{thing}_grease_filter_alarm"

    @property
    def is_on(self) -> bool:
        return int(self._reported.get("alarmgreasefilter", 0) or 0) > 0


class ZephyrCharcoalFilterAlarm(ZephyrEntity, BinarySensorEntity):
    """Charcoal filter needs replacing."""

    _attr_name = "Charcoal filter"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator, thing: str) -> None:
        super().__init__(coordinator, thing)
        self._attr_unique_id = f"{thing}_charcoal_filter_alarm"

    @property
    def is_on(self) -> bool:
        return int(self._reported.get("alarmcharcoalfilter", 0) or 0) > 0
