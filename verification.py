import cv2

class Verification:
    def __init__(self):
        pass

    def verify_face(self):
        """Captures face using the webcam for verification."""
        cap = cv2.VideoCapture(0)
        cv2.namedWindow('Verification')

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break
            cv2.imshow('Verification', frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            if cv2.getWindowProperty('Verify - Press q to capture', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()
