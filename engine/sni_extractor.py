"""
TLS SNI extractor and HTTP Host header parser.
Python port of sni_extractor.cpp / sni_extractor.h.
"""

import struct
from typing import Optional


def extract_tls_sni(payload: bytes) -> Optional[str]:
    """
    Parse a TLS ClientHello record and return the SNI hostname if present.
    Scans the payload for the handshake signature to be more robust.
    """
    try:
        if len(payload) < 43:
            return None
            
        # Scan for Handshake (0x16) followed by ClientHello (0x01)
        # Usually starts at index 0, but we'll check a few bytes
        start_idx = -1
        for i in range(min(5, len(payload) - 10)):
            if payload[i] == 0x16 and payload[i+5] == 0x01:
                start_idx = i
                break
        
        if start_idx == -1:
            return None

        # Adjust offset relative to start_idx
        # Record Header (5) + Handshake Header (4) + Version (2) + Random (32) = 43
        offset = start_idx + 43

        if offset >= len(payload):
            return None

        # Session ID
        session_len = payload[offset]
        offset += 1 + session_len

        if offset + 2 > len(payload):
            return None

        # Cipher suites
        cipher_len = struct.unpack_from(">H", payload, offset)[0]
        offset += 2 + cipher_len

        if offset >= len(payload):
            return None

        # Compression methods
        comp_len = payload[offset]
        offset += 1 + comp_len

        if offset + 2 > len(payload):
            return None

        # Extensions
        ext_total_len = struct.unpack_from(">H", payload, offset)[0]
        offset += 2
        ext_end = offset + ext_total_len

        while offset + 4 <= ext_end and offset + 4 <= len(payload):
            ext_type = struct.unpack_from(">H", payload, offset)[0]
            ext_len = struct.unpack_from(">H", payload, offset + 2)[0]
            offset += 4

            if ext_type == 0x0000:  # SNI extension
                if offset + ext_len > len(payload):
                    return None
                # SNI list length (2 bytes) + type (1 byte) + name length (2 bytes)
                sni_name_len = struct.unpack_from(">H", payload, offset + 3)[0]
                sni_start = offset + 5
                if sni_start + sni_name_len <= len(payload):
                    return payload[sni_start:sni_start + sni_name_len].decode("utf-8", errors="ignore")

            offset += ext_len

    except Exception:
        pass

    return None


def extract_http_host(payload: bytes) -> Optional[str]:
    """
    Extract the Host header value from an HTTP request payload.
    Returns None if not found.
    """
    try:
        text = payload.decode("utf-8", errors="ignore")
        for line in text.splitlines():
            if line.lower().startswith("host:"):
                return line[5:].strip()
    except Exception:
        pass
    return None
