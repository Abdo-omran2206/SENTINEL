"""System services fetcher – Windows (PowerShell) and Linux (systemd)."""

import platform
import subprocess
from typing import List


def get_services(limit: int = 100) -> List[dict]:
    """
    Return a list of system services.
    Each dict: name, display_name, status.
    Cross-platform: Windows uses PowerShell Get-Service, Linux uses systemctl.
    """
    system = platform.system()
    services = []

    if system == "Windows":
        services = _get_windows_services(limit)
    elif system == "Linux":
        services = _get_linux_services(limit)
    elif system == "Darwin":
        services = _get_macos_services(limit)

    return services


def _get_windows_services(limit: int) -> List[dict]:
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "Get-Service | Select-Object -First {} Name,DisplayName,Status "
            "| ConvertTo-Csv -NoTypeInformation".format(limit)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        lines  = result.stdout.strip().splitlines()
        if not lines:
            return []

        out = []
        for line in lines[1:]:  # skip CSV header
            # Remove surrounding quotes and split
            parts = line.replace('"', '').split(',')
            if len(parts) >= 3:
                out.append({
                    "name":         parts[0].strip(),
                    "display_name": parts[1].strip(),
                    "status":       parts[2].strip(),
                })
        return out
    except Exception:
        return []


def _get_linux_services(limit: int) -> List[dict]:
    try:
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--no-pager", "--all",
             "--no-legend"],
            capture_output=True, text=True, timeout=8
        )
        out = []
        for line in result.stdout.strip().splitlines()[:limit]:
            parts = line.split()
            if len(parts) >= 4:
                out.append({
                    "name":         parts[0],
                    "display_name": " ".join(parts[4:]) if len(parts) > 4 else parts[0],
                    "status":       parts[2],
                })
        return out
    except Exception:
        return []


def _get_macos_services(limit: int) -> List[dict]:
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True, text=True, timeout=8
        )
        out = []
        for line in result.stdout.strip().splitlines()[1:limit + 1]:
            parts = line.split(None, 2)
            if len(parts) == 3:
                status = "running" if parts[0] != "-" else "stopped"
                out.append({
                    "name":         parts[2],
                    "display_name": parts[2],
                    "status":       status,
                })
        return out
    except Exception:
        return []
