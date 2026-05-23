# ARIA — Architecture Diagram

```text
+--------------------------------------------------------------------------------------+
| DATA SOURCES LAYER                                                                   |
|--------------------------------------------------------------------------------------|
| • Linux SSH / auth logs (sourcetype=linux_secure)                                    |
| • Windows Event Logs (sourcetype=WinEventLog)                                        |
| • Network / TCP stream logs (sourcetype=stream:tcp)                                  |
| • Firewall / IDS logs (sourcetype=cisco:asa)                                         |
| • Demo anomaly feed (sourcetype=aria_anomaly)                                        |
+--------------------------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------------+
| SPLUNK PLATFORM LAYER                                                                 |
|--------------------------------------------------------------------------------------|
| Splunk Enterprise                                                                     |
| ML / SPL commands found in agents:                                                    |
|   anomalydetection, stats, where, sort, head, rare, timechart, transaction,          |
|   join, eval, table, fields, values, dc, search                                       |
+--------------------------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------------+
| SPLUNK MCP SERVER LAYER                                                               |
|--------------------------------------------------------------------------------------|
| Agent-to-Splunk communication layer referenced in the project README                 |
| (backend/core/mcp_client.py exists but is empty in this codebase)                     |
+--------------------------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------------+
| ARIA ORCHESTRATOR LAYER                                                               |
|--------------------------------------------------------------------------------------|
| ARIAOrchestrator.run_full_investigation()                                             |
| Coordinates ThreatScout -> Investigator -> Correlator -> Strategist                  |
+--------------------------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------------+
| 4 AGENTS LAYER                                                                        |
|--------------------------------------------------------------------------------------|
| ThreatScout     | failed logins, anomalydetection, rare processes, outbound spikes    |
| Investigator    | timeline, activity pattern, lateral movement, auth chain             |
| Correlator      | correlation search + MITRE ATT&CK mapping                           |
| Strategist      | final asset aggregation + risk scoring + playbook generation          |
+--------------------------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------------+
| INCIDENT SYNTHESIS LAYER                                                              |
|--------------------------------------------------------------------------------------|
| IncidentReport built from:                                                            |
| threats, investigation.timeline, investigation.logs, correlation, strategy,          |
| risk_score, executive_summary, attack_stage, status                                   |
+--------------------------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------------+
| FASTAPI BACKEND LAYER                                                                 |
|--------------------------------------------------------------------------------------|
| Port: 8001                                                                            |
| Routes mounted under /api/v1:                                                         |
|   /incidents, /agents, /splunk, /chat, /demo                                          |
+--------------------------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------------+
| REACT FRONTEND LAYER                                                                  |
|--------------------------------------------------------------------------------------|
| Port: 5173                                                                            |
| Components: App, ThreatFeed, RiskGauge, AttackTimeline, ARIAChat, AgentProgress,     |
| ImpactBanner                                                                          |
+--------------------------------------------------------------------------------------+
```

## Component Details

| Component | Technology | Purpose |
|---|---|---|
| fastapi==0.115.6 | FastAPI | Backend API framework and route mounting |
| uvicorn[standard]==0.34.0 | Uvicorn | ASGI server used to run the FastAPI app on port 8000 |
| splunk-sdk==1.7.4 | Splunk Python SDK | Connects the backend to Splunk Enterprise and submits / queries data |
| httpx==0.28.1 | HTTP client | HTTP client dependency used by the backend codebase |
| python-dotenv==1.0.1 | python-dotenv | Loads environment variables from backend/.env |
| pydantic==2.10.6 | Pydantic | Data validation and API schemas |
| pydantic-settings==2.7.1 | Pydantic Settings | Typed configuration loading in backend/core/config.py |
| aiofiles==24.1.0 | aiofiles | Async file I/O support |
| pandas==2.2.3 | pandas | Data manipulation / analysis support |
| python-dateutil==2.9.0.post0 | python-dateutil | Date parsing and datetime helpers |

## Data Flow

1. The user clicks RUN SCAN in [frontend/src/App.jsx](frontend/src/App.jsx).
2. `runFullScan()` immediately checks the `scanning` flag, then sets `scanning=true`, `showProgress=true`, and clears `agentProgress`.
3. The frontend renders the [AgentProgress](frontend/src/components/AgentProgress.jsx) overlay while the simulated scan runs.
4. `runFullScan()` appends staged messages for ThreatScout, Investigator, Correlator, and Strategist using timed delays.
5. After the timed sequence, `runFullScan()` calls `loadData()`.
6. `loadData()` sets `loading=true` and requests `/api/v1/demo/run-scenario` and `/api/v1/splunk/status` in parallel.
7. `/api/v1/demo/run-scenario` returns the demo incident report built by `get_full_demo_report()` in [backend/demo/demo_data.py](backend/demo/demo_data.py).
8. `/api/v1/splunk/status` calls `default_splunk_client.test_connection()` in [backend/core/splunk_client.py](backend/core/splunk_client.py) and returns whether Splunk is connected.
9. The frontend stores the returned report in `report`, updates `splunkConnected`, sets `loading=false`, and then sets `scanning=false`.
10. The overlay remains visible until the user closes it, after which the dashboard shows the refreshed [ImpactBanner](frontend/src/components/ImpactBanner.jsx), [ThreatFeed](frontend/src/components/ThreatFeed.jsx), [RiskGauge](frontend/src/components/RiskGauge.jsx), [AttackTimeline](frontend/src/components/AttackTimeline.jsx), or [ARIAChat](frontend/src/components/ARIAChat.jsx) depending on the active tab.

## Splunk AI Capabilities

The following SPL and ML commands are actually present in the agent files under [backend/agents/](backend/agents):

- `anomalydetection`
- `stats`
- `where`
- `sort`
- `head`
- `rare`
- `timechart`
- `transaction`
- `join`
- `eval`
- `table`
- `fields`
- `values`
- `dc`
- `search`

## API Endpoints

All routes found in the five route files under [backend/api/v1/routes/](backend/api/v1/routes):

- [backend/api/v1/routes/agents.py](backend/api/v1/routes/agents.py)
  - `POST /api/v1/agents/run`
  - `GET /api/v1/agents/status`
- [backend/api/v1/routes/chat.py](backend/api/v1/routes/chat.py)
  - `POST /api/v1/chat/`
- [backend/api/v1/routes/demo.py](backend/api/v1/routes/demo.py)
  - `GET /api/v1/demo/run-scenario`
  - `GET /api/v1/demo/threats`
  - `GET /api/v1/demo/investigation`
  - `GET /api/v1/demo/correlation`
  - `GET /api/v1/demo/strategy`
- [backend/api/v1/routes/incidents.py](backend/api/v1/routes/incidents.py)
  - `GET /api/v1/incidents/`
  - `POST /api/v1/incidents/investigate`
- [backend/api/v1/routes/splunk.py](backend/api/v1/routes/splunk.py)
  - `POST /api/v1/splunk/query`
  - `GET /api/v1/splunk/status`
  - `GET /api/v1/splunk/events`
