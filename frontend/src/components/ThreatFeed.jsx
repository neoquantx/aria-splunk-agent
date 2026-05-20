import { useState } from 'react'
import { AlertTriangle, Shield, Wifi, Clock, ChevronRight, RefreshCw } from 'lucide-react'

const SEVERITY_CONFIG = {
  9: { color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/30', label: 'CRITICAL' },
  8: { color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/30', label: 'HIGH' },
  7: { color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/30', label: 'HIGH' },
  6: { color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/30', label: 'MEDIUM' },
  5: { color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/30', label: 'MEDIUM' },
}

const TYPE_ICONS = {
  brute_force: '🔐',
  anomaly_detected: '🤖',
  outbound_spike: '📡',
  lateral_movement: '🔀',
  default: '⚠️'
}

export default function ThreatFeed({ threats, onRefresh }) {
  const [selected, setSelected] = useState(null)

  const getSeverityConfig = (severity) => SEVERITY_CONFIG[severity] || SEVERITY_CONFIG[5]

  return (
    <div className="bg-soc-card border border-soc-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="text-soc-red" size={20} />
          <h2 className="text-white font-semibold text-lg">Live Threat Feed</h2>
          <span className="bg-soc-red/20 text-soc-red text-xs px-2 py-0.5 rounded-full font-mono">
            {threats.length} ACTIVE
          </span>
        </div>
        <button
          onClick={onRefresh}
          className="flex items-center gap-1.5 text-soc-muted hover:text-white text-sm transition-colors"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {threats.length === 0 ? (
          <div className="text-center py-12 text-soc-muted">
            <Shield size={40} className="mx-auto mb-3 opacity-30" />
            <p>No threats detected</p>
          </div>
        ) : (
          threats.map((threat, index) => {
            const config = getSeverityConfig(threat.severity)
            const icon = TYPE_ICONS[threat.type] || TYPE_ICONS.default
            const isSelected = selected === index

            return (
              <div
                key={index}
                onClick={() => setSelected(isSelected ? null : index)}
                className={`border rounded-lg p-4 cursor-pointer transition-all animate-slide-in ${config.border} ${config.bg} hover:brightness-110`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{icon}</span>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${config.color} bg-black/30`}>
                          {config.label}
                        </span>
                        <span className="text-white font-medium text-sm capitalize">
                          {threat.type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <p className="text-soc-muted text-xs">
                        {threat.description || `Source: ${threat.src_ip || threat.dest_ip || 'unknown'}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <div className={`text-lg font-bold font-mono ${config.color}`}>
                        {threat.severity}/10
                      </div>
                      <div className="text-xs text-soc-muted">severity</div>
                    </div>
                    <ChevronRight
                      size={16}
                      className={`text-soc-muted transition-transform ${isSelected ? 'rotate-90' : ''}`}
                    />
                  </div>
                </div>

                {isSelected && (
                  <div className="mt-3 pt-3 border-t border-white/10 grid grid-cols-2 gap-2 text-xs">
                    {threat.src_ip && <div><span className="text-soc-muted">Source IP: </span><span className="text-white font-mono">{threat.src_ip}</span></div>}
                    {threat.dest_ip && <div><span className="text-soc-muted">Dest IP: </span><span className="text-white font-mono">{threat.dest_ip}</span></div>}
                    {threat.user && <div><span className="text-soc-muted">User: </span><span className="text-white font-mono">{threat.user}</span></div>}
                    {threat.count && <div><span className="text-soc-muted">Count: </span><span className="text-white font-mono">{threat.count}</span></div>}
                    {threat.time_window && <div><span className="text-soc-muted">Window: </span><span className="text-white">{threat.time_window}</span></div>}
                    {threat.affected_assets && <div><span className="text-soc-muted">Affected: </span><span className="text-white">{threat.affected_assets.join(', ')}</span></div>}
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
