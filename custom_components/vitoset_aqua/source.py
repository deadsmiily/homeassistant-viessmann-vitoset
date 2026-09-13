"""Resolve the existing ViCare connection without copying credentials."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .const import SOURCE_DOMAIN


class SourceUnavailable(Exception):
    """The configured ViCare source is absent, stopped, or incompatible."""


def device_key(device: Any) -> str:
    """Identify a device across reloads and distinct gateways/installations."""
    accessor = device.getConfig()
    return f"{accessor.id}:{accessor.serial}:{accessor.device_id}"


def is_aqua(device: Any) -> bool:
    """Include the water softener that PyViCare excludes from client.devices."""
    return (
        str(device.getDeviceType()).lower() == "watersoftener"
        or "vitosetaqua" in str(device.getModel()).lower()
    )


def aqua_devices(hass: HomeAssistant, source_entry_id: str) -> list[Any]:
    """Read the live source each time so a ViCare reload is handled naturally."""
    entry = hass.config_entries.async_get_entry(source_entry_id)
    if entry is None or entry.domain != SOURCE_DOMAIN:
        raise SourceUnavailable("Die ausgewählte ViCare-Verbindung wurde entfernt.")
    if entry.state is not ConfigEntryState.LOADED:
        raise SourceUnavailable("Die ausgewählte ViCare-Verbindung ist nicht geladen.")
    runtime = getattr(entry, "runtime_data", None)
    client = getattr(runtime, "client", None)
    devices = getattr(client, "all_devices", None)
    if devices is None:
        raise SourceUnavailable("Die ViCare-Version bietet keine vollständige Geräteliste.")
    return [device for device in devices if is_aqua(device)]


def find_aqua(hass: HomeAssistant, source_entry_id: str, key: str) -> Any:
    """Resolve the selected physical device in the current source instance."""
    for device in aqua_devices(hass, source_entry_id):
        if device_key(device) == key:
            return device
    raise SourceUnavailable("Die ausgewählte Vitoset Aqua fehlt in der ViCare-Verbindung.")
