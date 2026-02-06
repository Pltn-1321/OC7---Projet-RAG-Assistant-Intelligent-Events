import { useState } from 'react'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Settings2, RotateCcw, Info } from 'lucide-react'
import { useChatStore } from '@/store/useChatStore'

interface ChatSettingsProps {
  trigger?: React.ReactNode
}

const DEFAULT_TOP_K = 5
const MIN_TOP_K = 1
const MAX_TOP_K = 20

export function ChatSettings({ trigger }: ChatSettingsProps) {
  const [open, setOpen] = useState(false)
  const { topK, setTopK } = useChatStore()

  const handleReset = () => {
    setTopK(DEFAULT_TOP_K)
  }

  const isModified = topK !== DEFAULT_TOP_K

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      {trigger || (
        <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
          <Settings2 className="h-4 w-4 mr-2" />
          Paramètres
        </Button>
      )}

      <SheetContent
        side="right"
        className="bg-card text-card-foreground sm:max-w-sm overflow-y-auto"
      >
        <SheetHeader>
          <SheetTitle className="text-lg font-semibold">
            Paramètres
          </SheetTitle>
          <SheetDescription>
            Configuration de la recherche d'événements
          </SheetDescription>
        </SheetHeader>

        <div className="mt-8 space-y-6">
          {/* Top K Section */}
          <div className="rounded-lg border bg-background/40 p-5 space-y-5">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">
                Nombre de résultats
              </label>
              <span className="text-2xl font-bold tabular-nums text-primary">
                {topK}
              </span>
            </div>

            {/* Slider */}
            <div className="space-y-2">
              <Slider
                value={[topK]}
                onValueChange={(value) => setTopK(value[0])}
                min={MIN_TOP_K}
                max={MAX_TOP_K}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{MIN_TOP_K}</span>
                <span>10</span>
                <span>{MAX_TOP_K}</span>
              </div>
            </div>

            {/* Hint */}
            <div className="flex gap-2 rounded-md bg-primary/5 border border-primary/10 p-3">
              <Info className="h-4 w-4 text-primary shrink-0 mt-0.5" />
              <div className="text-xs leading-relaxed text-muted-foreground">
                <p>
                  Contrôle le nombre d'événements analysés pour répondre à
                  votre question.
                </p>
                <p className="mt-1 font-medium text-foreground">
                  Recommandé : 5-10
                </p>
              </div>
            </div>
          </div>

          {/* Reset */}
          {isModified && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="w-full"
            >
              <RotateCcw className="h-3.5 w-3.5 mr-2" />
              Réinitialiser ({DEFAULT_TOP_K})
            </Button>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
