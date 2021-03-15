from flask import request
from flask import jsonify
from flask import Flask
import base64
import io
from PIL import Image
import tensorflow.keras
from tensorflow.keras import backend as K
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from cv2 import cv2


app = Flask(__name__)

def get_model():
    global model
    model = models.load_model('num_model.h5')
    print("* Model loaded!")


def preprocess_image(image, target_size):
    gray = image.convert('L')
    bw = gray.point(lambda x: 0 if x<100 else 255, '1')
    bw.save("bw_image.jpg")
    img_array = cv2.imread("bw_image.jpg", cv2.IMREAD_GRAYSCALE)
    img_array = cv2.bitwise_not(img_array)
    new_array = cv2.resize(img_array, target_size)
    user_test = tensorflow.keras.utils.normalize(new_array, axis=1)
    user_test = user_test.reshape((1,28,28))
    predicted = model.predict([user_test])
    
    return predicted

print("* Loading Keras Model...")
get_model()

@app.route('/predict', methods=['POST'])
def predict():
    message = request.get_json(force=True)
    encoded = message['image']
    decoded = base64.b64decode(encoded)

    image = Image.open(io.BytesIO(decoded))

    estimate = preprocess_image(image, target_size=(28,28))
    data = int(np.argmax(estimate))
    response = jsonify({'prediction': data})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == '__main__':
    app.run(debug=True)