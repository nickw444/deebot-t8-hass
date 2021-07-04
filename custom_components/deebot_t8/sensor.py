from typing import Optional

from deebot_t8 import DeebotEntity

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from . import DataEntry
from .const import (
    DOMAIN, CLEAN_TYPE_MAP, WATER_LEVEL_NAME_MAP, FAN_SPEED_NAME_MAP)
from .subscribed_entity_mixin import SubscribedEntityMixin


async def async_setup_entry(hass, config_entry: ConfigEntry,
                            async_add_entities):
    """Add switches for passed config_entry in HA."""
    entry_data: DataEntry = hass.data[DOMAIN][config_entry.entry_id]
    to_add = []
    for entity in entry_data.entities:
        to_add.extend([
            DeebotGenericSensor(
                entity,
                'Area Cleaned Total',
                "m²",
                'mdi:shape-square-plus',
                lambda: entity.state.total_stats.area if entity.state.total_stats is not None else None,
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Cleaning Time Total',
                'hours',
                'mdi:timer',
                lambda: round(entity.state.total_stats.time / 60 / 60,
                              1) if entity.state.total_stats is not None else None,
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Num Cleans Total',
                'cleanings',
                'mdi:counter',
                lambda: entity.state.total_stats.count if entity.state.total_stats is not None else None,
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Current Clean Type',
                None,
                'mdi:broom',
                lambda: CLEAN_TYPE_MAP.get(entity.state.clean_type),
            ),
            DeebotGenericSensor(
                entity,
                'Area Cleaned',
                "m²",
                'mdi:shape-square-plus',
                lambda: entity.state.clean_stats.area if entity.state.clean_stats is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Cleaning Time',
                "minutes",
                'mdi:timer',
                lambda: round(entity.state.clean_stats.time / 60,
                              1) if entity.state.clean_stats is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Avoid Count',
                "avoidances",
                'mdi:undo-variant',
                lambda: entity.state.clean_stats.avoid_count if entity.state.clean_stats is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Fan Speed',
                None,
                'mdi:weather-windy',
                lambda: FAN_SPEED_NAME_MAP.get(entity.state.vacuum_speed),
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Water Level',
                None,
                'mdi:water',
                lambda: WATER_LEVEL_NAME_MAP.get(entity.state.water_level),
            ),
        ])

    async_add_entities(to_add)
    return True


class DeebotGenericSensor(SubscribedEntityMixin, SensorEntity):
    def __init__(
            self, api_entity: DeebotEntity, attr_name: str,
            unit_of_measurement: Optional[str], icon: str,
            getter, enabled_by_default: bool = True):
        self.api_entity = api_entity
        self.attr_name = attr_name
        self.getter = getter

        self._attr_icon = icon
        self._attr_unit_of_measurement = unit_of_measurement
        self._attr_entity_registry_enabled_default = enabled_by_default

    @property
    def unique_id(self) -> str:
        return self.api_entity._device.id + '_' + self.attr_name

    @property
    def name(self) -> str:
        return self.api_entity._device.name + ' ' + self.attr_name

    @property
    def state(self):
        return self.getter()
