"""The Deebot T8 integration."""
from __future__ import annotations

from typing import NamedTuple, List

from deebot_t8 import (
    ApiClient, SubscriptionClient, PortalClient,
    DeebotAuthClient, DeebotEntity, Credentials)
from deebot_t8.auth_client import Authenticator

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN, ATTR_PASSWORD_HASH, ATTR_EMAIL, ATTR_COUNTRY,
    ATTR_CONTINENT, ATTR_DEVICE_ID, ATTR_CREDENTIALS)

PLATFORMS = ["vacuum", "switch", "binary_sensor", "sensor"]


class Services(NamedTuple):
    auth: DeebotAuthClient
    api: ApiClient
    subs: SubscriptionClient


class DataEntry(NamedTuple):
    services: Services
    entities: List[DeebotEntity]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Deebot component."""
    # Ensure our name space for storing objects is a known type. A dict is
    # common/preferred as it allows a separate instance of your class for each
    # instance that has been created in the UI.
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Deebot T8 from a config entry."""
    device_id = entry.data[ATTR_DEVICE_ID]
    account_id = entry.data[ATTR_EMAIL]
    password_hash = entry.data[ATTR_PASSWORD_HASH]
    country = entry.data[ATTR_COUNTRY]
    continent = entry.data[ATTR_CONTINENT]

    credentials_data = entry.data.get(ATTR_CREDENTIALS)
    credentials = None
    if credentials_data is not None:
        credentials = Credentials(*credentials_data)

    def on_credentials_changed(new_credentials: Credentials):
        hass.config_entries.async_update_entry(entry, data={
            **entry.data,
            ATTR_CREDENTIALS: new_credentials
        })

    portal_client = PortalClient(
        device_id=device_id,
        country=country,
        continent=continent,
    )
    auth_client = DeebotAuthClient(
        portal_client=portal_client,
        device_id=device_id,
        country=country,
    )
    authenticator = Authenticator(
        auth_client=auth_client,
        country=country,
        device_id=device_id,
        account_id=account_id,
        password_hash=password_hash,
        cached_credentials=credentials,
        on_credentials_changed=on_credentials_changed,
    )
    api_client = ApiClient(
        portal_client=portal_client,
        authenticator=authenticator,
    )
    subscription_client = SubscriptionClient(
        authenticator=authenticator,
        continent=continent,
        device_id=device_id,
    )

    devices = await hass.async_add_executor_job(
        api_client.get_devices_list
    )

    entities = []
    for d in devices:
        entity = DeebotEntity(
            api_client=api_client,
            subs_client=subscription_client,
            device=d)
        entities.append(entity)

    hass.data[DOMAIN][entry.entry_id] = DataEntry(
        services=Services(
            auth=auth_client,
            api=api_client,
            subs=subscription_client,
        ),
        entities=entities
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry,
                                                                 PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
