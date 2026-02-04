# Chat Feature

Complete chat interface for the RAG Assistant chatbot dashboard.

## Components

### ChatView

Main container component that orchestrates the entire chat experience.

**Features:**
- Session management with unique session IDs
- Real-time message display (user & assistant)
- Adjustable top_k parameter (1-20) for RAG retrieval
- Session history management
- Clear session dialog with confirmation
- Settings panel for configuration

**Usage:**
```tsx
import { ChatView } from '@/features/chat'

function App() {
  return <ChatView />
}
```

### MessageList

Scrollable message list with auto-scroll functionality.

**Features:**
- Display user and assistant messages
- Different styling for user (right, azure) vs assistant (left, sky)
- Show relative timestamps
- Auto-scroll to bottom on new messages (can be disabled)
- Empty state with welcome message
- Sources accordion for RAG results

**Props:**
```tsx
interface MessageListProps {
  messages: ChatMessage[]
  autoScroll?: boolean // default: true
}
```

### MessageInput

Text input component with send button.

**Features:**
- Auto-resizing textarea (max height: 200px)
- Enter to send (Shift+Enter for newline)
- Disabled state during API calls
- Clear input after send
- Loading placeholder

**Props:**
```tsx
interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string // default: "Posez votre question..."
}
```

### SourcesAccordion

Collapsible accordion showing event sources from RAG retrieval.

**Features:**
- Only renders if sources exist
- Shows source count in trigger
- Event cards with:
  - Title and similarity score
  - Date range
  - Location (city + address)
  - Category badge with color coding
  - Price (or "Gratuit")

**Props:**
```tsx
interface SourcesAccordionProps {
  sources: DocumentResult[]
}
```

## State Management

### Zustand Store (`useChatStore`)

```tsx
interface ChatState {
  sessionId: string | null
  setSessionId: (id: string | null) => void

  topK: number // 1-20, default: 5
  setTopK: (k: number) => void

  clearSession: () => void
}
```

**Persistence:** Only `topK` is persisted to localStorage. Session IDs are ephemeral (in-memory on backend).

### Local State (`ChatView`)

```tsx
const [messages, setMessages] = useState<ChatMessage[]>([])
const [showClearDialog, setShowClearDialog] = useState(false)
const [showSettings, setShowSettings] = useState(false)
```

## API Integration

### TanStack Query Mutations

**Send Message:**
```tsx
const { mutate: sendMessage, isPending } = useMutation({
  mutationFn: (query: string) => api.chat.sendMessage({
    query,
    session_id: sessionId || undefined,
    top_k: topK,
  }),
  onSuccess: (data) => {
    // Update session ID if new
    // Add user message to state
    // Add assistant response to state
  }
})
```

**Delete Session:**
```tsx
const { mutate: deleteSessionMutation, isPending: isDeleting } = useMutation({
  mutationFn: () => api.chat.deleteSession(sessionId!),
  onSuccess: () => {
    // Clear session from store
    // Clear messages
    // Close dialog
  }
})
```

## Styling

### Theme Colors (Mediterranean palette)

- **User messages**: `bg-mediterranean-azure text-white`
- **Assistant messages**: `bg-mediterranean-sky/50 border`
- **Category badges**: Dynamic colors via `getCategoryColor()`
  - Concert/Music: `bg-mediterranean-turquoise`
  - Expo/Art: `bg-mediterranean-ochre`
  - Theatre/Spectacle: `bg-mediterranean-terracotta`
  - Festival: `bg-mediterranean-azure`
  - Default: `bg-mediterranean-sky`

### Layout

- **Full height**: `h-full flex flex-col`
- **Responsive**: Mobile-first with responsive breakpoints
- **Scrollable**: MessageList uses `ScrollArea` from shadcn/ui
- **Fixed input**: MessageInput pinned at bottom

## Error Handling

- API errors are logged to console
- No toast notifications (library not installed)
- Loading states prevent duplicate submissions
- Disabled states during async operations

## Type Safety

All components use TypeScript with proper type definitions from `@/lib/api/types`:

```tsx
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: DocumentResult[]
  timestamp: Date
}
```

## Utilities

### Date Formatting
- `formatRelativeTime(date)`: "il y a 2 minutes"
- `formatDateRange(start, end)`: "15-20 janvier 2024"

### Format Utilities
- `formatPrice(price)`: "10.00 €" or "Gratuit"
- `formatSimilarity(score)`: "85.5%"
- `getCategoryColor(category)`: Returns Tailwind color class
- `truncate(text, maxLength)`: Truncates with ellipsis

## Accessibility

- Semantic HTML structure
- ARIA labels on icon buttons (`sr-only` text)
- Keyboard navigation support (Enter to send)
- Focus management in dialogs
- Screen reader friendly

## Future Enhancements

- [ ] Add markdown rendering for assistant responses (react-markdown)
- [ ] Add toast notifications (sonner)
- [ ] Add typing indicator
- [ ] Add message persistence (save to localStorage)
- [ ] Add export conversation feature
- [ ] Add voice input support
- [ ] Add message reactions
- [ ] Add copy message to clipboard
