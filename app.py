from flask import Flask, render_template_string, request, jsonify
import RPi.GPIO as GPIO

# Initialize Flask app
app = Flask(__name__)

# GPIO Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
FAN_PIN = 17
GPIO.setup(FAN_PIN, GPIO.OUT)
fan_pwm = GPIO.PWM(FAN_PIN, 1000)  # 1kHz PWM frequency
fan_pwm.start(0)  # Start with 0% duty cycle (fan off)

fan_on = False  # Track fan state
fan_speed = 0  # Track fan speed

@app.route('/')
def index():
    return 'Hello world'

@app.route('/fanControl')
def fanControl():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fan Controller</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 20px; }
            .container { max-width: 400px; margin: auto; padding: 20px; background: rgba(0, 0, 0, 0.2); border-radius: 15px; }
            .button { padding: 10px 20px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; }
            .on { background: green; color: white; }
            .off { background: red; color: white; }
            .slider { width: 100%; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>WCM555 Fan Controller</h1>
            <button class="button on" onclick="controlFan(1)">Turn Fan On</button>
            <button class="button off" onclick="controlFan(0)">Turn Fan Off</button>
            <p>Status: <span id="fanStatus">Off</span></p>
            <input type="range" min="0" max="100" value="0" class="slider" id="pwmSlider" oninput="setFanSpeed(this.value)">
            <p>Speed: <span id="fanSpeed">0</span>%</p>
        </div>

        <script>
            function controlFan(state) {
                fetch('/controlFan?state=' + state)
                .then(response => response.json())
                .then(data => { document.getElementById("fanStatus").innerText = data.status; })
                .catch(error => console.error('Error:', error));
            }

            function setFanSpeed(speed) {
                fetch('/setFanSpeed?speed=' + speed)
                .then(response => response.json())
                .then(data => { document.getElementById("fanSpeed").innerText = data.speed; })
                .catch(error => console.error('Error:', error));
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/controlFan')
def control_fan():
    global fan_on
    global fan_speed
    state = request.args.get('state')
    if state == "1":
        fan_on = True
        fan_pwm.ChangeDutyCycle(fan_speed)  # Full speed
        return jsonify(status="On")
    else:
        fan_on = False
        fan_pwm.ChangeDutyCycle(0)  # Stop fan
        return jsonify(status="Off")

@app.route('/setFanSpeed')
def set_fan_speed():
    global fan_on
    global fan_speed
    fan_speed = request.args.get('speed', type=int)
    if fan_on:  # Only allow speed change if fan is on
        fan_pwm.ChangeDutyCycle(fan_speed)
        return jsonify(speed=fan_speed)
    return jsonify(speed=0)  # Keep speed at 0 if fan is off

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0')
    finally:
        fan_pwm.stop()
        GPIO.cleanup()  # Cleanup GPIO on exit
