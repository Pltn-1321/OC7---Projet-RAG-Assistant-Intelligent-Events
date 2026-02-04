import { Menu } from 'lucide-react'
import { useAppStore, type Section } from '@/store/useAppStore'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils/cn'

const sectionTitles: Record<Section, string> = {
  chat: 'Chat Conversationnel',
  'api-explorer': 'API Explorer',
  ragas: 'RAGAS Metrics',
  monitoring: 'Monitoring',
  index: 'Index Management',
}

interface HealthBadgeProps {
  isHealthy?: boolean
}

function HealthBadge({ isHealthy = true }: HealthBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-mediterranean-navy/70">Status:</span>
      <Badge
        variant={isHealthy ? 'default' : 'destructive'}
        className={cn(
          'flex items-center gap-2',
          isHealthy && 'bg-green-500 hover:bg-green-600'
        )}
      >
        <span
          className={cn(
            'w-2 h-2 rounded-full',
            isHealthy ? 'bg-white animate-pulse' : 'bg-red-200'
          )}
        />
        {isHealthy ? 'Healthy' : 'Offline'}
      </Badge>
    </div>
  )
}

export function Header() {
  const { activeSection, toggleSidebar } = useAppStore()

  return (
    <header className="sticky top-0 z-30 bg-mediterranean-sand border-b border-mediterranean-sky shadow-sm">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Left side: Menu button + App Title + Section Title */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden text-mediterranean-navy hover:bg-mediterranean-turquoise/20"
            onClick={toggleSidebar}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <span className="hidden md:block text-lg font-bold text-mediterranean-navy">
            Event AI Marseille
          </span>
          <span className="hidden md:block text-mediterranean-navy/30">|</span>
          <h2 className="text-xl font-semibold text-mediterranean-navy">
            {sectionTitles[activeSection]}
          </h2>
        </div>

        {/* Right side: Health badge */}
        <HealthBadge />
      </div>
    </header>
  )
}
