import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api/endpoints"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ResponseViewer } from "@/components/common/ResponseViewer"
import { Activity, Loader2 } from "lucide-react"

export function HealthTab() {
  const { mutate, isPending, data, error } = useMutation({
    mutationFn: api.health.check,
  })

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Health Check
          </CardTitle>
          <CardDescription>
            Check the API server health status and index information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={() => mutate()}
            disabled={isPending}
            className="w-full"
          >
            {isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Checking...
              </>
            ) : (
              "Fetch Health"
            )}
          </Button>

          {error && (
            <div className="p-4 rounded-md bg-red-900/20 border border-red-900 text-red-200">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{(error as any).detail || "Failed to fetch health status"}</p>
            </div>
          )}

          {data && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Status:</span>
                <Badge variant={data.status === "healthy" ? "success" : "destructive"}>
                  {data.status === "healthy" ? "Online" : "Offline"}
                </Badge>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 rounded-md bg-slate-800">
                  <p className="text-xs text-slate-400">Documents</p>
                  <p className="text-2xl font-bold text-white">{data.document_count ?? 'N/A'}</p>
                </div>
                <div className="p-3 rounded-md bg-slate-800">
                  <p className="text-xs text-slate-400">Embedding Dim</p>
                  <p className="text-2xl font-bold text-white">{data.embedding_dimension ?? 'N/A'}</p>
                </div>
                <div className="p-3 rounded-md bg-slate-800">
                  <p className="text-xs text-slate-400">Active Sessions</p>
                  <p className="text-2xl font-bold text-white">{data.active_sessions ?? 0}</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {data && <ResponseViewer data={data} title="Raw Response" />}
    </div>
  )
}
