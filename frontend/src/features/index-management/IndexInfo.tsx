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
import { getErrorMessage } from '@/lib/api/error-types'
import {
  Database,
  Layers,
  Cpu,
  RefreshCw,
  AlertCircle,
  Users,
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
    staleTime: 30000,
    retry: 1,
  })

  if (error) {
    return (
      <Card className="border-destructive/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive text-lg">
            <AlertCircle className="h-5 w-5" />
            Erreur de connexion
          </CardTitle>
          <CardDescription>
            Impossible de récupérer les informations de l'index
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            {getErrorMessage(error, "L'API backend est peut-être inaccessible.")}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
            Réessayer
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Database className="h-5 w-5 text-primary" />
              Index FAISS Actuel
            </CardTitle>
            <CardDescription>
              Informations sur l'index vectoriel en production
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            {health && (
              <Badge variant={health.status === 'healthy' ? 'success' : 'destructive'}>
                {health.status === 'healthy' ? 'Opérationnel' : 'Dégradé'}
              </Badge>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => refetch()}
              disabled={isFetching}
              className="h-8 w-8"
            >
              <RefreshCw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 rounded-lg bg-muted animate-pulse">
                <div className="h-3 w-20 bg-muted-foreground/20 rounded mb-3" />
                <div className="h-7 w-16 bg-muted-foreground/20 rounded mb-2" />
                <div className="h-3 w-24 bg-muted-foreground/20 rounded" />
              </div>
            ))}
          </div>
        ) : health ? (
          <div className="space-y-4">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard
                icon={<Layers className="h-4 w-4" />}
                iconColor="text-primary"
                label="Documents"
                value={(health.document_count ?? 0).toLocaleString()}
                detail="événements indexés"
              />
              <StatCard
                icon={<Cpu className="h-4 w-4" />}
                iconColor="text-accent"
                label="Dimensions"
                value={String(health.embedding_dimension ?? 1024)}
                detail="Mistral Embeddings"
              />
              <StatCard
                icon={<Users className="h-4 w-4" />}
                iconColor="text-destructive"
                label="Sessions"
                value={String(health.active_sessions ?? 0)}
                detail="sessions actives"
              />
            </div>

            {/* Provider Info */}
            <div className="flex items-center gap-2 pt-3 border-t">
              <span className="text-xs text-muted-foreground">Fournisseur d'embeddings :</span>
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

function StatCard({
  icon,
  iconColor,
  label,
  value,
  detail,
}: {
  icon: React.ReactNode
  iconColor: string
  label: string
  value: string
  detail: string
}) {
  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
        <span className={iconColor}>{icon}</span>
        {label}
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="text-xs text-muted-foreground mt-1">{detail}</p>
    </div>
  )
}
