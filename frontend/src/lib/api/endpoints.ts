import apiClient from './client'
import type {
  HealthResponse,
  SearchRequest,
  SearchResponse,
  ChatRequest,
  ChatResponse,
  Message,
  RebuildResponse,
  RebuildStatusResponse,
  EvaluationRequest,
  EvaluationResponse,
  EvaluationStatusResponse,
} from './types'

// Health Check
export const healthApi = {
  check: async (): Promise<HealthResponse> => {
    const { data } = await apiClient.get<HealthResponse>('/health')
    return data
  },
}

// Search (stateless semantic search)
export const searchApi = {
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const { data } = await apiClient.post<SearchResponse>('/search', request)
    return data
  },
}

// Chat (conversational with session management)
export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>('/chat', request)
    return data
  },

  getSession: async (sessionId: string): Promise<Message[]> => {
    const { data } = await apiClient.get<Message[]>(`/session/${sessionId}`)
    return data
  },

  deleteSession: async (sessionId: string): Promise<{ message: string }> => {
    const { data } = await apiClient.delete<{ message: string }>(`/session/${sessionId}`)
    return data
  },
}

// Rebuild Index (background task)
export const rebuildApi = {
  start: async (apiKey?: string): Promise<RebuildResponse> => {
    const headers = apiKey ? { 'X-API-Key': apiKey } : {}
    const { data } = await apiClient.post<RebuildResponse>('/rebuild', {}, { headers })
    return data
  },

  getStatus: async (taskId: string): Promise<RebuildStatusResponse> => {
    const { data } = await apiClient.get<RebuildStatusResponse>(`/rebuild/${taskId}`)
    return data
  },
}

// Evaluation (RAGAS metrics) - To be implemented on backend
export const evaluationApi = {
  start: async (request: EvaluationRequest = {}): Promise<EvaluationResponse> => {
    const { data } = await apiClient.post<EvaluationResponse>('/evaluate', request)
    return data
  },

  getStatus: async (taskId: string): Promise<EvaluationStatusResponse> => {
    const { data } = await apiClient.get<EvaluationStatusResponse>(`/evaluate/${taskId}`)
    return data
  },
}

// Export all APIs
export const api = {
  health: healthApi,
  search: searchApi,
  chat: chatApi,
  rebuild: rebuildApi,
  evaluation: evaluationApi,
}

export default api
