import { Sidebar } from './Sidebar'
import { Header } from './Header'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-mediterranean-sand via-white to-mediterranean-sky/10">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="flex flex-col h-screen md:ml-64">
        {/* Header */}
        <Header />

        {/* Page content */}
        <main className="flex-1 overflow-hidden px-6 py-4">
          {children}
        </main>

        {/* Footer (optional) */}
        <footer className="border-t border-mediterranean-sky/30 bg-white/50 backdrop-blur-sm">
          <div className="container mx-auto px-6 py-4">
            <p className="text-center text-sm text-mediterranean-navy/60">
              Events AI RAG Assistant - Powered by Mistral AI & FAISS
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}
