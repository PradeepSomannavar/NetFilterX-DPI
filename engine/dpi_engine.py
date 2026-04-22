import os
import json
from typing import List, Optional, Dict
import dpkt

from .packet_parser import parse_packet
from .connection_tracker import ConnectionTracker
from .rule_manager import RuleManager, map_sni_to_app
from .sni_extractor import extract_tls_sni, extract_http_host
from .types import Flow, FlowState, EngineStats, TimelineBucket, Protocol, PacketInfo


class DPIEngine:
    """
    Core Deep Packet Inspection engine.
    Orchestrates packet parsing, flow tracking, classification, and blocking.
    """

    def __init__(
        self,
        blocked_apps: Optional[List[str]] = None,
        blocked_ips: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
    ):
        self.connection_tracker = ConnectionTracker()
        self.rule_manager = RuleManager(
            blocked_apps or [],
            blocked_ips or [],
            blocked_domains or [],
        )
        self.stats = EngineStats()
        self.timeline: List[TimelineBucket] = []

    def process_packet(self, pkt: PacketInfo, raw_len: int):
        """Processes a single packet through the engine logic."""
        self.stats.total_packets += 1
        self.stats.total_bytes += raw_len

        # Protocol counters
        if pkt.protocol == Protocol.TCP:
            self.stats.tcp_packets += 1
        elif pkt.protocol == Protocol.UDP:
            self.stats.udp_packets += 1

        # Flow tracking
        flow = self.connection_tracker.get_or_create(
            pkt.src_ip, pkt.src_port,
            pkt.dst_ip, pkt.dst_port,
            pkt.protocol,
        )
        self.stats.active_flows = self.connection_tracker.flow_count
        flow.packets += 1
        flow.bytes += raw_len

        # Application classification (can upgrade from generic HTTPS/HTTP to specific App)
        if flow.app in ["Unknown", "HTTPS", "HTTP"] and len(pkt.payload) > 0:
            ports = {pkt.src_port, pkt.dst_port}

            # TLS/HTTPS logic
            if pkt.protocol == Protocol.TCP and 443 in ports:
                sni = extract_tls_sni(pkt.payload)
                if sni:
                    flow.sni = sni
                    flow.app = map_sni_to_app(sni)
                    flow.state = FlowState.CLASSIFIED
                else:
                    # Check if it looks like a TLS record but no SNI
                    if len(pkt.payload) > 5 and pkt.payload[0] == 0x16:
                        flow.app = "HTTPS"

            # HTTP logic
            elif pkt.protocol == Protocol.TCP and 80 in ports:
                host = extract_http_host(pkt.payload)
                if host:
                    flow.sni = host
                    flow.app = map_sni_to_app(host)
                    flow.state = FlowState.CLASSIFIED
                else:
                    flow.app = "HTTP"

            # DNS logic
            elif pkt.protocol == Protocol.UDP and 53 in ports:
                flow.app = "DNS"
                flow.state = FlowState.CLASSIFIED

        # Blocking rules evaluation
        if not flow.blocked:
            flow.blocked = self.rule_manager.is_blocked(flow)

        # Update engine stats
        if flow.blocked:
            self.stats.dropped += 1
        else:
            self.stats.forwarded += 1

    def analyze(self, pcap_path: str) -> dict:
        """Analyzes a full PCAP file and returns results for the UI."""
        if not os.path.exists(pcap_path):
            raise FileNotFoundError(f"PCAP file not found: {pcap_path}")

        self.stats = EngineStats()  # reset for new run
        self.connection_tracker = ConnectionTracker()
        self.timeline = []
        
        current_bucket = None
        bucket_size_ms = 1000

        with open(pcap_path, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            for ts, raw in pcap:
                ts_ms = ts * 1000
                
                # Create first bucket if needed
                if current_bucket is None:
                    current_bucket = TimelineBucket(start_time=ts_ms)
                
                # If we've crossed into a new second, push the old bucket
                elif ts_ms >= current_bucket.start_time + bucket_size_ms:
                    self.timeline.append(current_bucket)
                    # Handle potential gaps in traffic by aligning to the nearest second
                    current_bucket = TimelineBucket(start_time=ts_ms)

                pkt = parse_packet(raw, ts_ms)
                if pkt is None:
                    continue

                # Run through modular processor
                self.process_packet(pkt, len(raw))

                # Update bucket stats
                current_bucket.packets += 1
                # We need to know if THIS packet was blocked (the flow might have just become blocked)
                # Re-check flow status from tracker
                flow = self.connection_tracker.get_or_create(
                    pkt.src_ip, pkt.src_port, pkt.dst_ip, pkt.dst_port, pkt.protocol
                )
                if flow.blocked:
                    current_bucket.dropped += 1

        if current_bucket:
            self.timeline.append(current_bucket)

        # Aggregate application breakdown
        from .rule_manager import get_app_color
        
        # Build application breakdown and RE-CALCULATE consistency stats
        app_map = {}
        final_dropped = 0
        final_forwarded = 0
        
        for flow in self.connection_tracker.all_flows():
            app_name = flow.app or "Unknown"
            if app_name not in app_map:
                app_map[app_name] = {
                    "name": app_name,
                    "packets": 0,
                    "bytes": 0,
                    "color": get_app_color(app_name),
                    "isBlocked": False  # Initial state
                }
            
            app_map[app_name]["packets"] += flow.packets
            app_map[app_name]["bytes"] += flow.bytes
            
            # If ANY flow for this app is blocked, the whole app is marked BLOCKED
            if flow.blocked:
                app_map[app_name]["isBlocked"] = True
                final_dropped += flow.packets
            else:
                final_forwarded += flow.packets

        # Update global stats for mathematical consistency in UI
        self.stats.dropped = final_dropped
        self.stats.forwarded = final_forwarded

        app_breakdown = sorted(app_map.values(), key=lambda x: x["packets"], reverse=True)
        
        # Build protocol breakdown (derived from flows for consistency)
        proto_map = {"TCP": 0, "UDP": 0, "UNKNOWN": 0}
        for flow in self.connection_tracker.all_flows():
            proto_map[flow.protocol] = proto_map.get(flow.protocol, 0) + flow.packets
        
        protocol_breakdown = [
            {"name": k, "value": v} for k, v in proto_map.items() if v > 0
        ]

        start_ts = self.timeline[0].start_time if self.timeline else 0
        timeline_data = [
            {
                "t": f"{int((b.start_time - start_ts)/1000)}s", 
                "packets": b.packets, 
                "dropped": b.dropped
            }
            for b in self.timeline
        ]

        return {
            "stats": self.stats.to_dict(),
            "flows": [f.to_dict() for f in self.connection_tracker.all_flows()],
            "appBreakdown": app_breakdown,
            "protocolBreakdown": protocol_breakdown,
            "timelineData": timeline_data
        }
