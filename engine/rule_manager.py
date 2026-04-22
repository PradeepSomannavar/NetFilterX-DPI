"""
Blocking rule manager — evaluates IP, application, and domain rules.
Python port of rule_manager.cpp / rule_manager.h.
"""

from typing import List
from .types import Flow


# Maps SNI substrings to application names (mirrors mapSniToApp in JS and C++)
SNI_APP_MAP = [
    ("youtube", "YouTube"),
    ("facebook", "Facebook"),
    ("fbcdn", "Facebook"),
    ("google", "Google"),
    ("netflix", "Netflix"),
    ("instagram", "Instagram"),
    ("twitter", "Twitter"),
    ("twimg", "Twitter"),
    ("tiktok", "TikTok"),
    ("byte", "TikTok"),
    ("discord", "Discord"),
    ("zoom.us", "Zoom"),
    ("whatsapp", "WhatsApp"),
    ("telegram", "Telegram"),
    ("spotify", "Spotify"),
    ("github", "GitHub"),
    ("amazon", "Amazon"),
    ("aws", "Amazon"),
    ("microsoft", "Microsoft"),
    ("windows", "Microsoft"),
    ("cloudflare", "Cloudflare"),
]

# Predefined color palette for the UI
APP_COLORS = {
    # Streaming
    "YouTube": "#ef4444",    # Red
    "Netflix": "#e50914",    # Netflix Red
    "Twitch": "#9146ff",     # Purple
    "Spotify": "#1db954",    # Spotify Green
    
    # Social Media
    "Facebook": "#1877f2",   # Blue
    "Instagram": "#e4405f",  # Pink/Red
    "Twitter": "#1da1f2",    # Sky Blue
    "TikTok": "#00f2ea",     # Cyan
    "Discord": "#5865f2",    # Blurple
    "WhatsApp": "#25d366",   # Green
    
    # Infrastructure/Web
    "Google": "#4285f4",     # Google Blue
    "Cloudflare": "#f48120", # Orange
    "Microsoft": "#00a4ef",  # Azure Blue
    "Amazon": "#ff9900",     # Amazon Orange
    
    # Protocols
    "HTTPS": "#10b981",      # Emerald Green
    "HTTP": "#94a3b8",       # Slate
    "DNS": "#8b5cf6",        # Violet
    "TCP": "#0ea5e9",        # Light Blue
    "UDP": "#f59e0b",        # Amber
    "Unknown": "#475569",    # Dark Grey
}


def map_sni_to_app(sni: str) -> str:
    """Return application name for a given SNI hostname."""
    s = sni.lower()
    for keyword, app in SNI_APP_MAP:
        if keyword in s:
            return app
    return "Unknown"


def get_app_color(app: str) -> str:
    """Return hex color for a given application name."""
    return APP_COLORS.get(app, "#475569")


class RuleManager:
    """Evaluates blocking rules against a flow."""

    def __init__(
        self,
        blocked_apps: List[str],
        blocked_ips: List[str],
        blocked_domains: List[str],
    ):
        self.blocked_apps = set(blocked_apps)
        self.blocked_ips = set(blocked_ips)
        self.blocked_domains = list(blocked_domains)

    def is_blocked(self, flow: Flow) -> bool:
        """Return True if the flow should be dropped."""
        if flow.src_ip in self.blocked_ips:
            return True
        if flow.app in self.blocked_apps:
            return True
        if flow.sni:
            for domain in self.blocked_domains:
                if domain in flow.sni:
                    return True
        return False
