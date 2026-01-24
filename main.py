from flask import Flask, render_template, Response, request, jsonify
from motor_driver import MotorController
from camera import CameraStream

app = Flask(__name__)
car = MotorController() # Using MotorController class
camera = CameraStream() # Using CameraStream class

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(camera.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/control", methods=["POST"])
def control():
    data = request.get_json()
    cmd = data.get("cmd")

    if cmd == "w":
        car.backward() #camera is mounted to the back of the car so forwards means backwards
    elif cmd == "s":
        car.forward()
    elif cmd == "a":
        car.turn_left()
    elif cmd == "d":
        car.turn_right()
    elif cmd == "stop":
        car.stop_all()
    elif cmd == "inc_speed":
        car.change_speed(0.1)
    elif cmd == "dec_speed":
        car.change_speed(-0.1)

    return jsonify({"status": "ok", "speed": round(car.speed*100)})

if __name__ == '__main__':
    # 0.0.0.0 is essential for Access Point mode
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)