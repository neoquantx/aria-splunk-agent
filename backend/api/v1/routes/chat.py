from fastapi import APIRouter
from pydantic import BaseModel
from demo.demo_data import get_full_demo_report
import httpx
import logging
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
	message: str
	incident_id: str = "current"

async def query_splunk_ai_assistant(natural_language_query: str) -> str:
	"""Use Splunk AI Assistant to convert natural language to SPL."""
	try:
		async with httpx.AsyncClient(timeout=10, verify=False) as client:
			response = await client.post(
				f"https://{settings.SPLUNK_HOST}:{settings.SPLUNK_PORT}/services/saia/v1/generate",
				auth=(settings.SPLUNK_USERNAME, settings.SPLUNK_PASSWORD),
				json={
					"query": natural_language_query,
					"context": "security operations center"
				}
			)
			if response.status_code == 200:
				data = response.json()
				return data.get("spl", "")
	except Exception as e:
		logger.warning(f"AI Assistant not available: {e}")
	return ""

QUICK_ANSWERS = {
	"risk": lambda r: f"Current risk score is {r.get('risk_score', 'N/A')}/100. {r.get('executive_summary', '')}",
	"summary": lambda r: r.get('executive_summary', 'No summary available.'),
	"affected": lambda r: f"Affected systems: {', '.join([t.get('affected_assets', ['unknown'])[0] if isinstance(t.get('affected_assets'), list) else 'unknown' for t in r.get('threats', [])])}",
	"playbook": lambda r: str(r.get('strategy', {}).get('playbook', {}).get('immediate', ['No playbook available.'])),
	"mitre": lambda r: f"MITRE techniques detected: {', '.join([t.get('technique_id','') for t in r.get('correlation', {}).get('mitre_techniques', [])])}",
}

@router.post("/")
async def chat_with_aria(body: ChatMessage):
	"""Ask ARIA a natural language question. Uses Splunk AI Assistant for SPL generation."""
	report = get_full_demo_report()
	msg = body.message.lower()

	generated_spl = await query_splunk_ai_assistant(body.message)
	spl_context = f" (SPL via Splunk AI Assistant: `{generated_spl}`)" if generated_spl else ""

	for keyword, answer_fn in QUICK_ANSWERS.items():
		if keyword in msg:
			return {
				"response": answer_fn(report) + spl_context,
				"agent": "Strategist",
				"confidence": 0.92,
				"splunk_ai_assistant_used": bool(generated_spl),
				"generated_spl": generated_spl
			}

	if "attack" in msg or "stage" in msg:
		return {
			"response": f"Attack stage: {report.get('attack_stage', 'unknown')}. The attack progressed from brute force to lateral movement and data exfiltration.{spl_context}",
			"agent": "Investigator",
			"confidence": 0.88,
			"splunk_ai_assistant_used": bool(generated_spl),
			"generated_spl": generated_spl
		}

	if "recommend" in msg or "do" in msg or "action" in msg:
		actions = report.get('strategy', {}).get('playbook', {}).get('immediate', [])
		return {
			"response": "Immediate actions: " + " | ".join(actions[:3]) + spl_context,
			"agent": "Strategist",
			"confidence": 0.95,
			"splunk_ai_assistant_used": bool(generated_spl),
			"generated_spl": generated_spl
		}

	threat_names = [t.get('type','').replace('_',' ') for t in report.get('threats', [])]
	stage = report.get('attack_stage', 'unknown')
	risk = report.get('risk_score', 0)
    
	responses = [
		f"Current status: {risk}/100 risk, attack stage is {stage}. The primary threat is {threat_names[0] if threat_names else 'unknown'}.",
		f"ARIA has identified {len(report.get('threats',[]))} active threats. Highest severity: {max([t.get('severity',0) for t in report.get('threats',[])], default=0)}/10. Ask me about the playbook or affected systems.",
		f"Attack is at {stage} stage with risk {risk}/100. {len(report.get('correlation',{}).get('mitre_techniques',[]))} MITRE techniques mapped. Type 'playbook' for immediate actions.",
		f"I detected threats from {report.get('threats',[{}])[0].get('src_ip','unknown IP') if report.get('threats') else 'unknown'}. The attack progressed to {stage}. Ask me: risk score, affected systems, remediation, or MITRE techniques.",
	]
    
	import hashlib
	idx = int(hashlib.md5(body.message.encode()).hexdigest(), 16) % len(responses)
    
	return {
		"response": responses[idx],
		"agent": "Orchestrator",
		"confidence": 0.85,
		"splunk_ai_assistant_used": bool(generated_spl),
		"generated_spl": generated_spl
	}
