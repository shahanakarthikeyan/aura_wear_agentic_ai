from datetime import datetime, timedelta

class ProactiveAlertAgent:
    """
    SUB-AGENT 4: Proactive Alert Agent
    Sends ADVANCE warnings based on the 20-hour forecast.

    Unlike reactive systems that alert DURING a heart attack,
    Aura Wear alerts BEFORE — giving patients, caregivers, and
    hospitals a life-saving window to act.

    ALERT TIERS:
    ┌─────────────┬──────────────────────────────────────────────────┐
    │ SAFE        │ No action. Continue monitoring.                  │
    │ LOW         │ Wellness nudge. Encourage rest.                  │
    │ MODERATE    │ 8-20hr warning. Doctor check-in recommended.     │
    │ HIGH        │ 4-8hr warning. Caregiver + doctor notified.      │
    │ CRITICAL    │ <4hr warning. Emergency services alerted.        │
    └─────────────┴──────────────────────────────────────────────────┘
    """

    def __init__(self, patient_name: str):
        self.name         = "ProactiveAlertAgent"
        self.patient_name = patient_name
        self.alert_log    = []

    def notify(self, prediction: dict) -> str:
        """Sends the appropriate proactive alert based on risk forecast."""
        level   = prediction["risk_level"]
        hours   = prediction["predicted_hours"]
        score   = prediction["risk_score"]
        conf    = prediction["confidence_pct"]
        reasons = prediction["key_indicators"]

        print(f"\n  [{self.name}] Processing forecast → {level} risk")
        print(f"  Predicted cardiac event: {hours} | Confidence: {conf}%")
        print(f"  Key indicators: {', '.join(reasons)}")

        if level == "SAFE":
            self._safe_status(score)

        elif level == "LOW":
            self._low_risk_nudge(score, conf)

        elif level == "MODERATE":
            self._moderate_warning(score, hours, conf, reasons)

        elif level == "HIGH":
            self._high_risk_alert(score, hours, conf, reasons)

        elif level == "CRITICAL":
            self._critical_emergency(score, hours, conf, reasons, prediction)

        self.alert_log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level, "risk_score": score, "predicted_hours": hours
        })

        return level

    # ── SAFE ──────────────────────────────────────────────
    def _safe_status(self, score):
        print(f"\n  ✅ [SAFE] Risk Score: {score} — All vitals normal.")
        print(f"     Patient: Everything looks great! Keep it up.")

    # ── LOW RISK ──────────────────────────────────────────
    def _low_risk_nudge(self, score, conf):
        print(f"\n  💙 [LOW RISK] Risk Score: {score} | Confidence: {conf}%")
        print(f"     📲 Patient Nudge: 'Your heart is working a little harder today.")
        print(f"        Consider resting, hydrating, and avoiding strenuous activity.'")

    # ── MODERATE (8-20 hr warning) ─────────────────────────
    def _moderate_warning(self, score, hours, conf, reasons):
        print(f"\n  🟡 [MODERATE - ADVANCE WARNING] Risk Score: {score}")
        print(f"     ⏰ Estimated risk window: {hours}")
        print(f"     📲 Patient: 'Aura Wear detects elevated cardiac stress.")
        print(f"        Please rest and avoid exertion. Schedule a doctor check-in.'")
        print(f"     📞 Caregiver: 'Moderate cardiac risk detected for {self.patient_name}.")
        print(f"        Please check in with them and monitor closely.'")
        print(f"     🏥 Doctor Portal: Flagging {self.patient_name} for proactive check-in.")

    # ── HIGH (4-8 hr warning) ──────────────────────────────
    def _high_risk_alert(self, score, hours, conf, reasons):
        print(f"\n  🔴 [HIGH RISK - 4-8 HR WARNING] Risk Score: {score}")
        print(f"     ⏰ Predicted cardiac event in: {hours}")
        print(f"     📲 Patient: 'WARNING: High cardiac risk detected.")
        print(f"        Please go to the nearest hospital or call your doctor NOW.'")
        print(f"     📞 Caregiver: 'URGENT: {self.patient_name} shows HIGH cardiac risk.")
        print(f"        Take them to hospital immediately.'")
        print(f"     🏥 Hospital: Pre-alert sent. Patient vitals shared with cardiology.")
        print(f"     🚑 Ambulance: On standby (notified, not dispatched yet).")

    # ── CRITICAL (<4 hr warning) ───────────────────────────
    def _critical_emergency(self, score, hours, conf, reasons, prediction):
        eta = datetime.now() + timedelta(hours=2)
        print(f"\n  🚨 [CRITICAL - EMERGENCY ALERT] Risk Score: {score}")
        print(f"     ⏰ Predicted cardiac event in: {hours}")
        print(f"     📲 Patient: '🚨 EMERGENCY: Imminent heart attack risk detected!")
        print(f"        Call emergency services immediately. Do not drive yourself.'")
        print(f"     📞 Caregiver: '🚨 EMERGENCY: Call 112/911 for {self.patient_name} NOW.'")
        print(f"     🏥 Hospital ER: Patient en route. Cardiology team on standby.")
        print(f"        Live vitals being streamed. Estimated arrival: {eta.strftime('%H:%M')}")
        print(f"     🚑 Ambulance: DISPATCHED to patient location.")
        print(f"     📊 Indicators: {', '.join(reasons)}")