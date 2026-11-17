"""Publish the course robot's coordinate transforms from its Xacro model."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    package_share = Path(get_package_share_directory('course_description'))
    model_path = package_share / 'urdf' / 'vehicle.urdf.xacro'
    robot_description = xacro.process_file(str(model_path)).toxml()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),
    ])
