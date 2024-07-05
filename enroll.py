import cv2

class Enroll:
    def __init__(self):
        pass

    def capture_face(self):
        """Captures face using the webcam for enrollment."""
        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Enrollment')

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break
            cv2.imshow('Enrollment', frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            if cv2.getWindowProperty('Enrollment', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()
