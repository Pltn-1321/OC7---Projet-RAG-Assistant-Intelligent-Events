import { BarChart3 } from 'lucide-react'
import { UploadReport } from './UploadReport'
import { MetricsSummary } from './MetricsSummary'
import { MetricsCharts } from './MetricsCharts'
import { ResultsTable } from './ResultsTable'
import { useRagasStore } from './useRagasStore'

export function RagasView() {
  const { report } = useRagasStore()

  return (
    <div className="flex flex-col h-full p-6 overflow-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <BarChart3 className="h-7 w-7 text-mediterranean-azure" />
          <h2 className="text-2xl font-semibold text-mediterranean-navy">
            Metriques RAGAS
          </h2>
        </div>
        <p className="text-mediterranean-navy/60">
          Evaluez les performances de votre pipeline RAG avec les metriques de latence, pertinence et couverture
        </p>
      </div>

      {/* Upload Section */}
      <div className="mb-6">
        <UploadReport />
      </div>

      {/* Content - shown when report is loaded */}
      {report ? (
        <div className="space-y-6">
          {/* Metrics Summary Cards */}
          <section>
            <h3 className="text-lg font-medium text-mediterranean-navy mb-4">
              Resume des Metriques
            </h3>
            <MetricsSummary />
          </section>

          {/* Charts Section */}
          <section>
            <h3 className="text-lg font-medium text-mediterranean-navy mb-4">
              Visualisations
            </h3>
            <MetricsCharts />
          </section>

          {/* Results Table */}
          <section>
            <ResultsTable />
          </section>
        </div>
      ) : (
        /* Empty State */
        <div className="flex-1 flex flex-col items-center justify-center min-h-[400px]">
          <BarChart3 className="h-16 w-16 text-mediterranean-azure/30 mb-4" />
          <h3 className="text-xl font-medium text-mediterranean-navy mb-2">
            Aucun rapport charge
          </h3>
          <p className="text-mediterranean-navy/60 text-center max-w-md">
            Chargez un rapport d'evaluation JSON genere par le script{' '}
            <code className="bg-mediterranean-sky/30 px-1 py-0.5 rounded text-sm">
              evaluate_rag.py
            </code>{' '}
            pour visualiser les metriques de performance de votre pipeline RAG.
          </p>
        </div>
      )}
    </div>
  )
}
