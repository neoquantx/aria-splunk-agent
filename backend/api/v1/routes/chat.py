from fastapi import APIRouter
from pydantic import BaseModel
from demo.demo_data import get_full_demo_report

router = APIRouter()

class ChatMessage(BaseModel):
	message: str
	incident_id: str = "current"

QUICK_ANSWERS = {
	"risk": lambda r: f"Current risk score is {r.get('risk_score', 'N/A')}/100. {r.get('executive_summary', '')}",
	"summary": lambda r: r.get('executive_summary', 'No summary available.'),
	"affected": lambda r: f"Affected systems: {', '.join([t.get('affected_assets', ['unknown'])[0] if isinstance(t.get('affected_assets'), list) else 'unknown' for t in r.get('threats', [])])}",
	"playbook": lambda r: str(r.get('strategy', {}).get('playbook', {}).get('immediate', ['No playbook available.'])),
	"mitre": lambda r: f"MITRE techniques detected: {', '.join([t.get('technique_id','') for t in r.get('correlation', {}).get('mitre_techniques', [])])}",
}

@router.post("/")
async def chat_with_aria(body: ChatMessage):
	"""Ask ARIA a natural language question about the current incident."""
	report = get_full_demo_report()
	msg = body.message.lower()

	for keyword, answer_fn in QUICK_ANSWERS.items():
		if keyword in msg:
			return {
				"response": answer_fn(report),
				"agent": "Strategist",
				"confidence": 0.92
			}

	if "attack" in msg or "stage" in msg:
		return {"response": f"Attack stage: {report.get('attack_stage', 'unknown')}. The attack progressed from brute force to lateral movement and data exfiltration.", "agent": "Investigator", "confidence": 0.88}

	if "recommend" in msg or "do" in msg or "action" in msg:
		actions = report.get('strategy', {}).get('playbook', {}).get('immediate', [])
		return {"response": "Immediate actions: " + " | ".join(actions[:3]), "agent": "Strategist", "confidence": 0.95}

	return {
		"response": f"ARIA has detected {len(report.get('threats', []))} threats with a risk score of {report.get('risk_score', 0)}/100. Ask me about: risk score, affected systems, playbook, MITRE techniques, or attack stage.",
		"agent": "Orchestrator",
		"confidence": 0.85
	}
