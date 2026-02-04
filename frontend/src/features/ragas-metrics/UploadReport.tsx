import { useRef } from 'react'
import { Upload, FileJson, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useRagasStore } from './useRagasStore'
import type { EvaluationReport } from '@/lib/api/types'

/**
 * Validate the structure of an uploaded JSON file
 */
function isValidEvaluationReport(data: unknown): data is EvaluationReport {
  if (!data || typeof data !== 'object') return false

  const report = data as Record<string, unknown>

  // Check required fields
  if (typeof report.timestamp !== 'string') return false

  // Check metrics object
  if (!report.metrics || typeof report.metrics !== 'object') return false
  const metrics = report.metrics as Record<string, unknown>
  if (
    typeof metrics.avg_latency !== 'number' ||
    typeof metrics.avg_relevance !== 'number' ||
    typeof metrics.avg_coverage !== 'number' ||
    typeof metrics.success_rate !== 'number'
  ) {
    return false
  }

  // Check questions array
  if (!Array.isArray(report.questions)) return false
  for (const q of report.questions) {
    if (typeof q !== 'object' || !q) return false
    const question = q as Record<string, unknown>
    if (
      typeof question.question !== 'string' ||
      typeof question.answer !== 'string' ||
      typeof question.latency !== 'number' ||
      typeof question.relevance !== 'number' ||
      typeof question.coverage !== 'number' ||
      typeof question.success !== 'boolean'
    ) {
      return false
    }
  }

  return true
}

export function UploadReport() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { report, filename, setReport, setFilename, clearReport } = useRagasStore()

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Check file extension
    if (!file.name.endsWith('.json')) {
      alert('Veuillez selectionner un fichier JSON')
      return
    }

    try {
      const text = await file.text()
      const data = JSON.parse(text)

      if (!isValidEvaluationReport(data)) {
        alert('Le fichier JSON ne correspond pas au format EvaluationReport attendu')
        return
      }

      setReport(data)
      setFilename(file.name)
    } catch {
      alert('Erreur lors de la lecture du fichier JSON')
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  if (report && filename) {
    return (
      <Card className="border-mediterranean-azure/30 bg-mediterranean-sky/10">
        <CardContent className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <FileJson className="h-5 w-5 text-mediterranean-azure" />
            <div>
              <p className="font-medium text-mediterranean-navy">{filename}</p>
              <p className="text-sm text-mediterranean-navy/60">
                {report.questions.length} questions - {report.timestamp}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={clearReport}
            className="text-mediterranean-terracotta hover:text-mediterranean-terracotta/80"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-dashed border-2 border-mediterranean-azure/30 bg-transparent">
      <CardContent className="flex flex-col items-center justify-center p-8">
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileSelect}
          className="hidden"
        />
        <Upload className="h-10 w-10 text-mediterranean-azure/60 mb-4" />
        <h4 className="text-lg font-medium text-mediterranean-navy mb-2">
          Charger un rapport d'evaluation
        </h4>
        <p className="text-sm text-mediterranean-navy/60 mb-4 text-center">
          Selectionnez un fichier JSON genere par le script evaluate_rag.py
        </p>
        <Button onClick={handleUploadClick} className="bg-mediterranean-azure hover:bg-mediterranean-azure/90">
          <Upload className="h-4 w-4 mr-2" />
          Selectionner un fichier
        </Button>
      </CardContent>
    </Card>
  )
}
