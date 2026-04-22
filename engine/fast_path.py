"""
Fast-path classifier — quickly decides a packet's fate without deep inspection.
Python port of fast_path.cpp / fast_path.h.
"""

from .types import PacketInfo, Protocol
from .rule_manager import RuleManager


class FastPath:
    """
    Applies cheap pre-checks: IP block list and well-known port classification.
    Mirrors the C++ FastPath class.
    """

    def __init__(self, rule_manager: RuleManager):
        self.rule_manager = rule_manager

    def classify_by_port(self, pkt: PacketInfo) -> str:
        """Return a coarse application label based on port numbers."""
        ports = {pkt.src_port, pkt.dst_port}
        if 443 in ports and pkt.protocol == Protocol.TCP:
            return "HTTPS"
        if 80 in ports and pkt.protocol == Protocol.TCP:
            return "HTTP"
        if 53 in ports and pkt.protocol == Protocol.UDP:
            return "DNS"
        return "Unknown"

    def is_ip_blocked(self, src_ip: str) -> bool:
        return src_ip in self.rule_manager.blocked_ips
