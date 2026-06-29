"""Disk I/O speed screen – real-time read/write per disk."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable
from textual.containers import Container

from core.disk_io import get_disk_io
from utils.formatter import Formatter


def _speed_bar(speed: float, peak: float = 500 * 1024 * 1024, width: int = 18) -> str:
    """Draw a bar relative to a 500 MB/s peak."""
    pct    = min((speed / peak) * 100, 100) if peak else 0
    filled = int(width * pct / 100)
    empty  = width - filled
    color  = "cyan" if speed < 100 * 1024 * 1024 else ("yellow" if speed < 300 * 1024 * 1024 else "red")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class DiskIoScreen(Widget):
    """Real-time disk I/O speed monitor."""

    REFRESH_INTERVAL = 1.0

    def compose(self) -> ComposeResult:
        with Container(id="diskio-container"):
            yield Static("", id="diskio-bars", classes="info-card")
            yield DataTable(id="diskio-table", show_cursor=False)

    def on_mount(self) -> None:
        table = self.query_one("#diskio-table", DataTable)
        table.add_columns("Disk", "Read Speed", "Write Speed",
                          "Total Read", "Total Write",
                          "Read Ops", "Write Ops")
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            data  = get_disk_io()
            table = self.query_one("#diskio-table", DataTable)
            table.clear()

            bars_text = ""
            for disk, d in data.items():
                # visual bar strip
                bars_text += (
                    f"[b cyan]{disk}[/b cyan]\n"
                    f"  Read   {_speed_bar(d['read_speed'])}  "
                    f"[green]{Formatter.format_speed(d['read_speed'])}[/green]\n"
                    f"  Write  {_speed_bar(d['write_speed'])}  "
                    f"[magenta]{Formatter.format_speed(d['write_speed'])}[/magenta]\n\n"
                )
                table.add_row(
                    disk,
                    Formatter.format_speed(d["read_speed"]),
                    Formatter.format_speed(d["write_speed"]),
                    Formatter.format_bytes(d["read_total"]),
                    Formatter.format_bytes(d["write_total"]),
                    f"{d['read_count']:,}",
                    f"{d['write_count']:,}",
                )

            self.query_one("#diskio-bars", Static).update(
                bars_text or "[dim]No disk I/O data available.[/dim]"
            )
        except Exception:
            pass
