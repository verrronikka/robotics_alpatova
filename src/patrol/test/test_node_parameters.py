"""Test runtime parameter changes and timer preservation."""

from patrol.patrol import Patrol
import pytest
import rclpy
from rclpy.parameter import Parameter


@pytest.fixture
def patrol_node():
    """Create an isolated node and release its ROS resources."""
    rclpy.init()
    node = None
    try:
        node = Patrol()
        yield node
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


def test_frequency_change_replaces_timer(patrol_node):
    """Change ten hertz to five while keeping exactly one timer."""
    node = patrol_node
    old_timer = node.timer
    assert old_timer.timer_period_ns == 100_000_000

    result = node.set_parameters_atomically([
        Parameter('publish_hz', value=5.0),
    ])

    assert result.successful, result.reason
    assert node.get_parameter('publish_hz').value == 5.0
    assert node.publish_hz == 5.0
    assert node.timer is not old_timer
    assert node.timer.timer_period_ns == 200_000_000
    assert not node.timer.is_canceled()
    assert list(node.timers) == [node.timer]


@pytest.mark.parametrize('invalid_hz', [0.0, -1.0, float('nan')])
def test_invalid_frequency_preserves_timer(patrol_node, invalid_hz):
    """Reject invalid frequency without changing the active timer."""
    node = patrol_node
    result = node.set_parameters_atomically([
        Parameter('publish_hz', value=5.0),
    ])
    assert result.successful, result.reason
    old_timer = node.timer

    result = node.set_parameters_atomically([
        Parameter('publish_hz', value=invalid_hz),
    ])

    assert not result.successful
    assert result.reason
    assert node.get_parameter('publish_hz').value == 5.0
    assert node.publish_hz == 5.0
    assert node.timer is old_timer
    assert node.timer.timer_period_ns == 200_000_000
    assert not node.timer.is_canceled()
    assert list(node.timers) == [old_timer]


def test_speed_change_preserves_timer(patrol_node):
    """Apply new command settings without replacing the timer."""
    node = patrol_node
    old_timer = node.timer

    result = node.set_parameters_atomically([
        Parameter('linear_speed', value=0.8),
        Parameter('turn_rate', value=-0.4),
    ])

    assert result.successful, result.reason
    assert node.linear_speed == 0.8
    assert node.turn_rate == -0.4
    assert node.get_parameter('linear_speed').value == 0.8
    assert node.get_parameter('turn_rate').value == -0.4
    assert node.timer is old_timer
    assert list(node.timers) == [old_timer]


def test_invalid_batch_preserves_all_settings(patrol_node):
    """Reject the whole atomic request if one setting is invalid."""
    node = patrol_node
    old_timer = node.timer

    result = node.set_parameters_atomically([
        Parameter('publish_hz', value=5.0),
        Parameter('linear_speed', value=2.0),
    ])

    assert not result.successful
    assert node.get_parameter('publish_hz').value == 10.0
    assert node.get_parameter('linear_speed').value == 0.5
    assert node.publish_hz == 10.0
    assert node.linear_speed == 0.5
    assert node.timer is old_timer
    assert node.timer.timer_period_ns == 100_000_000
    assert not node.timer.is_canceled()
    assert list(node.timers) == [old_timer]
