"""Battery screen – charge level, status, time remaining."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container

from core.battery import get_battery_info


def _bar(percent: float, width: int = 32) -> str:
    filled = int(width * percent / 100)
    empty = width - filled
    color = "green" if percent > 40 else ("yellow" if percent > 15 else "red")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class BatteryScreen(Widget):
    """Battery status screen with charge bar."""

    REFRESH_INTERVAL = 5.0

    def compose(self) -> ComposeResult:
        with Container(id="bat-container"):
            yield Static("", id="bat-card", classes="info-card")

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            card = self.query_one("#bat-card", Static)
            data = get_battery_info()

            if data is None:
                card.update(
                    "[b cyan]  Battery[/b cyan]\n\n"
                    "  [dim]No battery detected on this system.[/dim]"
                )
                return

            pct = data["percent"]
            plug = "[green]Plugged In[/green]" if data["plugged"] else "[yellow]On Battery[/yellow]"
            color = "green" if pct > 40 else ("yellow" if pct > 15 else "red")
            charge_label = "Charging" if data["plugged"] else "Discharging"

            card.update(
                f"[b cyan]  Battery Status[/b cyan]\n\n"
                f"  {_bar(pct)}\n\n"
                f"  Charge      [{color}][b]{pct:.1f}%[/b][/{color}]  [dim]({charge_label})[/dim]\n"
                f"  Status      {plug}\n"
                f"  Time Left   [cyan]{data['time_left']}[/cyan]"
            )
        except Exception:
            pass
