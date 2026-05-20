import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentResult:
	agent_name: str
	findings: list[dict]
	confidence: float
	recommendations: list[str]
	raw_spl_results: list[dict]
	timestamp: str
	status: str


class BaseAgent(ABC):
	def __init__(self, name: str, splunk_client):
		self.name = name
		self.splunk_client = splunk_client
		self.logs = []

	@abstractmethod
	async def run(self, context: dict) -> AgentResult:
		raise NotImplementedError

	def log(self, message: str):
		entry = {
			"time": datetime.now().isoformat(),
			"agent": self.name,
			"msg": message,
		}
		self.logs.append(entry)
		logging.info("%s: %s", self.name, message)

	def build_result(
		self,
		findings,
		confidence,
		recommendations,
		raw_data,
	) -> AgentResult:
		clean_confidence = max(0.0, min(1.0, float(confidence)))
		status = "success" if findings or raw_data else "no_data"
		return AgentResult(
			agent_name=self.name,
			findings=list(findings),
			confidence=clean_confidence,
			recommendations=list(recommendations),
			raw_spl_results=list(raw_data),
			timestamp=datetime.now().isoformat(),
			status=status,
		)
