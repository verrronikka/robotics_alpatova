"""Relay turtlesim poses with best-effort reliability."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


class PoseRelay(Node):
    """Forward incoming poses to a sensor-like topic."""

    def __init__(self):
        super().__init__('pose_relay')

        sensor_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.pose_pub = self.create_publisher(
            Pose, 'sensor_pose', sensor_qos,
        )
        self.pose_sub = self.create_subscription(
            Pose, 'pose', self.on_pose, 10,
        )
        self.get_logger().info(
            'Relaying pose to sensor_pose with best_effort QoS',
        )

    def on_pose(self, message):
        """Publish each received pose without changing its contents."""
        self.pose_pub.publish(message)


def main(args=None):
    """Initialize ROS, relay messages, and release resources."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseRelay()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
