import re

from deebot_t8 import DeebotEntity
from deebot_t8.entity import VacuumState

from homeassistant.components.vacuum import (
    StateVacuumEntity, SUPPORT_BATTERY,
    SUPPORT_STATE, SUPPORT_SEND_COMMAND, SUPPORT_RETURN_HOME, SUPPORT_PAUSE,
    SUPPORT_LOCATE, SUPPORT_FAN_SPEED, SUPPORT_START, SUPPORT_MAP,
    STATE_RETURNING, STATE_CLEANING, SUPPORT_STOP, SUPPORT_STATUS, ATTR_STATUS)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_IDLE, STATE_PAUSED
from . import DOMAIN, DataEntry
from .const import (
    CLEAN_TYPE_MAP,
    FAN_SPEEDS, FAN_SPEED_NAME_MAP, FAN_SPEED_VALUE_MAP,
    WATER_LEVEL_VALUE_MAP)
from .subscribed_entity_mixin import SubscribedEntityMixin


async def async_setup_entry(hass, config_entry: ConfigEntry,
                            async_add_entities):
    """Add sensors for passed config_entry in HA."""
    entry_data: DataEntry = hass.data[DOMAIN][config_entry.entry_id]
    to_add = []
    for entity in entry_data.entities:
        to_add.append(DeebotT8VacuumEntity(entity))

    async_add_entities(to_add)

    return True


class DeebotT8VacuumEntity(SubscribedEntityMixin, StateVacuumEntity):
    def __init__(self, api_entity: DeebotEntity):
        self.api_entity = api_entity

    @property
    def supported_features(self):
        return (
                SUPPORT_START
                | SUPPORT_STOP
                | SUPPORT_PAUSE
                | SUPPORT_RETURN_HOME
                | SUPPORT_LOCATE
                | SUPPORT_STATE
                | SUPPORT_STATUS
                | SUPPORT_FAN_SPEED
                | SUPPORT_BATTERY
                | SUPPORT_MAP
                | SUPPORT_SEND_COMMAND
        )

    @property
    def fan_speed_list(self):
        """Get the list of available fan speed steps of the vacuum cleaner."""
        return [name for name, _ in FAN_SPEEDS]

    @property
    def state(self):
        if self.api_entity.state.state == VacuumState.RobotState.IDLE:
            return STATE_IDLE
        elif self.api_entity.state.state == VacuumState.RobotState.PAUSED:
            return STATE_PAUSED
        elif self.api_entity.state.state == VacuumState.RobotState.RETURNING:
            return STATE_RETURNING
        elif self.api_entity.state.state == VacuumState.RobotState.CLEANING:
            return STATE_CLEANING
        else:
            return None

    @property
    def status(self):
        return 'Charging' if self.api_entity.state.is_charging else None

    def start(self):
        if self.api_entity.state.state == VacuumState.RobotState.PAUSED:
            self.api_entity.resume()
        else:
            self.api_entity.clean()

    def pause(self):
        self.api_entity.pause()

    def stop(self, **kwargs):
        self.api_entity.stop()

    def return_to_base(self, **kwargs):
        self.api_entity.return_to_charge()

    def locate(self, **kwargs):
        self.api_entity.relocate()

    def set_fan_speed(self, fan_speed, **kwargs):
        self.api_entity.set_vacuum_speed(FAN_SPEED_VALUE_MAP[fan_speed])

    @property
    def fan_speed(self):
        """Return the fan speed of the vacuum cleaner."""
        if self.api_entity.state.vacuum_speed is not None:
            return FAN_SPEED_NAME_MAP[self.api_entity.state.vacuum_speed]

    def send_command(self, command, params=None, **kwargs):
        if command in ['clean_areas', 'clean_area']:
            area_ids = params['area_ids']
            self.api_entity.clean_areas(area_ids)

        elif command == 'clean_custom':
            custom_area = params['custom_area']
            self.api_entity.clean_custom(custom_area)

        elif command == 'set_water_level':
            water_level = params['water_level']
            level_value = list(WATER_LEVEL_VALUE_MAP.values())[water_level - 1]
            self.api_entity.set_water_level(level_value)

        elif command == 'set_clean_count':
            clean_count = params['clean_count']
            self.api_entity.set_clean_count(clean_count)

        elif command == 'play_sound':
            sound_id = None
            if params is not None:
                sound_id = params.get('sound_id')

            self.api_entity.play_sound(sound_id)

        else:
            raise Exception("Unhandled command: {}".format(command))

    @property
    def unique_id(self) -> str:
        return self.api_entity._device.id

    @property
    def name(self) -> str:
        return self.api_entity._device.name

    @property
    def battery_level(self):
        return self.api_entity.state.battery_level

    @property
    def state_attributes(self):
        vacuum_speed = None
        water_level = None
        if self.api_entity.state.vacuum_speed is not None:
            vacuum_speed = self.api_entity.state.vacuum_speed.value
        if self.api_entity.state.water_level is not None:
            water_level = self.api_entity.state.water_level.value

        attrs = {
            **super(DeebotT8VacuumEntity, self).state_attributes,
            ATTR_STATUS: self.status,
            'water_level': water_level,
            'vacuum_speed': vacuum_speed,
            'mop_attached': self.api_entity.state.mop_attached,
            'is_charging': self.api_entity.state.is_charging,
            'clean_type': CLEAN_TYPE_MAP.get(self.api_entity.state.clean_type),
            'clean_count': self.api_entity.state.clean_count,
            'true_detect_enabled': self.api_entity.state.true_detect_enabled,
            'cleaning_preference_enabled': self.api_entity.state.cleaning_preference_enabled,
        }

        if self.api_entity.state.lifespan is not None:
            for lifespan in self.api_entity.state.lifespan:
                component_snake = re.sub(
                    r'(?<!^)(?=[A-Z])', '_', lifespan.component).lower()
                perc = round(lifespan.left / lifespan.total * 100, 1)
                attrs[f'lifespan_{component_snake}'] = f'{perc}%'

        return attrs
