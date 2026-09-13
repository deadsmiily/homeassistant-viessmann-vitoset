"""Water consumption, flow, and salt range sensors."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_KEY, CONF_MODEL, DOMAIN
from .coordinator import VitosetCoordinator

DESCRIPTIONS = (
    SensorEntityDescription(
        key="total_liters",
        translation_key="total_liters",
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement="L",
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="today_liters",
        translation_key="today_liters",
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement="L",
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="flow_lpm",
        translation_key="flow_lpm",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement="L/min",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="salt_days",
        translation_key="salt_days",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement="d",
        suggested_display_precision=0,
        icon="mdi:shaker-outline",
    ),
    SensorEntityDescription(
        key="max_flow_lpm",
        translation_key="max_flow_lpm",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement="L/min",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """All sensors share the same coordinator/API request."""
    async_add_entities(
        VitosetSensor(entry.runtime_data, entry, description) for description in DESCRIPTIONS
    )


class VitosetSensor(CoordinatorEntity[VitosetCoordinator], SensorEntity):
    """Expose a validated value and mark missing readings unavailable."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VitosetCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_KEY]}:{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_KEY])},
            name="Vitoset Aqua",
            manufacturer="Viessmann",
            model=entry.data.get(CONF_MODEL, "Vitoset Aqua"),
        )

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get(self.entity_description.key) is not None
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.key)
