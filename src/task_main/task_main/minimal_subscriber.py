import rclpy
from rclpy.node import Node

from vision_msgs.msg import BoundingBoxArray

from geometry_msgs.msg import Twist
import time

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            BoundingBoxArray,
            '/main_camera/detection/bounding_boxes',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        #publisher
        self.publisher = self.create_publisher(Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)
        self.create_timer(0.1, self.timer_callback)

        self.duration_seconds = 2.0
        self.start_time = time.time() #to set the time last seen gate
        self.finished = False
        self.angularz = 0.8
        self.linearx = 0.0
        self.lineary = 0.0
        self.linearz = 0.0

    def listener_callback(self, msg: BoundingBoxArray):
        gatebox=None
        flarebox=None
        #self.get_logger().info(f"{msg.bounding_boxes}")
        for box in msg.bounding_boxes:
            if box.label_name == 'gate' and box.h>0.1 and box.w>0.1 : #detect the full gate rather than the gate pole
                gatebox=box
                self.start_time = time.time() #set the time last seen gate
            elif box.label_name == 'red_flare' and box.h > 0.3: #flarebox is tall, to prevent the one far away to be detected 
                flarebox=box

        if gatebox is not None: # once gate is detected 
            if 0.45<=gatebox.x<=0.55: #gate is middle
                self.linearx = 0.8 # go straight
                self.angularz = 0.0
            elif gatebox.x<0.45: #gate is left
                self.angularz = 0.5 #turn left
                self.lineary = 0.2 #move left
            elif gatebox.x>0.55: #gate is right
                self.angularz=-0.5 #turn right
                self.lineary = -0.2 #move right

            if 0.40<=gatebox.y<=0.50: #gate is middle
                self.linearz = 0.0
            elif gatebox.y>0.50: # gate is below
                self.linearz = -0.5 # move down
            elif gatebox.y<0.40: # gate is above, typically gate will not be above
                 self.linearz = 0.5 # move up
            self.get_logger().info(f"gatebox:{gatebox.x, gatebox.y}")
        else:
            self.get_logger().info('gate not found')
        
        #obstacle avoidance
        self.lineary = 0.0 #stop sideways movement if flare is at the side
        if self.linearx>0 and flarebox is not None: #if auv moving straight
            if 0.50<=flarebox.x<=0.75: # flare in the middle right
                self.lineary = 0.7 #move left
            elif 0.25<=flarebox.x<0.50: #flare in middle left
                self.lineary = -0.7 #move right
            self.get_logger().info(f"flarebox:{flarebox.x, flarebox.y, flarebox.h}")

    def timer_callback(self):
        elapsed = time.time() - self.start_time
        if self.linearx>0 and elapsed >= self.duration_seconds: # if last seen gate time > 2 second, gate has been passed thru
            self.get_logger().info('Publishing complete. Shutting down node.')
            self.finished = True #to indicate to stop while loop for rclpy.spin_once
            return

        msg = Twist()
        msg.linear.x = self.linearx   # Set forward/backward velocity
        msg.linear.y = self.lineary   # Set left(+)/right(-) velocity
        msg.linear.z = self.linearz   # Set up(+)/down(-) velocity
        msg.angular.x = 0.0  # Not used
        msg.angular.y = 0.0  # Not used
        msg.angular.z = self.angularz  # Set left(+)/right(-) yaw

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)

    node = MinimalSubscriber()

    while rclpy.ok() and not node.finished:
        rclpy.spin_once(node, timeout_sec=None)
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()