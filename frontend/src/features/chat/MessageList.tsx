import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { formatRelativeTime } from '@/lib/utils/date'
import type { DocumentResult } from '@/lib/api/types'
import { SourcesAccordion } from './SourcesAccordion'
import { Bot, User } from 'lucide-react'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: DocumentResult[]
  timestamp: Date
}

interface MessageListProps {
  messages: ChatMessage[]
  autoScroll?: boolean
}

export function MessageList({ messages, autoScroll = true }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, autoScroll])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-muted-foreground max-w-md">
          <Bot className="h-16 w-16 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium mb-2">Bienvenue sur l'assistant événements</h3>
          <p className="text-sm">
            Posez-moi vos questions sur les événements culturels à Marseille.
            Je peux vous aider à trouver des concerts, expositions, spectacles et plus encore.
          </p>
        </div>
      </div>
    )
  }

  return (
    <ScrollArea ref={scrollAreaRef} className="flex-1">
      <div className="space-y-4 p-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-mediterranean-azure text-white'
                  : 'bg-mediterranean-sky/50 border'
              }`}
            >
              {/* Message header */}
              <div className="flex items-center gap-2 mb-2">
                {message.role === 'assistant' && (
                  <Bot className="h-4 w-4 shrink-0 opacity-70" />
                )}
                {message.role === 'user' && (
                  <User className="h-4 w-4 shrink-0 opacity-70" />
                )}
                <span className="text-xs opacity-70">
                  {formatRelativeTime(message.timestamp)}
                </span>
              </div>

              {/* Message content */}
              <div
                className={`text-sm leading-relaxed whitespace-pre-wrap ${
                  message.role === 'user' ? 'text-white' : 'text-foreground'
                }`}
              >
                {message.content}
              </div>

              {/* Sources (only for assistant messages with RAG results) */}
              {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                <SourcesAccordion sources={message.sources} />
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
}
