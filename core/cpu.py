"""CPU data-fetching module – no UI concerns."""

import psutil


def get_cpu_info() -> dict:
    """Return a dict with all CPU metrics."""
    freq = psutil.cpu_freq()
    per_core = psutil.cpu_percent(percpu=True)

    return {
        "usage": psutil.cpu_percent(interval=None),
        "cores": psutil.cpu_count(logical=False) or 0,
        "threads": psutil.cpu_count(logical=True) or 0,
        "freq_current": freq.current if freq else 0.0,
        "freq_max": freq.max if freq else 0.0,
        "freq_min": freq.min if freq else 0.0,
        "per_core": per_core,
        "avg_per_core": sum(per_core) / len(per_core) if per_core else 0.0,
    }