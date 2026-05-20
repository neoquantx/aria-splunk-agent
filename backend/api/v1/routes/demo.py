from fastapi import APIRouter
from demo.demo_data import get_full_demo_report, get_demo_threats, get_demo_investigation, get_demo_correlation, get_demo_strategy

router = APIRouter()

@router.get("/run-scenario")
async def run_demo_scenario():
	"""Run a complete demo attack scenario — no Splunk required. Returns a full incident report."""
	return get_full_demo_report()

@router.get("/threats")
async def get_demo_threats_only():
	"""Get only the demo threat detections."""
	return {"threats": get_demo_threats()}

@router.get("/investigation")
async def get_demo_investigation_only():
	"""Get only the demo attack timeline."""
	return {"timeline": get_demo_investigation()}

@router.get("/correlation")
async def get_demo_correlation_only():
	"""Get only the demo MITRE ATT&CK correlation."""
	return get_demo_correlation()

@router.get("/strategy")
async def get_demo_strategy_only():
	"""Get only the demo remediation playbook."""
	return get_demo_strategy()
