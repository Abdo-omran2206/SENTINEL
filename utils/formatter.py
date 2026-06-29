class Formatter:
    """Utility class for formatting system data values."""

    @staticmethod
    def format_bytes(size: int) -> str:
        """Format byte count into a human-readable string (B → TB)."""
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    @staticmethod
    def format_speed(bytes_per_sec: float) -> str:
        """Format bytes/second into a human-readable network speed string."""
        for unit in ("B/s", "KB/s", "MB/s", "GB/s"):
            if bytes_per_sec < 1024:
                return f"{bytes_per_sec:.2f} {unit}"
            bytes_per_sec /= 1024
        return f"{bytes_per_sec:.2f} GB/s"

    @staticmethod
    def format_percent(value: float) -> str:
        """Format a float percentage to 2 decimal places."""
        return f"{value:.1f}%"