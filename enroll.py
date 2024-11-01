import cv2
import dlib
import numpy as np
import os
from keras.models import load_model

class Enroll:
    def __init__(self, model_path="cnn_model.h5", storage_path="face_data",
                 shape_predictor_path="face_data/shape_predictor_68_face_landmarks.dat"):
        # Load the trained CNN model
        self.model = load_model(model_path)
        self.storage_path = storage_path  # Directory where face encodings will be saved

        self.detector = dlib.get_frontal_face_detector()  # Dlib face detector
        self.predictor = dlib.shape_predictor(shape_predictor_path)

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)  # Create the storage directory if it doesn't exist

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def preprocess_face(self, face):
        # Resizes and normalizes the face image for the FaceNet model input.

        img_size = (50, 37)     # LFW image sizes
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


    def eye_aspect_ratio(self, eye):
        # Computes the Eye Aspect Ratio (EAR) to detect blinks.

        A = np.linalg.norm(eye[1] - eye[5])  # Vertical distance
        B = np.linalg.norm(eye[2] - eye[4])  # Vertical distance
        C = np.linalg.norm(eye[0] - eye[3])  # Horizontal distance
        return (A + B) / (2.0 * C)

    def enroll_face(self, username):
        # Enrolls a user by capturing face images and checking for liveliness using blink detection.

        cap = cv2.VideoCapture(0)
        face_encodings = []  # Store multiple face encodings (we will take 3)
        count = 0
        EAR_THRESHOLD = 0.25  # Threshold for blink detection
        CONSEC_FRAMES = 2  # Number of consecutive frames to confirm blink
        counter = 0
        blink_count = 0  # Counter for blinks
        success = False  # Track if enrollment is successful

        print("Press C to capture face after blink detection")

        while count < 3:  # Capture 3 faces
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)  # Detect faces

            for rect in rects:
                shape = self.predictor(gray, rect)  # Get facial landmarks
                shape = np.array([[p.x, p.y] for p in shape.parts()])

                left_eye = shape[36:42]  # Left eye landmarks
                right_eye = shape[42:48]  # Right eye landmarks

                # Calculate EAR for both eyes
                leftEAR = self.eye_aspect_ratio(left_eye)
                rightEAR = self.eye_aspect_ratio(right_eye)
                ear = (leftEAR + rightEAR) / 2.0  # Average EAR for both eyes

                if ear < EAR_THRESHOLD:
                    counter += 1
                else:
                    if counter >= CONSEC_FRAMES:
                        blink_count += 1
                        print(f"Blink detected: {blink_count}")
                    counter = 0

                # Draw rectangles around the face and eyes
                cv2.rectangle(frame, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 255, 0), 2)
                for (x, y) in np.concatenate([left_eye, right_eye], axis=0):
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            cv2.imshow('Enroll Face - Press "C" after blink detection', frame)

            # Capture the face after a blink is detected and 'C' is pressed
            if cv2.waitKey(1) & 0xFF == ord('c') and blink_count > 0:
                print(f"Capturing face {count + 1}...")
                if len(rects) > 0:
                    rect = rects[0]  # Take the first detected face
                    face = frame[rect.top():rect.bottom(), rect.left():rect.right()]  # Crop the face
                    face_encoding = self.generate_face_encoding(face)  # Generate the encoding
                    face_encodings.append(face_encoding)  # Store the encoding
                    count += 1  # Increment the face count

                    # Reset blink count after capture
                    blink_count = 0

                if count == 3:
                    success = True  # Enrollment was successful after capturing 3 faces

        cap.release()
        cv2.destroyAllWindows()

        # After loop ends, check if face encodings were captured and stored
        if success and face_encodings:
            # Average the encodings of the 3 captured faces
            avg_encoding = np.mean(face_encodings, axis=0)
            np.save(os.path.join(self.storage_path, f'{username}.npy'), avg_encoding)  # Save the average encoding
            print(f"Face encoding for {username} stored successfully.")
            return True  # Return True for successful enrollment
        else:
            print("No face detected or blink failed. Please try again.")
            return False  # Return False for failed enrollment

