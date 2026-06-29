"""Network connections & open ports screen."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable, Button
from textual.containers import Container, Horizontal
from textual import on

from core.connections import get_connections, get_listening_ports


_STATUS_COLOR = {
    "ESTABLISHED": "green",
    "LISTEN":      "cyan",
    "TIME_WAIT":   "yellow",
    "CLOSE_WAIT":  "yellow",
    "SYN_SENT":    "magenta",
    "FIN_WAIT1":   "dim",
    "FIN_WAIT2":   "dim",
    "CLOSED":      "dim",
}


class ConnectionsScreen(Widget):
    """Active network connections and open listening ports."""

    REFRESH_INTERVAL = 2.0
    _show_all: bool = True

    def compose(self) -> ComposeResult:
        with Container(id="conn-container"):
            yield Static("", id="conn-summary", classes="section-header")
            with Horizontal(id="conn-toolbar"):
                yield Button("All Connections", id="btn-all",    variant="primary")
                yield Button("Listening Only",  id="btn-listen", variant="default")
            yield DataTable(id="conn-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#conn-table", DataTable)
        table.add_columns("Proto", "Local Address", "Remote Address",
                          "Status", "PID", "Process")
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            conns = get_connections() if self._show_all else get_listening_ports()
            table = self.query_one("#conn-table", DataTable)
            table.clear()

            established = sum(1 for c in conns if c["status"] == "ESTABLISHED")
            listening   = sum(1 for c in conns if c["status"] == "LISTEN")

            self.query_one("#conn-summary", Static).update(
                f"[b cyan]  Connections[/b cyan]  "
                f"[green]Established {established}[/green]  "
                f"[cyan]Listening {listening}[/cyan]  "
                f"[dim]Total {len(conns)}[/dim]"
            )

            for c in conns:
                color  = _STATUS_COLOR.get(c["status"], "white")
                status = f"[{color}]{c['status']}[/{color}]"
                table.add_row(
                    c["proto"],
                    c["laddr"],
                    c["raddr"],
                    status,
                    str(c["pid"]) if c["pid"] else "—",
                    c["name"],
                )
        except Exception:
            pass

    @on(Button.Pressed, "#btn-all")
    def show_all(self) -> None:
        self._show_all = True
        self.query_one("#btn-all",    Button).variant = "primary"
        self.query_one("#btn-listen", Button).variant = "default"
        self._refresh()

    @on(Button.Pressed, "#btn-listen")
    def show_listen(self) -> None:
        self._show_all = False
        self.query_one("#btn-all",    Button).variant = "default"
        self.query_one("#btn-listen", Button).variant = "primary"
        self._refresh()
