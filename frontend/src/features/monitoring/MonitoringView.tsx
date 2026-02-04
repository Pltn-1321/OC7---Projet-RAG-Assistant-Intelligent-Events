import { Database, Layers, Users, Clock, Activity, RefreshCw } from 'lucide-react'
import { useHealthPolling } from './useHealthPolling'
import { HealthStatus } from './HealthStatus'
import { MetricCard } from './MetricCard'
import { cn } from '@/lib/utils/cn'

export function MonitoringView() {
  const { data, isLoading, isError, lastUpdated, consecutiveSuccesses } = useHealthPolling({
    enabled: true,
    refetchInterval: 5000,
  })

  const getStatus = () => {
    if (isLoading && !data) return 'loading'
    if (isError) return 'error'
    return data?.status ?? 'unhealthy'
  }

  const formatLastUpdated = (date: Date | null) => {
    if (!date) return '--:--:--'
    return date.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const getEmbeddingLabel = (dimension: number | undefined) => {
    if (!dimension) return '1024 (Mistral)'
    return `${dimension} (Mistral)`
  }

  const getUptimeIndicator = (successes: number) => {
    if (successes >= 12) return { text: 'Stable (> 1 min)', direction: 'up' as const }
    if (successes >= 6) return { text: 'En cours', direction: 'neutral' as const }
    return { text: 'Initialisation', direction: 'neutral' as const }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-mediterranean-navy">
            Monitoring
          </h2>
          <p className="text-mediterranean-navy/60 mt-1">
            Surveillance en temps réel du systeme RAG
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-mediterranean-navy/50">
            <span className="mr-2">Derniere maj:</span>
            <span className="font-mono font-medium text-mediterranean-navy">
              {formatLastUpdated(lastUpdated)}
            </span>
          </div>
          <div
            className={cn(
              'flex items-center gap-1 text-xs',
              isLoading ? 'text-mediterranean-azure' : 'text-mediterranean-navy/40'
            )}
          >
            <RefreshCw className={cn('h-3 w-3', isLoading && 'animate-spin')} />
            <span>Auto-refresh 5s</span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {/* API Status - Larger Card */}
        <div className="sm:col-span-2 lg:col-span-1">
          <HealthStatus status={getStatus()} />
        </div>

        {/* Document Count */}
        <MetricCard
          icon={Database}
          label="Documents indexes"
          value={data?.document_count ?? '--'}
          iconColor="text-mediterranean-turquoise"
          isLoading={isLoading && !data}
          trend={
            data?.document_count
              ? { direction: 'neutral', text: 'Evenements disponibles' }
              : undefined
          }
        />

        {/* Embedding Dimension */}
        <MetricCard
          icon={Layers}
          label="Dimension embeddings"
          value={getEmbeddingLabel(data?.embedding_dimension)}
          iconColor="text-mediterranean-ochre"
          isLoading={isLoading && !data}
          trend={
            data?.embedding_dimension
              ? {
                  direction: 'neutral',
                  text: data.embedding_dimension === 1024 ? 'Mistral AI' : 'Sentence Transformers',
                }
              : undefined
          }
        />

        {/* Active Sessions */}
        <MetricCard
          icon={Users}
          label="Sessions actives"
          value={data?.active_sessions ?? '--'}
          iconColor="text-mediterranean-terracotta"
          isLoading={isLoading && !data}
          trend={
            data?.active_sessions !== undefined
              ? {
                  direction: data.active_sessions > 0 ? 'up' : 'neutral',
                  text: data.active_sessions > 0 ? 'Utilisateurs connectes' : 'Aucune session',
                }
              : undefined
          }
        />

        {/* Last Check Time */}
        <MetricCard
          icon={Clock}
          label="Dernier controle"
          value={formatLastUpdated(lastUpdated)}
          iconColor="text-mediterranean-azure"
          isLoading={isLoading && !data}
        />

        {/* Uptime Indicator */}
        <MetricCard
          icon={Activity}
          label="Uptime"
          value={`${consecutiveSuccesses} checks`}
          iconColor="text-green-600"
          isLoading={false}
          trend={getUptimeIndicator(consecutiveSuccesses)}
        />
      </div>

      {/* Connection Error Message */}
      {isError && (
        <div className="bg-mediterranean-terracotta/10 border border-mediterranean-terracotta/30 rounded-lg p-4">
          <p className="text-mediterranean-terracotta font-medium">
            Erreur de connexion
          </p>
          <p className="text-mediterranean-terracotta/80 text-sm mt-1">
            Impossible de se connecter au serveur API. Verifiez que le backend est demarre
            sur <code className="bg-mediterranean-terracotta/20 px-1 rounded">http://localhost:8000</code>
          </p>
        </div>
      )}
    </div>
  )
}
