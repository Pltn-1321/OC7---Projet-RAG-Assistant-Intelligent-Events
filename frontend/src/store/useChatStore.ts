import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface SessionEntry {
  id: string
  title: string // first user message as preview
  createdAt: string // ISO date
}

interface ChatState {
  // Current session ID
  sessionId: string | null
  setSessionId: (id: string | null) => void

  // Top-k parameter for RAG retrieval
  topK: number
  setTopK: (k: number) => void

  // Session history (client-side index)
  sessions: SessionEntry[]
  addSession: (entry: SessionEntry) => void
  removeSession: (id: string) => void
  switchSession: (id: string) => void

  // Clear current session (start new)
  clearSession: () => void
}

const MAX_SESSIONS = 50

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      sessionId: null,
      topK: 5,
      sessions: [],

      // Actions
      setSessionId: (id) => set({ sessionId: id }),

      setTopK: (k) => set({ topK: Math.max(1, Math.min(20, k)) }),

      addSession: (entry) =>
        set((state) => {
          // Don't add duplicates
          if (state.sessions.some((s) => s.id === entry.id)) return state
          // Prepend new session, cap at MAX_SESSIONS
          const sessions = [entry, ...state.sessions].slice(0, MAX_SESSIONS)
          return { sessions }
        }),

      removeSession: (id) =>
        set((state) => ({
          sessions: state.sessions.filter((s) => s.id !== id),
          // If removing the active session, clear it
          ...(state.sessionId === id ? { sessionId: null } : {}),
        })),

      switchSession: (id) => {
        const session = get().sessions.find((s) => s.id === id)
        if (session) {
          set({ sessionId: id })
        }
      },

      clearSession: () => set({ sessionId: null }),
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        topK: state.topK,
        sessions: state.sessions,
      }),
    }
  )
)
