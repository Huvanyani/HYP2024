import cv2
import face_recognition
import numpy as np
import os


class Verification:
    def __init__(self, storage_path='face_data'):
        #  initializes the verification class

        self.storage_path = storage_path
        # Load the pre-trained face detector from OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def verify_face(self, username):
        # Captures face using the webcam for verification and compares with stored face score.

        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Verify - Press c to capture')

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

            cv2.imshow('Verify - Press c to capture', frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('c'):
                break
            if cv2.getWindowProperty('Verify - Press c to capture', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Process the captured frame to get the face score
        face_scores = face_recognition.face_encodings(frame)
        if face_scores:
            face_score = face_scores[0]
            stored_score_path = os.path.join(self.storage_path, f'{username}.npy')  # fetching the saved score
            if os.path.exists(stored_score_path):
                stored_score = np.load(stored_score_path)
                matches = face_recognition.compare_faces([stored_score], face_score)  # comparing the scores
                if matches[0]:
                    print(f"Face verification for {username} successful.")
                    return True
                else:
                    print(f"Face verification for {username} failed.")
                    return False
            else:
                print(f"No stored score for {username}. Please enroll first.")
                return False
        else:
            print("No face detected. Please try again.")
            return False
