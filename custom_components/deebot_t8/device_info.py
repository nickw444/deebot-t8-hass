from deebot_t8 import DeebotEntity

from homeassistant.const import (
    ATTR_SW_VERSION, ATTR_MANUFACTURER, ATTR_MODEL,
    ATTR_IDENTIFIERS, ATTR_NAME)
from homeassistant.helpers.entity import DeviceInfo
from . import DOMAIN


def get_device_info(entity: DeebotEntity) -> DeviceInfo:
    return {
        ATTR_NAME: entity._device.name,
        ATTR_IDENTIFIERS: {
            (DOMAIN, entity._device.id),
            (DOMAIN, entity._device.id_short)
        },
        ATTR_MODEL: entity._device.model_name,
        ATTR_MANUFACTURER: 'Ecovacs',
        ATTR_SW_VERSION: entity.state.firmware_version,
    }
