"""Observe a pose stream using configurable reliability."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


class PoseSubscriber(Node):
    """Count received poses and report progress once per second."""

    def __init__(self):
        super().__init__('pose_subscriber')

        reliability = self.declare_parameter(
            'subscriber_reliability', 'best_effort',
        ).value
        policies = {
            'reliable': ReliabilityPolicy.RELIABLE,
            'best_effort': ReliabilityPolicy.BEST_EFFORT,
        }
        if reliability not in policies:
            self.destroy_node()
            raise ValueError(
                'subscriber_reliability must be reliable or best_effort',
            )

        self.received = 0
        qos = QoSProfile(
            depth=10,
            reliability=policies[reliability],
            durability=DurabilityPolicy.VOLATILE,
        )
        self.pose_sub = self.create_subscription(
            Pose, 'sensor_pose', self.on_pose, qos,
        )
        self.timer = self.create_timer(1.0, self.report_received)
        self.get_logger().info(
            f'Subscribing to sensor_pose with {reliability} QoS',
        )

    def on_pose(self, message):
        """Count each delivered pose."""
        self.received += 1

    def report_received(self):
        """Log the total number of received poses."""
        self.get_logger().info(f'received={self.received}')


def main(args=None):
    """Initialize ROS, observe messages, and release resources."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseSubscriber()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
