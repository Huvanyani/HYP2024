import cv2
import face_recognition
import numpy as np
import os

class Verification:
    def __init__(self, storage_path='face_data'):

        # Initializes the Verification class.

        self.storage_path = storage_path
        # Load the pre-trained face detector from OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def verify_face(self, username):

        # Captures face using the webcam for verification and compares with stored face score.

        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Verify - Press q to capture')

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow('Verify - Press q to capture', frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            if cv2.getWindowProperty('Verify - Press q to capture', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()