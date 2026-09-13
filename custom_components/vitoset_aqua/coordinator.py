"""Poll water features through the already authenticated ViCare client."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_DEVICE_KEY, CONF_SOURCE_ENTRY_ID, UPDATE_SECONDS
from .source import SourceUnavailable, find_aqua
from .water_data import parse_water_features

_LOGGER = logging.getLogger(__name__)


def read_device(device: Any) -> dict[str, float | None]:
    """Run only in an executor: the source may synchronously refresh OAuth.

    Match the official coordinator's cache invalidation. Otherwise PyViCare
    may silently return old cached readings after communication failures.
    """
    device.service.clear_cache()
    payload = device.get_raw_json()
    return parse_water_features(payload, str(device.getId()))


class VitosetCoordinator(DataUpdateCoordinator[dict[str, float | None]]):
    """One shared request supplies all five sensors every five minutes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Vitoset Aqua",
            config_entry=entry,
            update_interval=timedelta(seconds=UPDATE_SECONDS),
            always_update=False,
        )
        self.entry = entry

    async def _async_update_data(self) -> dict[str, float | None]:
        try:
            device = find_aqua(
                self.hass,
                self.entry.data[CONF_SOURCE_ENTRY_ID],
                self.entry.data[CONF_DEVICE_KEY],
            )
            values = await self.hass.async_add_executor_job(read_device, device)
            # The source can reload while its blocking HTTP request is running.
            # Do not publish an old result as healthy after that transition.
            current_device = find_aqua(
                self.hass,
                self.entry.data[CONF_SOURCE_ENTRY_ID],
                self.entry.data[CONF_DEVICE_KEY],
            )
            if current_device is not device:
                raise SourceUnavailable(
                    "Die ViCare-Verbindung wurde während der Abfrage neu geladen."
                )
        except SourceUnavailable as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            # Do not expose raw API URLs, installation IDs, or auth details.
            # Reauthentication belongs to the source ViCare integration.
            raise UpdateFailed(
                f"ViCare-Wasserwerte konnten nicht gelesen werden ({type(err).__name__}). "
                "Bitte den Status der ViCare-Verbindung prüfen."
            ) from err
        if all(value is None for value in values.values()):
            raise UpdateFailed("Die API liefert derzeit keine gültigen Wasserwerte.")
        return values
