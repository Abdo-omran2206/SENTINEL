"""Logged-in users screen."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable
from textual.containers import Container

from core.users import get_users


class UsersScreen(Widget):
    """Shows all currently logged-in users."""

    REFRESH_INTERVAL = 5.0

    def compose(self) -> ComposeResult:
        with Container(id="users-container"):
            yield Static("", id="users-header", classes="section-header")
            yield DataTable(id="users-table", show_cursor=True)
            yield Static("", id="users-detail", classes="info-card")

    def on_mount(self) -> None:
        table = self.query_one("#users-table", DataTable)
        table.add_columns("Username", "Terminal", "Host / IP", "Logged In", "Duration")
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            users = get_users()
            table = self.query_one("#users-table", DataTable)
            table.clear()

            self.query_one("#users-header", Static).update(
                f"[b cyan]  Active Users[/b cyan]  "
                f"[cyan]{len(users)} session{'s' if len(users) != 1 else ''}[/cyan]"
            )

            for u in users:
                table.add_row(
                    u["name"],
                    u["terminal"],
                    u["host"],
                    u["started"],
                    u["duration"],
                )

            if not users:
                self.query_one("#users-detail", Static).update(
                    "[dim]No active user sessions detected.[/dim]"
                )
            else:
                names = ", ".join(set(u["name"] for u in users))
                self.query_one("#users-detail", Static).update(
                    f"[dim]Users:[/dim] [cyan]{names}[/cyan]"
                )
        except Exception:
            pass
