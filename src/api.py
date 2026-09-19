"""
FastAPI web interface for smart-log-analyzer.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.ingest import ingest_logs
from src.db import query_top_ips, query_hourly_volume, query_error_rate, create_table

app = FastAPI(
    title="Smart Log Analyzer API",
    description="API for ingesting and analyzing log files",
    version="1.0.0"
)


@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    create_table()
    print("✅ Database ready")


class IngestRequest(BaseModel):
    filepath: str


class IngestResponse(BaseModel):
    status: str
    logs_parsed: int
    logs_inserted: int
    total_logs: int


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Smart Log Analyzer API",
        "endpoints": {
            "/": "This help message",
            "/ingest": "POST - Ingest a log file",
            "/top-ips": "GET - Show top IPs",
            "/hourly-volume": "GET - Show hourly volume",
            "/error-rates": "GET - Show error rates"
        }
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    if not os.path.exists(request.filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {request.filepath}")

    logs = list(ingest_logs(request.filepath, verbose=False))

    from src.db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]
    conn.close()

    return IngestResponse(
        status="success",
        logs_parsed=len(logs),
        logs_inserted=len(logs),
        total_logs=total
    )


@app.get("/top-ips")
async def top_ips(limit: int = 5):
    results = query_top_ips(limit)
    return {"results": results}


@app.get("/hourly-volume")
async def hourly_volume():
    results = query_hourly_volume()
    return {"results": results}


@app.get("/error-rates")
async def error_rates():
    results = query_error_rate()
    return {"results": results}