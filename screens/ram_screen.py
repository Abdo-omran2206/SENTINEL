"""RAM screen – virtual memory and swap with visual bars."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container

from core.ram import get_ram_info
from utils.formatter import Formatter


def _bar(percent: float, width: int = 30) -> str:
    filled = int(width * percent / 100)
    empty = width - filled
    color = "red" if percent >= 85 else ("yellow" if percent >= 60 else "cyan")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class RamScreen(Widget):
    """RAM & swap usage screen with live refresh."""

    REFRESH_INTERVAL = 1.0

    def compose(self) -> ComposeResult:
        with Container(id="ram-container"):
            yield Static("", id="ram-virtual", classes="info-card")
            yield Static("", id="ram-swap",    classes="info-card")
            yield Static("", id="ram-detail",  classes="info-card")

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            d = get_ram_info()

            self.query_one("#ram-virtual", Static).update(
                f"[b cyan]  Virtual Memory[/b cyan]\n\n"
                f"  {_bar(d['percent'])}\n\n"
                f"  Usage     [b]{d['percent']:.1f}%[/b]\n"
                f"  Used      [cyan]{Formatter.format_bytes(d['used'])}[/cyan]\n"
                f"  Free      [cyan]{Formatter.format_bytes(d['available'])}[/cyan]\n"
                f"  Total     [cyan]{Formatter.format_bytes(d['total'])}[/cyan]"
            )

            self.query_one("#ram-swap", Static).update(
                f"[b cyan]  Swap Memory[/b cyan]\n\n"
                f"  {_bar(d['swap_percent'])}\n\n"
                f"  Usage     [b]{d['swap_percent']:.1f}%[/b]\n"
                f"  Used      [cyan]{Formatter.format_bytes(d['swap_used'])}[/cyan]\n"
                f"  Total     [cyan]{Formatter.format_bytes(d['swap_total'])}[/cyan]"
            )

            pressure = (
                "[green]Low[/green]" if d["percent"] < 60
                else ("[yellow]Moderate[/yellow]" if d["percent"] < 85
                      else "[red]High[/red]")
            )
            self.query_one("#ram-detail", Static).update(
                f"[b cyan]  Memory Pressure[/b cyan]\n\n"
                f"  Status    {pressure}\n"
                f"  Cached    [cyan]{Formatter.format_bytes(d['cached'])}[/cyan]"
            )
        except Exception as e:
            pass
