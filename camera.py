import cv2
import time

class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.prev_time = 0

    def gen_frames(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                break

            # FPS Logic
            curr_time = time.time()
            fps = 1 / (curr_time - self.prev_time) if self.prev_time else 0
            self.prev_time = curr_time

            cv2.putText(frame, f"{fps:.2f}", (4, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Encode
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def __del__(self):
        self.cap.release()