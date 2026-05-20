import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts'
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
  const data = [{ value: riskScore, fill: color }]

  return (
    <div className="space-y-4">
      <div className="bg-soc-card border border-soc-border rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="text-soc-red" size={20} />
          <h2 className="text-white font-semibold text-lg">Risk Score</h2>
        </div>

        <div className="relative h-48">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%" cy="70%"
              innerRadius="60%" outerRadius="90%"
              startAngle={180} endAngle={0}
              data={data}
            >
              <RadialBar dataKey="value" cornerRadius={8} background={{ fill: '#1a2235' }} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pb-4">
            <div className="text-5xl font-bold font-mono" style={{ color }}>{riskScore}</div>
            <div className="text-soc-muted text-sm">out of 100</div>
            <div className="text-xs font-bold mt-1 px-3 py-0.5 rounded-full" style={{ color, background: `${color}20` }}>
              {getLabel(riskScore)}
            </div>
          </div>
        </div>

        <div className="mt-2 grid grid-cols-3 gap-2">
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
