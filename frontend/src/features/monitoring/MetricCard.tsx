import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils/cn'
import type { LucideIcon } from 'lucide-react'

export type TrendDirection = 'up' | 'down' | 'neutral'

interface MetricCardProps {
  icon: LucideIcon
  label: string
  value: string | number
  trend?: {
    direction: TrendDirection
    text: string
  }
  iconColor?: string
  className?: string
  isLoading?: boolean
}

export function MetricCard({
  icon: Icon,
  label,
  value,
  trend,
  iconColor = 'text-mediterranean-azure',
  className,
  isLoading = false,
}: MetricCardProps) {
  const getTrendColor = (direction: TrendDirection) => {
    switch (direction) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-mediterranean-terracotta'
      default:
        return 'text-mediterranean-navy/50'
    }
  }

  const getTrendIcon = (direction: TrendDirection) => {
    switch (direction) {
      case 'up':
        return '\u2191'
      case 'down':
        return '\u2193'
      default:
        return '\u2192'
    }
  }

  return (
    <Card
      className={cn(
        'bg-white border-mediterranean-sky/30 hover:border-mediterranean-azure/50 transition-colors',
        className
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-mediterranean-navy/60 mb-1">
              {label}
            </p>
            {isLoading ? (
              <div className="h-8 w-20 bg-mediterranean-sky/30 animate-pulse rounded" />
            ) : (
              <p className="text-3xl font-bold text-mediterranean-navy">
                {value}
              </p>
            )}
            {trend && !isLoading && (
              <p className={cn('text-xs mt-2', getTrendColor(trend.direction))}>
                <span className="mr-1">{getTrendIcon(trend.direction)}</span>
                {trend.text}
              </p>
            )}
          </div>
          <div
            className={cn(
              'p-3 rounded-full bg-mediterranean-sky/20',
              iconColor
            )}
          >
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
