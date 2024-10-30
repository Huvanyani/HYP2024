import cv2
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_lfw_people
from FaceDetector import FaceDetector
from scipy.spatial.distance import euclidean  # For face verification

class FaceRecognitionCNN:
    def __init__(self, img_size=(50, 37)):
        # Image size matches the size used in LFW dataset
        self.img_size = img_size
        self.cnn_model = None

    def load_lfw_data(self):
        """
        Loads Labeled Faces in the Wild (LFW) dataset for face recognition training.
        """
        lfw_people = fetch_lfw_people(min_faces_per_person=2, resize=0.4)
        images = lfw_people.images
        labels = lfw_people.target
        label_names = lfw_people.target_names

        # Normalize the images
        images = images.reshape(-1, self.img_size[0], self.img_size[1], 1) / 255.0

        return images, labels, label_names

    def build_cnn_model(self, input_shape, num_classes):
        """
        Builds a simple CNN model for face encoding and classification.
        """
        model = Sequential()

        # Convolutional layers with pooling
        model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
        model.add(MaxPooling2D((2, 2)))

        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D((2, 2)))

        model.add(Conv2D(128, (3, 3), activation='relu'))
        model.add(MaxPooling2D((2, 2)))

        # Flatten and fully connected layers
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))  # This layer produces the "face encoding"
        model.add(Dense(num_classes, activation='softmax'))  # Classification layer for output

        # Compile the model
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        self.cnn_model = model
        return model

    def train_model(self, model, images, labels, epochs=10):
        """
        Trains the CNN model on the provided face images and labels.
        """
        # Split data into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)

        # Train the model
        model.fit(X_train, y_train, epochs=epochs, validation_data=(X_val, y_val))

        return model

    def generate_encoding(self, face_image):
        """
        Generates a face encoding for a single face using the trained CNN.
        The face_image should be pre-processed and normalized.
        """
        if self.cnn_model is None:
            raise ValueError("The CNN model has not been trained or loaded.")

        # Pass the face through the model to get the encoding (128-dimensional vector)
        face_image = face_image.reshape(1, self.img_size[0], self.img_size[1], 1)  # Reshape to match input shape
        face_encoding = self.cnn_model.predict(face_image)
        return face_encoding[0]

    def verify_face(self, known_encodings, new_face_image, threshold=0.6):
        """
        Verifies if the new face matches any known encodings based on a threshold.
        Uses Euclidean distance to compare encodings.
        """
        new_encoding = self.generate_encoding(new_face_image)

        # Calculate distances between the new encoding and known encodings
        for label, known_encoding in known_encodings.items():
            distance = euclidean(known_encoding, new_encoding)
            print(f"Distance to {label}: {distance}")

            if distance < threshold:
                print(f"Face matched with {label} (distance: {distance})")
                return label

        print("No matching face found.")
        return None
