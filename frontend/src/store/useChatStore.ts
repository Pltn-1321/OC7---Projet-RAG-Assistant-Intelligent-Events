import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ChatState {
  // Current session ID
  sessionId: string | null
  setSessionId: (id: string | null) => void

  // Top-k parameter for RAG retrieval
  topK: number
  setTopK: (k: number) => void

  // Clear session
  clearSession: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      // Initial state
      sessionId: null,
      topK: 5,

      // Actions
      setSessionId: (id) => set({ sessionId: id }),

      setTopK: (k) => set({ topK: Math.max(1, Math.min(20, k)) }), // Clamp between 1-20

      clearSession: () => set({ sessionId: null }),
    }),
    {
      name: 'chat-storage', // LocalStorage key
      partialize: (state) => ({
        topK: state.topK,
        // Don't persist sessionId (sessions are in-memory on backend)
      }),
    }
  )
)
