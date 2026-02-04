import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
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
import { useChatStore } from '@/store/useChatStore'
import { api } from '@/lib/api/endpoints'
import { truncate } from '@/lib/utils/format'
import { Trash2, Plus, Settings2 } from 'lucide-react'

export function ChatView() {
  const { sessionId, setSessionId, topK, setTopK, clearSession } = useChatStore()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [showClearDialog, setShowClearDialog] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  // Send message mutation
  const { mutate: sendMessage, isPending } = useMutation({
    mutationFn: (query: string) =>
      api.chat.sendMessage({
        query,
        session_id: sessionId || undefined,
        top_k: topK,
      }),
    onMutate: (query) => {
      // Add user message immediately (optimistic)
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          content: query,
          timestamp: new Date(),
        },
      ])
    },
    onSuccess: (data) => {
      // Set session ID if it's a new session
      if (!sessionId) {
        setSessionId(data.session_id)
      }

      // Add assistant response
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
    onError: (error: any) => {
      console.error('Chat error:', error)
      // Add error message to chat
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erreur de connexion au serveur. Vérifiez que le backend est lancé.'
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ **Erreur**: ${errorMessage}`,
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
    onError: (error: any) => {
      console.error('Delete session error:', error)
    },
  })

  const handleSendMessage = (query: string) => {
    sendMessage(query)
  }

  const handleNewSession = () => {
    clearSession()
    setMessages([])
  }

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
          <div className="flex items-center gap-3 flex-1">
            <h2 className="text-lg font-semibold">Chat Assistant</h2>
            {sessionId && (
              <Badge variant="outline" className="text-xs font-mono">
                Session: {truncate(sessionId, 8)}
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings2 className="h-4 w-4 mr-2" />
              Paramètres
            </Button>
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

        {/* Settings Panel */}
        {showSettings && (
          <div className="p-4 border-b bg-muted/50">
            <div className="max-w-md">
              <label className="text-sm font-medium mb-2 block">
                Nombre de résultats (top_k): {topK}
              </label>
              <div className="flex items-center gap-4">
                <span className="text-xs text-muted-foreground">1</span>
                <Slider
                  value={[topK]}
                  onValueChange={(value) => setTopK(value[0])}
                  min={1}
                  max={20}
                  step={1}
                  className="flex-1"
                />
                <span className="text-xs text-muted-foreground">20</span>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Nombre maximum d'événements à récupérer pour chaque recherche
              </p>
            </div>
          </div>
        )}

        {/* Messages */}
        <MessageList messages={messages} autoScroll={!isPending} />

        {/* Input */}
        <MessageInput
          onSend={handleSendMessage}
          disabled={isPending}
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
