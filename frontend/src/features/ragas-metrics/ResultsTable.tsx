import { useState, useMemo } from 'react'
import { ArrowUpDown, ChevronLeft, ChevronRight, CheckCircle, XCircle } from 'lucide-react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useRagasStore } from './useRagasStore'
import { formatLatency, truncate } from '@/lib/utils/format'
import type { QuestionResult } from '@/lib/api/types'

// Target thresholds
const TARGET_LATENCY_SECONDS = 3.0
const TARGET_RELEVANCE_SCORE = 0.8
const TARGET_COVERAGE = 0.7

type SortField = 'question' | 'latency' | 'relevance' | 'coverage' | 'success'
type SortDirection = 'asc' | 'desc'

const ITEMS_PER_PAGE = 10

export function ResultsTable() {
  const { report } = useRagasStore()
  const [sortField, setSortField] = useState<SortField>('latency')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [currentPage, setCurrentPage] = useState(1)

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
    setCurrentPage(1) // Reset to first page on sort
  }

  const sortedData = useMemo(() => {
    if (!report) return []

    return [...report.questions].sort((a, b) => {
      const multiplier = sortDirection === 'asc' ? 1 : -1

      switch (sortField) {
        case 'question':
          return multiplier * a.question.localeCompare(b.question)
        case 'latency':
          return multiplier * (a.latency - b.latency)
        case 'relevance':
          return multiplier * (a.relevance - b.relevance)
        case 'coverage':
          return multiplier * (a.coverage - b.coverage)
        case 'success':
          return multiplier * (Number(a.success) - Number(b.success))
        default:
          return 0
      }
    })
  }, [report, sortField, sortDirection])

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
    return sortedData.slice(startIndex, startIndex + ITEMS_PER_PAGE)
  }, [sortedData, currentPage])

  const totalPages = Math.ceil(sortedData.length / ITEMS_PER_PAGE)

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => handleSort(field)}
      className="h-8 flex items-center gap-1 text-mediterranean-navy/70 hover:text-mediterranean-navy"
    >
      {children}
      <ArrowUpDown className="h-3 w-3" />
    </Button>
  )

  const getMetricBadgeColor = (value: number, target: number, inverse = false) => {
    const meetsTarget = inverse ? value <= target : value >= target
    return meetsTarget ? 'success' : 'destructive'
  }

  if (!report) {
    return (
      <Card className="border-mediterranean-azure/20">
        <CardHeader>
          <CardTitle className="text-lg text-mediterranean-navy">Resultats Detailles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-mediterranean-navy/60">
            Chargez un rapport pour voir les resultats detailles
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-mediterranean-azure/20">
      <CardHeader>
        <CardTitle className="text-lg text-mediterranean-navy">
          Resultats Detailles ({report.questions.length} questions)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border border-mediterranean-azure/20">
          <Table>
            <TableHeader>
              <TableRow className="bg-mediterranean-sky/20 hover:bg-mediterranean-sky/30">
                <TableHead className="w-[40%]">
                  <SortButton field="question">Question</SortButton>
                </TableHead>
                <TableHead className="w-[15%]">
                  <SortButton field="latency">Latence</SortButton>
                </TableHead>
                <TableHead className="w-[15%]">
                  <SortButton field="relevance">Pertinence</SortButton>
                </TableHead>
                <TableHead className="w-[15%]">
                  <SortButton field="coverage">Couverture</SortButton>
                </TableHead>
                <TableHead className="w-[15%] text-center">
                  <SortButton field="success">Statut</SortButton>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedData.map((result: QuestionResult, index: number) => (
                <TableRow
                  key={index}
                  className="hover:bg-mediterranean-sky/10"
                >
                  <TableCell className="font-medium text-mediterranean-navy">
                    <span title={result.question}>{truncate(result.question, 60)}</span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={getMetricBadgeColor(result.latency, TARGET_LATENCY_SECONDS, true)}
                    >
                      {formatLatency(result.latency)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={getMetricBadgeColor(result.relevance, TARGET_RELEVANCE_SCORE)}
                    >
                      {(result.relevance * 100).toFixed(1)}%
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getMetricBadgeColor(result.coverage, TARGET_COVERAGE)}>
                      {(result.coverage * 100).toFixed(1)}%
                    </Badge>
                  </TableCell>
                  <TableCell className="text-center">
                    {result.success ? (
                      <CheckCircle className="h-5 w-5 text-green-600 inline-block" />
                    ) : (
                      <XCircle className="h-5 w-5 text-mediterranean-terracotta inline-block" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-mediterranean-navy/60">
              Page {currentPage} sur {totalPages}
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="border-mediterranean-azure/30"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="border-mediterranean-azure/30"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
