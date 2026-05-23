import { TrendingUp, Server, Users, Clock } from 'lucide-react'

export default function RiskGauge({ riskScore, attackStage, summary }) {
  const getColor = (score) => {
    if (score >= 70) return '#ff4444'
    if (score >= 40) return '#ffaa00'
    return '#00ff88'
  }

  const getLabel = (score) => {
    if (score >= 70) return 'CRITICAL'
    if (score >= 40) return 'ELEVATED'
    return 'LOW'
  }

  const color = getColor(riskScore)

  return (
    <div className="space-y-4">
      <div className="bg-soc-card border border-soc-border rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="text-soc-red" size={20} />
          <h2 className="text-white font-semibold text-lg">Risk Score</h2>
        </div>

        <div className="flex flex-col items-center py-4">
          <div
            className="relative w-48 h-48 rounded-full flex items-center justify-center"
            style={{
              background: `conic-gradient(${color} 0% ${riskScore}%, #1a2235 ${riskScore}% 100%)`,
              padding: '8px'
            }}
          >
            <div className="w-full h-full rounded-full bg-soc-card flex flex-col items-center justify-center">
              <div className="text-5xl font-bold font-mono" style={{ color }}>{riskScore}</div>
              <div className="text-soc-muted text-xs mt-1">out of 100</div>
              <div
                className="text-xs font-bold mt-2 px-3 py-0.5 rounded-full"
                style={{ color, background: `${color}25`, border: `1px solid ${color}40` }}
              >
                {getLabel(riskScore)}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 mt-2">
          {[
            { label: 'Threats', value: '3', icon: '🎯' },
            { label: 'Systems', value: '3', icon: '🖥️' },
            { label: 'Stage', value: attackStage?.replace('_', ' ') || 'N/A', icon: '📍' },
          ].map((stat) => (
            <div key={stat.label} className="bg-soc-surface rounded-lg p-2.5 text-center">
              <div className="text-lg">{stat.icon}</div>
              <div className="text-white text-sm font-bold capitalize">{stat.value}</div>
              <div className="text-soc-muted text-xs">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {summary && (
        <div className="bg-soc-card border border-red-400/20 rounded-xl p-5">
          <h3 className="text-red-400 font-semibold text-sm mb-2 flex items-center gap-2">
            <span>⚡</span> Executive Summary
          </h3>
          <p className="text-soc-text text-sm leading-relaxed">{summary}</p>
        </div>
      )}
    </div>
  )
}
