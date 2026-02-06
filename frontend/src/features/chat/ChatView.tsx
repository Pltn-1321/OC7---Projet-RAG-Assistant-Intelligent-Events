import { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { MessageList, type ChatMessage } from './MessageList'
import { MessageInput } from './MessageInput'
import { ChatSettings } from './ChatSettings'
import { ChatHistory } from './ChatHistory'
import { useChatStore } from '@/store/useChatStore'
import { api } from '@/lib/api/endpoints'
import { truncate } from '@/lib/utils/format'
import { getErrorMessage } from '@/lib/api/error-types'
import { Trash2, Plus, Loader2 } from 'lucide-react'

export function ChatView() {
  const { sessionId, setSessionId, topK, clearSession, addSession } =
    useChatStore()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [showClearDialog, setShowClearDialog] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)

  // Send message mutation
  const { mutate: sendMessage, isPending } = useMutation({
    mutationFn: (query: string) =>
      api.chat.sendMessage({
        query,
        session_id: sessionId || undefined,
        top_k: topK,
      }),
    onMutate: (query) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          content: query,
          timestamp: new Date(),
        },
      ])
    },
    onSuccess: (data, query) => {
      const isNewSession = !sessionId
      if (isNewSession) {
        setSessionId(data.session_id)
        // Register session in history with first message as title
        addSession({
          id: data.session_id,
          title: query,
          createdAt: new Date().toISOString(),
        })
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          sources: data.sources,
          timestamp: new Date(),
        },
      ])
    },
    onError: (error: unknown) => {
      console.error('Chat error:', error)
      const errorMessage = getErrorMessage(
        error,
        'Erreur de connexion au serveur. Vérifiez que le backend est lancé.'
      )
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `**Erreur** : ${errorMessage}`,
          timestamp: new Date(),
        },
      ])
    },
  })

  // Clear session mutation
  const { mutate: deleteSessionMutation, isPending: isDeleting } = useMutation({
    mutationFn: () => api.chat.deleteSession(sessionId!),
    onSuccess: () => {
      clearSession()
      setMessages([])
      setShowClearDialog(false)
    },
    onError: (error: unknown) => {
      console.error('Delete session error:', error)
    },
  })

  const handleSendMessage = (query: string) => {
    sendMessage(query)
  }

  const handleNewSession = useCallback(() => {
    clearSession()
    setMessages([])
  }, [clearSession])

  const handleSelectSession = useCallback(
    async (id: string) => {
      if (id === sessionId) return

      setIsLoadingHistory(true)
      setSessionId(id)
      setMessages([])

      try {
        const session = await api.chat.getSession(id)
        const loaded: ChatMessage[] = session.history.map((msg) => ({
          role: msg.role,
          content: msg.content,
          timestamp: new Date(session.created_at),
        }))
        setMessages(loaded)
      } catch {
        // Session may have expired on the backend
        setMessages([
          {
            role: 'assistant',
            content:
              'Cette session a expiré ou est introuvable sur le serveur. Vous pouvez continuer en envoyant un nouveau message.',
            timestamp: new Date(),
          },
        ])
      } finally {
        setIsLoadingHistory(false)
      }
    },
    [sessionId, setSessionId]
  )

  const handleClearSession = () => {
    if (sessionId) {
      deleteSessionMutation()
    } else {
      setMessages([])
      setShowClearDialog(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <Card className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b bg-card flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <h2 className="text-lg font-semibold shrink-0">Chat Assistant</h2>
            {sessionId && (
              <Badge variant="outline" className="text-xs font-mono truncate">
                {truncate(sessionId, 8)}
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <ChatHistory
              onSelectSession={handleSelectSession}
              onNewSession={handleNewSession}
            />
            <ChatSettings />
            <Button variant="outline" size="sm" onClick={handleNewSession}>
              <Plus className="h-4 w-4 mr-2" />
              Nouvelle session
            </Button>
            {sessionId && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowClearDialog(true)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Effacer
              </Button>
            )}
          </div>
        </div>

        {/* Messages */}
        {isLoadingHistory ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="flex items-center gap-3 text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span className="text-sm">Chargement de la conversation...</span>
            </div>
          </div>
        ) : (
          <MessageList messages={messages} autoScroll={!isPending} />
        )}

        {/* Input */}
        <MessageInput
          onSend={handleSendMessage}
          disabled={isPending || isLoadingHistory}
          placeholder={
            isPending ? 'En cours de traitement...' : 'Posez votre question...'
          }
        />
      </Card>

      {/* Clear Session Dialog */}
      <Dialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Effacer l'historique</DialogTitle>
            <DialogDescription>
              Voulez-vous vraiment effacer l'historique de cette conversation ?
              Cette action est irréversible.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowClearDialog(false)}
              disabled={isDeleting}
            >
              Annuler
            </Button>
            <Button
              variant="destructive"
              onClick={handleClearSession}
              disabled={isDeleting}
            >
              {isDeleting ? 'Suppression...' : 'Effacer'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
