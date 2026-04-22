"""
Flow / connection state tracker.
Python port of connection_tracker.cpp / connection_tracker.h.
"""

from typing import Dict, Optional
from .types import Flow, Protocol


class ConnectionTracker:
    """
    Maintains a table of active flows keyed by their bidirectional 5-tuple.
    Mirrors the C++ ConnectionTracker class.
    """

    def __init__(self):
        self._flows: Dict[str, Flow] = {}
        self._next_id: int = 1

    def _make_key(
        self,
        src_ip: str,
        src_port: int,
        dst_ip: str,
        dst_port: int,
        protocol: str,
    ) -> str:
        """Build a canonical bidirectional tuple key (lower IP first)."""
        proto_num = 6 if protocol == Protocol.TCP else 17
        if (src_ip, src_port) < (dst_ip, dst_port):
            return f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{proto_num}"
        return f"{dst_ip}:{dst_port}-{src_ip}:{src_port}-{proto_num}"

    def get_or_create(
        self,
        src_ip: str,
        src_port: int,
        dst_ip: str,
        dst_port: int,
        protocol: str,
    ) -> Flow:
        """Return the existing flow or create a new one."""
        key = self._make_key(src_ip, src_port, dst_ip, dst_port, protocol)
        if key not in self._flows:
            flow = Flow(
                id=self._next_id,
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol,
            )
            self._flows[key] = flow
            self._next_id += 1
        return self._flows[key]

    def all_flows(self):
        return list(self._flows.values())

    @property
    def flow_count(self) -> int:
        return len(self._flows)
