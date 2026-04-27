import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from enum import Enum, auto
from geometry_msgs.msg import Twist
import re

class State(Enum):
    RIGHT = auto()
    LEFT = auto()
    FORWARD = auto()
    BACKWARD = auto()
    IDLE = auto()
    UP = auto()
    DOWN = auto()

class TrackingControllerNode(Node):
    def __init__(self):
        super().__init__('tracking_controller_node')

        self.coord = self.create_subscription(String, '/object_coordinates', self._coord_cb ,10)
        self.cmd = self.create_publisher(Twist, '/cmd_vel', 10)

        self.timer = self.create_timer(0.5, self.update)
        
        self.center = [375, 315]
        self.dead_zone = 30
        
        self.state = State.IDLE

        self.turn_speed = 0.5
        self.fwd_speed = 1.0
        self.tilt_speed = 0.2


    def _coord_cb(self, msg: String):
        text = msg.data

        x     = int(re.search(r'x:\s*(\d+)', text).group(1))
        y     = int(re.search(r'y:\s*(\d+)', text).group(1))
        area  = int(re.search(r'area:\s*(\d+)', text).group(1))

        dx = x - self.image_center[0]
        dy = y - self.image_center[1] 

        self.dead_zone_x = 30   # horizontal 
        self.dead_zone_y = 60   # vertical 

        # Left/Right
        if abs(dx) > self.dead_zone_x:
            self.state = State.RIGHT if dx > 0 else State.LEFT
        #Up/Down
        elif abs(dy) > self.dead_zone_y:
            self.state = State.DOWN if dy > 0 else State.UP
        # Forward/Backward based on bounding box size
        elif area < 8000:
            self.state = State.FORWARD   # ball is far, move closer
        elif area > 20000:
            self.state = State.BACKWARD  # ball is too close, back up
        else:
            self.state = State.IDLE

        self.get_logger().info(f"x={x} y={y} area={area} state={self.state}")

    def update(self):
        twist = Twist()

        if self.state == State.RIGHT:
            twist.angular.z = -self.turn_speed  # rotate right
        elif self.state == State.LEFT:
            twist.angular.z = self.turn_speed   # rotate left
        elif self.state == State.FORWARD:
            twist.linear.x = self.fwd_speed
        elif self.state == State.BACKWARD:
            twist.linear.x = -self.fwd_speed
        elif self.state == State.UP:
            twist.angular.y = self.tilt_speed   # pitch up
        elif self.state == State.DOWN:
            twist.angular.y = -self.tilt_speed  # pitch down
        elif self.state == State.IDLE:
            pass  

        self.cmd.publish(twist)
        self.state = State.IDLE  # reset until next coord message

def main(args=None):
    rclpy.init(args=args)
    node = TrackingControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()