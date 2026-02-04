import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils/cn'
import { Wifi, WifiOff } from 'lucide-react'

interface HealthStatusProps {
  status: 'healthy' | 'unhealthy' | 'loading' | 'error'
  className?: string
}

export function HealthStatus({ status, className }: HealthStatusProps) {
  const isOnline = status === 'healthy'
  const isLoading = status === 'loading'
  const isError = status === 'error' || status === 'unhealthy'

  const getStatusConfig = () => {
    if (isLoading) {
      return {
        label: 'Connexion...',
        badgeClass: 'bg-mediterranean-ochre text-white border-mediterranean-ochre',
        iconClass: 'text-mediterranean-ochre',
        pulseClass: '',
        Icon: Wifi,
      }
    }
    if (isOnline) {
      return {
        label: 'En ligne',
        badgeClass: 'bg-green-600 text-white border-green-600',
        iconClass: 'text-green-600',
        pulseClass: 'animate-pulse-slow',
        Icon: Wifi,
      }
    }
    return {
      label: 'Hors ligne',
      badgeClass: 'bg-mediterranean-terracotta text-white border-mediterranean-terracotta',
      iconClass: 'text-mediterranean-terracotta',
      pulseClass: '',
      Icon: WifiOff,
    }
  }

  const config = getStatusConfig()

  return (
    <Card
      className={cn(
        'bg-white border-mediterranean-sky/30',
        className
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-mediterranean-navy/60 mb-3">
              Statut API
            </p>
            <div className="flex items-center gap-3">
              {/* Pulsing indicator dot */}
              <div className="relative">
                <div
                  className={cn(
                    'h-4 w-4 rounded-full',
                    isOnline ? 'bg-green-500' : isLoading ? 'bg-mediterranean-ochre' : 'bg-mediterranean-terracotta'
                  )}
                />
                {isOnline && (
                  <div
                    className="absolute inset-0 h-4 w-4 rounded-full bg-green-500 animate-ping opacity-75"
                  />
                )}
              </div>
              <Badge
                className={cn(
                  'text-sm px-3 py-1',
                  config.badgeClass
                )}
              >
                {config.label}
              </Badge>
            </div>
          </div>
          <div
            className={cn(
              'p-4 rounded-full',
              isOnline
                ? 'bg-green-100'
                : isLoading
                ? 'bg-mediterranean-ochre/20'
                : 'bg-mediterranean-terracotta/20',
              config.iconClass
            )}
          >
            <config.Icon className={cn('h-8 w-8', config.pulseClass)} />
          </div>
        </div>
        {isError && (
          <p className="text-xs text-mediterranean-terracotta mt-3">
            Impossible de se connecter au serveur API
          </p>
        )}
      </CardContent>
    </Card>
  )
}
