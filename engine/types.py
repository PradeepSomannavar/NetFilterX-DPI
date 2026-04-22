"""
Data classes and enumerations mirroring the original C++ types.h / types.cpp.
"""

from dataclasses import dataclass, field
from typing import Optional


class FlowState:
    NEW = "NEW"
    ESTABLISHED = "ESTABLISHED"
    CLASSIFIED = "CLASSIFIED"
    CLOSED = "CLOSED"


class Protocol:
    TCP = "TCP"
    UDP = "UDP"
    UNKNOWN = "UNKNOWN"


@dataclass
class PacketInfo:
    timestamp_ms: float = 0.0
    src_ip: str = ""
    dst_ip: str = ""
    src_port: int = 0
    dst_port: int = 0
    protocol: str = Protocol.UNKNOWN
    payload: bytes = b""
    length: int = 0


@dataclass
class Flow:
    id: int = 0
    src_ip: str = ""
    dst_ip: str = ""
    src_port: int = 0
    dst_port: int = 0
    protocol: str = Protocol.UNKNOWN
    app: str = "Unknown"
    sni: str = ""
    packets: int = 0
    bytes: int = 0
    blocked: bool = False
    state: str = FlowState.NEW

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "srcIp": self.src_ip,
            "dstIp": self.dst_ip,
            "srcPort": self.src_port,
            "dstPort": self.dst_port,
            "protocol": self.protocol,
            "app": self.app,
            "sni": self.sni,
            "packets": self.packets,
            "bytes": self.bytes,
            "blocked": self.blocked,
            "state": self.state,
        }


@dataclass
class EngineStats:
    total_packets: int = 0
    forwarded: int = 0
    dropped: int = 0
    active_flows: int = 0
    total_bytes: int = 0
    tcp_packets: int = 0
    udp_packets: int = 0

    def to_dict(self) -> dict:
        return {
            "totalPackets": self.total_packets,
            "forwarded": self.forwarded,
            "dropped": self.dropped,
            "activeFlows": self.active_flows,
            "totalBytes": self.total_bytes,
            "tcpPackets": self.tcp_packets,
            "udpPackets": self.udp_packets,
        }


@dataclass
class TimelineBucket:
    start_time: float
    packets: int = 0
    dropped: int = 0
