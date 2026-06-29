"""Network interfaces screen – all NICs with IPs, MACs and traffic."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable
from textual.containers import Container

from core.interfaces import get_interfaces
from utils.formatter import Formatter


class InterfacesScreen(Widget):
    """All network interfaces: status, IPs, MACs and traffic."""

    REFRESH_INTERVAL = 3.0

    def compose(self) -> ComposeResult:
        with Container(id="iface-container"):
            yield Static("", id="iface-cards", classes="info-card")
            yield DataTable(id="iface-table", show_cursor=True)

    def on_mount(self) -> None:
        table = self.query_one("#iface-table", DataTable)
        table.add_columns("Interface", "IPv4", "MAC",
                          "Speed", "Sent", "Recv", "Err↑", "Err↓")
        self._refresh()
        self.set_interval(self.REFRESH_INTERVAL, self._refresh)

    def _refresh(self) -> None:
        try:
            ifaces = get_interfaces()
            table  = self.query_one("#iface-table", DataTable)
            table.clear()

            cards_text = ""
            for iface in ifaces:
                status_icon  = "[green]●[/green]" if iface["is_up"] else "[red]○[/red]"
                status_label = "[green]UP[/green]" if iface["is_up"] else "[red]DOWN[/red]"
                speed_str    = f"{iface['speed']} Mbps" if iface["speed"] else "N/A"

                cards_text += (
                    f"  {status_icon} [b cyan]{iface['name']}[/b cyan]  {status_label}  "
                    f"[dim]{speed_str}[/dim]\n"
                    f"    IPv4  [cyan]{iface['ipv4']}[/cyan]   "
                    f"MAC   [dim]{iface['mac']}[/dim]\n"
                    f"    Sent  [magenta]{Formatter.format_bytes(iface['bytes_sent'])}[/magenta]   "
                    f"Recv  [green]{Formatter.format_bytes(iface['bytes_recv'])}[/green]\n\n"
                )

                table.add_row(
                    iface["name"],
                    iface["ipv4"],
                    iface["mac"],
                    speed_str,
                    Formatter.format_bytes(iface["bytes_sent"]),
                    Formatter.format_bytes(iface["bytes_recv"]),
                    str(iface["errout"]),
                    str(iface["errin"]),
                )

            self.query_one("#iface-cards", Static).update(
                f"[b cyan]  Network Interfaces[/b cyan]\n\n{cards_text}"
                if cards_text else "[dim]No interfaces found.[/dim]"
            )
        except Exception:
            pass
