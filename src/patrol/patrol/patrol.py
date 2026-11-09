"""Publish velocity commands using validated runtime parameters."""

from geometry_msgs.msg import Twist
from patrol.parameters import validate_values
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


def command_from_pose(pose, linear_speed=0.5, turn_rate=0.3):
    """Return a new velocity command without changing the input pose."""
    command = Twist()
    if pose is not None:
        command.linear.x = linear_speed
        command.angular.z = turn_rate
    return command


class Patrol(Node):
    """Store the latest pose and publish configurable velocity commands."""

    def __init__(self):
        super().__init__('patrol')

        self.declare_parameter('publish_hz', 10.0)
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)

        self.publish_hz = self.get_parameter('publish_hz').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.turn_rate = self.get_parameter('turn_rate').value

        accepted, reason = validate_values(
            self.publish_hz, self.linear_speed, self.turn_rate,
        )
        if not accepted:
            self.destroy_node()
            raise ValueError(reason)

        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10,
        )
        self.command_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(
            1.0 / self.publish_hz, self.on_timer,
        )

        self.add_on_set_parameters_callback(self.validate_parameters)
        self.add_post_set_parameters_callback(self.apply_parameters)

    def validate_parameters(self, updates):
        """Check proposed settings without changing active state."""
        proposed = {parameter.name: parameter.value for parameter in updates}
        accepted, reason = validate_values(
            proposed.get('publish_hz', self.publish_hz),
            proposed.get('linear_speed', self.linear_speed),
            proposed.get('turn_rate', self.turn_rate),
        )
        return SetParametersResult(successful=accepted, reason=reason)

    def apply_parameters(self, updates):
        """Apply accepted settings and replace the timer if needed."""
        old_hz = self.publish_hz

        for parameter in updates:
            if parameter.name in ('publish_hz', 'linear_speed', 'turn_rate'):
                setattr(self, parameter.name, parameter.value)

        if self.publish_hz != old_hz:
            self.timer.cancel()
            self.destroy_timer(self.timer)
            self.timer = self.create_timer(
                1.0 / self.publish_hz, self.on_timer,
            )

    def on_pose(self, message):
        """Store the latest pose."""
        self.latest_pose = message

    def on_timer(self):
        """Publish a command using the latest pose and accepted settings."""
        command = command_from_pose(
            self.latest_pose, self.linear_speed, self.turn_rate,
        )
        self.command_pub.publish(command)


def main(args=None):
    """Initialize ROS, process events, and release resources."""
    rclpy.init(args=args)
    node = None
    try:
        node = Patrol()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
