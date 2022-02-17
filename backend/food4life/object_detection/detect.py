from os import path
import cv2
import io
import numpy as np
from PIL import Image

CLASSNAMES_PATH = path.join(path.dirname(__file__), "model/obj.names")
CONFIG_PATH = path.join(path.dirname(__file__), "model/yolov4-config.cfg")
WEIGHTS_PATH = path.join(path.dirname(__file__), "model/yolov4.weights")

CONFIDENCE_THRESHOLD = 0.3
nmsthres = 0.1

# Configured to be the same as trained
IMAGE_TO_W = 416
IMAGE_TO_H = 416


def image_preprocess(img_passed):
    image = Image.open(io.BytesIO(img_passed))
    image = np.array(image).copy()
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


class YoloModel:
    def __init__(self):
        self.labels = self.get_labels()
        self.model = self.load_model()

    @staticmethod
    def get_labels():
        f = open(CLASSNAMES_PATH, "r")
        c = f.read()
        f.close()
        return c.split('\n')

    @staticmethod
    def load_model():
        model = cv2.dnn.readNetFromDarknet(CONFIG_PATH, WEIGHTS_PATH)
        return model

    def predict(self, image, threshold=CONFIDENCE_THRESHOLD):
        predictions_raw = {}
        predictions = []

        ln = self.model.getLayerNames()
        ln = [ln[i - 1] for i in self.model.getUnconnectedOutLayers()]

        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (IMAGE_TO_W, IMAGE_TO_H), swapRB=True, crop=False)
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
            predictions.append({'obj_id': obj_id, 'label': self.labels[obj_id], 'confidence': confidence})

        return predictions


def predict(file):
    model = YoloModel()
    try:
        image_passed = file.read()
        image_converted = image_preprocess(image_passed)
        # fixme: exceptions
        try:
            # using passed threshold
            threshold = 0.05
            predictions = model.predict(image_converted, threshold)
        except Exception as e:
            print(e)
            predictions = model.predict(image_converted)

        return {'result': predictions}

    except Exception as e:
        print(e)
        return {'message': 'Make sure an image is passed!'}
