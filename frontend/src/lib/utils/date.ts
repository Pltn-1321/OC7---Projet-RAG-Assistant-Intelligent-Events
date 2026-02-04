import { format, formatDistance } from 'date-fns'
import { fr } from 'date-fns/locale'

/**
 * Format date as relative time (e.g., "il y a 2 minutes")
 */
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return formatDistance(dateObj, new Date(), { addSuffix: true, locale: fr })
}

/**
 * Format date as "15 janvier 2024 à 14:30"
 */
export function formatDateTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return format(dateObj, "d MMMM yyyy 'à' HH:mm", { locale: fr })
}

/**
 * Format date as "15/01/2024"
 */
export function formatDateShort(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return format(dateObj, 'dd/MM/yyyy')
}

/**
 * Format date range as "15-20 janvier 2024"
 */
export function formatDateRange(start: string | Date, end: string | Date): string {
  const startDate = typeof start === 'string' ? new Date(start) : start
  const endDate = typeof end === 'string' ? new Date(end) : end

  // Same day
  if (formatDateShort(startDate) === formatDateShort(endDate)) {
    return format(startDate, "d MMMM yyyy", { locale: fr })
  }

  // Same month
  if (startDate.getMonth() === endDate.getMonth() && startDate.getFullYear() === endDate.getFullYear()) {
    return `${format(startDate, 'd', { locale: fr })}-${format(endDate, "d MMMM yyyy", { locale: fr })}`
  }

  // Different months
  return `${format(startDate, "d MMMM", { locale: fr })} - ${format(endDate, "d MMMM yyyy", { locale: fr })}`
}

/**
 * Check if date is in the past
 */
export function isPast(date: string | Date): boolean {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return dateObj < new Date()
}

/**
 * Check if date is upcoming (in the future)
 */
export function isUpcoming(date: string | Date): boolean {
  return !isPast(date)
}
