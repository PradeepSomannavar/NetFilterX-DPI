"""
FastAPI backend server for DPI Engine.
Python port of backend/index.js (Express).

Endpoints:
    POST /api/analyze      — Upload PCAP + rules, returns analysis JSON
    POST /api/report/pdf   — Accepts analysis JSON, returns PDF bytes
"""

import os
import sys
import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

# Allow imports from parent directory (engine package) and this directory (pcap_analyzer, pdf_generator)
_here = Path(__file__).parent          # backend/
_root = _here.parent                   # Packet_analyzer/
for _p in (_root, _here):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from pcap_analyzer import parse_pcap
from pdf_generator import generate_pdf_report

app = FastAPI(title="DPI Engine API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/api/analyze")
async def analyze(
    pcap: UploadFile = File(...),
    blockedApps: str = Form(default="[]"),
    blockedIPs: str = Form(default="[]"),
    blockedDomains: str = Form(default="[]"),
):
    """
    Accept a PCAP file and blocking-rule lists.
    Returns full DPI analysis as JSON.
    """
    if not pcap.filename:
        raise HTTPException(status_code=400, detail="No PCAP file uploaded")

    tmp_path = None
    try:
        # Save upload to a temp file
        suffix = Path(pcap.filename).suffix or ".pcap"
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, dir=UPLOAD_DIR
        ) as tmp:
            tmp.write(await pcap.read())
            tmp_path = tmp.name

        blocked_apps = json.loads(blockedApps)
        blocked_ips = json.loads(blockedIPs)
        blocked_domains = json.loads(blockedDomains)

        result = parse_pcap(
            tmp_path,
            blocked_apps=blocked_apps,
            blocked_ips=blocked_ips,
            blocked_domains=blocked_domains,
        )
        return JSONResponse(content=result)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze PCAP file: {exc}",
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/report/pdf")
async def report_pdf(request: Request):
    """
    Accept analysis JSON and return a generated PDF report.
    """
    try:
        data = await request.json()
        if not data or "stats" not in data:
            raise HTTPException(status_code=400, detail="Invalid analysis data")

        pdf_bytes = generate_pdf_report(data)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=DPI_Engine_Report.pdf"
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF report: {exc}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)
