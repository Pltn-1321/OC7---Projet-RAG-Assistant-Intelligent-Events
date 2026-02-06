import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/lib/api/endpoints'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getErrorMessage } from '@/lib/api/error-types'
import {
  RefreshCw,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from 'lucide-react'

const rebuildSchema = z.object({
  apiKey: z.string().optional(),
})

type RebuildFormData = z.infer<typeof rebuildSchema>

interface RebuildFormProps {
  onRebuildStarted: (taskId: string) => void
}

export function RebuildForm({ onRebuildStarted }: RebuildFormProps) {
  const {
    register,
    handleSubmit,
  } = useForm<RebuildFormData>({
    resolver: zodResolver(rebuildSchema),
    defaultValues: {
      apiKey: '',
    },
  })

  const rebuildMutation = useMutation({
    mutationFn: ({ apiKey }: { apiKey?: string }) =>
      api.rebuild.start(apiKey || undefined),
    onSuccess: (data) => {
      onRebuildStarted(data.task_id)
    },
  })

  const onSubmit = (data: RebuildFormData) => {
    rebuildMutation.mutate({ apiKey: data.apiKey })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <RefreshCw className="h-5 w-5 text-primary" />
          Reconstruire l'Index
        </CardTitle>
        <CardDescription>
          Reconstruit l'index FAISS à partir des documents existants (rag_documents.json)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Warning Note */}
        <div className="mb-5 p-3 rounded-lg border border-accent/40 bg-accent/5">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0 text-accent" />
            <div className="text-sm">
              <p className="font-medium text-foreground">Note importante</p>
              <p className="text-muted-foreground mt-1">
                La reconstruction utilise le fichier{' '}
                <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">
                  rag_documents.json
                </code>{' '}
                déjà présent sur le serveur. Pour mettre à jour les données
                sources, utilisez les notebooks Jupyter.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* API Key */}
          <div className="space-y-2">
            <Label htmlFor="apiKey">Clé API (X-API-Key)</Label>
            <Input
              id="apiKey"
              type="password"
              placeholder="Requis si REBUILD_API_KEY est configuré sur le backend"
              {...register('apiKey')}
            />
            <p className="text-xs text-muted-foreground">
              Clé d'authentification pour l'endpoint de reconstruction
            </p>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={rebuildMutation.isPending}
            className="w-full"
          >
            {rebuildMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Démarrage en cours...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Démarrer la Reconstruction
              </>
            )}
          </Button>

          {/* Error Display */}
          {rebuildMutation.error && (
            <div className="p-4 rounded-lg border border-destructive/30 bg-destructive/5">
              <div className="flex items-start gap-2">
                <XCircle className="h-4 w-4 mt-0.5 shrink-0 text-destructive" />
                <div>
                  <p className="font-semibold text-sm text-destructive">Erreur</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {getErrorMessage(rebuildMutation.error, 'Échec du démarrage de la reconstruction')}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Success Display */}
          {rebuildMutation.data && (
            <div className="p-4 rounded-lg border border-green-300 bg-green-50">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 mt-0.5 shrink-0 text-green-600" />
                <div>
                  <p className="font-semibold text-sm text-green-800">
                    Reconstruction démarrée
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    {rebuildMutation.data.message}
                  </p>
                  <div className="mt-2">
                    <Label className="text-xs text-green-700">Task ID</Label>
                    <code className="block mt-1 p-2 bg-green-100 rounded text-xs font-mono text-green-800">
                      {rebuildMutation.data.task_id}
                    </code>
                  </div>
                </div>
              </div>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}
