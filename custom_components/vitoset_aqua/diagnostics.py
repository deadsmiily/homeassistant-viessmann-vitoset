"""Minimal diagnostics: cached readings and status, without account identifiers."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_MODEL, CONF_SOURCE_ENTRY_ID, UPDATE_SECONDS


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Report only the companion's parsed state; do not request more API data."""
    source = hass.config_entries.async_get_entry(entry.data[CONF_SOURCE_ENTRY_ID])
    coordinator = getattr(entry, "runtime_data", None)
    error = getattr(coordinator, "last_exception", None)
    return {
        "model": entry.data.get(CONF_MODEL),
        "source_state": source.state.value if source is not None else "missing",
        "update_interval_seconds": UPDATE_SECONDS,
        "last_update_success": getattr(coordinator, "last_update_success", False),
        "last_error_type": type(error).__name__ if error is not None else None,
        "readings": getattr(coordinator, "data", None),
    }
