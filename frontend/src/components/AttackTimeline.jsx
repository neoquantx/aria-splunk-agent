const TACTIC_CONFIG = {
  failed_ssh: { color: '#ffaa00', bg: '#ffaa0015', label: 'Brute Force', mitre: 'T1110' },
  successful_ssh: { color: '#ff4444', bg: '#ff444415', label: 'Initial Access', mitre: 'T1078' },
  command_execution: { color: '#ff4444', bg: '#ff444415', label: 'Execution', mitre: 'T1059' },
  lateral_ssh: { color: '#f97316', bg: '#f9731615', label: 'Lateral Movement', mitre: 'T1021' },
  c2_contact: { color: '#8b5cf6', bg: '#8b5cf615', label: 'C2', mitre: 'T1071' },
  staging: { color: '#8b5cf6', bg: '#8b5cf615', label: 'Pre-Exfiltration', mitre: 'T1074' },
  large_file_transfer: { color: '#ec4899', bg: '#ec489915', label: 'Exfiltration', mitre: 'T1041' },
  default: { color: '#64748b', bg: '#64748b15', label: 'Event', mitre: '' },
}

export default function AttackTimeline({ timeline, correlation }) {
  const mitreMap = {}
  correlation?.mitre_techniques?.forEach(t => {
    if (t.technique_id) mitreMap[t.technique_id] = t
  })

  return (
    <div className="space-y-6">
      <div className="bg-soc-card border border-soc-border rounded-xl p-5">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <span className="text-xl">🕐</span>
            <h2 className="text-white font-semibold text-lg">Attack Timeline</h2>
            <span className="bg-purple-500/20 text-purple-400 text-xs px-2 py-0.5 rounded-full">
              {timeline.length} events
            </span>
          </div>
          {correlation?.is_coordinated && (
            <span className="bg-red-500/20 text-red-400 text-xs px-3 py-1 rounded-full border border-red-500/30 font-bold">
              ⚠️ COORDINATED ATTACK
            </span>
          )}
        </div>

        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-soc-border" />
          <div className="space-y-4">
            {timeline.map((event, index) => {
              const config = TACTIC_CONFIG[event.event_type] || TACTIC_CONFIG.default
              const time = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''

              return (
                <div key={index} className="relative flex gap-4 pl-14 animate-slide-in" style={{ animationDelay: `${index * 80}ms` }}>
                  <div
                    className="absolute left-3.5 w-5 h-5 rounded-full border-2 flex items-center justify-center"
                    style={{ borderColor: config.color, background: config.bg, top: '12px' }}
                  >
                    <div className="w-2 h-2 rounded-full" style={{ background: config.color }} />
                  </div>

                  <div className="flex-1 rounded-lg border p-3.5" style={{ borderColor: `${config.color}30`, background: config.bg }}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span className="text-xs font-bold px-2 py-0.5 rounded" style={{ color: config.color, background: `${config.color}20` }}>
                            {config.label}
                          </span>
                          {config.mitre && (
                            <span className="text-xs text-soc-muted font-mono bg-soc-surface px-2 py-0.5 rounded">
                              {config.mitre}
                            </span>
                          )}
                        </div>
                        <p className="text-white text-sm capitalize">{event.event_type?.replace(/_/g, ' ')}</p>
                        <div className="flex gap-3 mt-1 text-xs text-soc-muted flex-wrap">
                          {event.src && <span>From: <span className="text-soc-text font-mono">{event.src}</span></span>}
                          {event.dest && <span>To: <span className="text-soc-text font-mono">{event.dest}</span></span>}
                          {event.action && <span>Action: <span className="text-soc-text">{event.action}</span></span>}
                          {event.user && <span>User: <span className="text-soc-text font-mono">{event.user}</span></span>}
                        </div>
                      </div>
                      <span className="text-soc-muted text-xs font-mono whitespace-nowrap">{time}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {correlation?.mitre_techniques?.length > 0 && (
        <div className="bg-soc-card border border-purple-500/20 rounded-xl p-5">
          <h3 className="text-purple-400 font-semibold mb-3 flex items-center gap-2">
            <span>🎯</span> MITRE ATT&CK Techniques Detected
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {correlation.mitre_techniques.map((t, i) => (
              <div key={i} className="bg-soc-surface rounded-lg p-3 border border-purple-500/10">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-purple-400 text-sm font-bold">{t.technique_id}</span>
                  <span className="text-white text-sm">{t.technique_name}</span>
                </div>
                <span className="text-xs text-soc-muted bg-soc-card px-2 py-0.5 rounded">{t.tactic}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
