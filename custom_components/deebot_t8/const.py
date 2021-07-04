"""Constants for the Deebot T8 integration."""
from deebot_t8.entity import VacuumState

DOMAIN = "deebot_t8"

ATTR_EMAIL = "email"
ATTR_PASSWORD = "password"
ATTR_PASSWORD_HASH = "password_hash"
ATTR_COUNTRY = "country"
ATTR_CONTINENT = "continent"
ATTR_DEVICE_ID = "device_id"
ATTR_CREDENTIALS = "credentials"

# CH: msg.ecouser.net
# TW, MY, JP, SG, TH, HK, IN, KR: msg-as.ecouser.net
# US: msg-na.ecouser.net
# FR, ES, UK, NO, MX, DE, PT, CH, AU, IT, NL, SE, BE, DK: msg-eu.ecouser.net
# Any other country: msg-ww.ecouser.net

SERVER_COUNTRIES = [
    "CH",
    "TW", "MY", "JP", "SG", "TH", "HK", "IN", "KR",
    "US",
    "FR", "ES", "UK", "NO", "MX", "DE", "PT", "CH", "AU", "IT", "NL", "SE",
    "BE", "DK",
]
SERVER_CONTINENTS = [
    "CN",
    "AS",
    "NA",
    "EU",
    "WW"
]

FAN_SPEEDS = [
    ('Quiet', VacuumState.Speed.QUIET),
    ('Standard', VacuumState.Speed.STANDARD),
    ('Max', VacuumState.Speed.MAX),
    ('Max+', VacuumState.Speed.MAX_PLUS),
]

WATER_LEVELS = [
    ('Low', VacuumState.WaterFlow.LOW),
    ('Medium', VacuumState.WaterFlow.MEDIUM),
    ('High', VacuumState.WaterFlow.HIGH),
    ('Ultra High', VacuumState.WaterFlow.ULTRA_HIGH),
]

FAN_SPEED_NAME_MAP = {value: name for name, value in FAN_SPEEDS}
FAN_SPEED_VALUE_MAP = {name: value for name, value in FAN_SPEEDS}

WATER_LEVEL_NAME_MAP = {value: name for name, value in WATER_LEVELS}
WATER_LEVEL_VALUE_MAP = {name: value for name, value in WATER_LEVELS}

CLEAN_TYPE_MAP = {
    VacuumState.CleanType.AUTO: 'Auto',
    VacuumState.CleanType.SPOT_AREA: 'Spot Area',
    VacuumState.CleanType.CUSTOM_AREA: 'Custom Area',
    None: 'N/A',
}

SERVICE_SET_WATER_LEVEL = 'set_water_level'
