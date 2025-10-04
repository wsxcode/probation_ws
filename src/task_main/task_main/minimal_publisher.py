#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class MinimalPublisher(Node):
    def __init__(self, duration_seconds=3.0):
        super().__init__('minimal_publisher')
        self.publisher = self.create_publisher(Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)
        self.create_timer(0.2, self.timer_callback)

        self.duration_seconds = duration_seconds
        self.start_time = time.time()
        self.finished = False

    def timer_callback(self):
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration_seconds:
            self.get_logger().info('Publishing complete. Shutting down node.')
            self.finished = True
            #rclpy.shutdown()
            return

        msg = Twist()
        msg.linear.x = 0.0   # Set forward/backward velocity
        msg.linear.y = 0.0   # Set left(+)/right(-) velocity
        msg.linear.z = 0.0   # Set up(+)/down(-) velocity
        msg.angular.x = 0.0  # Not used
        msg.angular.y = 0.0  # Not used
        msg.angular.z = 0.0  # Set left(+)/right(-) yaw

        if elapsed < self.duration_seconds-0.3:
            msg.linear.z = -0.9  # First 2.7 seconds: Down
        else:
            msg.linear.z = 0.0  # after 2.7 seconds stop

        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing for {elapsed:.2f}s, Twist: {msg}') # msg.linear.x / msg.angular

def main(args=None):
    rclpy.init(args=args)
    node = MinimalPublisher(duration_seconds=2.9)
    while rclpy.ok() and not node.finished:
        rclpy.spin_once(node, timeout_sec=None)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
