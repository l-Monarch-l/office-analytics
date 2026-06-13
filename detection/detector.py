from ultralytics import YOLO
import cv2
import numpy as np
from .config import MODEL_PATH, CONF_THRESHOLD

class YOLODetector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
    
    def detect(self, frame):
        results = self.model(frame, conf=CONF_THRESHOLD, verbose=False)
        detections = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    if int(box.cls) == 0:  # person
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        detections.append((x1, y1, x2, y2, conf))
        return detections