"""Temperatures & fans screen."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container, Horizontal

from core.temperatures import get_temperatures, get_fans


def _temp_color(c: float) -> str:
    return "red" if c >= 85 else ("yellow" if c >= 65 else "green")


def _temp_bar(current: float, critical: float = 100.0, width: int = 20) -> str:
    pct    = min((current / (critical or 100)) * 100, 100)
    filled = int(width * pct / 100)
    empty  = width - filled
    color  = _temp_color(current)
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class TemperaturesScreen(Widget):
    """Hardware temperature and fan speed monitor."""

    REFRESH_INTERVAL = 2.0

    def compose(self) -> ComposeResult:
        with Container(id="temps-container"):
            with Horizontal(id="temps-row"):
                yield Static("", id="temps-sensors", classes="temps-card")
                yield Static("", id="temps-fans",    classes="temps-card")

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            temps = get_temperatures()
            fans  = get_fans()

            # ── Sensors ──────────────────────────────────────────────────
            sensor_widget = self.query_one("#temps-sensors", Static)
            if not temps:
                sensor_widget.update(
                    "[b cyan]  Temperature Sensors[/b cyan]\n\n"
                    "  [dim]Not available on this system.[/dim]\n"
                    "  [dim](Windows has limited sensor support)[/dim]"
                )
            else:
                lines = ["[b cyan]  Temperature Sensors[/b cyan]\n"]
                for sensor, readings in temps.items():
                    lines.append(f"  [dim]{sensor}[/dim]")
                    for r in readings:
                        crit  = r["critical"] or 100.0
                        bar   = _temp_bar(r["current"], crit)
                        color = _temp_color(r["current"])
                        lines.append(
                            f"    {r['label'][:14]:<14} {bar} "
                            f"[{color}]{r['current']:.0f}°C[/{color}]"
                            + (f"  [dim](crit {crit:.0f}°C)[/dim]" if r["critical"] else "")
                        )
                    lines.append("")
                sensor_widget.update("\n".join(lines))

            # ── Fans ─────────────────────────────────────────────────────
            fan_widget = self.query_one("#temps-fans", Static)
            if not fans:
                fan_widget.update(
                    "[b cyan]  Fan Speeds[/b cyan]\n\n"
                    "  [dim]No fan sensors detected.[/dim]"
                )
            else:
                lines = ["[b cyan]  Fan Speeds[/b cyan]\n"]
                for fan_name, readings in fans.items():
                    lines.append(f"  [dim]{fan_name}[/dim]")
                    for r in readings:
                        rpm = r["current"]
                        color = "green" if rpm > 0 else "red"
                        lines.append(f"    {r['label'][:14]:<14} [{color}]{rpm} RPM[/{color}]")
                    lines.append("")
                fan_widget.update("\n".join(lines))

        except Exception as e:
            pass
