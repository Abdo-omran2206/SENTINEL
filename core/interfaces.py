"""Network interfaces fetcher – all NICs, IPs, MACs, speeds."""

import psutil
import socket
from typing import List


def get_interfaces() -> List[dict]:
    """
    Return a list of network interfaces with addresses, stats and traffic.
    Each dict: name, ipv4, ipv6, mac, is_up, speed(Mbps),
               bytes_sent, bytes_recv, packets_sent, packets_recv.
    """
    addrs  = psutil.net_if_addrs()
    stats  = psutil.net_if_stats()
    io_map = psutil.net_io_counters(pernic=True)

    result = []
    for name, addr_list in addrs.items():
        ipv4 = ipv6 = mac = "N/A"
        for a in addr_list:
            if a.family == socket.AF_INET:
                ipv4 = a.address
            elif a.family == socket.AF_INET6:
                ipv6 = a.address.split("%")[0]  # strip zone id
            # AF_PACKET (Linux=17) or AF_LINK (macOS=-1) or psutil constant
            elif a.family in (psutil.AF_LINK,):
                mac = a.address

        stat = stats.get(name)
        nic  = io_map.get(name)

        result.append({
            "name":         name,
            "ipv4":         ipv4,
            "ipv6":         ipv6,
            "mac":          mac,
            "is_up":        stat.isup   if stat else False,
            "speed":        stat.speed  if stat else 0,   # Mbps
            "mtu":          stat.mtu    if stat else 0,
            "bytes_sent":   nic.bytes_sent   if nic else 0,
            "bytes_recv":   nic.bytes_recv   if nic else 0,
            "packets_sent": nic.packets_sent if nic else 0,
            "packets_recv": nic.packets_recv if nic else 0,
            "errin":        nic.errin        if nic else 0,
            "errout":       nic.errout       if nic else 0,
        })

    return result
