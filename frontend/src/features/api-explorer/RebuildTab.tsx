import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { api } from "@/lib/api/endpoints"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ResponseViewer } from "@/components/common/ResponseViewer"
import { RefreshCw, Loader2, CheckCircle2, XCircle, AlertTriangle } from "lucide-react"
import type { RebuildStatusResponse } from "@/lib/api/types"

const rebuildSchema = z.object({
  api_key: z.string().optional(),
})

const statusSchema = z.object({
  task_id: z.string().min(1, "Task ID is required"),
})

type RebuildFormData = z.infer<typeof rebuildSchema>
type StatusFormData = z.infer<typeof statusSchema>

export function RebuildTab() {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [statusData, setStatusData] = useState<RebuildStatusResponse | null>(null)

  const {
    register: registerRebuild,
    handleSubmit: handleSubmitRebuild,
  } = useForm<RebuildFormData>({
    resolver: zodResolver(rebuildSchema),
  })

  const {
    register: registerStatus,
    handleSubmit: handleSubmitStatus,
    formState: { errors: statusErrors },
  } = useForm<StatusFormData>({
    resolver: zodResolver(statusSchema),
  })

  const rebuildMutation = useMutation({
    mutationFn: ({ api_key }: { api_key?: string }) => api.rebuild.start(api_key),
    onSuccess: (data) => {
      setTaskId(data.task_id)
      setStatusData(null)
    },
  })

  const statusMutation = useMutation({
    mutationFn: (taskId: string) => api.rebuild.getStatus(taskId),
    onSuccess: (data) => {
      setStatusData(data)
    },
  })

  const onStartRebuild = (formData: RebuildFormData) => {
    rebuildMutation.mutate({ api_key: formData.api_key })
  }

  const onCheckStatus = (formData: StatusFormData) => {
    statusMutation.mutate(formData.task_id)
  }

  const getProgressPercentage = () => {
    if (!statusData || !statusData.progress) return 0
    return statusData.progress * 100
  }

  return (
    <div className="space-y-6">
      {/* Section 1: Trigger Rebuild */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Reconstruire l'index
          </CardTitle>
          <CardDescription>
            Reconstruit l'index FAISS à partir des documents existants (rag_documents.json)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4 p-3 rounded-md bg-amber-900/20 border border-amber-700 text-amber-200">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
              <div className="text-sm">
                <p className="font-medium">Note importante</p>
                <p className="text-amber-300/80 mt-1">
                  La reconstruction utilise le fichier <code className="bg-amber-950 px-1 rounded">rag_documents.json</code> déjà présent sur le serveur.
                  Pour mettre à jour les données, utilisez les notebooks Jupyter.
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmitRebuild(onStartRebuild)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api_key">X-API-Key</Label>
              <Input
                id="api_key"
                type="password"
                placeholder="Clé API requise (REBUILD_API_KEY)"
                {...registerRebuild("api_key")}
              />
              <p className="text-xs text-slate-400">
                Clé d'authentification pour l'endpoint de reconstruction
              </p>
            </div>

            <Button type="submit" disabled={rebuildMutation.isPending} className="w-full">
              {rebuildMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Démarrage...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Lancer la reconstruction
                </>
              )}
            </Button>
          </form>

          {rebuildMutation.error && (
            <div className="mt-4 p-4 rounded-md bg-red-900/20 border border-red-900 text-red-200">
              <p className="font-semibold">Erreur</p>
              <p className="text-sm">
                {(rebuildMutation.error as any).detail || "Échec du démarrage de la reconstruction"}
              </p>
            </div>
          )}

          {rebuildMutation.data && (
            <div className="mt-4 p-4 rounded-md bg-green-900/20 border border-green-900 text-green-200">
              <p className="font-semibold">Reconstruction démarrée</p>
              <p className="text-sm">{rebuildMutation.data.message}</p>
              <div className="mt-2">
                <Label>Task ID</Label>
                <code className="block mt-1 p-2 bg-slate-950 rounded text-xs">
                  {rebuildMutation.data.task_id}
                </code>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Section 2: Track Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5" />
            Suivre la progression
          </CardTitle>
          <CardDescription>
            Vérifier le statut d'une tâche de reconstruction
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmitStatus(onCheckStatus)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="task_id">Task ID *</Label>
              <Input
                id="task_id"
                placeholder="Entrez le Task ID"
                defaultValue={taskId || ""}
                {...registerStatus("task_id")}
              />
              {statusErrors.task_id && (
                <p className="text-sm text-red-400">{statusErrors.task_id.message}</p>
              )}
            </div>

            <Button type="submit" disabled={statusMutation.isPending} className="w-full">
              {statusMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Vérification...
                </>
              ) : (
                "Vérifier le statut"
              )}
            </Button>
          </form>

          {statusMutation.error && (
            <div className="mt-4 p-4 rounded-md bg-red-900/20 border border-red-900 text-red-200">
              <p className="font-semibold">Erreur</p>
              <p className="text-sm">
                {(statusMutation.error as any).detail || "Échec de la récupération du statut"}
              </p>
            </div>
          )}

          {statusData && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Statut:</span>
                <Badge
                  variant={
                    statusData.status === "completed"
                      ? "default"
                      : statusData.status === "failed"
                        ? "destructive"
                        : "secondary"
                  }
                >
                  {statusData.status === "in_progress" && (
                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  )}
                  {statusData.status === "completed" && (
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                  )}
                  {statusData.status === "failed" && <XCircle className="h-3 w-3 mr-1" />}
                  {statusData.status === "in_progress" ? "En cours" :
                   statusData.status === "completed" ? "Terminé" : "Échec"}
                </Badge>
              </div>

              {statusData.status === "in_progress" && statusData.progress !== undefined && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progression</span>
                    <span>{getProgressPercentage().toFixed(1)}%</span>
                  </div>
                  <Progress value={getProgressPercentage()} />
                </div>
              )}

              {statusData.message && (
                <p className="text-sm text-slate-300">{statusData.message}</p>
              )}

              {statusData.error && (
                <div className="p-3 rounded-md bg-red-900/20 border border-red-900 text-red-200">
                  <p className="text-sm font-semibold">Détails de l'erreur:</p>
                  <p className="text-sm">{statusData.error}</p>
                </div>
              )}

              {statusData.status === "completed" && (
                <div className="grid grid-cols-2 gap-3">
                  {statusData.documents_processed !== undefined && (
                    <div className="p-3 rounded-md bg-slate-800">
                      <p className="text-xs text-slate-400">Documents</p>
                      <p className="text-lg font-bold text-white">{statusData.documents_processed}</p>
                    </div>
                  )}
                  {statusData.embedding_dimension !== undefined && (
                    <div className="p-3 rounded-md bg-slate-800">
                      <p className="text-xs text-slate-400">Dimension Embedding</p>
                      <p className="text-lg font-bold text-white">{statusData.embedding_dimension}</p>
                    </div>
                  )}
                  {statusData.index_vectors !== undefined && (
                    <div className="p-3 rounded-md bg-slate-800">
                      <p className="text-xs text-slate-400">Vecteurs Index</p>
                      <p className="text-lg font-bold text-white">{statusData.index_vectors}</p>
                    </div>
                  )}
                  {statusData.elapsed_seconds !== undefined && (
                    <div className="p-3 rounded-md bg-slate-800">
                      <p className="text-xs text-slate-400">Temps écoulé</p>
                      <p className="text-lg font-bold text-white">{statusData.elapsed_seconds.toFixed(1)}s</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {statusData && <ResponseViewer data={statusData} title="Réponse brute" />}
    </div>
  )
}
