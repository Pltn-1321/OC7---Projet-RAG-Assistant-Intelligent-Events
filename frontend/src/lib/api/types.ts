// API Types - Mirroring FastAPI Pydantic models

export interface Location {
  city: string
  address?: string
  postal_code?: string
  coordinates?: {
    lat: number
    lon: number
  }
}

export interface DateRange {
  start: string // ISO 8601 date
  end: string   // ISO 8601 date
}

export interface Event {
  title: string
  description: string
  location: Location
  date_range: DateRange
  category?: string
  price?: number
  is_free?: boolean
  url?: string
  image_url?: string
}

// Search Request/Response
export interface SearchRequest {
  query: string
  top_k?: number // 1-20, default 5
}

export interface DocumentResult {
  title: string
  content: string
  metadata: Record<string, unknown>
  similarity: number  // 0-1
  distance: number    // L2 distance
}

export interface SearchResponse {
  results: DocumentResult[]
  query: string
}

// Chat Request/Response
export interface ChatRequest {
  query: string
  session_id?: string
  top_k?: number // 1-20, default 5
}

export interface ChatResponse {
  response: string
  sources: DocumentResult[]
  query: string
  session_id: string
}

// Session Management
export interface Message {
  role: "user" | "assistant"
  content: string
}

export interface SessionResponse {
  session_id: string
  history: Message[]
  created_at: string
  updated_at: string
}

// Health Check
export interface HealthResponse {
  status: "healthy" | "unhealthy"
  document_count: number
  embedding_dimension: number
  active_sessions: number
}

// Rebuild Index - Le backend reconstruit depuis rag_documents.json existant

export interface RebuildResponse {
  status: "accepted"
  message: string
  task_id: string
}

export interface RebuildStatusResponse {
  status: "in_progress" | "completed" | "failed"
  progress?: number // 0.0-1.0
  message?: string
  documents_processed?: number
  embedding_dimension?: number
  index_vectors?: number
  elapsed_seconds?: number
  error?: string
}

// RAGAS Evaluation (to be implemented)
export interface EvaluationRequest {
  test_file?: string
}

export interface EvaluationResponse {
  status: "accepted"
  task_id: string
}

export interface QuestionResult {
  question: string
  answer: string
  latency: number
  relevance: number
  coverage: number
  success: boolean
}

export interface EvaluationMetrics {
  avg_latency: number
  avg_relevance: number
  avg_coverage: number
  success_rate: number
}

export interface EvaluationReport {
  timestamp: string
  metrics: EvaluationMetrics
  questions: QuestionResult[]
}

export interface EvaluationStatusResponse {
  status: "in_progress" | "completed" | "failed"
  progress?: number
  result?: EvaluationReport
  error?: string
}

// API Error Response
export interface APIError {
  detail: string
  status_code: number
}
