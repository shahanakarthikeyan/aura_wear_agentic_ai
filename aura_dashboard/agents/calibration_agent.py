class CalibrationAgent:
    """
    SUB-AGENT 6: Calibration Agent
    Establishes a personal baseline for each patient during onboarding.
    Baseline = patient's healthy, resting bio-signal averages.
    Used by Prediction Agent to detect deviations specific to this patient.
    """

    def __init__(self):
        self.name     = "CalibrationAgent"
        self.baseline = None

    def calibrate(self, sensor_agent, samples: int = 8):
        """Collects 8 normal readings (~2 hours equivalent) for baseline."""
        print(f"  [{self.name}] Collecting {samples} baseline samples (~{samples*15} min)...")
        readings = []
        for _ in range(samples):
            r = sensor_agent.read()
            readings.append(r)

        keys = ["heart_rate", "spo2", "hrv", "systolic_bp", "stress_index"]
        self.baseline = {
            key: round(sum(r[key] for r in readings) / samples, 2)
            for key in keys
        }
        print(f"  [{self.name}] Baseline set: {self.baseline}")
        return self.baseline

    def get_baseline(self):
        return self.baseline