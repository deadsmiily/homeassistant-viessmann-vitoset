"""Validate the small, read-only subset of Viessmann water features we use."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

FIELDS = {
    "total_liters": ("water.consumption.summary", "total", "liter"),
    "today_liters": ("water.consumption.summary", "currentDay", "liter"),
    "flow_lpm": ("water.consumption.flow.current", "value", "liter/minute"),
    "salt_days": ("water.softener.salt.level.days", "remaining", "days"),
    "max_flow_lpm": ("water.consumption.flow.max", "value", "liter/minute"),
}


def parse_water_features(
    payload: Mapping[str, Any], device_id: str
) -> dict[str, float | None]:
    """Return validated values; unavailable/malformed measurements stay None.

    Filtering by deviceId also handles a future gateway-wide API response.
    Numeric zero is a valid reading, but never a fallback for missing data.
    """
    if not isinstance(payload, Mapping) or not isinstance(payload.get("data"), list):
        raise ValueError("Expected a Viessmann features response with a data list")

    features = {}
    for feature in payload["data"]:
        if not isinstance(feature, Mapping):
            continue
        if "deviceId" in feature and str(feature["deviceId"]) != str(device_id):
            continue
        name = feature.get("feature")
        if isinstance(name, str):
            features[name] = feature

    values: dict[str, float | None] = dict.fromkeys(FIELDS)
    for key, (feature_name, property_name, unit) in FIELDS.items():
        feature = features.get(feature_name, {})
        if feature.get("isEnabled") is not True or feature.get("isReady") is not True:
            continue
        properties = feature.get("properties")
        if not isinstance(properties, Mapping):
            continue
        prop = properties.get(property_name)
        if not isinstance(prop, Mapping) or prop.get("unit") != unit:
            continue
        value = prop.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        try:
            value = float(value)
        except (OverflowError, ValueError):
            continue
        if math.isfinite(value) and value >= 0:
            values[key] = value
    return values
