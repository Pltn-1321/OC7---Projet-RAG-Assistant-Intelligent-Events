import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAppStore } from '@/store/useAppStore'
import { AppLayout } from '@/components/layout/AppLayout'
import { ChatView } from '@/features/chat/ChatView'
import { ApiExplorerView } from '@/features/api-explorer/ApiExplorerView'
import { RagasView } from '@/features/ragas-metrics/RagasView'
import { MonitoringView } from '@/features/monitoring/MonitoringView'
import { IndexManagementView } from '@/features/index-management/IndexManagementView'

// Create a client for TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function AppContent() {
  const { activeSection } = useAppStore()

  // Render the appropriate view based on active section
  const renderSection = () => {
    switch (activeSection) {
      case 'chat':
        return <ChatView />
      case 'api-explorer':
        return <ApiExplorerView />
      case 'ragas':
        return <RagasView />
      case 'monitoring':
        return <MonitoringView />
      case 'index':
        return <IndexManagementView />
      default:
        return <ChatView />
    }
  }

  return <AppLayout>{renderSection()}</AppLayout>
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}

export default App
