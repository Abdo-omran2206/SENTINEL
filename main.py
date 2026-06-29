"""
Sentinel – God's Eye System Monitor
Entry point with sectioned sidebar navigation and 15 live views.
"""

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Container

# ── Screens ───────────────────────────────────────────────────────────────
from screens.dashboard         import DashboardScreen
from screens.cpu_screen        import CpuScreen
from screens.ram_screen        import RamScreen
from screens.gpu_screen        import GpuScreen
from screens.temperatures_screen import TemperaturesScreen
from screens.disk_screen       import DiskScreen
from screens.disk_io_screen    import DiskIoScreen
from screens.network_screen    import NetworkScreen
from screens.interfaces_screen import InterfacesScreen
from screens.connections_screen import ConnectionsScreen
from screens.processes_screen  import ProcessesScreen
from screens.services_screen   import ServicesScreen
from screens.users_screen      import UsersScreen
from screens.uptime_screen     import UptimeScreen
from screens.battery_screen    import BatteryScreen


# ── Sectioned navigation definition ──────────────────────────────────────
NAV_SECTIONS = [
    ("OVERVIEW", [
        ("dashboard",    "  Dashboard",    DashboardScreen),
    ]),
    ("HARDWARE", [
        ("cpu",          "  CPU",          CpuScreen),
        ("ram",          "  RAM",          RamScreen),
        ("gpu",          "  GPU",          GpuScreen),
        ("temperatures", "  Temperatures", TemperaturesScreen),
    ]),
    ("STORAGE", [
        ("disk",         "  Disk",         DiskScreen),
        ("disk_io",      "  Disk I/O",     DiskIoScreen),
    ]),
    ("NETWORK", [
        ("network",      "  Speed",        NetworkScreen),
        ("interfaces",   "  Interfaces",   InterfacesScreen),
        ("connections",  "  Connections",  ConnectionsScreen),
    ]),
    ("SYSTEM", [
        ("processes",    "  Processes",    ProcessesScreen),
        ("services",     "  Services",     ServicesScreen),
        ("users",        "  Users",        UsersScreen),
        ("uptime",       "  Uptime",       UptimeScreen),
    ]),
    ("POWER", [
        ("battery",      "  Battery",      BatteryScreen),
    ]),
]

# Flat list for easy lookup
ALL_NAV = [(nid, lbl, cls) for _, items in NAV_SECTIONS for nid, lbl, cls in items]


class NavItem(Static):
    """Clickable sidebar navigation entry."""

    def __init__(self, nav_id: str, label: str, **kwargs):
        super().__init__(label, id=f"nav-{nav_id}", classes="nav-item", **kwargs)
        self._nav_id = nav_id

    def on_click(self) -> None:
        self.app.switch_nav(self._nav_id)  # type: ignore[attr-defined]


class SentinelApp(App):
    """Sentinel – God's Eye real-time system monitor."""

    CSS_PATH = "sentinel.tcss"
    TITLE    = "Sentinel"

    BINDINGS = [
        ("q", "quit",          "Quit"),
        ("1", "nav_dashboard", "Dashboard"),
        ("2", "nav_cpu",       "CPU"),
        ("3", "nav_ram",       "RAM"),
        ("4", "nav_gpu",       "GPU"),
        ("5", "nav_disk",      "Disk"),
        ("6", "nav_network",   "Network"),
        ("7", "nav_processes", "Processes"),
        ("8", "nav_services",  "Services"),
        ("9", "nav_uptime",    "Uptime"),
    ]

    def compose(self) -> ComposeResult:
        # ── Sidebar with sections ─────────────────────────────────────
        with Container(id="sidebar"):
            yield Static(" SENTINEL", id="sidebar-logo")
            for section_label, items in NAV_SECTIONS:
                yield Static(section_label, classes="nav-section-header")
                for nav_id, label, _ in items:
                    yield NavItem(nav_id, label)

        # ── Content: all screen widgets stacked ───────────────────────
        with Container(id="content"):
            for nav_id, _, ScreenClass in ALL_NAV:
                yield ScreenClass(id=f"screen-{nav_id}")

        yield Static(
            " [dim]q[/dim] Quit  [dim]1-9[/dim] Quick Nav  "
            "[dim]Click sidebar[/dim] to switch screens",
            id="footer-bar",
        )

    def on_mount(self) -> None:
        self.switch_nav("dashboard")

    # ── Navigation ────────────────────────────────────────────────────

    def switch_nav(self, nav_id: str) -> None:
        """Show the chosen screen widget, hide all others, update sidebar."""
        for nid, _, _ in ALL_NAV:
            try:
                self.query_one(f"#screen-{nid}").display = (nid == nav_id)
                nav_w = self.query_one(f"#nav-{nid}", NavItem)
                if nid == nav_id:
                    nav_w.add_class("-active")
                else:
                    nav_w.remove_class("-active")
            except Exception:
                pass

    # ── Keybindings ───────────────────────────────────────────────────
    def action_nav_dashboard(self) -> None: self.switch_nav("dashboard")
    def action_nav_cpu(self)       -> None: self.switch_nav("cpu")
    def action_nav_ram(self)       -> None: self.switch_nav("ram")
    def action_nav_gpu(self)       -> None: self.switch_nav("gpu")
    def action_nav_disk(self)      -> None: self.switch_nav("disk")
    def action_nav_network(self)   -> None: self.switch_nav("network")
    def action_nav_processes(self) -> None: self.switch_nav("processes")
    def action_nav_services(self)  -> None: self.switch_nav("services")
    def action_nav_uptime(self)    -> None: self.switch_nav("uptime")


if __name__ == "__main__":
    SentinelApp().run()