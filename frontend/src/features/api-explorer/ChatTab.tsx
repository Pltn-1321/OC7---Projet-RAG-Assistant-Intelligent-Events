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
import { MessageSquare, Loader2 } from "lucide-react"

const chatSchema = z.object({
  query: z.string().min(1, "Query is required"),
  session_id: z.string().optional(),
  top_k: z.number().min(1).max(20),
})

type ChatFormData = z.infer<typeof chatSchema>

export function ChatTab() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ChatFormData>({
    resolver: zodResolver(chatSchema),
    defaultValues: {
      top_k: 5,
    },
  })

  const { mutate, isPending, data, error } = useMutation({
    mutationFn: api.chat.sendMessage,
  })

  const onSubmit = (formData: ChatFormData) => {
    mutate(formData)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Chat (Conversational)
          </CardTitle>
          <CardDescription>
            Send a message with session management for conversational context
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="chat-query">Query *</Label>
              <Input
                id="chat-query"
                placeholder="Salut, quels concerts ce weekend ?"
                {...register("query")}
              />
              {errors.query && (
                <p className="text-sm text-red-400">{errors.query.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="session_id">Session ID (optional)</Label>
              <Input
                id="session_id"
                placeholder="Leave empty to generate new session"
                {...register("session_id")}
              />
              <p className="text-xs text-slate-400">
                Provide an existing session ID to continue a conversation
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="chat-top_k">Top K Results (1-20)</Label>
              <Input
                id="chat-top_k"
                type="number"
                min={1}
                max={20}
                {...register("top_k", { valueAsNumber: true })}
              />
              {errors.top_k && (
                <p className="text-sm text-red-400">{errors.top_k.message}</p>
              )}
            </div>

            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Sending...
                </>
              ) : (
                "Send Message"
              )}
            </Button>
          </form>

          {error && (
            <div className="mt-4 p-4 rounded-md bg-red-900/20 border border-red-900 text-red-200">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{getErrorMessage(error, "Chat request failed")}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {data && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Chat Response</CardTitle>
              <Badge variant="secondary">Session: {data.session_id}</Badge>
            </div>
            <CardDescription>Query: {data.query}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-md bg-slate-800">
              <p className="text-sm text-slate-100 whitespace-pre-wrap">{data.response}</p>
            </div>

            {data.sources && data.sources.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold mb-2">
                  Sources ({data.sources.length})
                </h4>
                <div className="space-y-2">
                  {data.sources.map((source, index) => (
                    <Card key={index} className="bg-slate-800 text-slate-100">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-sm text-white">{source.title}</CardTitle>
                          <Badge variant="outline" className="text-xs">
                            {(source.similarity * 100).toFixed(1)}%
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-xs text-slate-300 line-clamp-2">
                          {source.content}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {data && <ResponseViewer data={data} title="Raw Response" />}
    </div>
  )
}
