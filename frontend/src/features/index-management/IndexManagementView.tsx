import { useState } from 'react'
import { IndexInfo } from './IndexInfo'
import { RebuildForm } from './RebuildForm'
import { ProgressTracker } from './ProgressTracker'
import { Database } from 'lucide-react'

export function IndexManagementView() {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null)

  const handleRebuildStarted = (taskId: string) => {
    setActiveTaskId(taskId)
  }

  const handleCloseTracker = () => {
    setActiveTaskId(null)
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-mediterranean-azure/20">
            <Database className="h-6 w-6 text-mediterranean-turquoise" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-foreground">
              Gestion de l'Index
            </h2>
            <p className="text-sm text-muted-foreground">
              Surveillez et reconstruisez l'index vectoriel FAISS
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-6">
          {/* Current Index Info */}
          <section>
            <IndexInfo />
          </section>

          {/* Progress Tracker (when rebuild in progress) */}
          {activeTaskId && (
            <section>
              <ProgressTracker
                taskId={activeTaskId}
                onClose={handleCloseTracker}
              />
            </section>
          )}

          {/* Rebuild Form */}
          <section>
            <RebuildForm onRebuildStarted={handleRebuildStarted} />
          </section>
        </div>
      </div>
    </div>
  )
}
