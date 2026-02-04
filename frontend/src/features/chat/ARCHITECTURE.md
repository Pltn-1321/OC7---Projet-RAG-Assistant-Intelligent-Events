# Chat Feature Architecture

## Component Hierarchy

```
ChatView (Main Container)
├── Card (shadcn/ui)
│   ├── Header Section
│   │   ├── Title ("Chat Assistant")
│   │   ├── Session Badge (when sessionId exists)
│   │   └── Action Buttons
│   │       ├── Settings Button (toggles settings panel)
│   │       ├── New Session Button
│   │       └── Clear Button (when sessionId exists)
│   │
│   ├── Settings Panel (when showSettings = true)
│   │   └── Slider Component
│   │       ├── Label ("Nombre de résultats (top_k): {topK}")
│   │       └── Range Slider (1-20)
│   │
│   ├── MessageList (scrollable, flex-1)
│   │   └── ScrollArea
│   │       └── Message Items
│   │           ├── User Message
│   │           │   ├── User Icon
│   │           │   ├── Timestamp
│   │           │   └── Content
│   │           │
│   │           └── Assistant Message
│   │               ├── Bot Icon
│   │               ├── Timestamp
│   │               ├── Content
│   │               └── SourcesAccordion (if sources exist)
│   │                   └── Accordion
│   │                       ├── AccordionTrigger ("Sources (N événements)")
│   │                       └── AccordionContent
│   │                           └── Event Cards
│   │                               ├── Title + Similarity Badge
│   │                               ├── Date (Calendar icon)
│   │                               ├── Location (MapPin icon)
│   │                               └── Category + Price Badges
│   │
│   └── MessageInput (fixed bottom)
│       ├── Textarea (auto-resize)
│       └── Send Button (Send icon)
│
└── Clear Session Dialog (when showClearDialog = true)
    ├── DialogHeader
    │   ├── DialogTitle
    │   └── DialogDescription
    └── DialogFooter
        ├── Cancel Button
        └── Confirm Button
```

## Data Flow

```
User Input
    ↓
MessageInput.onSend(query)
    ↓
ChatView.handleSendMessage(query)
    ↓
TanStack Query Mutation
    ↓
api.chat.sendMessage({
    query,
    session_id: sessionId || undefined,
    top_k: topK
})
    ↓
[API Request to Backend]
    ↓
API Response (ChatResponse)
    ↓
onSuccess Callback
    ↓
1. Update sessionId (if new)
    setSessionId(data.session_id)
    ↓
2. Add user message to state
    setMessages([...messages, {
        role: 'user',
        content: query,
        timestamp: new Date()
    }])
    ↓
3. Add assistant response to state
    setMessages([...messages, {
        role: 'assistant',
        content: data.response,
        sources: data.sources,
        timestamp: new Date()
    }])
    ↓
MessageList re-renders
    ↓
Auto-scroll to bottom
    ↓
Display new messages
```

## State Management

### Zustand Store (`useChatStore`)

```
┌─────────────────────────────────────┐
│       useChatStore (Zustand)        │
├─────────────────────────────────────┤
│ State:                              │
│  - sessionId: string | null         │
│  - topK: number (1-20, default: 5)  │
│                                     │
│ Actions:                            │
│  - setSessionId(id)                 │
│  - setTopK(k)                       │
│  - clearSession()                   │
│                                     │
│ Persistence:                        │
│  - topK → localStorage              │
│  - sessionId → memory only          │
└─────────────────────────────────────┘
```

### Component State (`ChatView`)

```
┌─────────────────────────────────────┐
│      ChatView Local State           │
├─────────────────────────────────────┤
│ messages: ChatMessage[]             │
│  - Stores conversation history      │
│  - Array of user/assistant messages │
│  - Includes sources for assistant   │
│                                     │
│ showClearDialog: boolean            │
│  - Controls dialog visibility       │
│                                     │
│ showSettings: boolean               │
│  - Controls settings panel          │
└─────────────────────────────────────┘
```

## API Integration (TanStack Query)

### Send Message Mutation

```typescript
const { mutate: sendMessage, isPending } = useMutation({
  mutationFn: (query: string) => api.chat.sendMessage({
    query,
    session_id: sessionId || undefined,
    top_k: topK,
  }),
  onSuccess: (data, query) => {
    // 1. Update session ID if new
    if (!sessionId) setSessionId(data.session_id)

    // 2. Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: query,
      timestamp: new Date(),
    }])

    // 3. Add assistant response
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: data.response,
      sources: data.sources,
      timestamp: new Date(),
    }])
  },
  onError: (error) => {
    console.error('Chat error:', error)
  }
})
```

### Delete Session Mutation

```typescript
const { mutate: deleteSessionMutation, isPending: isDeleting } = useMutation({
  mutationFn: () => api.chat.deleteSession(sessionId!),
  onSuccess: () => {
    clearSession()        // Clear Zustand store
    setMessages([])       // Clear local messages
    setShowClearDialog(false)  // Close dialog
  },
  onError: (error) => {
    console.error('Delete session error:', error)
  }
})
```

## Message Types

```typescript
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: DocumentResult[]  // Only for assistant messages
  timestamp: Date
}

// Example user message
{
  role: 'user',
  content: 'Quels concerts ce weekend ?',
  timestamp: new Date()
}

// Example assistant message (with RAG)
{
  role: 'assistant',
  content: 'Voici quelques concerts ce weekend...',
  sources: [
    {
      title: 'Concert de Jazz',
      content: '...',
      metadata: {
        title: 'Concert de Jazz',
        category: 'Concert',
        location: { city: 'Marseille', address: '...' },
        date_range: { start: '2024-01-15', end: '2024-01-15' },
        price: 25.00,
        is_free: false
      },
      similarity: 0.87,
      distance: 0.13
    },
    // ... more sources
  ],
  timestamp: new Date()
}
```

## Styling Theme

### Color Palette (Mediterranean)

```css
/* User messages */
.user-message {
  background: bg-mediterranean-azure;
  color: text-white;
  align: right;
}

/* Assistant messages */
.assistant-message {
  background: bg-mediterranean-sky/50;
  border: border;
  align: left;
}

/* Category badges */
.category-concert { background: bg-mediterranean-turquoise; }
.category-expo    { background: bg-mediterranean-ochre; }
.category-theatre { background: bg-mediterranean-terracotta; }
.category-festival{ background: bg-mediterranean-azure; }
.category-default { background: bg-mediterranean-sky; }

/* Success badge (free events) */
.badge-success {
  background: bg-green-600;
  color: text-white;
}
```

### Layout Structure

```
┌────────────────────────────────────┐
│          Header (fixed)            │
│  [Title] [Session Badge] [Buttons] │
├────────────────────────────────────┤
│       Settings Panel (optional)    │
│  [Slider: top_k 1──●────── 20]    │
├────────────────────────────────────┤
│                                    │
│        Message List (flex-1)       │
│         (scrollable area)          │
│                                    │
│  ┌──────────────────────────┐     │
│  │ User: Hello              │     │
│  └──────────────────────────┘     │
│                                    │
│  ┌──────────────────────────┐     │
│  │ Bot: Hi! How can I help? │     │
│  └──────────────────────────┘     │
│                                    │
├────────────────────────────────────┤
│       Message Input (fixed)        │
│  [Textarea───────────] [Send →]   │
└────────────────────────────────────┘
```

## Event Flow Diagram

### New Conversation

```
User opens ChatView
    ↓
sessionId = null
messages = []
    ↓
Display empty state
("Bienvenue sur l'assistant événements")
    ↓
User types query
    ↓
User presses Enter / clicks Send
    ↓
Call api.chat.sendMessage()
    ↓
Backend creates new session
    ↓
Receive session_id in response
    ↓
Store session_id in Zustand
    ↓
Display user + assistant messages
```

### Continuing Conversation

```
sessionId exists
messages has history
    ↓
User types query
    ↓
User presses Enter / clicks Send
    ↓
Call api.chat.sendMessage()
with existing session_id
    ↓
Backend appends to session history
    ↓
Receive response
    ↓
Append to local messages array
    ↓
Auto-scroll to bottom
```

### Clear Session

```
User clicks "Effacer" button
    ↓
Show confirmation dialog
    ↓
User confirms
    ↓
Call api.chat.deleteSession(sessionId)
    ↓
Backend deletes session
    ↓
Clear Zustand store (sessionId = null)
    ↓
Clear local messages array
    ↓
Display empty state
```

## Performance Considerations

1. **Auto-scroll Behavior**
   - Disabled during loading (`isPending`)
   - Prevents jumpy scrolling
   - Uses `scrollIntoView({ behavior: 'smooth' })`

2. **Textarea Auto-resize**
   - Calculates height on every change
   - Max height: 200px
   - Prevents infinite growth

3. **Message Rendering**
   - Uses React keys (index-based)
   - Could be improved with unique message IDs

4. **State Updates**
   - Uses functional setState for message array
   - Prevents race conditions
   - Maintains immutability

5. **API Calls**
   - Debouncing not implemented (Enter to send)
   - Disabled state prevents duplicate submissions
   - TanStack Query handles caching and deduplication

## Error Handling

```
API Error
    ↓
onError callback in mutation
    ↓
Log to console
    ↓
(Future: Show toast notification)
    ↓
User can retry
```

## Accessibility Features

1. **Keyboard Navigation**
   - Enter to send message
   - Shift+Enter for newline
   - Tab through buttons

2. **Screen Readers**
   - ARIA labels on icon buttons
   - `sr-only` text for context
   - Semantic HTML structure

3. **Focus Management**
   - Auto-focus textarea after send
   - Dialog focus trapping
   - Keyboard shortcuts

4. **Color Contrast**
   - High contrast text
   - Distinct message backgrounds
   - Visible focus states

## Future Enhancements

1. **Streaming Responses**
   ```
   SSE (Server-Sent Events)
       ↓
   Stream tokens as they arrive
       ↓
   Display typing indicator
       ↓
   Append tokens to message
   ```

2. **Message Persistence**
   ```
   Save to localStorage
       ↓
   Restore on mount
       ↓
   Optional: Sync with backend
   ```

3. **Rich Text Support**
   ```
   Install react-markdown
       ↓
   Parse assistant responses
       ↓
   Render with syntax highlighting
   ```

4. **Voice Input**
   ```
   Web Speech API
       ↓
   Record audio
       ↓
   Convert to text
       ↓
   Send as query
   ```
