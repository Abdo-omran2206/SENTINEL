"""Logged-in users fetcher – cross-platform via psutil."""

import psutil
import datetime
from typing import List


def get_users() -> List[dict]:
    """
    Return a list of currently logged-in users.
    Each dict: name, terminal, host, started (human-readable).
    """
    users = []
    try:
        for u in psutil.users():
            started_dt = datetime.datetime.fromtimestamp(u.started)
            now        = datetime.datetime.now()
            duration   = now - started_dt
            hours      = int(duration.total_seconds() // 3600)
            minutes    = int((duration.total_seconds() % 3600) // 60)

            users.append({
                "name":     u.name,
                "terminal": u.terminal or "N/A",
                "host":     u.host or "local",
                "started":  started_dt.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{hours}h {minutes}m",
            })
    except Exception:
        pass
    return users
