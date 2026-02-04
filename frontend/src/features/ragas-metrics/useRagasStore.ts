import { create } from 'zustand'
import type { EvaluationReport } from '@/lib/api/types'

interface RagasState {
  // Loaded evaluation report
  report: EvaluationReport | null
  setReport: (report: EvaluationReport | null) => void

  // Filename of the loaded report
  filename: string | null
  setFilename: (filename: string | null) => void

  // Clear all data
  clearReport: () => void
}

export const useRagasStore = create<RagasState>()((set) => ({
  // Initial state
  report: null,
  filename: null,

  // Actions
  setReport: (report) => set({ report }),
  setFilename: (filename) => set({ filename }),

  clearReport: () => set({ report: null, filename: null }),
}))
