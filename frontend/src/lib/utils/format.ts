/**
 * Format price in euros
 */
export function formatPrice(price: number | undefined): string {
  if (price === undefined || price === 0) {
    return 'Gratuit'
  }
  return `${price.toFixed(2)} €`
}

/**
 * Format similarity score as percentage
 */
export function formatSimilarity(score: number): string {
  return `${(score * 100).toFixed(1)}%`
}

/**
 * Truncate text to max length with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Capitalize first letter
 */
export function capitalize(text: string): string {
  if (!text) return ''
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
}

/**
 * Format latency in seconds
 */
export function formatLatency(seconds: number): string {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`
  }
  return `${seconds.toFixed(2)}s`
}

/**
 * Get category color for badges
 */
export function getCategoryColor(category?: string): string {
  if (!category) return 'bg-gray-500'

  const lowerCategory = category.toLowerCase()

  if (lowerCategory.includes('concert') || lowerCategory.includes('musique')) {
    return 'bg-mediterranean-turquoise'
  }
  if (lowerCategory.includes('expo') || lowerCategory.includes('art')) {
    return 'bg-mediterranean-ochre'
  }
  if (lowerCategory.includes('théâtre') || lowerCategory.includes('spectacle')) {
    return 'bg-mediterranean-terracotta'
  }
  if (lowerCategory.includes('festival')) {
    return 'bg-mediterranean-azure'
  }

  return 'bg-mediterranean-sky'
}
