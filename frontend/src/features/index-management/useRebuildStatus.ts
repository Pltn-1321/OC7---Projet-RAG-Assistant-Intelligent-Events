import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api/endpoints'
import type { RebuildStatusResponse } from '@/lib/api/types'

/**
 * Custom hook to poll rebuild status with automatic refetching
 * Polls every 2 seconds while status is 'in_progress'
 */
export function useRebuildStatus(taskId: string | null) {
  return useQuery<RebuildStatusResponse>({
    queryKey: ['rebuild', taskId],
    queryFn: () => api.rebuild.getStatus(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data
      return data?.status === 'in_progress' ? 2000 : false
    },
    refetchIntervalInBackground: false,
    staleTime: 1000,
    retry: 2,
  })
}
