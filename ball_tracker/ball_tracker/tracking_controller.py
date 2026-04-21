import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from enum import Enum, auto

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
        self.cmd = self.create_publisher(Float64MultiArray, '/forward_command_controller/commands', 10)

        self.timer = self.create_timer(0.1, self.update)
        
        self.center = [375, 315]
        self.dead_zone = 30
        self.state = State.IDLE

    def _coord_cb(self, msg: String):
        text = msg.data
        parts = text.replace("x: ", "").replace("y: ", "").split(",")
        x = int(parts[0].strip())
        y = int(parts[1].strip())

        dx = x - self.image_center[0]
        dy = y - self.image_center[1]

        if abs(dx) > self.dead_zone:
            self.state = State.RIGHT if dx > 0 else State.LEFT
        else:
            self.state = State.IDLE

        self.get_logger().info(f"x={x} y={y} dx={dx} state={self.state}")

        # can maybe implement forward movement based on size of bounding box

    def update(self):
        cmd = Float64MultiArray()

        if self.state == State.RIGHT:
            # turn right — adjust hip joints
            cmd.data = self._turn_command(direction=1)
        elif self.state == State.LEFT:
            cmd.data = self._turn_command(direction=-1)
        elif self.state == State.FORWARD:
            cmd.data = self._forward_command()
        else:
            cmd.data = self._idle_command()

        self.cmd.publish(cmd)
        self.state = State.IDLE  # reset until next coord message

    def _idle_command(self):
        # neutral standing position — 12 joints all zero
        return [0.0] * 12

    def _turn_command(self, direction):
        # joints order: [rf1,rf2,rf3, lf1,lf2,lf3, rb1,rb2,rb3, lb1,lb2,lb3]
        turn = 0.2 * direction
        return [turn, 0.0, 0.0,   # rf
               -turn, 0.0, 0.0,   # lf
                turn, 0.0, 0.0,   # rb
               -turn, 0.0, 0.0]   # lb

    def _forward_command(self):
        return [0.0, 0.1, -0.1,   # rf
                0.0, 0.1, -0.1,   # lf
                0.0, 0.1, -0.1,   # rb
                0.0, 0.1, -0.1]   # lb

def main(args=None):
    rclpy.init(args=args)
    node = TrackingControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()