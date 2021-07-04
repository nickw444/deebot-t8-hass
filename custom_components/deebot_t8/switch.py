from typing import Any

from deebot_t8 import DeebotEntity

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from . import DataEntry
from .const import DOMAIN
from .subscribed_entity_mixin import SubscribedEntityMixin


async def async_setup_entry(hass, config_entry: ConfigEntry,
                            async_add_entities):
    """Add switches for passed config_entry in HA."""
    entry_data: DataEntry = hass.data[DOMAIN][config_entry.entry_id]
    to_add = []
    for entity in entry_data.entities:
        to_add.extend([
            DeebotGenericSwitch(
                entity,
                'Cleaning Preference',
                'mdi:broom',
                lambda: entity.state.cleaning_preference_enabled,
                lambda enabled: entity.set_clean_preference(enabled)
            ),
            DeebotGenericSwitch(
                entity,
                'TrueDetect',
                'mdi:laser-pointer',
                lambda: entity.state.true_detect_enabled,
                lambda enabled: entity.set_true_detect(enabled)
            ),
            DeebotGenericSwitch(
                entity,
                'Auto Boost Suction',
                'mdi:weather-windy',
                lambda: entity.state.auto_boost_suction_enabled,
                lambda enabled: entity.set_auto_boost_suction(enabled),
                False
            ),
            DeebotGenericSwitch(
                entity,
                'Auto Empty',
                'mdi:delete-restore',
                lambda: entity.state.auto_empty_enabled,
                lambda enabled: entity.set_auto_empty(enabled),
                False,
            )
        ])

    async_add_entities(to_add)
    return True


class DeebotGenericSwitch(SubscribedEntityMixin, SwitchEntity):
    def __init__(self, api_entity: DeebotEntity, attr_name: str, icon: str,
                 getter,
                 setter, enabled_by_default: bool = True):
        self.api_entity = api_entity
        self.attr_name = attr_name
        self.getter = getter
        self.setter = setter
        self._attr_icon = icon
        self._attr_entity_registry_enabled_default = enabled_by_default

    @property
    def unique_id(self) -> str:
        return self.api_entity._device.id + '_' + self.attr_name

    @property
    def name(self) -> str:
        return self.api_entity._device.name + ' ' + self.attr_name

    def turn_on(self, **kwargs: Any) -> None:
        self.setter(True)

    def turn_off(self, **kwargs: Any) -> None:
        self.setter(False)

    @property
    def is_on(self) -> bool:
        return self.getter()

