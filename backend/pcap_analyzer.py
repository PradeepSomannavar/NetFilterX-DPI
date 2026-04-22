"""
PCAP analyzer — thin wrapper around the DPI engine for the FastAPI layer.
Python port of backend/pcapAnalyzer.js.
"""

import sys
import os
from typing import List, Dict, Any

# Allow running from the backend directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.dpi_engine import DPIEngine


def parse_pcap(
    file_path: str,
    blocked_apps: List[str] = None,
    blocked_ips: List[str] = None,
    blocked_domains: List[str] = None,
) -> Dict[str, Any]:
    """
    Run DPI analysis on a PCAP file and return the structured result dict.
    Mirrors the parsePcap() function from pcapAnalyzer.js.
    """
    engine = DPIEngine(
        blocked_apps=blocked_apps or [],
        blocked_ips=blocked_ips or [],
        blocked_domains=blocked_domains or [],
    )
    return engine.analyze(file_path)
