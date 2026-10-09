
from pathlib import Path

import numpy as np
from PIL import Image
from tensorflow import keras


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "static" / "models" / "cat_dog_classifier.keras"
IMG_SIZE = (160, 160)

model = None


def get_model():
    global model

    if model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "The trained model was not found. "
                "Place cat_dog_classifier.keras in static/models/."
            )

        model = keras.models.load_model(
            MODEL_PATH,
            compile=False
        )

    return model


def classify_image(image_path):
    classifier_model = get_model()

    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image = image.resize(IMG_SIZE)

        image_array = np.asarray(image, dtype=np.float32) / 255.0

    image_array = np.expand_dims(image_array, axis=0)

    dog_probability = float(
        classifier_model.predict(image_array, verbose=0)[0][0]
    )

    if dog_probability >= 0.5:
        label = "Dog"
        confidence = dog_probability * 100
    else:
        label = "Cat"
        confidence = (1 - dog_probability) * 100

    return {
        "label": label,
        "confidence": round(confidence, 2),
    }
