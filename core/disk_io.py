"""Disk I/O speed fetcher – real-time read/write MB/s per disk."""

import psutil
import time
from typing import Dict

_prev_io: Dict   = {}
_prev_time: float = 0.0


def get_disk_io() -> Dict[str, dict]:
    """
    Return per-disk dict with real-time read/write speeds and cumulative totals.
    Keys: read_speed(B/s), write_speed(B/s), read_total(B), write_total(B),
          read_count, write_count.
    """
    global _prev_io, _prev_time

    try:
        current_io   = psutil.disk_io_counters(perdisk=True)
        current_time = time.time()
        elapsed      = current_time - _prev_time if _prev_time else 1.0

        result = {}
        for disk, counters in current_io.items():
            prev = _prev_io.get(disk)
            if prev and elapsed > 0:
                read_speed  = max((counters.read_bytes  - prev.read_bytes)  / elapsed, 0)
                write_speed = max((counters.write_bytes - prev.write_bytes) / elapsed, 0)
            else:
                read_speed = write_speed = 0.0

            result[disk] = {
                "read_speed":  read_speed,
                "write_speed": write_speed,
                "read_total":  counters.read_bytes,
                "write_total": counters.write_bytes,
                "read_count":  counters.read_count,
                "write_count": counters.write_count,
            }

        _prev_io   = current_io
        _prev_time = current_time
        return result

    except Exception:
        return {}
