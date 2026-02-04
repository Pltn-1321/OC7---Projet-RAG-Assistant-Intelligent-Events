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
import { RefreshCw, Loader2, AlertTriangle } from 'lucide-react'

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
        <CardTitle className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5 text-mediterranean-turquoise" />
          Reconstruire l'Index
        </CardTitle>
        <CardDescription>
          Reconstruit l'index FAISS à partir des documents existants (rag_documents.json)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 p-3 rounded-lg bg-amber-950/30 border border-amber-500/30 text-amber-300">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
            <div className="text-sm">
              <p className="font-medium">Note importante</p>
              <p className="text-amber-300/80 mt-1">
                La reconstruction utilise le fichier <code className="bg-amber-950 px-1 rounded">rag_documents.json</code> déjà présent sur le serveur.
                Pour mettre à jour les données sources, utilisez les notebooks Jupyter.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
            className="w-full bg-mediterranean-azure hover:bg-mediterranean-turquoise"
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
            <div className="p-4 rounded-lg bg-red-950/30 border border-red-500/30 text-red-300">
              <p className="font-semibold text-sm">Erreur</p>
              <p className="text-sm mt-1">
                {(rebuildMutation.error as any)?.detail ||
                  (rebuildMutation.error as any)?.message ||
                  'Échec du démarrage de la reconstruction'}
              </p>
            </div>
          )}

          {/* Success Display */}
          {rebuildMutation.data && (
            <div className="p-4 rounded-lg bg-green-950/30 border border-green-500/30 text-green-300">
              <p className="font-semibold text-sm">Reconstruction démarrée</p>
              <p className="text-sm mt-1">{rebuildMutation.data.message}</p>
              <div className="mt-2">
                <Label className="text-xs">Task ID</Label>
                <code className="block mt-1 p-2 bg-black/30 rounded text-xs font-mono">
                  {rebuildMutation.data.task_id}
                </code>
              </div>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}
