import logging

from agents.base_agent import AgentResult, BaseAgent


logger = logging.getLogger(__name__)


class Strategist(BaseAgent):
	PLAYBOOKS = {
		"reconnaissance": {
			"immediate": [
				"Block attacking IP at firewall",
				"Enable failed login alerting",
			],
			"short_term": [
				"Review firewall rules",
				"Enable geo-blocking for unusual regions",
			],
			"long_term": [
				"Implement SIEM correlation rules",
				"Deploy honeypots",
			],
		},
		"initial_access": {
			"immediate": [
				"Disable compromised account immediately",
				"Force all user password resets",
				"Revoke all active sessions",
			],
			"short_term": [
				"Enable MFA for all admin accounts",
				"Audit privileged access",
			],
			"long_term": [
				"Implement zero-trust architecture",
				"Deploy PAM solution",
			],
		},
		"lateral_movement": {
			"immediate": [
				"Isolate all affected hosts from network",
				"Block internal SMB/RDP from compromised IPs",
			],
			"short_term": [
				"Audit all service accounts",
				"Review network segmentation",
			],
			"long_term": [
				"Implement microsegmentation",
				"Deploy EDR on all endpoints",
			],
		},
		"exfiltration": {
			"immediate": [
				"Block all outbound from affected hosts",
				"Notify data protection officer",
				"Preserve forensic evidence",
			],
			"short_term": [
				"Identify all exfiltrated data",
				"Notify affected parties",
			],
			"long_term": [
				"Implement DLP solution",
				"Encrypt sensitive data at rest",
			],
		},
	}

	def __init__(self, splunk_client):
		super().__init__("Strategist", splunk_client)

	async def run(self, context: dict) -> AgentResult:
		attack_stage = context.get("attack_stage", "reconnaissance")
		threat_count = len(context.get("threats", []) or [])
		mitre_count = len(context.get("mitre_techniques", []) or [])
		is_coordinated = context.get("is_coordinated_attack", False)

		base_score = 20
		base_score += min(threat_count * 10, 30)
		base_score += min(mitre_count * 5, 20)
		if is_coordinated:
			base_score += 20
		stage_bonus = {
			"reconnaissance": 0,
			"initial_access": 10,
			"lateral_movement": 15,
			"exfiltration": 20,
		}
		risk_score = min(100, base_score + stage_bonus.get(attack_stage, 0))

		playbook = self.PLAYBOOKS.get(attack_stage, self.PLAYBOOKS["reconnaissance"])

		self.log("Running final asset aggregation search")
		splunk_results = await self.splunk_client.async_run_spl_search(
			"search index=* | stats dc(host) as unique_hosts, dc(src_ip) as unique_ips, dc(user) as unique_users by index | addtotals"
		)

		executive_summary = (
			f"ARIA detected a {attack_stage.replace('_', ' ')} attack with risk score {risk_score}/100. "
			f"{threat_count} threats identified across {mitre_count} MITRE ATT&CK techniques. "
			f"{'This appears to be a coordinated campaign.' if is_coordinated else 'No evidence of coordination.'} "
			f"Immediate containment is {'critical' if risk_score > 70 else 'recommended'}."
		)

		findings = [
			{
				"risk_score": risk_score,
				"executive_summary": executive_summary,
				"playbook": playbook,
				"attack_stage": attack_stage,
			}
		]
		recommendations = playbook["immediate"] + playbook["short_term"]

		if not splunk_results:
			logger.info("Strategist final asset aggregation search returned no data")

		return self.build_result(findings, 0.9, recommendations, splunk_results)
