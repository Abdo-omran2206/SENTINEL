"""Dashboard overview screen – shows a snapshot of every subsystem."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container

from core.cpu import get_cpu_info
from core.ram import get_ram_info
from core.disk import get_disk_info
from core.network import get_network_info
from core.battery import get_battery_info
from utils.formatter import Formatter
import platform
import getpass


def _bar(percent: float, width: int = 20) -> str:
    """Return a coloured ASCII progress bar string."""
    filled = int(width * percent / 100)
    empty = width - filled
    if percent >= 85:
        color = "red"
    elif percent >= 60:
        color = "yellow"
    else:
        color = "green"
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class MetricCard(Static):
    """A single metric card widget."""

    def __init__(self, card_id: str, title: str, **kwargs):
        super().__init__("", id=card_id, classes="dash-card", **kwargs)
        self._title = title

    def set_content(self, lines: list) -> None:
        title_line = f"[b cyan]{self._title}[/b cyan]"
        body = "\n".join(lines)
        self.update(f"{title_line}\n\n{body}")


class DashboardScreen(Widget):
    """Home screen: live snapshot of all subsystems."""

    REFRESH_INTERVAL = 1.0

    def compose(self) -> ComposeResult:
        with Container(id="dash-grid"):
            yield MetricCard("card-cpu",     "  CPU")
            yield MetricCard("card-ram",     "  RAM")
            yield MetricCard("card-disk",    "  DISK")
            yield MetricCard("card-net",     "  NETWORK")
            yield MetricCard("card-battery", "  BATTERY")
            yield MetricCard("card-system",  "  SYSTEM")

    def on_mount(self) -> None:
        self._refresh_all()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh_all)

    def _refresh_all(self) -> None:
        self._update_cpu()
        self._update_ram()
        self._update_disk()
        self._update_network()
        self._update_battery()
        self._update_system()

    def _update_cpu(self) -> None:
        try:
            d = get_cpu_info()
            card = self.query_one("#card-cpu", MetricCard)
            card.set_content([
                f"{_bar(d['usage'])}  [b]{d['usage']:.1f}%[/b]",
                f"Cores [cyan]{d['cores']}[/cyan]   Threads [cyan]{d['threads']}[/cyan]",
                f"Freq  [cyan]{d['freq_current']:.0f} MHz[/cyan]",
            ])
        except Exception as e:
            self.query_one("#card-cpu", MetricCard).set_content([f"[red]Error: {e}[/red]"])

    def _update_ram(self) -> None:
        try:
            d = get_ram_info()
            card = self.query_one("#card-ram", MetricCard)
            card.set_content([
                f"{_bar(d['percent'])}  [b]{d['percent']:.1f}%[/b]",
                f"Used  [cyan]{Formatter.format_bytes(d['used'])}[/cyan] / {Formatter.format_bytes(d['total'])}",
                f"Swap  [cyan]{d['swap_percent']:.1f}%[/cyan]",
            ])
        except Exception as e:
            self.query_one("#card-ram", MetricCard).set_content([f"[red]Error: {e}[/red]"])

    def _update_disk(self) -> None:
        try:
            parts = get_disk_info()
            card = self.query_one("#card-disk", MetricCard)
            lines = []
            for p in parts[:3]:
                lines.append(
                    f"{p['device']:8s} {_bar(p['percent'], 12)} [b]{p['percent']:.1f}%[/b]"
                )
            card.set_content(lines or ["No disks found."])
        except Exception as e:
            self.query_one("#card-disk", MetricCard).set_content([f"[red]Error: {e}[/red]"])

    def _update_network(self) -> None:
        try:
            d = get_network_info()
            card = self.query_one("#card-net", MetricCard)
            card.set_content([
                f"[green]Down[/green]  [b]{Formatter.format_speed(d['download_speed'])}[/b]",
                f"[magenta]Up[/magenta]    [b]{Formatter.format_speed(d['upload_speed'])}[/b]",
                f"IP    [cyan]{d['ip']}[/cyan]",
            ])
        except Exception as e:
            self.query_one("#card-net", MetricCard).set_content([f"[red]Error: {e}[/red]"])

    def _update_battery(self) -> None:
        try:
            card = self.query_one("#card-battery", MetricCard)
            data = get_battery_info()
            if data is None:
                card.set_content(["[dim]No battery detected.[/dim]"])
                return
            plug = "[green]Plugged In[/green]" if data["plugged"] else "[yellow]On Battery[/yellow]"
            card.set_content([
                f"{_bar(data['percent'])}  [b]{data['percent']:.1f}%[/b]",
                plug,
                f"Time   [cyan]{data['time_left']}[/cyan]",
            ])
        except Exception as e:
            self.query_one("#card-battery", MetricCard).set_content([f"[red]Error: {e}[/red]"])

    def _update_system(self) -> None:
        try:
            card = self.query_one("#card-system", MetricCard)
            card.set_content([
                f"Host  [cyan]{platform.node()}[/cyan]",
                f"OS    [cyan]{platform.system()} {platform.release()}[/cyan]",
                f"User  [cyan]{getpass.getuser()}[/cyan]",
            ])
        except Exception as e:
            self.query_one("#card-system", MetricCard).set_content([f"[red]Error: {e}[/red]"])
