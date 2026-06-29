"""Battery data-fetching module – no UI concerns."""

import psutil
from typing import Optional


def get_battery_info() -> Optional[dict]:
    """Return battery metrics dict, or None if no battery is present."""
    battery = psutil.sensors_battery()
    if battery is None:
        return None

    secs = battery.secsleft
    if secs == psutil.POWER_TIME_UNLIMITED:
        time_left = "Charging (AC)"
    elif secs == psutil.POWER_TIME_UNKNOWN or secs < 0:
        time_left = "Unknown"
    else:
        hours = secs // 3600
        minutes = (secs % 3600) // 60
        time_left = f"{hours}h {minutes}m"

    return {
        "percent": battery.percent,
        "plugged": battery.power_plugged,
        "time_left": time_left,
        "secs_left": secs,
    }