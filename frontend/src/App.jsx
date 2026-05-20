import { useState, useEffect } from 'react'
import { Shield, Activity, AlertTriangle, Terminal, Wifi, WifiOff } from 'lucide-react'
import ThreatFeed from './components/ThreatFeed'
import RiskGauge from './components/RiskGauge'
import AttackTimeline from './components/AttackTimeline'
import ARIAChat from './components/ARIAChat'
import { getHealthCheck, getDemoScenario, getSplunkStatus } from './api'

export default function App() {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [splunkConnected, setSplunkConnected] = useState(false)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date().toLocaleTimeString()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [demoRes, splunkRes] = await Promise.all([
        getDemoScenario(),
        getSplunkStatus().catch(() => ({ data: { connected: false } }))
      ])
      setReport(demoRes.data)
      setSplunkConnected(splunkRes.data.connected)
    } catch (err) {
      console.error('Failed to load data:', err)
    }
    setLoading(false)
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
            onClick={loadData}
            className="bg-soc-green text-black text-xs font-bold px-4 py-1.5 rounded-full hover:bg-opacity-80 transition-all"
          >
            RUN SCAN
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <Activity className="text-soc-green mx-auto mb-4 animate-pulse" size={48} />
              <p className="text-soc-green font-mono">ARIA scanning for threats...</p>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && (
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
            )}
            {activeTab === 'timeline' && (
              <AttackTimeline timeline={report?.investigation?.timeline || []} correlation={report?.correlation || {}} />
            )}
            {activeTab === 'chat' && (
              <ARIAChat report={report} />
            )}
          </>
        )}
      </main>
    </div>
  )
}
