"""GPU data-fetching module – works with NVIDIA via GPUtil, graceful fallback."""

from typing import Optional, List


def get_gpu_info() -> Optional[List[dict]]:
    """
    Return a list of GPU dicts, or None if no GPU / GPUtil not installed.
    Each dict: name, load(%), vram_used(MB), vram_total(MB), vram_free(MB),
                temperature(°C), driver, uuid.
    """
    try:
        import GPUtil  # type: ignore
        gpus = GPUtil.getGPUs()
        if not gpus:
            return None
        result = []
        for g in gpus:
            result.append({
                "name":       g.name,
                "load":       round(g.load * 100, 1),
                "vram_used":  g.memoryUsed,
                "vram_total": g.memoryTotal,
                "vram_free":  g.memoryFree,
                "vram_pct":   round((g.memoryUsed / g.memoryTotal) * 100, 1) if g.memoryTotal else 0,
                "temperature":g.temperature,
                "driver":     g.driver,
                "uuid":       g.uuid,
            })
        return result
    except Exception:
        return None
