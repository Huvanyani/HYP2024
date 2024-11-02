import cv2
import numpy as np
import os
import dlib
from keras.models import load_model
from scipy.spatial.distance import euclidean

class Verification:
    def __init__(self, model_path="cnn_model.h5", storage_path="face_data",
                 shape_predictor_path="face_data/shape_predictor_68_face_landmarks.dat"):
        self.model = load_model(model_path)  # Load the trained CNN model
        self.storage_path = storage_path  # Directory where face encodings are stored
        self.detector = dlib.get_frontal_face_detector()  # Dlib face detector
        self.predictor = dlib.shape_predictor(shape_predictor_path)  # Dlib shape predictor for facial landmarks

        # "C:\\Users\\Huvanyani\\OneDrive - University of Johannesburg\\School\\2024\\Password Manager\\facenet_model.h5"

    def preprocess_face(self, face):
        # Resizes and normalizes the face image for the FaceNet model input.

        # img_size = (160, 160)  # Update image size to match FaceNet input (160x160)

        img_size = (50, 37)     # LFW image sizes; Original Model

        """"
        # If the face is in grayscale, convert it to RGB (FaceNet expects 3 channels)
        if len(face.shape) == 2 or (
                len(face.shape) == 3 and face.shape[2] == 1):  # If the image has 1 channel (grayscale)
            face = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)  # Convert to RGB
        """
        if len(face.shape) == 3 and face.shape[2] == 3:  # If the image has 3 channels (RGB)
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

        # Resizing the face
        face = cv2.resize(face, img_size)
        face = face.reshape(img_size[0], img_size[1])  # Original Model

        # Reshape for the model input, ensuring the size matches (160x160x3)
        #   face = face.reshape(1, img_size[0], img_size[1], 3)   Reshape for FaceNet (batch_size, height, width, channels)

        # Normalize the pixel values to [0, 1] range
        face = face / 255.0

        return face

    def generate_face_encoding(self, face):
        # Generates a face encoding using the FaceNet model.

        preprocessed_face = self.preprocess_face(face)  # Preprocess the face

        # Ensure the face input is in numpy array format
        if not isinstance(preprocessed_face, np.ndarray):
            preprocessed_face = np.array(preprocessed_face)

        # preprocessed_face = preprocessed_face.reshape(1, 160, 160, 3)  # Match FaceNet input size

        preprocessed_face = preprocessed_face.reshape(1, 50, 37, 1)     # Original Model

        # Get encoding from the FaceNet model
        encoding = self.model.predict(preprocessed_face)

        return encoding[0]

    def eye_aspect_ratio(self, eye):
        # Computes the Eye Aspect Ratio (EAR) to detect blinks.

        A = np.linalg.norm(eye[1] - eye[5])  # Vertical distance
        B = np.linalg.norm(eye[2] - eye[4])  # Vertical distance
        C = np.linalg.norm(eye[0] - eye[3])  # Horizontal distance
        return (A + B) / (2.0 * C)

    def verify_face(self, username, threshold):
        # Captures the face and verifies it with blink detection and comparison to stored encoding.

        cap = cv2.VideoCapture(0)
        blink_count = 0
        EAR_THRESHOLD = 0.25  # Eye aspect ratio threshold for detecting blinks
        CONSEC_FRAMES = 2  # Number of consecutive frames where the eyes must be below the EAR threshold
        counter = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)  # Detect faces in grayscale image

            for rect in rects:
                shape = self.predictor(gray, rect)  # Get the facial landmarks
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

                # Draw rectangles around the face and eyes
                cv2.rectangle(frame, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 255, 0), 2)
                for (x, y) in np.concatenate([left_eye, right_eye], axis=0):
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            cv2.imshow('Verify - Press c to capture', frame)

            # Only proceed if 'c' is pressed and at least one blink is detected
            if cv2.waitKey(1) & 0xFF == ord('c') and blink_count > 0:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Process the captured frame to extract the face encoding
        if len(rects) > 0:
            rect = rects[0]  # We take the first detected face for verification
            face = frame[rect.top():rect.bottom(), rect.left():rect.right()]
            face_encoding = self.generate_face_encoding(face)  # Get the face encoding for the captured face

            # Load the stored encoding
            stored_score_path = os.path.join(self.storage_path, f'{username}.npy')
            if os.path.exists(stored_score_path):
                stored_encoding = np.load(stored_score_path)
                # Compute the Euclidean distance between the stored encoding and the captured encoding
                distance = euclidean(stored_encoding, face_encoding)

                # Verify if the distance is within the acceptable threshold
                if distance < threshold:
                    print(f"Face verification for {username} successful (distance: {distance})")
                    return True
                else:
                    print(f"Face verification for {username} failed (distance: {distance})")
                    return False
            else:
                print(f"No stored encoding found for {username}. Please enroll first.")
                return False
        else:
            print("No face detected. Please try again.")
            return False

    def verify(self, username, threshold):
        # Detects the face from the webcam, captures it when 'C' is pressed, and verifies it with stored encoding.

        cap = cv2.VideoCapture(0)
        print("Press 'C' to capture the face for verification")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)  # Detect faces in grayscale image

            for rect in rects:
                # Draw rectangles around the detected face
                cv2.rectangle(frame, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 255, 0), 2)

            cv2.imshow('Verify - Press "C" to capture', frame)

            # If 'C' is pressed, capture the face and break out of the loop
            if cv2.waitKey(1) & 0xFF == ord('c'):
                if len(rects) > 0:
                    rect = rects[0]  # We take the first detected face for verification
                    face = frame[rect.top():rect.bottom(), rect.left():rect.right()]
                    face_encoding = self.generate_face_encoding(face)  # Get the face encoding for the captured face

                    cap.release()
                    cv2.destroyAllWindows()

                    # Load the stored encoding
                    stored_score_path = os.path.join(self.storage_path, f'{username}.npy')
                    if os.path.exists(stored_score_path):
                        stored_encoding = np.load(stored_score_path)
                        # Compute the Euclidean distance between the stored encoding and the captured encoding
                        distance = euclidean(stored_encoding, face_encoding)

                        # Verify if the distance is within the acceptable threshold
                        if distance < threshold:
                            print(f"Face verification for {username} successful (distance: {distance})")
                            return True
                        else:
                            print(f"Face verification for {username} failed (distance: {distance})")
                            return False
                    else:
                        print(f"No stored encoding found for {username}. Please enroll first.")
                        return False
                else:
                    print("No face detected. Please try again.")

        cap.release()
        cv2.destroyAllWindows()
        return False