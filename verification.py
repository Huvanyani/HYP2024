import cv2
import face_recognition
import numpy as np
import os
import dlib


class Verification:
    def __init__(self, storage_path='face_data',
                 shape_predictor_path='face_data/shape_predictor_68_face_landmarks.dat'):
        # Initializing the verification class.
        self.storage_path = storage_path
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(shape_predictor_path)

    def eye_aspect_ratio(self, eye):
        # Calculates the eye aspect ratio (EAR) using numpy.
        A = np.linalg.norm(eye[1] - eye[5])  # vertical on eye 1
        B = np.linalg.norm(eye[2] - eye[4])  # vertical on eye 2
        C = np.linalg.norm(eye[0] - eye[3])  # distance between the eyes
        ear = (A + B) / (2.0 * C)  # eye aspect ratio
        return ear

    def verify_face(self, username, threshold=0.8):
        # Captures face using the webcam for verification and compares with stored face score.
        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Verify - Press c to capture')
        blink_count = 0
        EAR_THRESHOLD = 0.25  # threshold to detect blinks
        CONSEC_FRAMES = 2  # number of frames to ensure the eye is closed
        counter = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break

            # turning image to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)

            for rect in rects:
                shape = self.predictor(gray, rect)
                shape = np.array([[p.x, p.y] for p in shape.parts()])  # storing landmark coordinates
                left_eye = shape[36:42]  # left eye coordinates
                right_eye = shape[42:48]  # right eye coordinates
                # getting the eye aspect ratio of both eyes
                leftEAR = self.eye_aspect_ratio(left_eye)
                rightEAR = self.eye_aspect_ratio(right_eye)
                ear = (leftEAR + rightEAR) / 2.0

                if ear < EAR_THRESHOLD:
                    counter += 1
                else:
                    if counter >= CONSEC_FRAMES:
                        blink_count += 1
                    counter = 0

                # combining the landmarks into a single array along the axis
                for (x, y) in np.concatenate((left_eye, right_eye), axis=0):
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # drawing a dot on each detected landmark

                cv2.rectangle(frame, (rect.left(), rect.top()), (rect.right(), rect.bottom()), (0, 255, 0),
                              2)  # drawing a rectangle around detected face

            cv2.imshow('Verify - Press c to capture', frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('c') and blink_count > 0:
                break
            if cv2.getWindowProperty('Verify - Press c to capture', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

        face_scores = face_recognition.face_encodings(frame)
        if face_scores:
            face_score = face_scores[0]
            stored_score_path = os.path.join(self.storage_path, f'{username}.npy')  # retrieving the stored face score
            if os.path.exists(stored_score_path):
                stored_score = np.load(stored_score_path)  # loading the stored face encoding

                # Comparing the stored face score with the captured face score using a threshold
                face_distance = face_recognition.face_distance([stored_score], face_score)

                if face_distance[0] <= threshold:
                    print(f"Face verification for {username} successful")
                    return True
                else:
                    print(
                        f"Face verification for {username} failed.")
                    return False
            else:
                print(f"No stored score for {username}. Please enroll first.")
                return False
        else:
            print("No face detected. Please try again.")
            return False

# references:
# 1. Soukupová, T., & Cech, J. (2016). Real-Time Eye Blink Detection using Facial Landmarks.
# 2. Pathak, A. (2018). GitHub Repository on Eye Blink Detection using EAR. https://github.com/pathak-ashutosh/Eye-blink-detection
