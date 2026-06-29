"""System uptime & load average fetcher – cross-platform via psutil."""

import psutil
import platform
import datetime


def get_uptime() -> dict:
    """
    Return system uptime, boot time, load average and OS info.
    load_1/5/15 are 0.0 on Windows (not supported by the OS).
    """
    boot_ts  = psutil.boot_time()
    boot_dt  = datetime.datetime.fromtimestamp(boot_ts)
    now      = datetime.datetime.now()
    delta    = now - boot_dt

    days    = delta.days
    hours   = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60

    # Load average – raises AttributeError on Windows
    try:
        load = psutil.getloadavg()
    except (AttributeError, OSError):
        load = (0.0, 0.0, 0.0)

    cpu_count = psutil.cpu_count(logical=True) or 1

    return {
        "boot_time":     boot_dt.strftime("%Y-%m-%d  %H:%M:%S"),
        "uptime_str":    f"{days}d  {hours}h  {minutes}m  {seconds}s",
        "uptime_days":   days,
        "uptime_hours":  hours,
        "uptime_mins":   minutes,
        "uptime_secs":   seconds,
        "load_1":        load[0],
        "load_5":        load[1],
        "load_15":       load[2],
        "cpu_count":     cpu_count,
        "os_name":       platform.system(),
        "os_version":    platform.version(),
        "os_release":    platform.release(),
        "machine":       platform.machine(),
        "hostname":      platform.node(),
        "python":        platform.python_version(),
        "architecture":  platform.architecture()[0],
    }
