"""Temperature & fan sensors – cross-platform via psutil."""

from typing import Optional
import psutil


def get_temperatures() -> dict:
    """
    Return a dict of sensor_name -> list of readings.
    Each reading: label, current(°C), high(°C), critical(°C).
    Returns empty dict on Windows (limited support) or when unavailable.
    """
    result = {}
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return {}
        for sensor_name, readings in temps.items():
            result[sensor_name] = [
                {
                    "label":    r.label or sensor_name,
                    "current":  r.current,
                    "high":     r.high,
                    "critical": r.critical,
                }
                for r in readings
            ]
    except (AttributeError, OSError):
        pass
    return result


def get_fans() -> dict:
    """
    Return a dict of fan_name -> list of fan RPM readings.
    Returns empty dict when unavailable.
    """
    result = {}
    try:
        fans = psutil.sensors_fans()
        if not fans:
            return {}
        for fan_name, readings in fans.items():
            result[fan_name] = [
                {"label": r.label or fan_name, "current": r.current}
                for r in readings
            ]
    except (AttributeError, OSError):
        pass
    return result
