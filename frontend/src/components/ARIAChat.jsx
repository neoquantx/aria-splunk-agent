import { useState, useRef, useEffect } from 'react'
import { Send, Shield, User } from 'lucide-react'
import { sendChatMessage } from '../api'

const QUICK_QUESTIONS = [
  { label: '📊 Risk Score', message: 'What is the current risk score?' },
  { label: '🎯 MITRE Techniques', message: 'What MITRE ATT&CK techniques were detected?' },
  { label: '🖥️ Affected Systems', message: 'Which systems are affected?' },
  { label: '🛡️ Remediation', message: 'What actions should I take right now?' },
  { label: '📋 CISO Summary', message: 'Give me a summary suitable for the CISO' },
  { label: '⚔️ Attack Stage', message: 'What stage is the attack at?' },
]

export default function ARIAChat({ report }) {
  const [messages, setMessages] = useState([
    {
      role: 'aria',
      text: `ARIA online. I've analysed the current incident — risk score ${report?.risk_score || 0}/100, attack stage: ${report?.attack_stage || 'unknown'}. What would you like to know?`,
      agent: 'Orchestrator',
      time: new Date().toLocaleTimeString()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const userMsg = text || input.trim()
    if (!userMsg || loading) return
    setInput('')

    setMessages(prev => [...prev, {
      role: 'user',
      text: userMsg,
      time: new Date().toLocaleTimeString()
    }])

    setLoading(true)
    try {
      const res = await sendChatMessage(userMsg)
      setMessages(prev => [...prev, {
        role: 'aria',
        text: res.data.response,
        agent: res.data.agent,
        confidence: res.data.confidence,
        time: new Date().toLocaleTimeString()
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'aria',
        text: 'Connection to backend lost. Please ensure the server is running.',
        agent: 'System',
        time: new Date().toLocaleTimeString()
      }])
    }
    setLoading(false)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-soc-card border border-soc-border rounded-xl overflow-hidden">
        <div className="border-b border-soc-border px-5 py-4 flex items-center gap-3">
          <Shield className="text-soc-green" size={20} />
          <div>
            <h2 className="text-white font-semibold">Ask ARIA</h2>
            <p className="text-soc-muted text-xs">AI-powered security analyst — powered by Splunk ML</p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-soc-green animate-pulse" />
            <span className="text-soc-green text-xs">Active</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 px-5 py-3 border-b border-soc-border bg-soc-surface/50">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q.label}
              onClick={() => sendMessage(q.message)}
              disabled={loading}
              className="text-xs px-3 py-1.5 rounded-full border border-soc-border text-soc-muted hover:text-white hover:border-soc-blue transition-all disabled:opacity-50"
            >
              {q.label}
            </button>
          ))}
        </div>

        <div className="h-96 overflow-y-auto p-5 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'aria' ? 'bg-soc-green/20' : 'bg-soc-blue/20'}`}>
                {msg.role === 'aria'
                  ? <Shield size={16} className="text-soc-green" />
                  : <User size={16} className="text-soc-blue" />
                }
              </div>
              <div className={`max-w-lg ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                <div className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${msg.role === 'aria' ? 'bg-soc-surface text-soc-text' : 'bg-soc-blue/20 text-white'}`}>
                  {msg.text}
                </div>
                <div className="flex items-center gap-2 mt-1 text-xs text-soc-muted">
                  <span>{msg.time}</span>
                  {msg.agent && <span className="bg-soc-surface px-2 py-0.5 rounded font-mono">via {msg.agent}</span>}
                  {msg.confidence && <span>{Math.round(msg.confidence * 100)}% confidence</span>}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-soc-green/20 flex items-center justify-center">
                <Shield size={16} className="text-soc-green" />
              </div>
              <div className="bg-soc-surface rounded-xl px-4 py-3">
                <div className="flex gap-1">
                  {[0,1,2].map(i => (
                    <div key={i} className="w-2 h-2 rounded-full bg-soc-green animate-bounce" style={{ animationDelay: `${i * 150}ms` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-soc-border p-4">
          <div className="flex gap-3">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="Ask ARIA about threats, remediation, MITRE techniques..."
              className="flex-1 bg-soc-surface border border-soc-border rounded-lg px-4 py-2.5 text-sm text-white placeholder-soc-muted outline-none focus:border-soc-blue transition-colors"
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="bg-soc-green text-black p-2.5 rounded-lg hover:bg-opacity-80 transition-all disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
