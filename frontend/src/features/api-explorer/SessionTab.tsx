import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { api } from "@/lib/api/endpoints"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ResponseViewer } from "@/components/common/ResponseViewer"
import { getErrorMessage } from "@/lib/api/error-types"
import { History, Loader2, Trash2 } from "lucide-react"
import type { Message } from "@/lib/api/types"

const sessionSchema = z.object({
  session_id: z.string().min(1, "Session ID is required"),
})

type SessionFormData = z.infer<typeof sessionSchema>

export function SessionTab() {
  const [sessionHistory, setSessionHistory] = useState<Message[] | null>(null)
  const [deleteMessage, setDeleteMessage] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SessionFormData>({
    resolver: zodResolver(sessionSchema),
  })

  const getHistoryMutation = useMutation({
    mutationFn: (sessionId: string) => api.chat.getSession(sessionId),
    onSuccess: (data) => {
      setSessionHistory(data)
      setDeleteMessage(null)
    },
    onError: () => {
      setSessionHistory(null)
    },
  })

  const deleteSessionMutation = useMutation({
    mutationFn: (sessionId: string) => api.chat.deleteSession(sessionId),
    onSuccess: (data) => {
      setDeleteMessage(data.message)
      setSessionHistory(null)
    },
  })

  const onGetHistory = (formData: SessionFormData) => {
    getHistoryMutation.mutate(formData.session_id)
  }

  const onDeleteSession = (formData: SessionFormData) => {
    deleteSessionMutation.mutate(formData.session_id)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Session Management
          </CardTitle>
          <CardDescription>
            View conversation history or delete a session
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="session_id">Session ID *</Label>
              <Input
                id="session_id"
                placeholder="Enter session ID from chat response"
                {...register("session_id")}
              />
              {errors.session_id && (
                <p className="text-sm text-red-400">{errors.session_id.message}</p>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                type="button"
                onClick={handleSubmit(onGetHistory)}
                disabled={getHistoryMutation.isPending}
                className="flex-1"
                variant="default"
              >
                {getHistoryMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Loading...
                  </>
                ) : (
                  <>
                    <History className="h-4 w-4 mr-2" />
                    Get History
                  </>
                )}
              </Button>

              <Button
                type="button"
                onClick={handleSubmit(onDeleteSession)}
                disabled={deleteSessionMutation.isPending}
                className="flex-1"
                variant="destructive"
              >
                {deleteSessionMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Session
                  </>
                )}
              </Button>
            </div>
          </form>

          {getHistoryMutation.error && (
            <div className="mt-4 p-4 rounded-md bg-red-900/20 border border-red-900 text-red-200">
              <p className="font-semibold">Error</p>
              <p className="text-sm">
                {getErrorMessage(getHistoryMutation.error, "Failed to fetch session history")}
              </p>
            </div>
          )}

          {deleteSessionMutation.error && (
            <div className="mt-4 p-4 rounded-md bg-red-900/20 border border-red-900 text-red-200">
              <p className="font-semibold">Error</p>
              <p className="text-sm">
                {getErrorMessage(deleteSessionMutation.error, "Failed to delete session")}
              </p>
            </div>
          )}

          {deleteMessage && (
            <div className="mt-4 p-4 rounded-md bg-green-900/20 border border-green-900 text-green-200">
              <p className="font-semibold">Success</p>
              <p className="text-sm">{deleteMessage}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {sessionHistory && (
        <Card>
          <CardHeader>
            <CardTitle>Conversation History</CardTitle>
            <CardDescription>
              {sessionHistory.length} message(s) in this session
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {sessionHistory.map((message, index) => (
              <div
                key={index}
                className={`p-3 rounded-md ${
                  message.role === "user"
                    ? "bg-blue-900/20 border border-blue-900"
                    : "bg-slate-800"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={message.role === "user" ? "default" : "secondary"}>
                    {message.role}
                  </Badge>
                </div>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {sessionHistory && <ResponseViewer data={sessionHistory} title="Raw Message Array" />}
    </div>
  )
}
