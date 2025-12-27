# car_control.py
from flask import Flask, render_template, Response, request, jsonify
import cv2
import time
import threading
import lgpio

app = Flask(__name__)

# --- CAMERA STREAM ---

def gen_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    prev_time = 0
    fps = 0

    while True:
        success, frame = cap.read()
        if not success:
            print("⚠️ Failed to grab frame")
            break

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        # Draw FPS on frame
        cv2.putText(frame, f"{fps:.2f}", (4, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield multipart HTTP response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

# --- MOTOR CONTROL ---
chip = lgpio.gpiochip_open(0)

# BCM pin numbers
LEFT_FWD  = 17
LEFT_BWD  = 18
RIGHT_FWD = 22
RIGHT_BWD = 23
ENA = 12   # PWM0
ENB = 13   # PWM1

lgpio.gpio_claim_output(chip, ENA, 0)
lgpio.gpio_claim_output(chip, ENB, 0)

# claim output pins
for p in [LEFT_FWD, LEFT_BWD, RIGHT_FWD, RIGHT_BWD]:
    lgpio.gpio_claim_output(chip, p, 0)

speed = 0.4  # initial 40% duty

pwm_freq = 1000  # Hz
pwm_period = 1.0 / pwm_freq

def pwm_loop(pin):
    global speed
    while True:
        on_time = pwm_period * speed
        off_time = pwm_period - on_time
        lgpio.gpio_write(chip, pin, 1)
        time.sleep(on_time)
        lgpio.gpio_write(chip, pin, 0)
        time.sleep(off_time)

# Start PWM threads
threading.Thread(target=pwm_loop, args=(ENA,), daemon=True).start()
threading.Thread(target=pwm_loop, args=(ENB,), daemon=True).start()

# ---------------------
# Motor movement helpers
# ---------------------
def stop_all():
    for pin in [LEFT_FWD, LEFT_BWD, RIGHT_FWD, RIGHT_BWD]:
        lgpio.gpio_write(chip, pin, 0)

def forward():
    lgpio.gpio_write(chip, LEFT_BWD, 0)
    lgpio.gpio_write(chip, RIGHT_BWD, 0)
    lgpio.gpio_write(chip, LEFT_FWD, 1)
    lgpio.gpio_write(chip, RIGHT_FWD, 1)

def backward():
    lgpio.gpio_write(chip, LEFT_FWD, 0)
    lgpio.gpio_write(chip, RIGHT_FWD, 0)
    lgpio.gpio_write(chip, LEFT_BWD, 1)
    lgpio.gpio_write(chip, RIGHT_BWD, 1)

def turn_left():
    lgpio.gpio_write(chip, LEFT_FWD, 0)
    lgpio.gpio_write(chip, LEFT_BWD, 1)
    lgpio.gpio_write(chip, RIGHT_BWD, 0)
    lgpio.gpio_write(chip, RIGHT_FWD, 1)

def turn_right():
    lgpio.gpio_write(chip, RIGHT_FWD, 0)
    lgpio.gpio_write(chip, RIGHT_BWD, 1)
    lgpio.gpio_write(chip, LEFT_BWD, 0)
    lgpio.gpio_write(chip, LEFT_FWD, 1)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/control", methods=["POST"])
def control():
    global speed
    data = request.get_json()
    cmd = data.get("cmd")

    if cmd == "w":
        #forward()
        backward()
    elif cmd == "s":
        #backward()
        forward()
    elif cmd == "a":
        turn_left()
    elif cmd == "d":
        turn_right()
    elif cmd == "stop":
        stop_all()
    elif cmd == "inc_speed":
        speed = min(speed + 0.1, 1.0)
    elif cmd == "dec_speed":
        speed = max(speed - 0.1, 0.2)

    return jsonify({"status": "ok", "speed": round(speed*100)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
