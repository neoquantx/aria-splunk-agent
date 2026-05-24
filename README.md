# ▲ ARIA — Agentic Response & Investigation Assistant

![MIT License](https://img.shields.io/badge/License-MIT-green.svg) ![Security Track](https://img.shields.io/badge/Track-Security-red.svg) ![Built with Splunk](https://img.shields.io/badge/Built%20with-Splunk-black.svg) ![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)

ARIA is an AI-powered multi-agent security operations assistant that detects, investigates, correlates, and responds to threats using Splunk, Splunk AI, and a clean FastAPI + React stack. It turns noisy security telemetry into actionable incident context and recommendations. SOC analysts spend 60+ minutes per alert — ARIA does it in 60 seconds using 4 specialized AI agents.

---

## The Problem

Security Operations Center teams are overwhelmed by high alert volumes, fragmented logs, and the time it takes to manually reconstruct what happened during an incident. A single suspicious event can require searching multiple data sources, correlating timestamps, identifying affected hosts, and deciding whether the activity is brute force, lateral movement, command execution, or exfiltration.

ARIA reduces that manual work by splitting the investigation into four specialized agents that run in sequence over Splunk data. Each agent focuses on one task: detecting threats, building an incident timeline, mapping the activity to MITRE ATT&CK, and generating a response playbook. The result is faster triage, clearer evidence, and less analyst fatigue.

---

## How ARIA Works

| Agent | Role | Splunk Capability |
|---|---|---|
| ThreatScout | Detects suspicious login activity, anomalies, rare processes, and outbound spikes | anomalydetection, rare |
| Investigator | Reconstructs the incident timeline and attack progression | SPL timechart, transaction |
| Correlator | Maps findings to MITRE ATT&CK and hosted security models | MITRE ATT&CK + Foundation-Sec-1.1-8B |
| Strategist | Calculates risk and generates response guidance | Risk scoring + playbook generation |

---

## Splunk AI Capabilities Used

- Splunk Python SDK (splunk-sdk 1.7.4)
- Splunk ML Toolkit — anomalydetection, predict, rare commands
- Splunk MCP Server — agent-to-Splunk communication
- Splunk AI Assistant — natural language to SPL
- Foundation-Sec-1.1-8B — Splunk hosted security model
- Cisco Deep Time Series Model — anomaly forecasting

---

## Architecture

See [architecture_diagram.png](architecture_diagram.png) and [architecture_diagram.md](architecture_diagram.md) in the root of this repository.

---

## Prerequisites

1. Splunk Enterprise (free trial or developer license)
   - Download: https://www.splunk.com/en_us/download/splunk-enterprise.html
   - Start: /Applications/Splunk/bin/splunk start
   - Web UI: http://localhost:8000
2. Python 3.11
3. Node.js 18+
4. Git

---

## Quick Start

### Step 1 — Clone

```bash
git clone https://github.com/neoquantx/aria-splunk-agent.git
cd aria-splunk-agent
```

### Step 2 — Configure

```bash
cp backend/.env.example backend/.env
```

Open backend/.env and set these values:
- SPLUNK_PASSWORD — your Splunk admin password (set during Splunk install)
- SPLUNK_USERNAME — admin (default)
- SPLUNK_HOST — localhost (default)
- SPLUNK_PORT — 8089 (default)

### Step 3 — Load sample data into Splunk

```bash
cd backend
python3 demo/load_splunk_data.py
```

This loads 39 realistic security events (brute force attack, lateral movement, C2 communication, exfiltration) into Splunk index=main.

### Step 4 — Start backend

```bash
cd backend
python3 -m uvicorn main:app --reload
```

### Step 5 — Start frontend

Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```

### Step 6 — Open ARIA

- Dashboard: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Splunk: http://localhost:8000

---

## Demo Mode (No Splunk Required)

If you do not have Splunk running, use demo mode:
GET http://localhost:8000/api/v1/demo/run-scenario

Returns a complete realistic incident report with threats, MITRE ATT&CK mapping, and remediation playbook — no Splunk connection needed.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/incidents/ | List recent incidents |
| POST | /api/v1/incidents/investigate | Run the full ARIA investigation pipeline |
| POST | /api/v1/agents/run | Trigger all 4 ARIA agents |
| GET | /api/v1/agents/status | Get current agent status and progress |
| POST | /api/v1/splunk/query | Run a raw SPL query |
| GET | /api/v1/splunk/status | Check Splunk connection status |
| GET | /api/v1/splunk/events | Get recent events from Splunk |
| POST | /api/v1/chat/ | Ask ARIA a natural language question |
| GET | /api/v1/demo/run-scenario | Return the complete demo incident report |
| GET | /api/v1/demo/threats | Return only demo threats |
| GET | /api/v1/demo/investigation | Return only the demo timeline |
| GET | /api/v1/demo/correlation | Return only the demo MITRE mapping |
| GET | /api/v1/demo/strategy | Return only the demo playbook |

---

## Project Structure

```text
aria-splunk-agent/
├── architecture_diagram.png    ← Architecture diagram
├── architecture_diagram.md     ← Detailed architecture
├── README.md
├── LICENSE
├── docker-compose.yml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── core/
│   │   ├── config.py
│   │   ├── splunk_client.py
│   │   └── mcp_client.py
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── threat_scout.py
│   │   ├── investigator.py
│   │   ├── correlator.py
│   │   ├── strategist.py
│   │   └── orchestrator.py
│   ├── api/v1/routes/
│   │   ├── incidents.py
│   │   ├── agents.py
│   │   ├── splunk.py
│   │   ├── chat.py
│   │   └── demo.py
│   └── demo/
│       ├── demo_data.py
│       └── load_splunk_data.py
└── frontend/
    └── src/
        └── components/
            ├── ThreatFeed.jsx
            ├── RiskGauge.jsx
            ├── AttackTimeline.jsx
            ├── ARIAChat.jsx
            ├── AgentProgress.jsx
            └── ImpactBanner.jsx
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Port 8000 in use | Stop the other process: `lsof -ti:8000 | xargs kill` |
| Splunk login fails | Reset: `/Applications/Splunk/bin/splunk edit user admin -password newpass -auth admin:oldpass` |
| blake2b warning | Harmless warning from pyenv OpenSSL — ignore it, the app still works |
| No data in Splunk | Run: `python3 demo/load_splunk_data.py` |

---

## License

MIT License — see LICENSE file.
