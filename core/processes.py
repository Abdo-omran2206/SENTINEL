"""Process data-fetching module – no UI concerns."""

import psutil
from typing import List, Literal


def get_processes(
    sort_by: Literal["cpu", "memory"] = "cpu",
    search: str = "",
    limit: int = 20,
) -> List[dict]:
    """Return a list of top processes sorted by cpu or memory usage."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            info = p.info
            name = info.get("name") or ""
            if search and search.lower() not in name.lower():
                continue
            procs.append({
                "pid": info["pid"],
                "name": name,
                "cpu": info["cpu_percent"] or 0.0,
                "memory": info["memory_percent"] or 0.0,
                "status": info.get("status", "?"),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    key = "cpu" if sort_by == "cpu" else "memory"
    procs.sort(key=lambda x: x[key], reverse=True)
    return procs[:limit]


def kill_process(pid: int) -> tuple[bool, str]:
    """Attempt to terminate a process. Returns (success, message)."""
    try:
        p = psutil.Process(pid)
        p.terminate()
        return True, f"Process {pid} terminated."
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found."
    except psutil.AccessDenied:
        return False, f"Access denied to process {pid}."
    except Exception as e:
        return False, str(e)