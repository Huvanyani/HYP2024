import cv2

class FaceDetector:
    def __init__(self):
        # Load the pre-trained face detection model (Haar Cascade in this case)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_faces(self, frame):
        # Detect faces in the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def detect_face(self):
        # Capture a single face using the webcam
        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Face Detector - Press c to capture')

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                return None  # Return None if no face is captured

            # Detect faces in the frame
            faces = self.detect_faces(frame)

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow('Face Detector - Press c to capture', frame)

            # Wait for user to press 'c' to capture the face
            key = cv2.waitKey(1)
            if key & 0xFF == ord('c'):
                break
            if cv2.getWindowProperty('Face Detector - Press c to capture', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Return the captured face region if faces were detected
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            return frame[y:y + h, x:x + w]  # Return the cropped face
        else:
            print("No face detected")
            return None  # Return None if no face was detected
