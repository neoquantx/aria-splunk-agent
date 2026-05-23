import { useEffect, useState } from 'react'
import { Zap, Clock, TrendingDown, Award } from 'lucide-react'

export default function ImpactBanner({ riskScore, threatCount }) {
  const [secondsCount, setSecondsCount] = useState(0)
  const targetSeconds = 12
  const minutesSaved = 58

  useEffect(() => {
    let count = 0
    const timer = setInterval(() => {
      count++
      setSecondsCount(count)
      if (count >= targetSeconds) clearInterval(timer)
    }, 80)
    return () => clearInterval(timer)
  }, [])

  const stats = [
    {
      icon: <Clock size={18} className="text-soc-green" />,
      value: `${secondsCount}s`,
      label: 'Investigation time',
      sub: 'vs 60+ min manually',
      color: 'text-soc-green'
    },
    {
      icon: <TrendingDown size={18} className="text-soc-amber" />,
      value: `${minutesSaved} min`,
      label: 'Analyst time saved',
      sub: 'per incident',
      color: 'text-soc-amber'
    },
    {
      icon: <Zap size={18} className="text-soc-blue" />,
      value: `${threatCount || 3}`,
      label: 'Threats correlated',
      sub: 'across 4 AI agents',
      color: 'text-soc-blue'
    },
    {
      icon: <Award size={18} className="text-purple-400" />,
      value: '4',
      label: 'MITRE techniques',
      sub: 'auto-mapped',
      color: 'text-purple-400'
    },
  ]

  return (
    <div className="bg-gradient-to-r from-soc-surface via-soc-card to-soc-surface border border-soc-green/20 rounded-xl p-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Zap className="text-soc-green" size={16} />
        <span className="text-soc-green text-xs font-bold tracking-widest uppercase">
          ARIA Investigation Complete
        </span>
        <div className="flex-1 h-px bg-soc-green/20" />
        <span className="text-soc-muted text-xs">
          Powered by Splunk ML Toolkit + 4 AI Agents
        </span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {stats.map((stat, i) => (
          <div
            key={i}
            className="bg-soc-bg rounded-lg p-3 border border-soc-border flex items-start gap-3"
          >
            <div className="mt-0.5">{stat.icon}</div>
            <div>
              <div className={`text-xl font-bold font-mono ${stat.color}`}>
                {stat.value}
              </div>
              <div className="text-white text-xs font-medium">{stat.label}</div>
              <div className="text-soc-muted text-xs">{stat.sub}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
