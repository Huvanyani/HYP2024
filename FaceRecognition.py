import os
import cv2
import numpy as np
from keras.models import load_model
import dlib


class FaceRecognition:
    def __init__(self, img_size=(50, 37), model_path="cnn_model.h5", storage_path="face_data",
                 shape_predictor_path="face_data/shape_predictor_68_face_landmarks.dat"):
        # Image size matches the size used in LFW dataset
        self.model = load_model(model_path)
        self.storage_path = storage_path  # Directory where face encodings will be saved

        self.detector = dlib.get_frontal_face_detector()  # Dlib face detector
        self.predictor = dlib.shape_predictor(shape_predictor_path)

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)  # Create the storage directory if it doesn't exist

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    @staticmethod
    def preprocess_face(face):
        # Resizes and normalizes the face image for the FaceNet model input.

        img_size = (50, 37)  # LFW image sizes
        #   img_size = (160, 160)  # Update image size to match FaceNet input (160x160)

        """
        # If the face is in grayscale, convert it to RGB (FaceNet expects 3 channels)
        if len(face.shape) == 2 or (
                len(face.shape) == 3 and face.shape[2] == 1):  # If the image has 1 channel (grayscale)
            face = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)  # Convert to RGB
        """

        if len(face.shape) == 3 and face.shape[2] == 3:  # If the image has 3 channels (RGB)
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

        print(f"Original face size: {face.shape}")

        # Resize the face to the required dimensions (160x160)
        face = cv2.resize(face, img_size)

        # Reshape for the model input, ensuring the size matches (160x160x3)
        #   face = face.reshape(1, img_size[0], img_size[1], 3)  # Reshape for FaceNet (batch_size, height, width, channels)

        face = face.reshape(img_size[0], img_size[1])
        print(f"Resized face size: {face.shape}")

        # Normalize the pixel values to [0, 1] range
        face = face / 255.0

        return face

    def generate_face_encoding(self, face):
        # Generates a face encoding using the FaceNet model.

        preprocessed_face = self.preprocess_face(face)  # Preprocess the face

        # Ensure the face input is in numpy array format
        if not isinstance(preprocessed_face, np.ndarray):
            preprocessed_face = np.array(preprocessed_face)

        # Make sure the input is reshaped correctly for prediction (batch_size, height, width, channels)
        #   preprocessed_face = preprocessed_face.reshape(1, 160, 160, 3)  # Match FaceNet input size

        preprocessed_face = preprocessed_face.reshape(1, 50, 37, 1)

        # Get encoding from the FaceNet model
        encoding = self.model.predict(preprocessed_face)

        return encoding[0]

    @staticmethod
    def eye_aspect_ratio(eye):
        # Computes the Eye Aspect Ratio (EAR) to detect blinks.

        A = np.linalg.norm(eye[1] - eye[5])  # Vertical distance
        B = np.linalg.norm(eye[2] - eye[4])  # Vertical distance
        C = np.linalg.norm(eye[0] - eye[3])  # Horizontal distance
        return (A + B) / (2.0 * C)