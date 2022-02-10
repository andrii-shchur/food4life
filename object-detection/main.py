import cv2, io, numpy as np
from PIL import Image
from sys import path
from flask import Flask, request, jsonify

CLASSNAMES_PATH = path[0] + "\\model\\obj.names"
CONFIG_PATH = path[0] + "\\model\\yolov4-config.cfg"
WEIGHTS_PATH = path[0] + "\\model\\yolov4.weights"

CONFIDENCE_THRESHOLD = 0.3
nmsthres = 0.1

# Configured to be the same as trained
IMAGE_TO_W = 416
IMAGE_TO_H = 416


def image_preprocess(img_passed):
    image = Image.open(io.BytesIO(img_passed))
    image = np.array(image).copy()
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


class yolo_model():
    def __init__(self):
        self.labels = self.get_labels()
        self.model = self.load_model()


    def get_labels(self):
        f = open(CLASSNAMES_PATH, "r")
        c = f.read()
        f.close()
        return c.split('\n')

    
    def load_model(self):
        model = cv2.dnn.readNetFromDarknet(CONFIG_PATH, WEIGHTS_PATH)
        return model


    def predict(self, image, threshold=CONFIDENCE_THRESHOLD):
        predictions_raw = {}
        predictions = []

        ln = self.model.getLayerNames()
        ln = [ln[i-1] for i in self.model.getUnconnectedOutLayers()]

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
                        if predictions_raw[class_id] < float(confidence): predictions_raw[class_id] = float(confidence)
                    else: predictions_raw[class_id] = float(confidence)
                
        for obj_id, confidence in predictions_raw.items():
            predictions.append({'obj_id': obj_id, 'label': self.labels[obj_id], 'confidence': confidence})

        return predictions



def create_app():
    app = Flask(__name__)
    model = yolo_model()

    @app.route('/image/recognize', methods=['POST'])
    def predict():
        try:
            image_passed = request.files["image"].read()
            image_converted = image_preprocess(image_passed)
            try:
                # using passed threshold
                threshold = float(request.values['threshold'])
                predictions = model.predict(image_converted, threshold)
            except:
                predictions = model.predict(image_converted)

            return jsonify({'result': predictions}), 200

        except:
            return {'error': 'Make sure an image is passed!'}, 400

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)