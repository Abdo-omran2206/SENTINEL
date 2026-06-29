"""System uptime & load screen."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container, Horizontal

from core.uptime import get_uptime


def _load_bar(load: float, cpu_count: int, width: int = 20) -> str:
    """Bar relative to cpu_count (100% load = all CPUs pegged)."""
    pct    = min((load / max(cpu_count, 1)) * 100, 100)
    filled = int(width * pct / 100)
    empty  = width - filled
    color  = "red" if pct >= 90 else ("yellow" if pct >= 70 else "green")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class UptimeScreen(Widget):
    """System uptime, boot info, load average and OS details."""

    REFRESH_INTERVAL = 5.0

    def compose(self) -> ComposeResult:
        with Container(id="uptime-container"):
            with Horizontal(id="uptime-row"):
                yield Static("", id="uptime-uptime",  classes="info-card")
                yield Static("", id="uptime-load",    classes="info-card")
            yield Static("", id="uptime-os",       classes="info-card")

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            d = get_uptime()

            self.query_one("#uptime-uptime", Static).update(
                f"[b cyan]  System Uptime[/b cyan]\n\n"
                f"  [b]{d['uptime_str']}[/b]\n\n"
                f"  Boot Time  [cyan]{d['boot_time']}[/cyan]\n"
                f"  Hostname   [cyan]{d['hostname']}[/cyan]"
            )

            cpu = d["cpu_count"]
            load_windows = d["load_1"] == 0.0 and d["load_5"] == 0.0

            if load_windows:
                load_text = "[dim]Load average not available on Windows.[/dim]"
            else:
                b1  = _load_bar(d["load_1"],  cpu)
                b5  = _load_bar(d["load_5"],  cpu)
                b15 = _load_bar(d["load_15"], cpu)
                load_text = (
                    f"  1 min   {b1}  [b]{d['load_1']:.2f}[/b]\n"
                    f"  5 min   {b5}  [b]{d['load_5']:.2f}[/b]\n"
                    f"  15 min  {b15}  [b]{d['load_15']:.2f}[/b]\n\n"
                    f"  [dim](CPU count: {cpu})[/dim]"
                )

            self.query_one("#uptime-load", Static).update(
                f"[b cyan]  Load Average[/b cyan]\n\n{load_text}"
            )

            self.query_one("#uptime-os", Static).update(
                f"[b cyan]  System Information[/b cyan]\n\n"
                f"  OS          [cyan]{d['os_name']} {d['os_release']}[/cyan]\n"
                f"  Version     [dim]{d['os_version'][:60]}[/dim]\n"
                f"  Machine     [cyan]{d['machine']}[/cyan]  "
                f"Architecture [cyan]{d['architecture']}[/cyan]\n"
                f"  Python      [cyan]{d['python']}[/cyan]"
            )
        except Exception:
            pass
