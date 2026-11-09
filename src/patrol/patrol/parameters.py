"""Validate patrol settings without changing node state."""

import math


def validate_values(publish_hz, linear_speed, turn_rate):
    """Return acceptance and a reason for a proposed configuration."""
    settings = (
        ('publish_hz', publish_hz, 1.0, 30.0),
        ('linear_speed', linear_speed, 0.0, 1.0),
        ('turn_rate', turn_rate, -1.0, 1.0),
    )

    for name, value, minimum, maximum in settings:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f'{name} must be a number'
        if not math.isfinite(value):
            return False, f'{name} must be finite'
        if not minimum <= value <= maximum:
            return False, f'{name} must be in [{minimum}, {maximum}]'

    return True, ''
