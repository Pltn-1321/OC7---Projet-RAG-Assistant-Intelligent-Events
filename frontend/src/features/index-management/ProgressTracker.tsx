import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { getErrorMessage } from '@/lib/api/error-types'
import {
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  Cpu,
  Activity,
  X,
} from 'lucide-react'
import { useRebuildStatus } from './useRebuildStatus'

interface ProgressTrackerProps {
  taskId: string
  onClose: () => void
}

export function ProgressTracker({ taskId, onClose }: ProgressTrackerProps) {
  const queryClient = useQueryClient()
  const { data: status, isLoading, error, isFetching } = useRebuildStatus(taskId)

  const progressPercentage = status?.progress ? Math.round(status.progress * 100) : 0

  // Invalidate health query when rebuild completes
  useEffect(() => {
    if (status?.status === 'completed') {
      queryClient.invalidateQueries({ queryKey: ['health'] })
    }
  }, [status?.status, queryClient])

  const getStatusBadge = () => {
    if (!status) return null

    switch (status.status) {
      case 'in_progress':
        return (
          <Badge variant="secondary" className="bg-primary/10 text-primary">
            <Loader2 className="h-3 w-3 animate-spin mr-1" />
            En cours
          </Badge>
        )
      case 'completed':
        return (
          <Badge variant="success">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Terminé
          </Badge>
        )
      case 'failed':
        return (
          <Badge variant="destructive">
            <XCircle className="h-3 w-3 mr-1" />
            Échoué
          </Badge>
        )
      default:
        return null
    }
  }

  if (error) {
    return (
      <Card className="border-destructive/30">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-destructive flex items-center gap-2 text-lg">
              <XCircle className="h-5 w-5" />
              Erreur de suivi
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Impossible de récupérer le statut de la tâche : {taskId}
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            {getErrorMessage(error, 'Tâche introuvable ou expirée')}
          </p>
        </CardContent>
      </Card>
    )
  }

  const cardClassName =
    status?.status === 'completed'
      ? 'border-green-300 bg-green-50/50'
      : status?.status === 'failed'
        ? 'border-destructive/30'
        : ''

  return (
    <Card className={cardClassName}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Activity className="h-5 w-5 text-primary" />
              Progression de la Reconstruction
            </CardTitle>
            <CardDescription className="flex items-center gap-2">
              <span className="font-mono text-xs">{taskId}</span>
              {isFetching && status?.status === 'in_progress' && (
                <Loader2 className="h-3 w-3 animate-spin text-primary" />
              )}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {getStatusBadge()}
            {(status?.status === 'completed' || status?.status === 'failed') && (
              <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            <span className="text-sm text-muted-foreground">
              Chargement du statut...
            </span>
          </div>
        ) : status ? (
          <>
            {/* Progress Bar (only for in_progress) */}
            {status.status === 'in_progress' && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progression</span>
                  <span className="font-medium text-primary">
                    {progressPercentage}%
                  </span>
                </div>
                <Progress value={progressPercentage} className="h-2" />
                {status.message && (
                  <p className="text-xs text-muted-foreground">{status.message}</p>
                )}
              </div>
            )}

            {/* Error Display */}
            {status.status === 'failed' && status.error && (
              <div className="p-3 rounded-lg border border-destructive/30 bg-destructive/5">
                <p className="text-sm font-medium text-destructive">Erreur :</p>
                <p className="text-sm text-muted-foreground mt-1">{status.error}</p>
              </div>
            )}

            {/* Success Metrics */}
            {status.status === 'completed' && (
              <div className="space-y-4">
                {status.message && (
                  <p className="text-sm text-green-700">{status.message}</p>
                )}
                <MetricsGrid status={status} />
              </div>
            )}

            {/* In Progress Metrics */}
            {status.status === 'in_progress' && (
              <div className="grid grid-cols-2 gap-3">
                {status.documents_processed != null && (
                  <MetricTile
                    icon={<Layers className="h-3 w-3" />}
                    label="Documents traités"
                    value={status.documents_processed.toLocaleString()}
                  />
                )}
                {status.elapsed_seconds != null && (
                  <MetricTile
                    icon={<Clock className="h-3 w-3" />}
                    label="Temps écoulé"
                    value={`${status.elapsed_seconds.toFixed(1)}s`}
                  />
                )}
              </div>
            )}
          </>
        ) : null}
      </CardContent>
    </Card>
  )
}

function MetricsGrid({ status }: { status: {
  documents_processed?: number
  embedding_dimension?: number
  index_vectors?: number
  elapsed_seconds?: number
} }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {status.documents_processed != null && (
        <MetricTile
          icon={<Layers className="h-3 w-3 text-primary" />}
          label="Documents traités"
          value={status.documents_processed.toLocaleString()}
        />
      )}
      {status.embedding_dimension != null && (
        <MetricTile
          icon={<Cpu className="h-3 w-3 text-accent" />}
          label="Dimensions"
          value={String(status.embedding_dimension)}
        />
      )}
      {status.index_vectors != null && (
        <MetricTile
          icon={<Activity className="h-3 w-3 text-destructive" />}
          label="Vecteurs index"
          value={status.index_vectors.toLocaleString()}
        />
      )}
      {status.elapsed_seconds != null && (
        <MetricTile
          icon={<Clock className="h-3 w-3 text-muted-foreground" />}
          label="Temps écoulé"
          value={`${status.elapsed_seconds.toFixed(1)}s`}
        />
      )}
    </div>
  )
}

function MetricTile({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="p-3 rounded-lg border bg-muted/30">
      <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
        {icon}
        {label}
      </div>
      <p className="text-xl font-bold text-foreground">{value}</p>
    </div>
  )
}
