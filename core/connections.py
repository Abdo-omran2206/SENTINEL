"""Network connections & open ports fetcher – cross-platform via psutil."""

import psutil
from typing import List

# Cache PID → process name to avoid repeated lookups
_pid_cache: dict = {}


def get_connections(kind: str = "inet") -> List[dict]:
    """
    Return a list of active network connections.
    Each dict: proto, laddr, raddr, status, pid, name.
    """
    global _pid_cache

    conns = []
    try:
        for conn in psutil.net_connections(kind=kind):
            pid  = conn.pid
            name = "—"
            if pid:
                if pid not in _pid_cache:
                    try:
                        _pid_cache[pid] = psutil.Process(pid).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        _pid_cache[pid] = "?"
                name = _pid_cache[pid]

            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "—"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "—"

            conns.append({
                "proto":  "TCP" if conn.type == 1 else "UDP",
                "laddr":  laddr,
                "raddr":  raddr,
                "status": conn.status if conn.status else "—",
                "pid":    pid or 0,
                "name":   name,
            })
    except (psutil.AccessDenied, PermissionError):
        pass
    except Exception:
        pass

    return conns


def get_listening_ports() -> List[dict]:
    """Return only LISTEN-state connections (open ports)."""
    return [c for c in get_connections() if c["status"] == "LISTEN"]
