from fastapi import APIRouter
from agents.orchestrator import ARIAOrchestrator
from core.splunk_client import default_splunk_client
import asyncio

router = APIRouter()

@router.get("/")
async def list_incidents():
	"""List recent incidents — returns demo data if Splunk unavailable."""
	from demo.demo_data import get_demo_threats
	return {"incidents": get_demo_threats(), "source": "demo"}

@router.post("/investigate")
async def investigate_incident(body: dict = None):
	"""Run full ARIA investigation pipeline."""
	try:
		orchestrator = ARIAOrchestrator(default_splunk_client)
		report = await orchestrator.run_full_investigation()
		return report
	except Exception as e:
		from demo.demo_data import get_full_demo_report
		return get_full_demo_report()
