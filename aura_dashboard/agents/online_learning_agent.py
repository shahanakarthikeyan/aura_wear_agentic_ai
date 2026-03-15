import json
from datetime import datetime

class OnlineLearningAgent:
    """
    SUB-AGENT 5: Online Learning Agent
    Continuously learns from each patient's own data to improve prediction accuracy.

    HOW IT WORKS:
    1. Collects labeled sessions (sensor window + actual outcome)
    2. Builds a personal risk profile for each patient
    3. Detects patterns unique to that individual
    4. Feeds data back to retrain the ML model over time

    PRODUCTION INTEGRATION:
    - Connect to your ML pipeline (scikit-learn, TensorFlow, etc.)
    - Use accumulated data to retrain model periodically
    - Fine-tune the global model with patient-specific data
    """

    def __init__(self, patient_name: str):
        self.name         = "OnlineLearningAgent"
        self.patient_name = patient_name
        self.sessions     = []           # full session logs
        self.risk_profile = {}           # patient's personal risk trends
        self.log_file     = f"aura_{patient_name.replace(' ', '_')}_data.json"

    def log_session(self, stats: dict, prediction: dict, alert_level: str):
        """Stores each prediction session for future model training."""
        entry = {
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "window_stats": stats,
            "prediction":   prediction,
            "alert_level":  alert_level,
            "patient":      self.patient_name,
        }
        self.sessions.append(entry)
        print(f"  [{self.name}] Session logged for training. "
              f"Total sessions: {len(self.sessions)}")

    def update_risk_profile(self, stats: dict, risk_score: float):
        """
        Builds a personal risk profile by tracking trends over time.
        The profile helps detect what's 'abnormal' for THIS patient specifically.
        """
        profile = self.risk_profile

        # Track rolling average risk score
        prev_avg = profile.get("avg_risk", 0)
        n        = profile.get("session_count", 0)
        profile["avg_risk"]      = round((prev_avg * n + risk_score) / (n + 1), 3)
        profile["session_count"] = n + 1
        profile["last_updated"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Track personal normal ranges (from low-risk sessions only)
        if risk_score < 0.3:
            for key in ["heart_rate_mean", "spo2_mean", "hrv_mean", "systolic_bp_mean"]:
                val = stats.get(key)
                if val:
                    profile[f"personal_normal_{key}"] = round(
                        (profile.get(f"personal_normal_{key}", val) + val) / 2, 2
                    )

        self.risk_profile = profile
        print(f"  [{self.name}] Risk profile updated. "
              f"Personal avg risk: {profile['avg_risk']} | "
              f"Sessions: {profile['session_count']}")

    def get_training_summary(self) -> dict:
        """Returns a summary of data accumulated for model retraining."""
        high_risk = sum(1 for s in self.sessions if s["prediction"]["risk_score"] >= 0.6)
        return {
            "patient":          self.patient_name,
            "total_sessions":   len(self.sessions),
            "high_risk_events": high_risk,
            "risk_profile":     self.risk_profile,
            "ready_to_retrain": len(self.sessions) >= 10,
        }

    def export_training_data(self):
        """Exports all session data as JSON for ML model retraining."""
        export = {
            "patient":      self.patient_name,
            "exported_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_profile": self.risk_profile,
            "sessions":     self.sessions,
        }
        with open(self.log_file, "w") as f:
            json.dump(export, f, indent=2)
        print(f"  [{self.name}] Training data exported: {self.log_file}")
        print(f"  [{self.name}] {len(self.sessions)} sessions ready for model retraining.")