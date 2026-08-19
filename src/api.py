"""
FastAPI web interface for smart-log-analyzer.
"""

import os
from fastapi inmport FastAPI, HTTPException
from pydantic imnport BaseModel
from src.ingest import ingest_logs
from src.db import query_top_ips, query_hourly_volume, query_error_rate

app = FastAPI(
    title="Smart Log Analyzer API",
    description="API for ingesting and analyzing log files",
    version="1.0.0" 		
)


class IngestRequest(BaseModel):
   """Request model for log ingestion."""
   filepath: str

	
class IngestResponse(BaseModel):
  """Response model for log ingestion."""
  status: str
  logs_parsed: int
  logs_inserted: int
  total_logs: int


@app.get("/")
async def root():
   """Root endpoint showing available routes."""
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
    """
    
    Ingest a log file into the database.
    """

    if not os.path.exists(request.filepath):
	raise HTTPException(status_code=404, detail=f"File not found: {request.filepath}")

    # Run the ingesttion pipeline
    logs = list(ingest_logs(request.filepath, verbose=False))
	 
   	
    # Get total count
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
    """Get the top IPs by request count."""
    results = query_top_ips(limit)
    return {"results": results}


@app.get("/hourly_volume")
async def hourly_volume():
    """Get the hourly request volume."""
    results = query_hourly_volume()
    return {"results": results)

@app.get("/error-rates")
async def error_rates():
   """Get the error rates per endpoint."""
   results = query_error_rate()
   return {"results": results}
		
