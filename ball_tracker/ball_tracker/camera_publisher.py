import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import cv2
from cv_bridge import CvBridge


class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        self.publisher = self.create_publisher(CompressedImage, '/camera/image_raw', 10)
        
        br = CvBridge()
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2) 

        if not cap.isOpened():
            print("Error: Could not open camera.")
        else:
            while True:
                ret, frame = cap.read()
                if ret:
                    img = br.cv2_to_imgmsg(frame)
                    self.publisher.publish(img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    camera = CameraNode()
    rclpy.spin(camera)
    camera.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()