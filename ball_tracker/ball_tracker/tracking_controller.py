import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from enum import Enum, auto
from geometry_msgs.msg import Twist

class State(Enum):
    RIGHT = auto()
    LEFT = auto()
    FORWARD = auto()
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


    def _coord_cb(self, msg: String):
        text = msg.data
        parts = text.replace("x: ", "").replace("y: ", "").split(",")
        x = int(parts[0].strip())
        y = int(parts[1].strip())

        dx = x - self.center[0]
        dy = y - self.center[1]

        if abs(dx) > self.dead_zone:
            self.state = State.RIGHT if dx > 0 else State.LEFT
        else:
            self.state = State.IDLE

        self.get_logger().info(f"x={x} y={y} dx={dx} state={self.state}")

        # can maybe implement forward movement based on size of bounding box

    def update(self):
        twist = Twist()

        if self.state == State.RIGHT:
            twist.angular.z = -self.turn_speed  # rotate right
        elif self.state == State.LEFT:
            twist.angular.z = self.turn_speed   # rotate left
        elif self.state == State.FORWARD:
            twist.linear.x = self.fwd_speed
        elif self.state == State.IDLE:
            pass  # all zeros = stop

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