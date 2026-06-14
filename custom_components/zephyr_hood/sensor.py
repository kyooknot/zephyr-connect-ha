"""Sensor platform for the Zephyr Hood integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ZephyrEntity


@dataclass(frozen=True, kw_only=True)
class ZephyrSensorDescription:
    key: str
    name: str
    field: str
    icon: str | None = None


# Cumulative runtime counters reported by the hood, in minutes.
USAGE_SENSORS: tuple[ZephyrSensorDescription, ...] = (
    ZephyrSensorDescription(
        key="grease_filter_usage",
        name="Grease filter usage",
        field="usegreasefiltertime",
        icon="mdi:air-filter",
    ),
    ZephyrSensorDescription(
        key="charcoal_filter_usage",
        name="Charcoal filter usage",
        field="usecharcoalfiltertime",
        icon="mdi:air-filter",
    ),
    ZephyrSensorDescription(
        key="fan_runtime",
        name="Fan runtime",
        field="usefantime",
        icon="mdi:fan-clock",
    ),
    ZephyrSensorDescription(
        key="light_runtime",
        name="Light runtime",
        field="uselighttime",
        icon="mdi:lightbulb-on-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []
    for thing in coordinator.devices:
        entities.extend(ZephyrUsageSensor(coordinator, thing, desc) for desc in USAGE_SENSORS)
        entities.append(ZephyrFaultSensor(coordinator, thing))
    async_add_entities(entities)


class ZephyrUsageSensor(ZephyrEntity, SensorEntity):
    """A cumulative runtime counter (filter life / fan / light hours)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator, thing: str, desc: ZephyrSensorDescription) -> None:
        super().__init__(coordinator, thing)
        self._desc = desc
        self._attr_name = desc.name
        self._attr_icon = desc.icon
        self._attr_unique_id = f"{thing}_{desc.key}"

    @property
    def native_value(self) -> int | None:
        value = self._reported.get(self._desc.field)
        return None if value is None else int(value)


class ZephyrFaultSensor(ZephyrEntity, SensorEntity):
    """Reported fault code(s); 'OK' when the hood reports none."""

    _attr_name = "Fault code"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, thing: str) -> None:
        super().__init__(coordinator, thing)
        self._attr_unique_id = f"{thing}_fault_code"

    @property
    def native_value(self) -> str | None:
        fault = self._reported.get("faultCode")
        if fault is None:
            return None
        if isinstance(fault, (list, tuple)):
            return ", ".join(str(f) for f in fault) if fault else "OK"
        return "OK" if fault in (0, "0", "") else str(fault)
