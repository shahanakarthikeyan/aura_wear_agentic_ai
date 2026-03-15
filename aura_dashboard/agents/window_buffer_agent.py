from collections import deque

class WindowBufferAgent:
    """
    SUB-AGENT 2: Window Buffer Agent
    Maintains a rolling 3-4 hour window of sensor readings.
    Each reading represents 15 minutes → window = 12 to 16 readings.

    This window is the INPUT to the Prediction Agent.
    The Prediction Agent uses the full window (not just latest reading)
    to generate a 20-hour risk forecast.
    """

    def __init__(self, window_size: int = 16):
        self.name        = "WindowBufferAgent"
        self.window_size = window_size   # 16 readings × 15 min = 4 hours
        self.buffer      = deque(maxlen=window_size)
        self.min_readings = 12           # Minimum 3 hours before prediction starts

    def add(self, reading: dict):
        """Add a new sensor reading to the rolling window."""
        self.buffer.append(reading)
        filled = len(self.buffer)
        print(f"  [{self.name}] Window: {filled}/{self.window_size} readings "
              f"(~{filled * 15} min of data)")

    def is_ready(self) -> bool:
        """Returns True once we have at least 3 hours (12 readings) of data."""
        return len(self.buffer) >= self.min_readings

    def get_window(self) -> list:
        """Returns the current rolling window as a list."""
        return list(self.buffer)

    def get_stats(self) -> dict:
        """
        Extracts statistical features from the window.
        These features are fed into the Prediction Agent (and ML model).
        """
        if not self.buffer:
            return {}

        window = list(self.buffer)
        keys   = ["heart_rate", "spo2", "hrv", "systolic_bp", "stress_index"]
        stats  = {}

        for key in keys:
            values = [r[key] for r in window]
            stats[f"{key}_mean"]  = round(sum(values) / len(values), 2)
            stats[f"{key}_min"]   = round(min(values), 2)
            stats[f"{key}_max"]   = round(max(values), 2)
            stats[f"{key}_trend"] = round(values[-1] - values[0], 2)  # change over window

        stats["window_size_readings"] = len(window)
        stats["window_duration_min"]  = len(window) * 15
        return stats