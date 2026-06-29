"""CPU screen – per-core bars, frequency, thread info."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container

from core.cpu import get_cpu_info


def _bar(percent: float, width: int = 28) -> str:
    filled = int(width * percent / 100)
    empty = width - filled
    color = "red" if percent >= 85 else ("yellow" if percent >= 60 else "cyan")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


class CoreBar(Static):
    """A labelled progress bar row for a single CPU core."""

    def __init__(self, core_id: int, **kwargs):
        super().__init__("", id=f"core-{core_id}", classes="core-bar", **kwargs)
        self._core_id = core_id

    def refresh_value(self, percent: float) -> None:
        bar = _bar(percent)
        color = "red" if percent >= 85 else ("yellow" if percent >= 60 else "cyan")
        label = f"Core {self._core_id:>2}"
        self.update(f"[dim]{label}[/dim]  {bar}  [{color}]{percent:>5.1f}%[/{color}]")


class CpuScreen(Widget):
    """Full CPU details: per-core usage, frequency, stats."""

    REFRESH_INTERVAL = 1.0
    _cores_built = False

    def compose(self) -> ComposeResult:
        yield Static("", id="cpu-summary", classes="section-header")
        yield Container(id="cpu-cores-container")

    def on_mount(self) -> None:
        self._build_core_bars()
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _build_core_bars(self) -> None:
        if self._cores_built:
            return
        try:
            data = get_cpu_info()
            container = self.query_one("#cpu-cores-container")
            for i in range(len(data["per_core"])):
                container.mount(CoreBar(i))
            self._cores_built = True
        except Exception:
            pass

    def _refresh(self) -> None:
        try:
            data = get_cpu_info()
            summary = self.query_one("#cpu-summary", Static)
            summary.update(
                f"[b cyan]Overall[/b cyan]  [b]{data['usage']:.1f}%[/b]    "
                f"[dim]Cores[/dim] [cyan]{data['cores']}[/cyan]  "
                f"[dim]Threads[/dim] [cyan]{data['threads']}[/cyan]    "
                f"[dim]Freq[/dim] [cyan]{data['freq_current']:.0f}[/cyan] / "
                f"[cyan]{data['freq_max']:.0f}[/cyan] MHz"
            )
            for i, pct in enumerate(data["per_core"]):
                try:
                    self.query_one(f"#core-{i}", CoreBar).refresh_value(pct)
                except Exception:
                    pass
        except Exception as e:
            pass
