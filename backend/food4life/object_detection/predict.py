from os import path
import cv2
import io
import numpy as np
from PIL import Image
from threading import RLock

CLASSNAMES_PATH = path.join(path.dirname(__file__), "model/obj.names")
CONFIG_PATH = path.join(path.dirname(__file__), "model/yolov4-config.cfg")
WEIGHTS_PATH = path.join(path.dirname(__file__), "model/yolov4.weights")

# Configured to be the same as trained
IMAGE_TO_W = 416
IMAGE_TO_H = 416
_lock = RLock()


def image_preprocess(pil_img: Image.Image):
    image = np.array(pil_img).copy()
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


class YoloModel:
    def __init__(self):
        self.labels = self.get_labels()
        self.model = self.load_model()

    @staticmethod
    def get_labels():
        with open(CLASSNAMES_PATH, "r") as f:
            return f.readlines()

    @staticmethod
    def load_model():
        model = cv2.dnn.readNetFromDarknet(CONFIG_PATH, WEIGHTS_PATH)
        return model

    def predict(self, image, threshold=0.3):
        predictions_raw = {}
        predictions = []

        ln = self.model.getLayerNames()
        ln = [ln[i - 1] for i in self.model.getUnconnectedOutLayers()]

        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (IMAGE_TO_W, IMAGE_TO_H), swapRB=True, crop=False)
        with _lock:
            self.model.setInput(blob)
            layerOutputs = self.model.forward(ln)

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]

                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > threshold:
                    class_id = int(class_id)
                    if class_id in predictions_raw.keys():
                        if predictions_raw[class_id] < float(confidence):
                            predictions_raw[class_id] = float(confidence)
                    else:
                        predictions_raw[class_id] = float(confidence)

        for obj_id, confidence in predictions_raw.items():
            predictions.append({'obj_id': obj_id, 'label': self.labels[obj_id].strip(), 'confidence': confidence})

        return predictions


model = YoloModel()


def predict(file):
    fp = io.BytesIO(file.read())
    # todo: check format?
    try:
        Image.open(fp).verify()
    except Exception as e:
        print(e)
        return None
    img = Image.open(fp)
    image_converted = image_preprocess(img)

    # using passed threshold
    predictions = model.predict(image_converted, threshold=0.05)
    return predictions
