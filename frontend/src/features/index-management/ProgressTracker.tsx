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
          <Badge variant="secondary" className="bg-mediterranean-azure/20 text-mediterranean-turquoise">
            <Loader2 className="h-3 w-3 animate-spin mr-1" />
            En cours
          </Badge>
        )
      case 'completed':
        return (
          <Badge variant="success">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Termine
          </Badge>
        )
      case 'failed':
        return (
          <Badge variant="destructive">
            <XCircle className="h-3 w-3 mr-1" />
            Echoue
          </Badge>
        )
      default:
        return null
    }
  }

  if (error) {
    return (
      <Card className="border-red-500/30 bg-red-950/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-red-400 flex items-center gap-2">
              <XCircle className="h-5 w-5" />
              Erreur de suivi
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-300/80">
            Impossible de recuperer le statut de la tache: {taskId}
          </p>
          <p className="text-xs text-red-400/60 mt-2">
            {getErrorMessage(error, 'Tache introuvable ou expiree')}
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={
      status?.status === 'completed'
        ? 'border-green-500/30 bg-green-950/20'
        : status?.status === 'failed'
        ? 'border-red-500/30 bg-red-950/20'
        : 'border-mediterranean-azure/30 bg-mediterranean-navy/20'
    }>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-mediterranean-turquoise" />
              Progression de la Reconstruction
            </CardTitle>
            <CardDescription className="flex items-center gap-2 mt-1">
              <span className="font-mono text-xs">{taskId}</span>
              {isFetching && status?.status === 'in_progress' && (
                <Loader2 className="h-3 w-3 animate-spin text-mediterranean-turquoise" />
              )}
            </CardDescription>
          </div>
          {(status?.status === 'completed' || status?.status === 'failed') && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-mediterranean-turquoise" />
            <span className="text-sm text-muted-foreground">
              Chargement du statut...
            </span>
          </div>
        ) : status ? (
          <>
            {/* Status Badge */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Statut:</span>
              {getStatusBadge()}
            </div>

            {/* Progress Bar (only for in_progress) */}
            {status.status === 'in_progress' && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progression</span>
                  <span className="font-medium text-mediterranean-turquoise">
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
              <div className="p-3 rounded-lg bg-red-950/50 border border-red-500/30">
                <p className="text-sm font-medium text-red-300">Erreur:</p>
                <p className="text-sm text-red-300/80 mt-1">{status.error}</p>
              </div>
            )}

            {/* Success Metrics */}
            {status.status === 'completed' && (
              <div className="space-y-4">
                {status.message && (
                  <p className="text-sm text-green-300">{status.message}</p>
                )}

                <div className="grid grid-cols-2 gap-3">
                  {status.documents_processed !== undefined && (
                    <div className="p-3 rounded-lg bg-mediterranean-navy/40 border border-mediterranean-azure/20">
                      <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                        <Layers className="h-3 w-3 text-mediterranean-turquoise" />
                        Documents traites
                      </div>
                      <p className="text-xl font-bold text-mediterranean-sky">
                        {status.documents_processed.toLocaleString()}
                      </p>
                    </div>
                  )}

                  {status.embedding_dimension !== undefined && (
                    <div className="p-3 rounded-lg bg-mediterranean-navy/40 border border-mediterranean-azure/20">
                      <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                        <Cpu className="h-3 w-3 text-mediterranean-ochre" />
                        Dimensions
                      </div>
                      <p className="text-xl font-bold text-mediterranean-sky">
                        {status.embedding_dimension}
                      </p>
                    </div>
                  )}

                  {status.index_vectors !== undefined && (
                    <div className="p-3 rounded-lg bg-mediterranean-navy/40 border border-mediterranean-azure/20">
                      <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                        <Activity className="h-3 w-3 text-mediterranean-terracotta" />
                        Vecteurs index
                      </div>
                      <p className="text-xl font-bold text-mediterranean-sky">
                        {status.index_vectors.toLocaleString()}
                      </p>
                    </div>
                  )}

                  {status.elapsed_seconds !== undefined && (
                    <div className="p-3 rounded-lg bg-mediterranean-navy/40 border border-mediterranean-azure/20">
                      <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                        <Clock className="h-3 w-3 text-mediterranean-sand" />
                        Temps ecoule
                      </div>
                      <p className="text-xl font-bold text-mediterranean-sky">
                        {status.elapsed_seconds.toFixed(1)}s
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* In Progress Metrics */}
            {status.status === 'in_progress' && (
              <div className="grid grid-cols-2 gap-3">
                {status.documents_processed !== undefined && (
                  <div className="p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                      <Layers className="h-3 w-3" />
                      Documents traites
                    </div>
                    <p className="text-lg font-semibold">
                      {status.documents_processed.toLocaleString()}
                    </p>
                  </div>
                )}

                {status.elapsed_seconds !== undefined && (
                  <div className="p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
                      <Clock className="h-3 w-3" />
                      Temps ecoule
                    </div>
                    <p className="text-lg font-semibold">
                      {status.elapsed_seconds.toFixed(1)}s
                    </p>
                  </div>
                )}
              </div>
            )}
          </>
        ) : null}
      </CardContent>
    </Card>
  )
}
