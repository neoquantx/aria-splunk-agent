import dataclasses
import logging
import uuid
from datetime import datetime

from agents.correlator import Correlator
from agents.investigator import Investigator
from agents.strategist import Strategist
from agents.threat_scout import ThreatScout


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class IncidentReport:
	id: str
	timestamp: str
	threats: list[dict]
	investigation: dict
	correlation: dict
	strategy: dict
	risk_score: int
	executive_summary: str
	attack_stage: str
	status: str


class ARIAOrchestrator:
	def __init__(self, splunk_client):
		self.splunk_client = splunk_client
		self.threat_scout = ThreatScout(self.splunk_client)
		self.investigator = Investigator(self.splunk_client)
		self.correlator = Correlator(self.splunk_client)
		self.strategist = Strategist(self.splunk_client)
		self.current_report = None
		self.status = "idle"
		self.progress_log = []

	async def run_full_investigation(self, progress_callback=None) -> IncidentReport:
		try:
			self.status = "scanning"
			self._report_progress(progress_callback, "ThreatScout running...")
			threat_result = await self.threat_scout.run({})

			self.status = "investigating"
			self._report_progress(progress_callback, "Investigator running...")
			top_threat_context = threat_result.findings[0] if threat_result.findings else {}
			investigation_result = await self.investigator.run(top_threat_context)

			self.status = "correlating"
			self._report_progress(progress_callback, "Correlator mapping MITRE ATT&CK...")
			correlation_result = await self.correlator.run(
				{
					"threats": threat_result.findings,
					"investigation": investigation_result.findings,
				}
			)

			self.status = "strategizing"
			self._report_progress(progress_callback, "Strategist generating playbook...")
			attack_stage = (
				investigation_result.raw_spl_results[0].get("attack_stage", "reconnaissance")
				if investigation_result.raw_spl_results
				else "reconnaissance"
			)
			if attack_stage == "reconnaissance" and investigation_result.findings:
				attack_stage = investigation_result.findings[0].get("attack_stage", attack_stage)

			strategy_result = await self.strategist.run(
				{
					"threats": threat_result.findings,
					"attack_stage": attack_stage,
					"mitre_techniques": correlation_result.findings,
					"is_coordinated_attack": correlation_result.confidence > 0.6,
				}
			)

			risk = strategy_result.findings[0].get("risk_score", 50) if strategy_result.findings else 50
			summary = (
				strategy_result.findings[0].get("executive_summary", "Investigation complete.")
				if strategy_result.findings
				else "Investigation complete."
			)

			report = IncidentReport(
				id=str(uuid.uuid4()),
				timestamp=datetime.now().isoformat(),
				threats=threat_result.findings,
				investigation={"timeline": investigation_result.findings, "logs": investigation_result.raw_spl_results},
				correlation={
					"mitre_techniques": correlation_result.findings,
					"is_coordinated": correlation_result.confidence > 0.6,
				},
				strategy={"playbook": strategy_result.findings, "recommendations": strategy_result.recommendations},
				risk_score=risk,
				executive_summary=summary,
				attack_stage=attack_stage,
				status="complete",
			)

			self.current_report = report
			self.status = "complete"
			self._report_progress(progress_callback, "Investigation complete.")
			return report

		except Exception as exc:
			self.status = "error"
			logger.exception("ARIA full investigation failed: %s", exc)
			error_report = IncidentReport(
				id=str(uuid.uuid4()),
				timestamp=datetime.now().isoformat(),
				threats=[],
				investigation={},
				correlation={},
				strategy={},
				risk_score=0,
				executive_summary="",
				attack_stage="",
				status="error",
			)
			self.current_report = error_report
			return error_report

	def _report_progress(self, progress_callback, message: str) -> None:
		entry = {"time": datetime.now().isoformat(), "message": message, "status": self.status}
		self.progress_log.append(entry)
		if progress_callback is None:
			return
		try:
			progress_callback(message)
		except Exception:
			logger.exception("Progress callback failed")
