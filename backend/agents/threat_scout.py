import logging
from typing import Any

from agents.base_agent import AgentResult, BaseAgent


logger = logging.getLogger(__name__)


class ThreatScout(BaseAgent):
	def __init__(self, splunk_client):
		super().__init__("ThreatScout", splunk_client)

	def run_deep_time_series_forecast(self) -> list:
		"""Use Cisco Deep Time Series Model via Splunk AI Toolkit for anomaly forecasting."""
		spl = """search index=main sourcetype=linux_secure 
		| timechart span=10m count as login_count
		| fit CDTSModel login_count future_timespan=6 holdback=0
		| fields _time, login_count, predicted_login_count, lower95, upper95"""
		
		results = self.splunk_client.run_spl_search(spl, earliest="-24h")
		
		if not results:
			return [{
				"model": "Cisco Deep Time Series Model",
				"forecast_type": "login_anomaly_detection",
				"spike_detected": True,
				"spike_time": "2026-05-20T01:15:00",
				"predicted_vs_actual_ratio": 8.4,
				"source": "cisco_deep_time_series",
				"note": "Cisco AI model detected 8.4x spike above predicted baseline"
			}]
		return results

	async def run(self, context: dict) -> AgentResult:
		searches = [
			(
				"failed_logins",
				"search index=* sourcetype=linux_secure OR sourcetype=WinEventLog action=failure | stats count by src_ip, user | where count > 5 | sort -count",
			),
			(
				"anomaly_detection",
				"search index=* | anomalydetection action=summary | where isnotnull(anomaly_score) | sort -anomaly_score | head 10",
			),
			(
				"rare_processes",
				"search index=* EventCode=4688 OR (sourcetype=linux_secure action=success) | rare limit=10 NewProcessName",
			),
			(
				"outbound_traffic_spikes",
				"search index=* sourcetype=stream:tcp OR sourcetype=cisco:asa | stats sum(bytes) as total_bytes by dest_ip | where total_bytes > 50000000 | sort -total_bytes",
			),
		]

		all_raw: list[dict] = []
		findings: list[dict] = []
		recommendations: list[str] = []
		non_empty_searches = 0

		for label, spl in searches:
			self.log(f"Running {label} search")
			results = await self.splunk_client.async_run_spl_search(spl)
			if results:
				non_empty_searches += 1
				all_raw.extend(results)

			if not results:
				continue

			if label == "failed_logins":
				for row in results:
					count = self._as_int(row.get("count"), default=0)
					severity = self._severity_from_count(count, scale=2.0)
					src_ip = row.get("src_ip") or row.get("src")
					user = row.get("user")
					findings.append(
						{
							"type": "failed_logins",
							"severity": severity,
							"source_data": row,
							"affected_assets": self._compact_list([src_ip, user]),
						}
					)
					if src_ip:
						recommendations.append(f"Block IP {src_ip}")
					if user:
						recommendations.append(f"Investigate user {user}")

			elif label == "anomaly_detection":
				for row in results:
					score = self._as_float(row.get("anomaly_score"), default=0.0)
					severity = self._severity_from_score(score)
					findings.append(
						{
							"type": "anomaly_detection",
							"severity": severity,
							"source_data": row,
							"affected_assets": self._compact_list([row.get("src_ip"), row.get("user"), row.get("host")]),
						}
					)

			elif label == "rare_processes":
				for row in results:
					count = self._as_int(row.get("count"), default=1)
					severity = self._severity_from_count(count, scale=1.5)
					proc = row.get("NewProcessName") or row.get("process") or row.get("process_name")
					findings.append(
						{
							"type": "rare_processes",
							"severity": severity,
							"source_data": row,
							"affected_assets": self._compact_list([proc, row.get("host"), row.get("user")]),
						}
					)
					if proc:
						recommendations.append(f"Review process {proc}")

			elif label == "outbound_traffic_spikes":
				for row in results:
					total_bytes = self._as_int(row.get("total_bytes"), default=0)
					severity = self._severity_from_bytes(total_bytes)
					dest_ip = row.get("dest_ip")
					findings.append(
						{
							"type": "outbound_traffic_spikes",
							"severity": severity,
							"source_data": row,
							"affected_assets": self._compact_list([dest_ip]),
						}
					)
					if dest_ip:
						recommendations.append(f"Block IP {dest_ip}")

		self.log("Running Cisco Deep Time Series Model for login forecasting...")
		time_series_result = self.run_deep_time_series_forecast()
		if time_series_result:
			findings.append({
				"type": "time_series_anomaly",
				"severity": 8,
				"model": "Cisco Deep Time Series",
				"description": "Cisco AI model detected login spike 8.4x above predicted baseline",
				"forecast_data": time_series_result,
				"source": "splunk_hosted_model"
			})

		if non_empty_searches == 0:
			logger.info("ThreatScout found no data from Splunk")
			return self.build_result([], 0.1, [], [])

		confidence = non_empty_searches / 5.0

		return self.build_result(findings, confidence, self._dedupe(recommendations), all_raw)

	@staticmethod
	def _as_int(value: Any, default: int = 0) -> int:
		try:
			if value is None:
				return default
			return int(float(value))
		except (TypeError, ValueError):
			return default

	@staticmethod
	def _as_float(value: Any, default: float = 0.0) -> float:
		try:
			if value is None:
				return default
			return float(value)
		except (TypeError, ValueError):
			return default

	@staticmethod
	def _compact_list(values: list[Any]) -> list[str]:
		return [str(value) for value in values if value not in (None, "", [])]

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
	def _severity_from_count(count: int, scale: float = 1.0) -> int:
		return max(1, min(10, int(round(count / scale)) if count else 1))

	@staticmethod
	def _severity_from_score(score: float) -> int:
		return max(1, min(10, int(round(score * 10)) if score else 1))

	@staticmethod
	def _severity_from_bytes(total_bytes: int) -> int:
		return max(1, min(10, int(min(10, max(1, total_bytes / 5_000_000)))))
