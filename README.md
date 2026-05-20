---
# ▲ ARIA — Agentic Response & Investigation Assistant

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Track: Security](https://img.shields.io/badge/Track-Security-red.svg)
![Built with Splunk](https://img.shields.io/badge/Built%20with-Splunk-black.svg)

ARIA is an AI-powered multi-agent system that autonomously detects, investigates, and responds to security threats using Splunk's AI capabilities and MCP Server. What takes a SOC analyst 60+ minutes, ARIA completes in under 60 seconds.

---

## The Problem

Security Operations Center (SOC) analysts are overwhelmed. The average organisation receives thousands of alerts per day, and manual triage of each alert takes 30-60 minutes. Threats go undetected. Analysts burn out. ARIA solves this.

---

## How It Works

ARIA uses 4 specialised AI agents that collaborate through Splunk MCP Server:

| Agent | Role | Splunk Capability Used |
|---|---|---|
| ThreatScout | Detects anomalies and suspicious patterns | Splunk ML Toolkit — anomalydetection command |
| Investigator | Builds attack timeline from raw events | Splunk SPL search — transaction and timechart |
| Correlator | Maps findings to MITRE ATT&CK framework | Splunk stats correlation + Python MITRE mapping |
| Strategist | Generates prioritised remediation playbook | Splunk risk scoring + PLAYBOOKS engine |

---

## Architecture

See `architecture_diagram.png` in the root of this repository.

---

## Tech Stack

- **Backend:** Python, FastAPI, Splunk Python SDK (splunklib)
- **AI:** Splunk ML Toolkit, Splunk anomalydetection, Splunk AI Assistant
- **Data:** Splunk MCP Server, Splunk Enterprise
- **Frontend:** React, Vite, Tailwind CSS, Recharts
- **Infrastructure:** Docker, docker-compose

---

## Quick Start

### Prerequisites
- Splunk Enterprise (free trial or developer license)
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/aria-splunk-agent.git
cd aria-splunk-agent
```

2. Configure environment:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set your SPLUNK_PASSWORD
```

3. Install and run backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

4. Install and run frontend:
```bash
cd frontend
npm install
npm run dev
```

5. Open http://localhost:5173

### Demo Mode (No Splunk Required)

If you do not have Splunk running, use the demo endpoint to see ARIA in action with realistic pre-loaded attack data:

GET http://localhost:8000/api/v1/demo/run-scenario

This simulates a complete brute-force to exfiltration attack chain with realistic data.

---

## Splunk AI Capabilities Used

- **Splunk MCP Server** — agent-to-Splunk communication layer
- **Splunk ML Toolkit** — `anomalydetection` command for real-time threat detection
- **Splunk SPL** — `predict`, `timechart`, `transaction`, `rare` commands
- **Splunk AI Assistant** — natural language security query interface

---

## Project Structure

aria-splunk-agent/
├── architecture_diagram.png    ← Architecture diagram (hackathon requirement)
├── README.md
├── LICENSE
├── docker-compose.yml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── core/
│   │   ├── config.py
│   │   └── splunk_client.py
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
│       └── demo_data.py
└── frontend/
└── (React app)

---

## License

MIT License — see LICENSE file for details.

---

