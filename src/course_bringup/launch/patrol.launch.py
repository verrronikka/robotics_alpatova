"""Launch turtlesim, patrol, pose relay, subscriber, and optional recording."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    """Describe the system and its configurable launch arguments."""
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')
    sensor_topic = PathJoinSubstitution(['/', namespace, 'sensor_pose'])

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace', default_value='robot_a',
            description='Namespace for patrol and pose processing nodes.',
        ),
        DeclareLaunchArgument(
            'record', default_value='false',
            description='Enable MCAP recording of sensor_pose.',
        ),
        DeclareLaunchArgument(
            'bag_dir', default_value='evidence/pr05/bag',
            description='Output directory for a new bag recording.',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='best_effort',
            choices=['reliable', 'best_effort'],
            description='Reliability requested by the pose subscriber.',
        ),
        LogInfo(msg=[
            'namespace=', namespace,
            ', subscriber_reliability=', subscriber_reliability,
            ', record=', record,
            ', sensor_topic=', sensor_topic,
        ]),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            namespace='/',
            output='screen',
        ),
        Node(
            package='patrol',
            executable='patrol',
            namespace=namespace,
            remappings=[
                ('turtle1/pose', '/turtle1/pose'),
                ('cmd_vel', '/turtle1/cmd_vel'),
            ],
            output='screen',
        ),
        Node(
            package='patrol',
            executable='pose_relay',
            namespace=namespace,
            remappings=[('pose', '/turtle1/pose')],
            output='screen',
        ),
        Node(
            package='patrol',
            executable='pose_subscriber',
            namespace=namespace,
            parameters=[{
                'subscriber_reliability': subscriber_reliability,
            }],
            output='screen',
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-s', 'mcap',
                '-o', bag_dir,
                '--topics', sensor_topic,
            ],
            condition=IfCondition(record),
            output='screen',
        ),
    ])
