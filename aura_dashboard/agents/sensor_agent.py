import random
from datetime import datetime

class SensorAgent:
    """
    SUB-AGENT 1: Sensor Agent
    Reads bio-signals every cycle (each cycle = 15 min of real time in simulation).
    3-4 hours = 12-16 readings to fill the prediction window.

    DEMO: auto mode simulates gradual cardiac deterioration over time.
    PRODUCTION: Replace simulate() with actual hardware SDK calls.
    """

    def __init__(self, mode="auto"):
        self.name  = "SensorAgent"
        self.mode  = mode
        self.cycle = 0

    def simulate(self):
        """Each call = 1 reading (represents 15 minutes of real time)."""
        self.cycle += 1

        if self.mode == "auto":
            data = self._auto_progression()
        elif self.mode == "critical":
            data = self._critical_readings()
        elif self.mode == "warning":
            data = self._warning_readings()
        else:
            data = self._normal_readings()

        data["timestamp"]     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["sim_time_min"]  = self.cycle * 15  # simulated minutes elapsed
        return data

    def _auto_progression(self):
        """
        Simulates gradual deterioration:
        Cycles  1-8  → Normal    (0 - 2 hours)
        Cycles  9-12 → Warning   (2 - 3 hours)
        Cycles 13-16 → Critical  (3 - 4 hours)  → triggers 20hr forecast
        """
        if self.cycle <= 8:    return self._normal_readings()
        elif self.cycle <= 12: return self._warning_readings()
        else:                  return self._critical_readings()

    def _normal_readings(self):
        return {
            "heart_rate":   random.randint(65, 80),
            "spo2":         round(random.uniform(97.5, 99.5), 1),
            "hrv":          round(random.uniform(55.0, 80.0), 1),
            "systolic_bp":  random.randint(110, 125),
            "body_temp":    round(random.uniform(36.4, 36.8), 1),
            "stress_index": round(random.uniform(0.1, 0.3), 2),
        }

    def _warning_readings(self):
        return {
            "heart_rate":   random.randint(90, 115),
            "spo2":         round(random.uniform(94.5, 96.8), 1),
            "hrv":          round(random.uniform(25.0, 42.0), 1),
            "systolic_bp":  random.randint(135, 152),
            "body_temp":    round(random.uniform(37.0, 37.5), 1),
            "stress_index": round(random.uniform(0.55, 0.75), 2),
        }

    def _critical_readings(self):
        return {
            "heart_rate":   random.randint(125, 160),
            "spo2":         round(random.uniform(90.0, 93.5), 1),
            "hrv":          round(random.uniform(8.0, 20.0), 1),
            "systolic_bp":  random.randint(158, 185),
            "body_temp":    round(random.uniform(37.6, 38.3), 1),
            "stress_index": round(random.uniform(0.85, 1.0), 2),
        }

    def validate(self, data):
        if not (30 <= data["heart_rate"] <= 220): return False
        if not (80 <= data["spo2"] <= 100):       return False
        return True

    def read(self):
        return self.simulate()