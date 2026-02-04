import type { DocumentResult } from '@/lib/api/types'
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
                const title = metadata.title || source.title || 'Sans titre'
                const category = metadata.category
                const location = metadata.location
                const dateRange = metadata.date_range
                const price = metadata.price
                const isFree = metadata.is_free

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
