"""
PDF report generator using ReportLab.
Python port of backend/pdfGenerator.js.
"""

from datetime import datetime
from io import BytesIO
from typing import Any, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def _format_bytes(n: int) -> str:
    """Human-readable byte size string."""
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    if n < 1024 ** 3:
        return f"{n / 1024 ** 2:.1f} MB"
    return f"{n / 1024 ** 3:.2f} GB"


def generate_pdf_report(data: Dict[str, Any]) -> bytes:
    """
    Generate a PDF analysis report from DPI engine output.
    Returns raw PDF bytes.
    Mirrors generatePDFReport() from pdfGenerator.js.
    """
    stats = data.get("stats", {})
    app_breakdown = data.get("appBreakdown", [])
    protocol_breakdown = data.get("protocolBreakdown", [])

    buf = BytesIO()
    page_w, page_h = A4
    c = canvas.Canvas(buf, pagesize=A4)

    y = page_h - 40 * mm

    def draw_text(text: str, x_mm: float, bold: bool = False, size: int = 12,
                  color: tuple = (0, 0, 0)):
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.setFillColorRGB(*color)
        c.drawString(x_mm * mm, y, text)

    def kv(label: str, value: str):
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(18 * mm, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(70 * mm, y, str(value))
        y -= 7 * mm

    def section(title: str):
        nonlocal y
        y -= 4 * mm
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0, 0.4, 0.7)
        c.drawString(18 * mm, y, title)
        y -= 7 * mm
        c.setFillColorRGB(0, 0, 0)

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0, 0.4, 0.75)
    c.drawString(18 * mm, y, "DPI ENGINE — ANALYSIS REPORT")
    y -= 8 * mm

    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(18 * mm, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 10 * mm

    # Overview
    section("OVERVIEW")
    kv("Total Packets", f"{stats.get('totalPackets', 0):,}")
    kv("Total Bytes", _format_bytes(stats.get("totalBytes", 0)))
    kv("Forwarded Packets", f"{stats.get('forwarded', 0):,}")
    kv("Dropped Packets", f"{stats.get('dropped', 0):,}")
    kv("Active Flows", f"{stats.get('activeFlows', 0):,}")

    # Protocol
    section("PROTOCOL DISTRIBUTION")
    for p in protocol_breakdown:
        kv(p["name"], f"{p['value']:,} packets")

    # Application breakdown with bar
    section("APPLICATION BREAKDOWN")
    total_pkts = stats.get("totalPackets", 1) or 1

    for app in app_breakdown:
        if y < 30 * mm:
            c.showPage()
            y = page_h - 20 * mm

        pct = (app["packets"] / total_pkts) * 100
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(18 * mm, y, app["name"])

        c.setFont("Helvetica", 11)
        c.drawString(60 * mm, y, f"{app['packets']:,} pkts  ({pct:.1f}%)")

        # Draw bar
        bar_max = 60 * mm
        bar_w = bar_max * (app["packets"] / total_pkts)
        c.setFillColorRGB(0.2, 0.55, 0.9)
        c.rect(120 * mm, y - 1 * mm, bar_w, 4 * mm, fill=1, stroke=0)

        y -= 7 * mm

    c.save()
    return buf.getvalue()
