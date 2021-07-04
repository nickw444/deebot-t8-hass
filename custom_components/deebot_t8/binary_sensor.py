from deebot_t8 import DeebotEntity

from homeassistant.components.binary_sensor import BinarySensorEntity
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
            DeebotGenericBinarySensor(
                entity,
                'Mop Attached',
                'mdi:water',
                lambda: entity.state.mop_attached,
            ),
            DeebotGenericBinarySensor(
                entity,
                'Charging',
                'mdi:power-plug',
                lambda: entity.state.is_charging,
            ),
        ])

    async_add_entities(to_add)
    return True


class DeebotGenericBinarySensor(SubscribedEntityMixin, BinarySensorEntity):
    def __init__(
            self, api_entity: DeebotEntity, attr_name: str, icon: str,
            getter):
        self.api_entity = api_entity
        self.attr_name = attr_name
        self._icon = icon
        self.getter = getter

    @property
    def unique_id(self) -> str:
        return self.api_entity._device.id + '_' + self.attr_name

    @property
    def name(self) -> str:
        return self.api_entity._device.name + ' ' + self.attr_name

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def is_on(self):
        return self.getter()
