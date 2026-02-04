import { useQuery } from '@tanstack/react-query'
import { healthApi } from '@/lib/api/endpoints'
import type { HealthResponse } from '@/lib/api/types'

interface UseHealthPollingOptions {
  enabled?: boolean
  refetchInterval?: number
}

interface UseHealthPollingResult {
  data: HealthResponse | undefined
  isLoading: boolean
  isError: boolean
  error: Error | null
  lastUpdated: Date | null
  consecutiveSuccesses: number
}

// Track consecutive successes for uptime indicator
let consecutiveSuccessCount = 0

export function useHealthPolling(options: UseHealthPollingOptions = {}): UseHealthPollingResult {
  const { enabled = true, refetchInterval = 5000 } = options

  const query = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const result = await healthApi.check()
      consecutiveSuccessCount++
      return result
    },
    refetchInterval: enabled ? refetchInterval : false,
    retry: 2,
    staleTime: 0,
  })

  // Reset consecutive count on error
  if (query.isError) {
    consecutiveSuccessCount = 0
  }

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    lastUpdated: query.dataUpdatedAt ? new Date(query.dataUpdatedAt) : null,
    consecutiveSuccesses: consecutiveSuccessCount,
  }
}
