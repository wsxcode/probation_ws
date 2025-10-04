#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from mavros_msgs.srv import SetMode

class SetModeClient(Node):
    def __init__(self):
        super().__init__('set_mode_client')
        self.client = self.create_client(SetMode, '/mavros/set_mode')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting...')

    def send_request(self, mode: str):
        req = SetMode.Request()
        req.custom_mode = mode
        req.base_mode = 0  # leave base_mode as 0 unless you need a specific bitmask
        return self.client.call_async(req)

def main():
    if len(sys.argv) < 2:
        print('Usage: set_mode_client.py <MODE_STRING>')
        return

    mode = sys.argv[1]

    rclpy.init()
    client_node = SetModeClient()

    future = client_node.send_request(mode)
    rclpy.spin_until_future_complete(client_node, future)

    try:
        resp = future.result()
        client_node.get_logger().info(f'Service response: {resp}')
    except Exception as e:
        client_node.get_logger().error(f'Service call failed: {e}')

    client_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
