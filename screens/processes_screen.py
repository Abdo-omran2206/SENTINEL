"""Processes screen – top-20 processes with sort toggle and kill."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable, Input, Button
from textual.containers import Container, Horizontal
from textual import on

from core.processes import get_processes, kill_process


class ProcessesScreen(Widget):
    """Process manager screen with search, sort toggle and kill."""

    REFRESH_INTERVAL = 2.0

    _sort_by: str = "cpu"
    _search: str = ""

    def compose(self) -> ComposeResult:
        with Container(id="proc-container"):
            with Horizontal(id="proc-toolbar"):
                yield Input(placeholder="Search process name...", id="proc-search")
                yield Button("Sort: CPU", id="btn-sort", variant="primary")
                yield Button("Kill Selected", id="btn-kill", variant="error")
            yield Static("", id="proc-status")
            yield DataTable(id="proc-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#proc-table", DataTable)
        table.add_columns("Name", "PID", "CPU %", "RAM %", "Status")
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            procs = get_processes(sort_by=self._sort_by, search=self._search)
            table = self.query_one("#proc-table", DataTable)
            table.clear()
            for p in procs:
                cpu_color = "red" if p["cpu"] > 50 else ("yellow" if p["cpu"] > 20 else "white")
                mem_color = "red" if p["memory"] > 20 else ("yellow" if p["memory"] > 10 else "white")
                table.add_row(
                    p["name"],
                    str(p["pid"]),
                    f"[{cpu_color}]{p['cpu']:.1f}[/{cpu_color}]",
                    f"[{mem_color}]{p['memory']:.2f}[/{mem_color}]",
                    p["status"],
                )
        except Exception:
            pass

    @on(Input.Changed, "#proc-search")
    def on_search_changed(self, event: Input.Changed) -> None:
        self._search = event.value
        self._refresh()

    @on(Button.Pressed, "#btn-sort")
    def on_sort_toggle(self) -> None:
        self._sort_by = "memory" if self._sort_by == "cpu" else "cpu"
        label = "Sort: CPU" if self._sort_by == "cpu" else "Sort: RAM"
        self.query_one("#btn-sort", Button).label = label
        self._refresh()

    @on(Button.Pressed, "#btn-kill")
    def on_kill_pressed(self) -> None:
        self._do_kill()

    def _do_kill(self) -> None:
        try:
            table = self.query_one("#proc-table", DataTable)
            row_idx = table.cursor_row
            row_data = table.get_row_at(row_idx)
            pid = int(str(row_data[1]))
            success, msg = kill_process(pid)
            status = self.query_one("#proc-status", Static)
            color = "green" if success else "red"
            status.update(f"[{color}]{msg}[/{color}]")
            self._refresh()
        except Exception as e:
            try:
                self.query_one("#proc-status", Static).update(f"[red]Error: {e}[/red]")
            except Exception:
                pass
