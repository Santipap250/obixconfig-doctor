from flask import Flask, render_template, request
from analyzer.prop_logic import analyze_propeller
from analyzer.thrust_logic import calculate_thrust_weight, estimate_battery_runtime
from analyzer.battery_logic import analyze_battery

app = Flask(__name__)

# ===============================
# LOGIC วิเคราะห์โดรน
# ===============================
def analyze_drone(size, battery, style, prop_result, weight):
    analysis = {}

    analysis["overview"] = (
        f'โดรน {size}" แบต {battery}, สไตล์ {style}, ใบพัด: {prop_result["summary"]}'
    )

   
    analysis["weight_class"] = classify_weight(size, weight)

    analysis["basic_tips"] = [
        "ตรวจสอบใบพัดไม่บิดงอ",
        "ขันน็อตมอเตอร์ให้แน่น",
        "เช็คจุดบัดกรี ESC และแบตเตอรี่"
    ]

    # PID + Filter
    if style == "freestyle":
        pid = {
            "roll": {"p":48,"i":52,"d":38},
            "pitch":{"p":48,"i":52,"d":38},
            "yaw":{"p":40,"i":45,"d":0}
        }
        filter_desc = {"gyro_lpf2":90,"dterm_lpf1":120,"dyn_notch":2}
        extra_tips = ["Freestyle, สมดุล แรงพอดี"]

    elif style == "racing":
        pid = {
            "roll": {"p":55,"i":45,"d":42},
            "pitch":{"p":55,"i":45,"d":42},
            "yaw":{"p":50,"i":40,"d":0}
        }
        filter_desc = {"gyro_lpf2":120,"dterm_lpf1":150,"dyn_notch":3}
        extra_tips = ["Racing, ตอบสนองไว"]

    else:
        pid = {
            "roll": {"p":42,"i":50,"d":32},
            "pitch":{"p":42,"i":50,"d":32},
            "yaw":{"p":35,"i":45,"d":0}
        }
        filter_desc = {"gyro_lpf2":70,"dterm_lpf1":90,"dyn_notch":1}
        extra_tips = ["Long Range, Smooth, ประหยัดแบต"]

    analysis["pid"] = pid
    analysis["filter"] = filter_desc
    analysis["extra_tips"] = extra_tips
    analysis["thrust_ratio"] = calculate_thrust_weight(
        prop_result["effect"]["motor_load"], weight
    )
    analysis["battery_est"] = estimate_battery_runtime(weight, battery)

    return analysis
# ===============================
# ROUTE: Landing Page
# ===============================
@app.route("/landing")
def landing():
    return render_template("landing.html")

# ===============================
# ROUTE: หน้า Loading
# ===============================
@app.route("/")
def loading():
    return render_template("loading.html")

# ===============================
# ROUTE: เช็ค backend
# ===============================
@app.route("/ping")
def ping():
    return "pong"

# ===============================
# ROUTE: แอพจริง
# ===============================
@app.route("/app", methods=["GET", "POST"])
def index():
    analysis = None

    if request.method == "POST":
        size = float(request.form["size"])
        battery = request.form["battery"]
        style = request.form["style"]
        weight = float(request.form.get("weight", 1.0))
        prop_size = float(request.form["prop_size"])
        blade_count = int(request.form["blades"])
        prop_pitch = float(request.form["pitch"])

        prop_result = analyze_propeller(
            prop_size, prop_pitch, blade_count, style
        )

        analysis = analyze_drone(
            size, battery, style, prop_result, weight
        )
        analysis["prop_result"] = prop_result

    return render_template("index.html", analysis=analysis)

# ===============================
# RUN
# ===============================
import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
    )