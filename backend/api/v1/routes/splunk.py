from fastapi import APIRouter
from core.splunk_client import default_splunk_client
from pydantic import BaseModel
import asyncio

router = APIRouter()

class SPLQuery(BaseModel):
	query: str
	earliest: str = "-1h"
	latest: str = "now"

@router.post("/query")
async def run_spl_query(body: SPLQuery):
	"""Run a raw SPL query against Splunk."""
	results = await asyncio.to_thread(
		default_splunk_client.run_spl_search,
		body.query, body.earliest, body.latest
	)
	return {"results": results, "count": len(results)}

@router.get("/status")
async def splunk_status():
	"""Check if Splunk connection is active."""
	connected = await asyncio.to_thread(default_splunk_client.test_connection)
	return {"connected": connected, "host": "localhost", "port": 8089}

@router.get("/events")
async def get_recent_events():
	"""Get recent events from Splunk for the dashboard."""
	results = await asyncio.to_thread(
		default_splunk_client.run_spl_search,
		"search index=* | head 20 | fields _time, sourcetype, _raw",
		"-1h", "now"
	)
	return {"events": results, "count": len(results)}
