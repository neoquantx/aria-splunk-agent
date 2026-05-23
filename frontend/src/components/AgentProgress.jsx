import { X, CheckCircle, Loader } from 'lucide-react'

const AGENT_CONFIG = {
  ThreatScout: { icon: '🔍', color: 'text-red-400', border: 'border-red-400/30', bg: 'bg-red-400/10' },
  Investigator: { icon: '🕵️', color: 'text-amber-400', border: 'border-amber-400/30', bg: 'bg-amber-400/10' },
  Correlator:   { icon: '🔗', color: 'text-purple-400', border: 'border-purple-400/30', bg: 'bg-purple-400/10' },
  Strategist:   { icon: '🛡️', color: 'text-green-400', border: 'border-green-400/30', bg: 'bg-green-400/10' },
}

const ALL_AGENTS = ['ThreatScout', 'Investigator', 'Correlator', 'Strategist']

export default function AgentProgress({ progress, scanning, onClose }) {
  const agentMessages = {}
  progress.forEach(p => {
    if (!agentMessages[p.agent]) agentMessages[p.agent] = []
    agentMessages[p.agent].push(p.message)
  })

  const activeAgent = scanning && progress.length > 0
    ? progress[progress.length - 1].agent
    : null

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-soc-card border border-soc-border rounded-xl w-full max-w-2xl p-6">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-soc-green animate-pulse" />
            <h2 className="text-white font-bold text-lg">
              {scanning ? 'ARIA Investigation Running...' : 'Investigation Complete'}
            </h2>
          </div>
          {!scanning && (
            <button onClick={onClose} className="text-soc-muted hover:text-white transition-colors">
              <X size={20} />
            </button>
          )}
        </div>

        <div className="space-y-3">
          {ALL_AGENTS.map((agentName) => {
            const config = AGENT_CONFIG[agentName]
            const messages = agentMessages[agentName] || []
            const isActive = activeAgent === agentName
            const isDone = !scanning || (progress.length > 0 && 
              ALL_AGENTS.indexOf(agentName) < ALL_AGENTS.indexOf(activeAgent))
            const isPending = !messages.length && !isActive

            return (
              <div
                key={agentName}
                className={`border rounded-xl p-4 transition-all duration-300 ${
                  isActive ? `${config.border} ${config.bg}` :
                  isDone ? 'border-green-400/20 bg-green-400/5' :
                  'border-soc-border bg-soc-surface'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xl">{config.icon}</span>
                  <span className={`font-bold text-sm ${isPending ? 'text-soc-muted' : 'text-white'}`}>
                    {agentName}
                  </span>
                  <div className="ml-auto">
                    {isActive && <Loader size={16} className={`${config.color} animate-spin`} />}
                    {isDone && <CheckCircle size={16} className="text-green-400" />}
                    {isPending && <div className="w-4 h-4 rounded-full border border-soc-border" />}
                  </div>
                </div>

                {messages.length > 0 && (
                  <div className="space-y-1 pl-9">
                    {messages.map((msg, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className="text-soc-green text-xs mt-0.5">›</span>
                        <p className={`text-xs ${i === messages.length - 1 ? 'text-soc-text' : 'text-soc-muted'}`}>
                          {msg}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {isPending && (
                  <p className="text-soc-muted text-xs pl-9">Waiting...</p>
                )}
              </div>
            )
          })}
        </div>

        {!scanning && (
          <button
            onClick={onClose}
            className="w-full mt-4 bg-soc-green text-black font-bold py-2.5 rounded-lg hover:bg-opacity-80 transition-all"
          >
            View Results →
          </button>
        )}
      </div>
    </div>
  )
}
