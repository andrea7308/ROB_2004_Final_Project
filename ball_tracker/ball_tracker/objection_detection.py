import cv2
from cv_bridge import CvBridge
import rclpy
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from vision_msgs.msg import Detection2DArray
from std_msgs.msg import String



class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')

        self.sub = self.create_subscription(CompressedImage, '/camera/image_raw', self._image_cb, 10)

        self.det = self.create_publisher(Detection2DArray, '/object_tracking/image_raw', 10)

        self.coord = self.create_publisher(String, '/object_coordinates', 10)

        self.get_logger.info("Object Detection Node started")

        self.back_sub = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=25, detectShadows=True)
        self.kernel = np.ones((20,20), np.uint8)
        self.bridge = CvBridge

    def _img_cb(self, img: CompressedImage):


        cv_img = self.bridge.imgmsg_to_cv2(img, 'rgb8')

        fg_mask = cv2.self.back_sub.apply(cv_img)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        fg_mask = cv2.medianBlur(fg_mask, 5)
        _, fg_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(c) for c in contours]

        if len(areas) < 1:
            self._publish_img(cv_img)
            return

        max_index = np.argmax(areas)
        cnt = contours[max_index]
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(cv_img, (x, y), (x+w, y+h), (0, 255, 0), 3)

        x2 = x + int(w/2)
        y2 = y + int(h/2)
        cv2.circle(cv_img, (x2, y2), 4, (0, 255, 0), -1)

        text = "x: " + str(x2) + ", y: " + str(y2)
        cv2.putText(cv_img, text, (x2 - 10, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        self.coord.publish(String(data=text))

        self._publish_img(cv_img)

    def _publish_img(self, img):
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