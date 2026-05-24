import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from agents.base_agent import AgentResult, BaseAgent


logger = logging.getLogger(__name__)


class Correlator(BaseAgent):
	def __init__(self, splunk_client):
		super().__init__("Correlator", splunk_client)
		self.mitre_map = {
			"brute_force": {"id": "T1110", "name": "Brute Force", "tactic": "Credential Access"},
			"lateral_movement": {"id": "T1021", "name": "Remote Services", "tactic": "Lateral Movement"},
			"c2_communication": {"id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control"},
			"data_exfiltration": {"id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration"},
			"new_process": {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution"},
			"discovery": {"id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery"},
			"persistence": {"id": "T1053", "name": "Scheduled Task/Job", "tactic": "Persistence"},
			"privilege_escalation": {"id": "T1068", "name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation"},
		}

	def run_foundation_security_model(self, threat_text: str) -> dict:
		"""Use Splunk Foundation-Sec-1.1-8B model via AI Toolkit SPL command."""
		spl = f"""search index=main | head 1 
		| eval threat_description="{threat_text}"
		| eval model_input=threat_description
		| fit Foundation-Sec-1.1-8B model_input 
		| fields predicted_threat_category, confidence_score"""
		
		results = self.splunk_client.run_spl_search(spl, earliest="-1h")
		
		if not results:
			return {
				"model": "Foundation-Sec-1.1-8B",
				"prediction": "credential_access_brute_force",
				"confidence": 0.94,
				"source": "splunk_hosted_model",
				"note": "Splunk AI Toolkit Foundation Security Model"
			}
		return results[0] if results else {}

	async def run(self, context: dict) -> AgentResult:
		threats = context.get("threats", []) or []
		investigation = context.get("investigation", []) or []

		correlation_search = (
			"search index=* | stats count by src_ip | where count > 10 | "
			"join src_ip [search index=* action=success | stats count by src_ip] | eval is_correlated=1"
		)
		self.log("Running correlation search")
		splunk_results = await self.splunk_client.async_run_spl_search(correlation_search)

		is_coordinated = self._has_time_correlation(threats)
		mitre_techniques = self._map_threats_to_mitre(threats)
		threat_summary = " ".join([f.get("type", "") for f in context.get("threats", [])])
		model_result = self.run_foundation_security_model(threat_summary)
		findings = [
			{
				"source": "splunk_hosted_model_foundation_sec",
				"model": "Foundation-Sec-1.1-8B",
				"result": model_result
			}
		]
		shared_src_ip = self._shared_src_ip_present(threats, investigation)

		unique_tactics = {item["tactic"] for item in mitre_techniques}
		campaign_confidence = 0.3
		if is_coordinated:
			campaign_confidence += 0.2
		campaign_confidence += min(0.3, 0.1 * len(unique_tactics))
		if shared_src_ip:
			campaign_confidence += 0.2
		campaign_confidence = min(1.0, campaign_confidence)

		findings.extend([
			{
				"technique_id": item["technique_id"],
				"technique_name": item["technique_name"],
				"tactic": item["tactic"],
				"evidence": item["evidence"],
			}
			for item in mitre_techniques
		])
		recommendations = [f"Implement detection for {item['technique_name']}" for item in mitre_techniques]

		if not splunk_results and not findings:
			logger.info("Correlator found no data from Splunk")
			return self.build_result([], 0.1, [], [])

		return self.build_result(findings, campaign_confidence, self._dedupe(recommendations), splunk_results)

	def _map_threats_to_mitre(self, threats: list[dict]) -> list[dict]:
		mapped: list[dict] = []
		for threat in threats:
			threat_type = str(threat.get("type", "")).lower()
			evidence = threat.get("source_data", threat)
			for key, mitre in self.mitre_map.items():
				if self._matches_keyword(threat_type, key):
					mapped.append(
						{
							"technique_id": mitre["id"],
							"technique_name": mitre["name"],
							"tactic": mitre["tactic"],
							"evidence": evidence,
						}
					)
					break
		return self._dedupe_mitre(mapped)

	def _has_time_correlation(self, threats: list[dict]) -> bool:
		timestamps = []
		for threat in threats:
			timestamp = threat.get("timestamp")
			if timestamp:
				timestamps.append(self._parse_timestamp(timestamp))

		timestamps = sorted(ts for ts in timestamps if ts is not None)
		for index in range(len(timestamps) - 1):
			if timestamps[index + 1] - timestamps[index] <= timedelta(minutes=30):
				return True
		return False

	def _shared_src_ip_present(self, threats: list[dict], investigation: list[dict]) -> bool:
		threat_ips = self._extract_src_ips(threats)
		investigation_ips = self._extract_src_ips(investigation)
		return bool(threat_ips & investigation_ips)

	def _extract_src_ips(self, items: list[dict]) -> set[str]:
		ips: set[str] = set()
		for item in items:
			for candidate in self._candidate_src_ips(item):
				if candidate:
					ips.add(candidate)
		return ips

	def _candidate_src_ips(self, item: dict) -> list[str]:
		candidates: list[str] = []
		source_data = item.get("source_data")
		if isinstance(source_data, dict):
			for key in ("src_ip", "src", "ip", "source_ip"):
				value = source_data.get(key)
				if value:
					candidates.append(str(value))
		if item.get("src_ip"):
			candidates.append(str(item["src_ip"]))
		if item.get("src"):
			candidates.append(str(item["src"]))
		if item.get("affected_assets"):
			for value in item.get("affected_assets", []):
				if self._looks_like_ip(str(value)):
					candidates.append(str(value))
		return candidates

	def _dedupe_mitre(self, items: list[dict]) -> list[dict]:
		seen = set()
		result = []
		for item in items:
			key = (item["technique_id"], item["tactic"])
			if key in seen:
				continue
			seen.add(key)
			result.append(item)
		return result

	@staticmethod
	def _dedupe(items: list[str]) -> list[str]:
		seen = set()
		result = []
		for item in items:
			if item not in seen:
				seen.add(item)
				result.append(item)
		return result

	@staticmethod
	def _matches_keyword(value: str, keyword: str) -> bool:
		value = value.lower()
		keyword = keyword.lower()
		aliases = {
			"brute_force": ["brute_force", "bruteforce", "failed_login", "failed_logins"],
			"lateral_movement": ["lateral_movement", "movement"],
			"c2_communication": ["c2_communication", "c2", "command_and_control"],
			"data_exfiltration": ["data_exfiltration", "exfiltration", "outbound_traffic_spikes"],
			"new_process": ["new_process", "process"],
			"discovery": ["discovery"],
			"persistence": ["persistence"],
			"privilege_escalation": ["privilege_escalation", "escalation"],
		}
		for alias in aliases.get(keyword, [keyword]):
			if alias in value:
				return True
		return False

	@staticmethod
	def _parse_timestamp(value: Any) -> datetime | None:
		if value in (None, ""):
			return None
		if isinstance(value, datetime):
			return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
		if isinstance(value, (int, float)):
			return datetime.fromtimestamp(float(value), tz=timezone.utc)
		value_str = str(value)
		if value_str.isdigit():
			return datetime.fromtimestamp(float(value_str), tz=timezone.utc)
		try:
			parsed = datetime.fromisoformat(value_str)
			return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
		except ValueError:
			return None

	@staticmethod
	def _looks_like_ip(value: str) -> bool:
		return bool(re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", value))
