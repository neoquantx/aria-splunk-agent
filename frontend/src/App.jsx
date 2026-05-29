import { useEffect, useState, useCallback } from 'react'
import { Shield, Activity, AlertTriangle, Terminal, Wifi, WifiOff } from 'lucide-react'
import ThreatFeed from './components/ThreatFeed'
import RiskGauge from './components/RiskGauge'
import AttackTimeline from './components/AttackTimeline'
import ARIAChat from './components/ARIAChat'
import AgentProgress from './components/AgentProgress'
import ImpactBanner from './components/ImpactBanner'
import { getHealthCheck, getDemoScenario, getSplunkStatus } from './api'

const FALLBACK_REPORT = {
  id: "demo-001",
  timestamp: new Date().toISOString(),
  threats: [
    { type: "brute_force", severity: 9, src_ip: "185.220.101.47", user: "admin", count: 847, time_window: "20 minutes", affected_assets: ["web-server-01"], description: "847 failed SSH attempts from external IP" },
    { type: "anomaly_detected", severity: 7, src_ip: "185.220.101.47", anomaly_score: 0.94, description: "Unusual login time pattern detected by Splunk ML", affected_assets: ["web-server-01"] },
    { type: "outbound_spike", severity: 8, dest_ip: "45.142.212.100", total_bytes: 157286400, description: "Large outbound transfer to unknown external IP", affected_assets: ["internal-host-03"] }
  ],
  investigation: {
    timeline: [
      { timestamp: "2026-05-20T01:15:00", event_type: "failed_ssh", src: "185.220.101.47", dest: "web-server-01", action: "failed password", user: "admin" },
      { timestamp: "2026-05-20T01:22:00", event_type: "failed_ssh", src: "185.220.101.47", dest: "web-server-01", action: "failed password", user: "admin" },
      { timestamp: "2026-05-20T01:28:00", event_type: "failed_ssh", src: "185.220.101.47", dest: "web-server-01", action: "failed password", user: "admin" },
      { timestamp: "2026-05-20T01:34:00", event_type: "failed_ssh", src: "185.220.101.47", dest: "web-server-01", action: "failed password", user: "admin" },
      { timestamp: "2026-05-20T01:35:00", event_type: "successful_ssh", src: "185.220.101.47", dest: "web-server-01", action: "accepted password", user: "admin" },
      { timestamp: "2026-05-20T01:36:00", event_type: "command_execution", src: "185.220.101.47", dest: "web-server-01", action: "whoami", user: "admin" },
      { timestamp: "2026-05-20T01:36:30", event_type: "command_execution", src: "185.220.101.47", dest: "web-server-01", action: "id", user: "admin" },
      { timestamp: "2026-05-20T01:52:00", event_type: "lateral_ssh", src: "web-server-01", dest: "internal-host-02", action: "ssh connection established", user: "svc-web" },
      { timestamp: "2026-05-20T02:10:00", event_type: "lateral_ssh", src: "internal-host-02", dest: "internal-host-03", action: "ssh connection established", user: "svc-admin" },
      { timestamp: "2026-05-20T02:31:00", event_type: "c2_contact", src: "internal-host-03", dest: "45.142.212.100", action: "https session initiated", user: "svc-admin" },
      { timestamp: "2026-05-20T02:40:00", event_type: "staging", src: "internal-host-03", dest: "45.142.212.100", action: "prepare archive for transfer", user: "svc-admin" },
      { timestamp: "2026-05-20T02:47:00", event_type: "large_file_transfer", src: "internal-host-03", dest: "45.142.212.100", action: "file transfer completed", user: "svc-admin" }
    ]
  },
  correlation: {
    mitre_techniques: [
      { technique_id: "T1110", technique_name: "Brute Force", tactic: "Credential Access" },
      { technique_id: "T1021", technique_name: "Remote Services", tactic: "Lateral Movement" },
      { technique_id: "T1059", technique_name: "Command and Scripting Interpreter", tactic: "Execution" },
      { technique_id: "T1071", technique_name: "Application Layer Protocol", tactic: "Command and Control" }
    ],
    is_coordinated: true,
    campaign_confidence: 0.87
  },
  strategy: {
    playbook: {
      immediate: ["Block all outbound from affected hosts", "Notify data protection officer", "Preserve forensic evidence", "Disable compromised admin credentials", "Isolate internal-host-03"],
      short_term: ["Identify all exfiltrated data", "Notify affected parties", "Review all privileged SSH activity"],
      long_term: ["Implement DLP solution", "Encrypt sensitive data at rest", "Deploy MFA and PAM"]
    }
  },
  risk_score: 91,
  executive_summary: "ARIA detected an active exfiltration attack with a high degree of confidence. The activity progressed from brute-force access to lateral movement and command execution before outbound staging and transfer. Immediate containment and evidence preservation are critical.",
  attack_stage: "exfiltration",
  status: "complete"
}

export default function App() {
  const [report, setReport] = useState(FALLBACK_REPORT)
  const [loading, setLoading] = useState(false)
  const [splunkConnected, setSplunkConnected] = useState(false)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [scanning, setScanning] = useState(false)
  const [agentProgress, setAgentProgress] = useState([])
  const [showProgress, setShowProgress] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date().toLocaleTimeString()), 1000)
    return () => clearInterval(timer)
  }, [])

  const loadData = useCallback(async () => {
    try {
      const demoRes = await getDemoScenario()
      if (demoRes.data && demoRes.data.threats && demoRes.data.threats.length > 0) {
        setReport(demoRes.data)
      }
      const splunkRes = await getSplunkStatus().catch(() => ({ data: { connected: false } }))
      setSplunkConnected(splunkRes.data.connected)
    } catch (err) {
      console.log('Using offline demo data')
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const runFullScan = async () => {
    if (scanning) return
    setScanning(true)
    setShowProgress(true)
    setAgentProgress([])

    const steps = [
      { agent: 'ThreatScout', message: 'Scanning all indexes for anomalies...', delay: 800 },
      { agent: 'ThreatScout', message: '3 threats detected — severity 9, 7, 8', delay: 1600 },
      { agent: 'Investigator', message: 'Building attack timeline from 12 events...', delay: 2600 },
      { agent: 'Investigator', message: 'Attack stage identified: exfiltration', delay: 3400 },
      { agent: 'Correlator', message: 'Mapping to MITRE ATT&CK framework...', delay: 4400 },
      { agent: 'Correlator', message: '4 techniques matched — T1110, T1021, T1059, T1071', delay: 5200 },
      { agent: 'Strategist', message: 'Calculating risk score and generating playbook...', delay: 6200 },
      { agent: 'Strategist', message: 'Risk score: 91/100 — CRITICAL. Playbook ready.', delay: 7000 },
    ]

    for (const step of steps) {
      await new Promise(r => setTimeout(r, step.delay - (steps.indexOf(step) > 0 ? steps[steps.indexOf(step)-1].delay : 0)))
      setAgentProgress(prev => [...prev, step])
    }

    await loadData()
    setScanning(false)
  }

  return (
    <div className="min-h-screen bg-soc-bg text-soc-text">
      {/* Top Navigation Bar */}
      <nav className="bg-soc-surface border-b border-soc-border px-6 py-3 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <Shield className="text-soc-green" size={28} />
          <div>
            <h1 className="text-lg font-bold text-white tracking-wider">▲ ARIA</h1>
            <p className="text-xs text-soc-muted">Agentic Response & Investigation Assistant</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          {['dashboard', 'timeline', 'chat'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`capitalize text-sm px-4 py-1.5 rounded-full transition-all ${
                activeTab === tab
                  ? 'bg-soc-blue text-white'
                  : 'text-soc-muted hover:text-white'
              }`}
            >
              {tab === 'chat' ? 'Ask ARIA' : tab}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            {splunkConnected
              ? <><Wifi size={14} className="text-soc-green" /><span className="text-soc-green">Splunk Live</span></>
              : <><WifiOff size={14} className="text-soc-amber" /><span className="text-soc-amber">Demo Mode</span></>
            }
          </div>
          <span className="text-soc-muted font-mono text-xs">{currentTime}</span>
          <button
            onClick={runFullScan}
            disabled={scanning}
            className={`text-black text-xs font-bold px-4 py-1.5 rounded-full transition-all ${
              scanning 
                ? 'bg-soc-amber animate-pulse cursor-not-allowed' 
                : 'bg-soc-green hover:bg-opacity-80'
            }`}
          >
            {scanning ? 'SCANNING...' : 'RUN SCAN'}
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {showProgress && (
          <AgentProgress
            progress={agentProgress}
            scanning={scanning}
            onClose={() => setShowProgress(false)}
          />
        )}
        <>
          {activeTab === 'dashboard' && (
            <>
              <ImpactBanner riskScore={report?.risk_score || 0} threatCount={report?.threats?.length || 0} />
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className="xl:col-span-2 space-y-6">
                  <ThreatFeed threats={report?.threats || []} onRefresh={loadData} />
                </div>
                <div className="space-y-6">
                  <RiskGauge
                    riskScore={report?.risk_score || 0}
                    attackStage={report?.attack_stage || 'unknown'}
                    summary={report?.executive_summary || ''}
                  />
                </div>
              </div>
            </>
          )}
          {activeTab === 'timeline' && (
            <AttackTimeline timeline={report?.investigation?.timeline || []} correlation={report?.correlation || {}} />
          )}
          {activeTab === 'chat' && (
            <ARIAChat report={report} />
          )}
        </>
      </main>
    </div>
  )
}
