import { useState } from 'react'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useChatStore, type SessionEntry } from '@/store/useChatStore'
import { formatRelativeTime } from '@/lib/utils/date'
import { truncate } from '@/lib/utils/format'
import { History, MessageSquare, Trash2, Plus } from 'lucide-react'

interface ChatHistoryProps {
  onSelectSession: (sessionId: string) => void
  onNewSession: () => void
}

export function ChatHistory({ onSelectSession, onNewSession }: ChatHistoryProps) {
  const [open, setOpen] = useState(false)
  const { sessions, sessionId, removeSession } = useChatStore()

  const handleSelect = (id: string) => {
    onSelectSession(id)
    setOpen(false)
  }

  const handleNew = () => {
    onNewSession()
    setOpen(false)
  }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
        <History className="h-4 w-4 mr-2" />
        Historique
        {sessions.length > 0 && (
          <span className="ml-1.5 text-xs bg-primary/10 text-primary rounded-full px-1.5">
            {sessions.length}
          </span>
        )}
      </Button>

      <SheetContent side="left" className="bg-card text-card-foreground sm:max-w-sm overflow-hidden flex flex-col">
        <SheetHeader>
          <SheetTitle className="text-lg font-semibold">
            Conversations
          </SheetTitle>
          <SheetDescription>
            Retrouvez vos conversations passées
          </SheetDescription>
        </SheetHeader>

        <div className="mt-4 flex flex-col flex-1 min-h-0">
          <Button onClick={handleNew} className="w-full mb-4 shrink-0">
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle conversation
          </Button>

          {sessions.length === 0 ? (
            <div className="flex-1 flex items-center justify-center text-center p-6">
              <div className="text-muted-foreground">
                <MessageSquare className="h-10 w-10 mx-auto mb-3 opacity-40" />
                <p className="text-sm">Aucune conversation</p>
                <p className="text-xs mt-1">
                  Vos conversations apparaîtront ici
                </p>
              </div>
            </div>
          ) : (
            <ScrollArea className="flex-1">
              <div className="space-y-1 pr-3">
                {sessions.map((session) => (
                  <SessionItem
                    key={session.id}
                    session={session}
                    isActive={session.id === sessionId}
                    onSelect={() => handleSelect(session.id)}
                    onRemove={() => removeSession(session.id)}
                  />
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}

function SessionItem({
  session,
  isActive,
  onSelect,
  onRemove,
}: {
  session: SessionEntry
  isActive: boolean
  onSelect: () => void
  onRemove: () => void
}) {
  return (
    <div
      className={`group flex items-center gap-2 rounded-lg p-3 cursor-pointer transition-colors ${
        isActive
          ? 'bg-primary/10 border border-primary/20'
          : 'hover:bg-muted/60 border border-transparent'
      }`}
      onClick={onSelect}
    >
      <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate text-foreground">
          {truncate(session.title, 40)}
        </p>
        <p className="text-xs text-muted-foreground">
          {formatRelativeTime(session.createdAt)}
        </p>
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="h-7 w-7 opacity-0 group-hover:opacity-100 shrink-0"
        onClick={(e) => {
          e.stopPropagation()
          onRemove()
        }}
      >
        <Trash2 className="h-3.5 w-3.5 text-muted-foreground" />
      </Button>
    </div>
  )
}
