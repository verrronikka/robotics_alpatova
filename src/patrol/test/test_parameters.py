"""Test patrol parameter validation without starting ROS."""

from patrol.parameters import validate_values
import pytest


@pytest.mark.parametrize('hz, speed, turn', [
    (10.0, 0.5, 0.3),
    (5.0, 0.5, 0.3),
    (1.0, 0.0, -1.0),
    (30.0, 1.0, 1.0),
])
def test_valid_values(hz, speed, turn):
    """Accept defaults, five hertz, and inclusive range boundaries."""
    accepted, reason = validate_values(hz, speed, turn)

    assert accepted
    assert reason == ''


@pytest.mark.parametrize('hz, speed, turn', [
    (0.0, 0.5, 0.3),
    (-1.0, 0.5, 0.3),
    (0.99, 0.5, 0.3),
    (30.01, 0.5, 0.3),
    (float('nan'), 0.5, 0.3),
    (float('inf'), 0.5, 0.3),
    (float('-inf'), 0.5, 0.3),
    (10.0, -0.01, 0.3),
    (10.0, 1.01, 0.3),
    (10.0, float('nan'), 0.3),
    (10.0, float('inf'), 0.3),
    (10.0, 0.5, -1.01),
    (10.0, 0.5, 1.01),
    (10.0, 0.5, float('nan')),
    (10.0, 0.5, float('inf')),
    (True, 0.5, 0.3),
    ('5.0', 0.5, 0.3),
])
def test_invalid_values(hz, speed, turn):
    """Reject invalid settings and explain the rejection."""
    accepted, reason = validate_values(hz, speed, turn)

    assert not accepted
    assert reason
