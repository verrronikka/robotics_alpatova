"""Test velocity selection without starting ROS nodes."""

from patrol.patrol import command_from_pose
import pytest
from turtlesim.msg import Pose


def test_no_pose_returns_zero_command():
    """Return zero in every velocity component before the first pose."""
    command = command_from_pose(None)

    assert (
        command.linear.x,
        command.linear.y,
        command.linear.z,
        command.angular.x,
        command.angular.y,
        command.angular.z,
    ) == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_pose_returns_motion_command():
    """Return the required velocities without modifying the pose."""
    pose = Pose(x=5.0, y=4.0, theta=0.2)
    before = (pose.x, pose.y, pose.theta)

    command = command_from_pose(pose)

    assert command.linear.x == pytest.approx(0.5)
    assert command.angular.z == pytest.approx(0.3)
    assert (
        command.linear.y,
        command.linear.z,
        command.angular.x,
        command.angular.y,
    ) == (0.0, 0.0, 0.0, 0.0)
    assert (pose.x, pose.y, pose.theta) == before
