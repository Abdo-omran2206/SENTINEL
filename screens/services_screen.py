"""System services screen – cross-platform."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable, Input
from textual.containers import Container, Horizontal
from textual import on

from core.services import get_services


_STATUS_COLOR = {
    "Running":  "green",
    "Stopped":  "red",
    "running":  "green",
    "stopped":  "red",
    "active":   "green",
    "inactive": "dim",
    "failed":   "red",
}


class ServicesScreen(Widget):
    """System services with search filter."""

    REFRESH_INTERVAL = 10.0
    _search: str = ""
    _all_services: list = []

    def compose(self) -> ComposeResult:
        with Container(id="svc-container"):
            with Horizontal(id="svc-toolbar"):
                yield Input(placeholder="Search service name...", id="svc-search")
            yield Static("", id="svc-status", classes="section-header")
            yield DataTable(id="svc-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#svc-table", DataTable)
        table.add_columns("Name", "Display Name", "Status")
        self._load()
        self.set_interval(self.REFRESH_INTERVAL, self._load)

    def _load(self) -> None:
        self._all_services = get_services(limit=200)
        self._render()

    def _render(self) -> None:
        try:
            query   = self._search.lower()
            visible = [
                s for s in self._all_services
                if not query
                or query in s["name"].lower()
                or query in s["display_name"].lower()
            ]

            running = sum(1 for s in visible if s["status"].lower() in ("running", "active"))
            stopped = len(visible) - running

            self.query_one("#svc-status", Static).update(
                f"[b cyan]  Services[/b cyan]  "
                f"[green]Running {running}[/green]  "
                f"[red]Stopped {stopped}[/red]  "
                f"[dim]Total {len(visible)}[/dim]"
            )

            table = self.query_one("#svc-table", DataTable)
            table.clear()
            for s in visible:
                color  = _STATUS_COLOR.get(s["status"], "white")
                status = f"[{color}]{s['status']}[/{color}]"
                table.add_row(s["name"], s["display_name"], status)
        except Exception:
            pass

    @on(Input.Changed, "#svc-search")
    def on_search(self, event: Input.Changed) -> None:
        self._search = event.value
        self._render()
