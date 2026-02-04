import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  ReferenceLine,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useRagasStore } from './useRagasStore'

// Mediterranean color palette
const COLORS = {
  azure: '#0E7C7B',
  turquoise: '#17B5B4',
  sky: '#9BDEDF',
  ochre: '#F4A261',
  terracotta: '#E76F51',
  navy: '#0A2F51',
  success: '#16a34a',
  failure: '#E76F51',
}

// Target threshold for latency
const TARGET_LATENCY_SECONDS = 3.0

export function MetricsCharts() {
  const { report } = useRagasStore()

  if (!report) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-mediterranean-azure/20">
          <CardHeader>
            <div className="h-5 bg-mediterranean-sky/30 rounded w-40 animate-pulse" />
          </CardHeader>
          <CardContent>
            <div className="h-[300px] bg-mediterranean-sky/20 rounded animate-pulse" />
          </CardContent>
        </Card>
        <Card className="border-mediterranean-azure/20">
          <CardHeader>
            <div className="h-5 bg-mediterranean-sky/30 rounded w-40 animate-pulse" />
          </CardHeader>
          <CardContent>
            <div className="h-[300px] bg-mediterranean-sky/20 rounded animate-pulse" />
          </CardContent>
        </Card>
      </div>
    )
  }

  // Prepare data for latency bar chart
  const latencyData = report.questions.map((q, index) => ({
    name: `Q${index + 1}`,
    latency: q.latency,
    meetsTarget: q.latency <= TARGET_LATENCY_SECONDS,
    question: q.question.slice(0, 50) + (q.question.length > 50 ? '...' : ''),
  }))

  // Prepare data for pie chart
  const successCount = report.questions.filter((q) => q.success).length
  const failureCount = report.questions.length - successCount
  const pieData = [
    { name: 'Succes', value: successCount, color: COLORS.success },
    { name: 'Echec', value: failureCount, color: COLORS.failure },
  ]

  // Custom tooltip for bar chart
  const LatencyTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: { question: string; latency: number } }> }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white border border-mediterranean-azure/20 rounded-lg shadow-lg p-3">
          <p className="text-sm text-mediterranean-navy font-medium mb-1">{data.question}</p>
          <p className="text-sm text-mediterranean-navy/70">
            Latence: <span className="font-semibold">{data.latency.toFixed(2)}s</span>
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Latency Bar Chart */}
      <Card className="border-mediterranean-azure/20">
        <CardHeader>
          <CardTitle className="text-lg text-mediterranean-navy">Latence par Question</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={latencyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis
                dataKey="name"
                tick={{ fill: COLORS.navy, fontSize: 12 }}
                tickLine={{ stroke: COLORS.navy }}
              />
              <YAxis
                tick={{ fill: COLORS.navy, fontSize: 12 }}
                tickLine={{ stroke: COLORS.navy }}
                label={{
                  value: 'Secondes',
                  angle: -90,
                  position: 'insideLeft',
                  fill: COLORS.navy,
                  fontSize: 12,
                }}
              />
              <Tooltip content={<LatencyTooltip />} />
              <ReferenceLine
                y={TARGET_LATENCY_SECONDS}
                stroke={COLORS.terracotta}
                strokeDasharray="5 5"
                label={{
                  value: 'Cible',
                  position: 'right',
                  fill: COLORS.terracotta,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="latency" radius={[4, 4, 0, 0]}>
                {latencyData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.meetsTarget ? COLORS.turquoise : COLORS.ochre}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Success/Failure Pie Chart */}
      <Card className="border-mediterranean-azure/20">
        <CardHeader>
          <CardTitle className="text-lg text-mediterranean-navy">Distribution Succes/Echec</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                label={({ name, value, percent }) =>
                  `${name ?? ''}: ${value ?? 0} (${(((percent as number) ?? 0) * 100).toFixed(0)}%)`
                }
                labelLine={{ stroke: COLORS.navy, strokeWidth: 1 }}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`${value ?? 0} questions`]}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid rgba(14, 124, 123, 0.2)',
                  borderRadius: '8px',
                }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => <span style={{ color: COLORS.navy }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
