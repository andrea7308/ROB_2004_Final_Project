import cv2
from cv_bridge import CvBridge
import rclpy
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
# from vision_msgs.msg import Image
from std_msgs.msg import String



class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')

        self.sub = self.create_subscription(Image, '/camera/image_raw', self._img_cb, 10)

        self.det = self.create_publisher(Image, '/object_tracking/image_raw', 10)

        self.coord = self.create_publisher(String, '/object_coordinates', 10)

        self.get_logger().info("Object Detection Node started")

        self.kernel = np.ones((10,10), np.uint8)
        self.bridge = CvBridge()

    def _img_cb(self, img: Image):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(img, 'bgr8')
        except Exception as e:
            self.get_logger().error(f"Image decode failed: {e}")
            return

        if cv_img is None or cv_img.size == 0:
            self.get_logger().warn("Empty image received")
            return
        
        # hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

        blurred = cv2.GaussianBlur(cv_img, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Purple HSV range
        lower_purple = np.array([127, 180, 50])
        upper_purple = np.array([147, 255, 120])

        # cx, cy = cv_img.shape[1]//2, cv_img.shape[0]//2
        # print("Center HSV:", hsv[cy, cx])

        fg_mask = cv2.inRange(hsv, lower_purple, upper_purple)

        # Clean up mask
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        fg_mask = cv2.medianBlur(fg_mask, 5)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in contours]

        if len(areas) < 1:
            self._publish_img(cv_img)
            return

        max_index = np.argmax(areas)
        cnt = contours[max_index]
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(cv_img, (x, y), (x+w, y+h), (255, 0, 255), 3)  # magenta box

        x2 = x + int(w/2)
        y2 = y + int(h/2)
        cv2.circle(cv_img, (x2, y2), 4, (255, 0, 255), -1)

        text = "x: " + str(x2) + ", y: " + str(y2)
        cv2.putText(cv_img, text, (x2 - 10, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        self.coord.publish(String(data=text))
        self.get_logger().info(f"Published coordinates {text}")

        self._publish_img(cv_img)

    def _publish_img(self, img):
        self.get_logger().info("In _publish_img function")
        imgmsg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
        self.det.publish(imgmsg)
        
def main(args=None):
    rclpy.init(args=args)
    object_tracker = ObjectDetectionNode()
    rclpy.spin(object_tracker)
    object_tracker.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()