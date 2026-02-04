import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Section = 'chat' | 'api-explorer' | 'ragas' | 'monitoring' | 'index'

interface AppState {
  // Active section in sidebar
  activeSection: Section
  setActiveSection: (section: Section) => void

  // Sidebar collapsed state (for mobile)
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void

  // Theme (future: dark mode support)
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      activeSection: 'chat',
      sidebarCollapsed: false,
      theme: 'light',

      // Actions
      setActiveSection: (section) => set({ activeSection: section }),

      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'app-storage', // LocalStorage key
      partialize: (state) => ({
        activeSection: state.activeSection,
        theme: state.theme,
        // Don't persist sidebarCollapsed (should reset on page load)
      }),
    }
  )
)
