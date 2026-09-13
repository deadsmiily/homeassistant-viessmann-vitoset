"""Vitoset Aqua: read-only water sensors using an existing ViCare connection."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import CONF_SOURCE_ENTRY_ID
from .coordinator import VitosetCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load the companion after its source has finished loading."""
    source = hass.config_entries.async_get_entry(entry.data[CONF_SOURCE_ENTRY_ID])
    if source is None or source.state is not ConfigEntryState.LOADED:
        raise ConfigEntryNotReady("Die ausgewählte ViCare-Verbindung ist noch nicht geladen.")

    coordinator = VitosetCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    @callback
    def source_state_changed() -> None:
        """Stop showing healthy values when the source stops; recover on reload."""
        if source.state is ConfigEntryState.LOADED:
            hass.async_create_task(
                coordinator.async_request_refresh(), "Refresh Vitoset Aqua after ViCare reload"
            )
        else:
            coordinator.async_set_update_error(
                UpdateFailed("Die ViCare-Verbindung ist vorübergehend nicht verfügbar.")
            )

    entry.async_on_unload(source.async_on_state_change(source_state_changed))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload sensors without modifying the ViCare source."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
