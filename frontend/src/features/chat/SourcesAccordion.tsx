import type { DocumentResult, Location, DateRange } from '@/lib/api/types'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { Badge } from '@/components/ui/badge'
import { formatPrice, formatSimilarity, getCategoryColor } from '@/lib/utils/format'
import { formatDateRange } from '@/lib/utils/date'
import { Calendar, MapPin, Tag, Target } from 'lucide-react'

interface SourcesAccordionProps {
  sources: DocumentResult[]
}

// Type guards for metadata fields
function isLocation(value: unknown): value is Location {
  return (
    typeof value === 'object' &&
    value !== null &&
    'city' in value &&
    typeof (value as Location).city === 'string'
  )
}

function isDateRange(value: unknown): value is DateRange {
  return (
    typeof value === 'object' &&
    value !== null &&
    'start' in value &&
    'end' in value &&
    typeof (value as DateRange).start === 'string' &&
    typeof (value as DateRange).end === 'string'
  )
}

function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number'
}

function isBoolean(value: unknown): value is boolean {
  return typeof value === 'boolean'
}

export function SourcesAccordion({ sources }: SourcesAccordionProps) {
  if (!sources || sources.length === 0) {
    return null
  }

  return (
    <div className="mt-4">
      <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="sources">
          <AccordionTrigger className="text-sm font-medium">
            📚 Sources ({sources.length} événement{sources.length > 1 ? 's' : ''})
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              {sources.map((source, index) => {
                const metadata = source.metadata || {}
                const title = (isString(metadata.title) ? metadata.title : null) || source.title || 'Sans titre'
                const category = isString(metadata.category) ? metadata.category : undefined
                const location = isLocation(metadata.location) ? metadata.location : undefined
                const dateRange = isDateRange(metadata.date_range) ? metadata.date_range : undefined
                const price = isNumber(metadata.price) ? metadata.price : undefined
                const isFree = isBoolean(metadata.is_free) ? metadata.is_free : undefined

                return (
                  <div
                    key={index}
                    className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                  >
                    {/* Header with title and similarity */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h4 className="font-medium text-sm leading-tight flex-1">
                        {title}
                      </h4>
                      <Badge
                        variant="outline"
                        className="shrink-0 text-xs"
                      >
                        <Target className="h-3 w-3 mr-1" />
                        {formatSimilarity(source.similarity)}
                      </Badge>
                    </div>

                    {/* Metadata */}
                    <div className="space-y-1.5 text-xs text-muted-foreground">
                      {/* Date */}
                      {dateRange && (
                        <div className="flex items-center gap-1.5">
                          <Calendar className="h-3 w-3 shrink-0" />
                          <span>
                            {formatDateRange(dateRange.start, dateRange.end)}
                          </span>
                        </div>
                      )}

                      {/* Location */}
                      {location?.city && (
                        <div className="flex items-center gap-1.5">
                          <MapPin className="h-3 w-3 shrink-0" />
                          <span>
                            {location.city}
                            {location.address && ` - ${location.address}`}
                          </span>
                        </div>
                      )}

                      {/* Category and Price */}
                      <div className="flex items-center gap-2 flex-wrap">
                        {category && (
                          <Badge
                            className={`${getCategoryColor(category)} text-white text-xs`}
                          >
                            <Tag className="h-3 w-3 mr-1" />
                            {category}
                          </Badge>
                        )}
                        <Badge variant={isFree ? 'success' : 'secondary'} className="text-xs">
                          {formatPrice(price)}
                        </Badge>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  )
}
