from fastapi import APIRouter
from agents.orchestrator import ARIAOrchestrator
from core.splunk_client import default_splunk_client

router = APIRouter()

_status = {"status": "idle", "progress": []}

@router.post("/run")
async def run_agents():
	"""Trigger all 4 ARIA agents to run a full investigation."""
	try:
		_status["status"] = "running"
		_status["progress"] = []

		def on_progress(msg: str):
			_status["progress"].append(msg)

		orchestrator = ARIAOrchestrator(default_splunk_client)
		report = await orchestrator.run_full_investigation(progress_callback=on_progress)
		_status["status"] = "complete"
		return {"status": "complete", "report": report}
	except Exception as e:
		_status["status"] = "error"
		from demo.demo_data import get_full_demo_report
		return {"status": "demo", "report": get_full_demo_report()}

@router.get("/status")
async def get_agent_status():
	"""Get current agent run status and progress log."""
	return _status
