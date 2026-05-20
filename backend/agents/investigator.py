import logging
from datetime import datetime, timezone
from typing import Any

from agents.base_agent import AgentResult, BaseAgent


logger = logging.getLogger(__name__)


class Investigator(BaseAgent):
	def __init__(self, splunk_client):
		super().__init__("Investigator", splunk_client)

	async def run(self, context: dict) -> AgentResult:
		threat_ip = context.get("src_ip", "*")
		threat_user = context.get("user", "*")

		searches = [
			(
				"timeline",
				f"search index=* (src_ip={threat_ip} OR user={threat_user}) | sort _time | head 50 | fields _time, sourcetype, action, src_ip, dest_ip, user, _raw",
			),
			(
				"activity_pattern",
				f"search index=* src_ip={threat_ip} | timechart span=5m count by action",
			),
			(
				"lateral_movement",
				f"search index=* src_ip={threat_ip} | stats values(dest_ip) as destinations, values(dest_port) as ports, dc(dest_ip) as unique_targets by src_ip",
			),
			(
				"auth_chain",
				f"search index=* user={threat_user} | transaction maxspan=1h | table _time, duration, eventcount, src_ip, action",
			),
		]

		raw_data: list[dict] = []
		timeline: list[dict] = []
		failed_login_seen = False
		successful_login_seen = False
		destination_ips: set[str] = set()
		exfiltration_seen = False

		for search_name, spl in searches:
			self.log(f"Running {search_name} search")
			results = await self.splunk_client.async_run_spl_search(spl)
			if not results:
				continue

			raw_data.extend(results)
			self._inspect_results_for_stage_flags(results, destination_ips)

			if search_name == "timeline":
				for row in results:
					entry = self._timeline_entry(
						row.get("_time"),
						row.get("sourcetype") or "event",
						row.get("src_ip") or threat_ip,
						row.get("dest_ip") or "",
						row.get("action") or "",
					)
					timeline.append(entry)
					if self._is_failed_action(row):
						failed_login_seen = True
					if self._is_success_action(row):
						successful_login_seen = True
					if self._has_exfiltration_bytes(row):
						exfiltration_seen = True

			elif search_name == "activity_pattern":
				for row in results:
					time_value = row.get("_time")
					for field_name, field_value in row.items():
						if field_name == "_time" or field_value in (None, ""):
							continue
						count_value = self._as_int(field_value, default=0)
						if count_value <= 0:
							continue
						timeline.append(
							self._timeline_entry(
								time_value,
								"activity_pattern",
								threat_ip,
								"",
								field_name,
							)
						)
						if field_name.lower() in {"success", "login_success", "authenticated"}:
							successful_login_seen = True
						if field_name.lower() in {"failure", "failed", "bad_password"}:
							failed_login_seen = True
						if field_name.lower().startswith("byte") or "bytes" in field_name.lower():
							if count_value > 50_000_000:
								exfiltration_seen = True

			elif search_name == "lateral_movement":
				for row in results:
					if self._as_int(row.get("unique_targets"), default=0) > 1:
						destination_ips.update(self._normalize_destinations(row.get("destinations")))
					if self._has_exfiltration_bytes(row):
						exfiltration_seen = True

			elif search_name == "auth_chain":
				for row in results:
					timeline.append(
						self._timeline_entry(
							row.get("_time"),
							"auth_chain",
							row.get("src_ip") or threat_ip,
							"",
							row.get("action") or "",
						)
					)
					if self._is_failed_action(row):
						failed_login_seen = True
					if self._is_success_action(row):
						successful_login_seen = True
					if self._has_exfiltration_bytes(row):
						exfiltration_seen = True

		timeline.sort(key=lambda item: item["timestamp"])
		attack_stage = self._determine_attack_stage(
			failed_login_seen=failed_login_seen,
			successful_login_seen=successful_login_seen,
			destination_ips=destination_ips,
			exfiltration_seen=exfiltration_seen,
		)
		recommendations = self._recommendations_for_stage(attack_stage, threat_ip, threat_user)

		if not raw_data:
			logger.info("Investigator found no data from Splunk")
			return self.build_result([], 0.1, [], [])

		for row in timeline:
			row["attack_stage"] = attack_stage

		return self.build_result(
			findings=timeline,
			confidence=0.8,
			recommendations=recommendations,
			raw_data=raw_data,
		)

	def _determine_attack_stage(
		self,
		failed_login_seen: bool,
		successful_login_seen: bool,
		destination_ips: set[str],
		exfiltration_seen: bool,
	) -> str:
		if exfiltration_seen:
			return "exfiltration"
		if len(destination_ips) > 1:
			return "lateral_movement"
		if successful_login_seen:
			return "initial_access"
		if failed_login_seen:
			return "reconnaissance"
		return "reconnaissance"

	def _recommendations_for_stage(self, attack_stage: str, threat_ip: str, threat_user: str) -> list[str]:
		if attack_stage == "initial_access":
			return [
				f"Force password reset for {threat_user}",
				"Enable MFA immediately",
			]
		if attack_stage == "lateral_movement":
			return [
				f"Isolate host {threat_ip}",
				f"Audit all sessions from this IP",
			]
		if attack_stage == "exfiltration":
			return [
				"Block outbound to suspect IPs",
				"Capture forensic image",
			]
		return [
			"Enable account lockout policy",
			"Add IP to blocklist",
		]

	def _inspect_results_for_stage_flags(self, results: list[dict], destination_ips: set[str]) -> None:
		for row in results:
			destination_ips.update(self._normalize_destinations(row.get("destinations")))

	@staticmethod
	def _timeline_entry(timestamp: Any, event_type: str, src: Any, dest: Any, action: Any) -> dict:
		return {
			"timestamp": Investigator._normalize_timestamp(timestamp),
			"event_type": str(event_type),
			"src": str(src) if src not in (None, "") else "",
			"dest": str(dest) if dest not in (None, "") else "",
			"action": str(action) if action not in (None, "") else "",
		}

	@staticmethod
	def _normalize_timestamp(value: Any) -> str:
		if value in (None, ""):
			return datetime.now(timezone.utc).isoformat()
		if isinstance(value, (int, float)):
			return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
		value_str = str(value)
		if value_str.isdigit():
			return datetime.fromtimestamp(float(value_str), tz=timezone.utc).isoformat()
		try:
			return datetime.fromisoformat(value_str).isoformat()
		except ValueError:
			return value_str

	@staticmethod
	def _normalize_destinations(value: Any) -> set[str]:
		if value in (None, ""):
			return set()
		if isinstance(value, (list, tuple, set)):
			return {str(item) for item in value if item not in (None, "")}
		return {str(value)}

	@staticmethod
	def _as_int(value: Any, default: int = 0) -> int:
		try:
			if value is None:
				return default
			return int(float(value))
		except (TypeError, ValueError):
			return default

	@staticmethod
	def _is_failed_action(row: dict) -> bool:
		action = str(row.get("action", "")).lower()
		raw = str(row.get("_raw", "")).lower()
		return "fail" in action or "failure" in action or "fail" in raw or "failure" in raw

	@staticmethod
	def _is_success_action(row: dict) -> bool:
		action = str(row.get("action", "")).lower()
		raw = str(row.get("_raw", "")).lower()
		return "success" in action or "login" in action and "success" in raw or "success" in raw

	@staticmethod
	def _has_exfiltration_bytes(row: dict) -> bool:
		for key, value in row.items():
			if "byte" not in str(key).lower():
				continue
			if Investigator._as_int(value, default=0) > 50_000_000:
				return True
		return False
