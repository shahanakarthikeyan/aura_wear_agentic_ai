import json
import time
import random
from datetime import datetime
from flask import Flask, Response, render_template, stream_with_context
from collections import deque
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from agents.sensor_agent import SensorAgent
from agents.calibration_agent import CalibrationAgent
from agents.window_buffer_agent import WindowBufferAgent
from agents.prediction_agent import PredictionAgent
from agents.proactive_alert_agent import ProactiveAlertAgent
from agents.online_learning_agent import OnlineLearningAgent

app = Flask(__name__)

# ── Initialize all agents ──────────────────────────────────
sensor      = SensorAgent(mode="auto")
calibration = CalibrationAgent()
window      = WindowBufferAgent(window_size=16)
predictor   = PredictionAgent()
alerter     = ProactiveAlertAgent("Demo Patient")
learner     = OnlineLearningAgent("Demo Patient")

# Calibrate on startup
calibration.calibrate(sensor, samples=8)

# Reset sensor cycle for clean demo
sensor.cycle = 0

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/stream")
def stream():
    """Server-Sent Events endpoint — pushes data to dashboard every 2 seconds."""
    def generate():
        cycle = 0
        while True:
            cycle += 1
            data = sensor.simulate()

            if not sensor.validate(data):
                continue

            window.add(data)

            prediction = {}
            alert_level = "COLLECTING"

            if window.is_ready():
                stats      = window.get_stats()
                baseline   = calibration.get_baseline()
                prediction = predictor.predict(stats, baseline)
                alert_level = prediction.get("risk_level", "SAFE")
                learner.log_session(stats, prediction, alert_level)
                learner.update_risk_profile(stats, prediction.get("risk_score", 0))

            payload = {
                "cycle":        cycle,
                "timestamp":    data["timestamp"],
                "sim_time":     f"{(cycle * 15) // 60}h {(cycle * 15) % 60}m",
                "heart_rate":   data["heart_rate"],
                "spo2":         data["spo2"],
                "hrv":          data["hrv"],
                "systolic_bp":  data["systolic_bp"],
                "body_temp":    data["body_temp"],
                "stress_index": round(data["stress_index"] * 100),
                "alert_level":  alert_level,
                "risk_score":   round(prediction.get("risk_score", 0) * 100),
                "predicted_hours": prediction.get("predicted_hours", "Collecting data..."),
                "confidence":   prediction.get("confidence_pct", 0),
                "indicators":   prediction.get("key_indicators", ["Accumulating data..."]),
                "window_fill":  min(len(window.buffer), 16),
                "is_ready":     window.is_ready(),
            }

            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(2)

    return Response(stream_with_context(generate()),
                    mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  AURA WEAR Dashboard Starting...")
    print("  Open browser at: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=False, threaded=True, port=5000)