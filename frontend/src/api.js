import axios from 'axios'

const DEFAULT_API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: DEFAULT_API,
  timeout: 30000,
})

export const getHealthCheck = () => api.get('/')
export const getDemoScenario = () => api.get('/api/v1/demo/run-scenario')
export const getDemoThreats = () => api.get('/api/v1/demo/threats')
export const getSplunkStatus = () => api.get('/api/v1/splunk/status')
export const getAgentStatus = () => api.get('/api/v1/agents/status')
export const runAgents = () => api.post('/api/v1/agents/run')
export const getIncidents = () => api.get('/api/v1/incidents/')
export const sendChatMessage = (message) => api.post('/api/v1/chat/', { message })

export default api
