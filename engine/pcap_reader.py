"""
PCAP file reader using dpkt.
Python port of pcap_reader.cpp / pcap_reader.h.
Falls back to a manual struct-based reader if dpkt is unavailable.
"""

import struct
from typing import Generator, Tuple


# PCAP global header constants
PCAP_MAGIC_LE = 0xA1B2C3D4
PCAP_MAGIC_BE = 0xD4C3B2A1
PCAP_MAGIC_NS_LE = 0xA1B23C4D
PCAP_GLOBAL_HEADER_SIZE = 24
PCAP_PACKET_HEADER_SIZE = 16


def read_pcap(filepath: str) -> Generator[Tuple[float, bytes], None, None]:
    """
    Yield (timestamp_ms, raw_bytes) for every packet in a PCAP file.
    Supports both little-endian and big-endian PCAP files.
    """
    try:
        import dpkt
        with open(filepath, "rb") as f:
            capture = dpkt.pcap.Reader(f)
            for ts, buf in capture:
                yield ts * 1000.0, buf
        return
    except ImportError:
        pass

    # Manual PCAP parser fallback
    with open(filepath, "rb") as f:
        header = f.read(PCAP_GLOBAL_HEADER_SIZE)
        if len(header) < PCAP_GLOBAL_HEADER_SIZE:
            return

        magic = struct.unpack_from("<I", header, 0)[0]
        if magic == PCAP_MAGIC_LE or magic == PCAP_MAGIC_NS_LE:
            endian = "<"
            nano = (magic == PCAP_MAGIC_NS_LE)
        elif magic == PCAP_MAGIC_BE:
            endian = ">"
            nano = False
        else:
            raise ValueError(f"Unrecognized PCAP magic: {magic:#010x}")

        while True:
            pkt_hdr = f.read(PCAP_PACKET_HEADER_SIZE)
            if len(pkt_hdr) < PCAP_PACKET_HEADER_SIZE:
                break

            ts_sec, ts_frac, incl_len, orig_len = struct.unpack_from(
                f"{endian}IIII", pkt_hdr
            )

            raw = f.read(incl_len)
            if len(raw) < incl_len:
                break

            if nano:
                ts_ms = ts_sec * 1000.0 + ts_frac / 1_000_000.0
            else:
                ts_ms = ts_sec * 1000.0 + ts_frac / 1000.0

            yield ts_ms, raw
