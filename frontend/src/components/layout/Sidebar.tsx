import { MessageSquare, Wrench, BarChart3, Activity, Database, X } from 'lucide-react'
import { useAppStore, type Section } from '@/store/useAppStore'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils/cn'

interface NavItem {
  id: Section
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const navigationItems: NavItem[] = [
  { id: 'chat', label: 'Chat Conversationnel', icon: MessageSquare },
  { id: 'api-explorer', label: 'API Explorer', icon: Wrench },
  { id: 'ragas', label: 'RAGAS Metrics', icon: BarChart3 },
  { id: 'monitoring', label: 'Monitoring', icon: Activity },
  { id: 'index', label: 'Index Management', icon: Database },
]

export function Sidebar() {
  const { activeSection, setActiveSection, sidebarCollapsed, toggleSidebar } = useAppStore()

  const handleNavClick = (section: Section) => {
    setActiveSection(section)
    // Auto-close sidebar on mobile after navigation
    if (window.innerWidth < 768) {
      toggleSidebar()
    }
  }

  return (
    <>
      {/* Mobile Overlay */}
      {!sidebarCollapsed && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 h-full z-50 transition-transform duration-300',
          'bg-gradient-to-b from-mediterranean-navy to-mediterranean-azure',
          'w-64 md:w-64 md:translate-x-0',
          sidebarCollapsed ? '-translate-x-full' : 'translate-x-0'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-mediterranean-turquoise to-mediterranean-ochre rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-white font-semibold text-lg">Events AI</h1>
                <p className="text-mediterranean-sky text-xs">RAG Assistant</p>
              </div>
            </div>
            {/* Close button for mobile */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden text-white hover:bg-mediterranean-turquoise/30"
              onClick={toggleSidebar}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          <Separator className="bg-mediterranean-turquoise/30" />

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = activeSection === item.id

              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={cn(
                    'w-full flex items-center gap-3 px-4 py-3 rounded-lg',
                    'transition-all duration-200 text-left',
                    'hover:bg-mediterranean-turquoise/30',
                    isActive && [
                      'bg-mediterranean-turquoise',
                      'border-l-4 border-mediterranean-ochre',
                      'shadow-lg',
                    ]
                  )}
                >
                  <Icon
                    className={cn(
                      'w-5 h-5 flex-shrink-0',
                      isActive ? 'text-white' : 'text-mediterranean-sky'
                    )}
                  />
                  <span
                    className={cn(
                      'text-sm font-medium',
                      isActive ? 'text-white' : 'text-mediterranean-sky'
                    )}
                  >
                    {item.label}
                  </span>
                </button>
              )
            })}
          </nav>

          <Separator className="bg-mediterranean-turquoise/30" />

          {/* Footer */}
          <div className="p-4">
            <div className="bg-mediterranean-navy/50 rounded-lg p-3 border border-mediterranean-turquoise/20">
              <p className="text-xs text-mediterranean-sky mb-1">Version</p>
              <p className="text-sm text-white font-mono">1.0.0</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Spacer for desktop layout */}
      <div className="hidden md:block md:w-64 flex-shrink-0" />
    </>
  )
}
