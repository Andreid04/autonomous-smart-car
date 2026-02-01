import cv2
import time
import pyaudio
import wave
import io
from queue import Queue
import threading

class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.prev_time = 0

        # Audio Setup - Don't start the stream yet!
        self.audio = pyaudio.PyAudio()
        # Try Index 1 (pulse) or 2 (default) if 0 fails
        self.mic_index = 2 
        self.rate = 16000 # or 48000 for better quality 
        self.chunk = 1024

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

    def gen_audio(self):
        """Streams audio as one continuous 'infinite' WAV file"""
        stream = None
        try:
            stream = self.audio.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=self.rate,
                                    input=True,
                                    input_device_index=self.mic_index,
                                    frames_per_buffer=self.chunk)

            # 1. Create a "dummy" header for an infinitely long WAV file
            with io.BytesIO() as header_io:
                with wave.open(header_io, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(self.rate)
                    wf.setnframes(0) # it is low for no buffered audio
                header = header_io.getvalue()
            
            # 2. Yield the header FIRST
            yield header

            # 3. Yield the raw PCM data continuously
            while True:
                data = stream.read(self.chunk, exception_on_overflow=False)
                yield data
            
        except Exception as e:
            print(f"Audio stream error: {e}")
        finally:
            if stream:
                stream.stop_stream()
                stream.close()

    def __del__(self):
        self.cap.release()
        self.audio.terminate()