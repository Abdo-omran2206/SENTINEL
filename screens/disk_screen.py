"""Disk screen – all partitions with usage bars."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable
from textual.containers import Container

from core.disk import get_disk_info
from utils.formatter import Formatter


def _bar(percent: float, width: int = 16) -> str:
    filled = int(width * percent / 100)
    empty = width - filled
    color = "red" if percent >= 85 else ("yellow" if percent >= 60 else "cyan")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class DiskScreen(Widget):
    """Disk partitions screen with live refresh."""

    REFRESH_INTERVAL = 3.0

    def compose(self) -> ComposeResult:
        with Container(id="disk-container"):
            yield Static("", id="disk-cards", classes="info-card")
            yield DataTable(id="disk-table", show_cursor=True)

    def on_mount(self) -> None:
        table = self.query_one("#disk-table", DataTable)
        table.add_columns("Device", "Mount", "FS", "Total", "Used", "Free", "Usage %")
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            parts = get_disk_info()
            table = self.query_one("#disk-table", DataTable)
            table.clear()

            cards_text = ""
            for p in parts:
                table.add_row(
                    p["device"],
                    p["mountpoint"],
                    p["fstype"],
                    Formatter.format_bytes(p["total"]),
                    Formatter.format_bytes(p["used"]),
                    Formatter.format_bytes(p["free"]),
                    f"{p['percent']:.1f}%",
                )
                bar = _bar(p["percent"])
                color = "red" if p["percent"] >= 85 else ("yellow" if p["percent"] >= 60 else "cyan")
                cards_text += (
                    f"[b cyan]{p['device']}[/b cyan]  [{color}]{p['percent']:.1f}%[/{color}]  "
                    f"[dim]Used[/dim] [cyan]{Formatter.format_bytes(p['used'])}[/cyan]"
                    f" / [cyan]{Formatter.format_bytes(p['total'])}[/cyan]\n"
                    f"  {bar}\n\n"
                )

            self.query_one("#disk-cards", Static).update(cards_text or "No disk partitions found.")
        except Exception:
            pass
