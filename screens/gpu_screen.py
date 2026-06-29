"""GPU monitor screen."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container

from core.gpu import get_gpu_info


def _bar(percent: float, width: int = 30) -> str:
    filled = int(width * percent / 100)
    empty  = width - filled
    color  = "red" if percent >= 85 else ("yellow" if percent >= 60 else "green")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class GpuScreen(Widget):
    """GPU usage, VRAM, temperature with live refresh."""

    REFRESH_INTERVAL = 1.0

    def compose(self) -> ComposeResult:
        with Container(id="gpu-container"):
            yield Static("", id="gpu-content", classes="info-card")

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            widget = self.query_one("#gpu-content", Static)
            gpus   = get_gpu_info()

            if gpus is None:
                widget.update(
                    "[b cyan]  GPU Monitor[/b cyan]\n\n"
                    "  [dim]No NVIDIA GPU detected, or GPUtil not installed.[/dim]\n\n"
                    "  [dim]Install:[/dim]  [cyan]pip install gputil[/cyan]\n"
                    "  [dim]Supports:[/dim] NVIDIA GPUs only (AMD/Intel fallback coming)."
                )
                return

            lines = ["[b cyan]  GPU Monitor[/b cyan]\n"]
            for i, g in enumerate(gpus):
                load_bar  = _bar(g["load"])
                vram_bar  = _bar(g["vram_pct"])
                temp_color = "red" if g["temperature"] >= 85 else ("yellow" if g["temperature"] >= 70 else "green")

                lines += [
                    f"  [b]GPU {i} — {g['name']}[/b]",
                    f"",
                    f"  Usage     {load_bar}  [b]{g['load']:.1f}%[/b]",
                    f"  VRAM      {vram_bar}  [b]{g['vram_pct']:.1f}%[/b]",
                    f"            [dim]{g['vram_used']:.0f} MB used / {g['vram_total']:.0f} MB total[/dim]",
                    f"  Temp      [{temp_color}][b]{g['temperature']}°C[/b][/{temp_color}]",
                    f"  Driver    [cyan]{g['driver']}[/cyan]",
                    f"",
                ]

            widget.update("\n".join(lines))
        except Exception as e:
            self.query_one("#gpu-content", Static).update(f"[red]Error: {e}[/red]")
