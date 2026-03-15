class PredictionAgent:
    """
    SUB-AGENT 3: Prediction Agent
    Core intelligence of Aura Wear.

    INPUT  : Statistical features extracted from 3-4 hours of sensor data
    OUTPUT : Risk score (0.0 - 1.0) + predicted time to cardiac event

    FORECAST HORIZON: 20 hours
    - If risk is detected now, the system predicts WHEN in the next 20 hours
      the patient is most at risk — enabling proactive intervention.

    PRODUCTION: Replace _score_from_stats() with your trained ML model:
        features = list(stats.values())
        risk_score = model.predict([features])[0]
    """

    def __init__(self):
        self.name = "PredictionAgent"

    def predict(self, stats: dict, baseline: dict) -> dict:
        """
        Analyzes 3-4 hour window statistics to generate a 20-hour forecast.

        Returns:
            risk_score      : 0.0 (safe) to 1.0 (imminent attack)
            risk_level      : LOW / MODERATE / HIGH / CRITICAL
            predicted_hours : estimated hours until cardiac event
            confidence      : prediction confidence %
            key_indicators  : which signals drove the prediction
        """
        if not stats:
            return self._empty_result()

        risk_score, indicators = self._score_from_stats(stats, baseline)
        risk_level, predicted_hours = self._forecast_horizon(risk_score)
        confidence = self._estimate_confidence(stats)

        result = {
            "risk_score":       round(risk_score, 2),
            "risk_level":       risk_level,
            "predicted_hours":  predicted_hours,
            "confidence_pct":   confidence,
            "key_indicators":   indicators,
            "window_duration":  f"{stats.get('window_duration_min', 0)} min",
            "forecast_horizon": "20 hours",
        }

        print(f"  [{self.name}] Risk: {risk_score:.2f} ({risk_level}) | "
              f"Predicted event in: ~{predicted_hours} hrs | "
              f"Confidence: {confidence}%")

        return result

    def _score_from_stats(self, stats: dict, baseline: dict) -> tuple:
        """
        Rule-based scoring from window statistics.
        REPLACE THIS with model.predict([features]) in production.
        """
        risk  = 0.0
        flags = []

        # ── Heart Rate: mean elevation + upward trend ──────
        hr_mean  = stats.get("heart_rate_mean", 70)
        hr_trend = stats.get("heart_rate_trend", 0)
        if hr_mean > 110:
            risk += 0.25; flags.append("Sustained high heart rate")
        elif hr_mean > 95:
            risk += 0.12; flags.append("Elevated heart rate")
        if hr_trend > 20:
            risk += 0.10; flags.append("Heart rate rising trend")

        # ── SpO2: prolonged low oxygen ─────────────────────
        spo2_mean = stats.get("spo2_mean", 98)
        spo2_min  = stats.get("spo2_min", 98)
        if spo2_mean < 94:
            risk += 0.25; flags.append("Sustained low oxygen (SpO2)")
        elif spo2_mean < 96:
            risk += 0.12; flags.append("Mildly reduced oxygen")
        if spo2_min < 92:
            risk += 0.10; flags.append("Critical SpO2 drop detected")

        # ── HRV: prolonged suppression = cardiac stress ────
        hrv_mean  = stats.get("hrv_mean", 60)
        hrv_trend = stats.get("hrv_trend", 0)
        if hrv_mean < 20:
            risk += 0.20; flags.append("Severely suppressed HRV")
        elif hrv_mean < 35:
            risk += 0.10; flags.append("Low heart rate variability")
        if hrv_trend < -20:
            risk += 0.08; flags.append("HRV declining rapidly")

        # ── Blood Pressure: sustained hypertension ─────────
        bp_mean = stats.get("systolic_bp_mean", 120)
        bp_max  = stats.get("systolic_bp_max", 120)
        if bp_mean > 155:
            risk += 0.15; flags.append("Sustained hypertension")
        elif bp_mean > 140:
            risk += 0.07; flags.append("Elevated blood pressure")
        if bp_max > 175:
            risk += 0.07; flags.append("Hypertensive spike detected")

        # ── Stress: prolonged high stress ─────────────────
        stress_mean = stats.get("stress_index_mean", 0.3)
        if stress_mean > 0.8:
            risk += 0.10; flags.append("Sustained high stress index")
        elif stress_mean > 0.6:
            risk += 0.05; flags.append("Elevated stress level")

        return min(round(risk, 2), 1.0), flags if flags else ["All vitals within range"]

    def _forecast_horizon(self, risk_score: float) -> tuple:
        """Maps risk score to predicted hours until cardiac event."""
        if risk_score >= 0.80:
            return "CRITICAL", "< 4 hours"
        elif risk_score >= 0.60:
            return "HIGH",     "4 - 8 hours"
        elif risk_score >= 0.40:
            return "MODERATE", "8 - 20 hours"
        elif risk_score >= 0.20:
            return "LOW",      "> 20 hours"
        else:
            return "SAFE",     "No event predicted"

    def _estimate_confidence(self, stats: dict) -> int:
        """Confidence increases with more data in window."""
        readings = stats.get("window_size_readings", 0)
        if readings >= 16: return 94
        elif readings >= 12: return 85
        elif readings >= 8:  return 72
        else:                return 60

    def _empty_result(self):
        return {
            "risk_score": 0.0, "risk_level": "UNKNOWN",
            "predicted_hours": "N/A", "confidence_pct": 0,
            "key_indicators": ["Insufficient data"], "forecast_horizon": "20 hours",
        }