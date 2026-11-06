"""Publish timed velocity commands using the latest turtlesim pose."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


def command_from_pose(pose):
    """Return a new velocity command without changing the input pose."""
    command = Twist()
    if pose is not None:
        command.linear.x = 0.5
        command.angular.z = 0.3
    return command


class Patrol(Node):
    """Store pose messages and publish commands every 0.1 seconds."""

    def __init__(self):
        super().__init__('patrol')
        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10,
        )
        self.command_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_pose(self, message):
        """Store the latest pose."""
        self.latest_pose = message

    def on_timer(self):
        """Publish a command selected from the latest pose."""
        command = command_from_pose(self.latest_pose)
        self.command_pub.publish(command)


def main(args=None):
    """Initialize ROS, process events, and release resources."""
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
