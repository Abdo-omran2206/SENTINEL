"""Network data-fetching module – no UI concerns."""

import psutil
import socket

# Baseline counters for delta speed calculations
_prev_counters = psutil.net_io_counters()


def get_network_info() -> dict:
    """Return a dict with network speed, totals, IP and hostname."""
    global _prev_counters

    current = psutil.net_io_counters()
    download_speed = max(current.bytes_recv - _prev_counters.bytes_recv, 0)
    upload_speed = max(current.bytes_sent - _prev_counters.bytes_sent, 0)
    _prev_counters = current

    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "N/A"

    return {
        "download_speed": download_speed,
        "upload_speed": upload_speed,
        "bytes_recv": current.bytes_recv,
        "bytes_sent": current.bytes_sent,
        "packets_recv": current.packets_recv,
        "packets_sent": current.packets_sent,
        "ip": ip,
        "hostname": socket.gethostname(),
    }