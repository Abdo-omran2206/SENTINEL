"""RAM data-fetching module – no UI concerns."""

import psutil


def get_ram_info() -> dict:
    """Return a dict with virtual memory and swap metrics."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "total": mem.total,
        "used": mem.used,
        "available": mem.available,
        "percent": mem.percent,
        "cached": getattr(mem, "cached", 0),
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent,
    }