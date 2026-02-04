import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api/endpoints'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Database,
  Layers,
  Cpu,
  RefreshCw,
  AlertCircle,
} from 'lucide-react'

export function IndexInfo() {
  const {
    data: health,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.health.check(),
    staleTime: 30000, // Cache for 30 seconds
    retry: 1,
  })

  if (error) {
    return (
      <Card className="border-red-500/30 bg-red-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-400">
            <AlertCircle className="h-5 w-5" />
            Erreur de connexion
          </CardTitle>
          <CardDescription className="text-red-300/70">
            Impossible de recuperer les informations de l'index
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-300/80 mb-4">
            {(error as any)?.message || "L'API backend est peut-etre inaccessible."}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
            className="border-red-500/30 hover:bg-red-950/30"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
            Reessayer
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-mediterranean-azure" />
              Index FAISS Actuel
            </CardTitle>
            <CardDescription>
              Informations sur l'index vectoriel en production
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 rounded-lg bg-muted animate-pulse">
                <div className="h-4 w-20 bg-muted-foreground/20 rounded mb-2" />
                <div className="h-8 w-16 bg-muted-foreground/20 rounded" />
              </div>
            ))}
          </div>
        ) : health ? (
          <div className="space-y-4">
            {/* Status Badge */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Statut:</span>
              <Badge
                variant={health.status === 'healthy' ? 'success' : 'destructive'}
              >
                {health.status === 'healthy' ? 'Operationnel' : 'Degraded'}
              </Badge>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Document Count */}
              <div className="p-4 rounded-lg bg-mediterranean-navy/30 border border-mediterranean-azure/20">
                <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
                  <Layers className="h-4 w-4 text-mediterranean-turquoise" />
                  Documents
                </div>
                <p className="text-2xl font-bold text-mediterranean-sky">
                  {(health.document_count ?? 0).toLocaleString()}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  evenements indexes
                </p>
              </div>

              {/* Embedding Dimension */}
              <div className="p-4 rounded-lg bg-mediterranean-navy/30 border border-mediterranean-azure/20">
                <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
                  <Cpu className="h-4 w-4 text-mediterranean-ochre" />
                  Dimensions
                </div>
                <p className="text-2xl font-bold text-mediterranean-sky">
                  {health.embedding_dimension ?? 1024}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Mistral Embeddings
                </p>
              </div>

              {/* Active Sessions */}
              <div className="p-4 rounded-lg bg-mediterranean-navy/30 border border-mediterranean-azure/20">
                <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
                  <Database className="h-4 w-4 text-mediterranean-terracotta" />
                  Sessions
                </div>
                <p className="text-2xl font-bold text-mediterranean-sky">
                  {health.active_sessions ?? 0}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  sessions actives
                </p>
              </div>
            </div>

            {/* Provider Info */}
            <div className="flex items-center gap-2 pt-2 border-t border-border/50">
              <span className="text-xs text-muted-foreground">Fournisseur d'embeddings:</span>
              <Badge variant="outline" className="text-xs">
                mistral-embed
              </Badge>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
