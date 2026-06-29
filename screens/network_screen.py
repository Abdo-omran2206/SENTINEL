"""Network screen – live download/upload speed, totals, IP."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container, Horizontal

from core.network import get_network_info
from utils.formatter import Formatter


class NetworkScreen(Widget):
    """Network statistics screen with live speed refresh."""

    REFRESH_INTERVAL = 1.0

    def compose(self) -> ComposeResult:
        with Container(id="net-container"):
            with Horizontal(id="net-speed-row"):
                yield Static("", id="net-dl", classes="net-card")
                yield Static("", id="net-ul", classes="net-card")
            yield Static("", id="net-info",  classes="info-card")
            yield Static("", id="net-total", classes="info-card")

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            d = get_network_info()

            self.query_one("#net-dl", Static).update(
                f"[b green]  Download[/b green]\n\n"
                f"  [b]{Formatter.format_speed(d['download_speed'])}[/b]"
            )
            self.query_one("#net-ul", Static).update(
                f"[b magenta]  Upload[/b magenta]\n\n"
                f"  [b]{Formatter.format_speed(d['upload_speed'])}[/b]"
            )
            self.query_one("#net-info", Static).update(
                f"[b cyan]  Connection Info[/b cyan]\n\n"
                f"  IP Address   [cyan]{d['ip']}[/cyan]\n"
                f"  Hostname     [cyan]{d['hostname']}[/cyan]"
            )
            self.query_one("#net-total", Static).update(
                f"[b cyan]  Session Totals[/b cyan]\n\n"
                f"  Received   [cyan]{Formatter.format_bytes(d['bytes_recv'])}[/cyan]  "
                f"[dim]({d['packets_recv']:,} packets)[/dim]\n"
                f"  Sent       [cyan]{Formatter.format_bytes(d['bytes_sent'])}[/cyan]  "
                f"[dim]({d['packets_sent']:,} packets)[/dim]"
            )
        except Exception:
            pass
