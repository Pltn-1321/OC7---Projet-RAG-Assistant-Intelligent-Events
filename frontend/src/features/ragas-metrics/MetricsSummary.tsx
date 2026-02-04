import { Clock, Target, Layers, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { useRagasStore } from './useRagasStore'
import { formatLatency } from '@/lib/utils/format'

// Target thresholds from backend constants
const TARGET_LATENCY_SECONDS = 3.0
const TARGET_RELEVANCE_SCORE = 0.8
const TARGET_COVERAGE = 0.7

interface MetricCardProps {
  title: string
  value: string
  target: string
  progress: number
  meetsTarget: boolean
  icon: React.ReactNode
}

function MetricCard({ title, value, target, progress, meetsTarget, icon }: MetricCardProps) {
  return (
    <Card className="border-mediterranean-azure/20">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-mediterranean-navy/70">{title}</CardTitle>
        <div className={meetsTarget ? 'text-green-600' : 'text-mediterranean-terracotta'}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-mediterranean-navy">{value}</div>
        <p className="text-xs text-mediterranean-navy/60 mb-2">Cible: {target}</p>
        <Progress
          value={Math.min(progress, 100)}
          className="h-2"
          style={{
            ['--progress-color' as string]: meetsTarget ? '#16a34a' : '#E76F51',
          }}
        />
        <div className="flex items-center mt-2">
          <span
            className={`text-xs font-medium ${meetsTarget ? 'text-green-600' : 'text-mediterranean-terracotta'}`}
          >
            {meetsTarget ? 'Objectif atteint' : 'En dessous de l\'objectif'}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

export function MetricsSummary() {
  const { report } = useRagasStore()

  if (!report) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="border-mediterranean-azure/20">
            <CardHeader className="pb-2">
              <div className="h-4 bg-mediterranean-sky/30 rounded w-20 animate-pulse" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-mediterranean-sky/30 rounded w-16 mb-2 animate-pulse" />
              <div className="h-2 bg-mediterranean-sky/30 rounded w-full animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const { metrics } = report

  // Calculate progress percentages
  // For latency, lower is better (inverse calculation)
  const latencyProgress = Math.max(0, ((TARGET_LATENCY_SECONDS - metrics.avg_latency) / TARGET_LATENCY_SECONDS) * 100 + 100)
  const relevanceProgress = (metrics.avg_relevance / TARGET_RELEVANCE_SCORE) * 100
  const coverageProgress = (metrics.avg_coverage / TARGET_COVERAGE) * 100
  const successProgress = metrics.success_rate * 100

  // Check if targets are met
  const latencyMeetsTarget = metrics.avg_latency <= TARGET_LATENCY_SECONDS
  const relevanceMeetsTarget = metrics.avg_relevance >= TARGET_RELEVANCE_SCORE
  const coverageMeetsTarget = metrics.avg_coverage >= TARGET_COVERAGE
  const successMeetsTarget = metrics.success_rate >= 0.7 // 70% success rate target

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="Latence Moyenne"
        value={formatLatency(metrics.avg_latency)}
        target={`< ${formatLatency(TARGET_LATENCY_SECONDS)}`}
        progress={latencyMeetsTarget ? 100 : Math.max(0, latencyProgress)}
        meetsTarget={latencyMeetsTarget}
        icon={<Clock className="h-4 w-4" />}
      />
      <MetricCard
        title="Pertinence Moyenne"
        value={`${(metrics.avg_relevance * 100).toFixed(1)}%`}
        target={`> ${(TARGET_RELEVANCE_SCORE * 100).toFixed(0)}%`}
        progress={relevanceProgress}
        meetsTarget={relevanceMeetsTarget}
        icon={<Target className="h-4 w-4" />}
      />
      <MetricCard
        title="Couverture Moyenne"
        value={`${(metrics.avg_coverage * 100).toFixed(1)}%`}
        target={`> ${(TARGET_COVERAGE * 100).toFixed(0)}%`}
        progress={coverageProgress}
        meetsTarget={coverageMeetsTarget}
        icon={<Layers className="h-4 w-4" />}
      />
      <MetricCard
        title="Taux de Succes"
        value={`${(metrics.success_rate * 100).toFixed(1)}%`}
        target="> 70%"
        progress={successProgress}
        meetsTarget={successMeetsTarget}
        icon={<CheckCircle className="h-4 w-4" />}
      />
    </div>
  )
}
