"""Choose a Vitoset Aqua from existing ViCare connections."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_DEVICE_KEY, CONF_MODEL, CONF_SOURCE_ENTRY_ID, DOMAIN, SOURCE_DOMAIN
from .source import SourceUnavailable, aqua_devices, device_key


class VitosetAquaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Reuse the account selected in ViCare; no additional login required."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        sources = self.hass.config_entries.async_entries(SOURCE_DOMAIN)
        if not sources:
            return self.async_abort(reason="no_vicare")

        choices: dict[str, str] = {}
        candidates: dict[str, dict[str, str]] = {}
        loaded_source = False
        for source in sources:
            try:
                devices = aqua_devices(self.hass, source.entry_id)
            except SourceUnavailable:
                continue
            loaded_source = True
            for device in devices:
                key = device_key(device)
                choice = f"{source.entry_id}|{key}"
                choices[choice] = f"{source.title} — {device.getModel()}"
                candidates[choice] = {
                    CONF_SOURCE_ENTRY_ID: source.entry_id,
                    CONF_DEVICE_KEY: key,
                    CONF_MODEL: str(device.getModel()),
                }

        if not choices:
            return self.async_abort(reason="no_aqua" if loaded_source else "vicare_not_ready")

        errors = {}
        if user_input is not None:
            selected = candidates.get(user_input.get("device", ""))
            if selected is None:
                errors["base"] = "device_unavailable"
            else:
                await self.async_set_unique_id(selected[CONF_DEVICE_KEY])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Vitoset Aqua", data=selected)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("device", default=next(iter(choices))): vol.In(choices)}
            ),
            errors=errors,
        )
