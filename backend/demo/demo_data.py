from datetime import datetime
from uuid import uuid4


def get_demo_threats() -> list[dict]:
	return [
		{
			"type": "brute_force",
			"severity": 9,
			"src_ip": "185.220.101.47",
			"user": "admin",
			"count": 847,
			"time_window": "20 minutes",
			"affected_assets": ["web-server-01"],
		},
		{
			"type": "anomaly_detected",
			"severity": 7,
			"src_ip": "185.220.101.47",
			"anomaly_score": 0.94,
			"description": "Unusual login time pattern detected by Splunk ML",
		},
		{
			"type": "outbound_spike",
			"severity": 8,
			"dest_ip": "45.142.212.100",
			"total_bytes": 157286400,
			"description": "Large outbound transfer to unknown external IP",
		},
	]


def get_demo_investigation() -> list[dict]:
	return [
		{
			"timestamp": "2026-05-20T01:15:00",
			"event_type": "failed_ssh",
			"src": "185.220.101.47",
			"dest": "web-server-01",
			"action": "failed password",
			"user": "admin",
		},
		{
			"timestamp": "2026-05-20T01:22:00",
			"event_type": "failed_ssh",
			"src": "185.220.101.47",
			"dest": "web-server-01",
			"action": "failed password",
			"user": "admin",
		},
		{
			"timestamp": "2026-05-20T01:28:00",
			"event_type": "failed_ssh",
			"src": "185.220.101.47",
			"dest": "web-server-01",
			"action": "failed password",
			"user": "admin",
		},
		{
			"timestamp": "2026-05-20T01:34:00",
			"event_type": "failed_ssh",
			"src": "185.220.101.47",
			"dest": "web-server-01",
			"action": "failed password",
			"user": "admin",
		},
		{
			"timestamp": "2026-05-20T01:35:00",
			"event_type": "successful_ssh",
			"src": "185.220.101.47",
			"dest": "web-server-01",
			"action": "accepted password",
			"user": "admin",
		},
		{
			"timestamp": "2026-05-20T01:36:00",
			"event_type": "command_execution",
			"src": "185.220.101.47",
			"dest": "web-server-01",
			"action": "whoami",
			"user": "admin",
		},
		{
			"timestamp": "2026-05-20T01:36:30",
			"event_type": "command_execution",
			"src": "185.220.101.47",
			"dest": "web-server-01",
			"action": "id",
			"user": "admin",
		},
		{
			"timestamp": "2026-05-20T01:52:00",
			"event_type": "lateral_ssh",
			"src": "web-server-01",
			"dest": "internal-host-02",
			"action": "ssh connection established",
			"user": "svc-web",
		},
		{
			"timestamp": "2026-05-20T02:10:00",
			"event_type": "lateral_ssh",
			"src": "internal-host-02",
			"dest": "internal-host-03",
			"action": "ssh connection established",
			"user": "svc-admin",
		},
		{
			"timestamp": "2026-05-20T02:31:00",
			"event_type": "c2_contact",
			"src": "internal-host-03",
			"dest": "45.142.212.100",
			"action": "https session initiated",
			"user": "svc-admin",
		},
		{
			"timestamp": "2026-05-20T02:40:00",
			"event_type": "staging",
			"src": "internal-host-03",
			"dest": "45.142.212.100",
			"action": "prepare archive for transfer",
			"user": "svc-admin",
		},
		{
			"timestamp": "2026-05-20T02:47:00",
			"event_type": "large_file_transfer",
			"src": "internal-host-03",
			"dest": "45.142.212.100",
			"action": "file transfer completed",
			"user": "svc-admin",
		},
	]


def get_demo_correlation() -> dict:
	return {
		"mitre_techniques": [
			{"technique_id": "T1110", "technique_name": "Brute Force", "tactic": "Credential Access"},
			{"technique_id": "T1021", "technique_name": "Remote Services", "tactic": "Lateral Movement"},
			{"technique_id": "T1059", "technique_name": "Command and Scripting Interpreter", "tactic": "Execution"},
			{"technique_id": "T1071", "technique_name": "Application Layer Protocol", "tactic": "Command and Control"},
			{"technique_id": "T1041", "technique_name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration"},
		],
		"is_coordinated": True,
		"campaign_confidence": 0.87,
		"kill_chain_stage": "exfiltration",
	}


def get_demo_strategy() -> dict:
	return {
		"risk_score": 91,
		"attack_stage": "exfiltration",
		"executive_summary": (
			"ARIA detected an active exfiltration attack with a high degree of confidence. "
			"The activity progressed from brute-force access to lateral movement and command execution before outbound staging and transfer. "
			"Immediate containment and evidence preservation are critical to limit ongoing loss and support response actions."
		),
		"playbook": {
			"immediate": [
				"Block all outbound from affected hosts",
				"Notify data protection officer",
				"Preserve forensic evidence",
				"Disable compromised admin credentials",
				"Isolate internal-host-03 from the network",
			],
			"short_term": [
				"Identify all exfiltrated data",
				"Notify affected parties",
				"Review all privileged SSH activity from 185.220.101.47",
			],
			"long_term": [
				"Implement DLP solution",
				"Encrypt sensitive data at rest",
				"Deploy MFA and PAM for administrative access",
			],
		},
	}


def get_full_demo_report() -> dict:
	investigation = get_demo_investigation()
	correlation = get_demo_correlation()
	strategy = get_demo_strategy()
	return {
		"id": str(uuid4()),
		"timestamp": datetime.now().isoformat(),
		"threats": get_demo_threats(),
		"investigation": {"timeline": investigation, "logs": investigation},
		"correlation": correlation,
		"strategy": strategy,
		"risk_score": strategy["risk_score"],
		"executive_summary": strategy["executive_summary"],
		"attack_stage": strategy["attack_stage"],
		"status": "complete",
	}
