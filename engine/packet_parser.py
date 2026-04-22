"""
Low-level Ethernet/IP/TCP/UDP packet parser.
Python port of packet_parser.cpp / packet_parser.h.
"""

import struct
from typing import Optional, Tuple
from .types import PacketInfo, Protocol


# Ethernet type for IPv4
ETH_TYPE_IPV4 = 0x0800

# IP protocol numbers
IP_PROTO_TCP = 6
IP_PROTO_UDP = 17


def parse_packet(raw: bytes, timestamp_ms: float) -> Optional[PacketInfo]:
    """
    Parse a raw Ethernet frame and extract a PacketInfo.
    Returns None if the packet is not IPv4 TCP/UDP.
    """
    if len(raw) < 14:
        return None

    eth_type = struct.unpack_from(">H", raw, 12)[0]
    if eth_type != ETH_TYPE_IPV4:
        return None

    if len(raw) < 34:
        return None

    ip_header_len = (raw[14] & 0x0F) * 4
    protocol = raw[23]

    src_ip = ".".join(str(b) for b in raw[26:30])
    dst_ip = ".".join(str(b) for b in raw[30:34])

    if protocol == IP_PROTO_TCP:
        if len(raw) < 14 + ip_header_len + 20:
            return None
        src_port = struct.unpack_from(">H", raw, 14 + ip_header_len)[0]
        dst_port = struct.unpack_from(">H", raw, 14 + ip_header_len + 2)[0]
        tcp_header_len = ((raw[14 + ip_header_len + 12] >> 4) & 0xF) * 4
        payload_offset = 14 + ip_header_len + tcp_header_len
        proto_name = Protocol.TCP

    elif protocol == IP_PROTO_UDP:
        if len(raw) < 14 + ip_header_len + 8:
            return None
        src_port = struct.unpack_from(">H", raw, 14 + ip_header_len)[0]
        dst_port = struct.unpack_from(">H", raw, 14 + ip_header_len + 2)[0]
        payload_offset = 14 + ip_header_len + 8
        proto_name = Protocol.UDP

    else:
        return None

    payload = raw[payload_offset:]

    return PacketInfo(
        timestamp_ms=timestamp_ms,
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_port=src_port,
        dst_port=dst_port,
        protocol=proto_name,
        payload=payload,
        length=len(raw),
    )
