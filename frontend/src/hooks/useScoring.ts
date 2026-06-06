import { useQuery, useMutation } from '@tanstack/react-query'
import api from '@/lib/api'

export function useInitiateScoring() {
    return useMutation({
        mutationFn: () => api.post('/scoring/initiate').then((r) => r.data),
    })
}

export function useRunStatus(runId: number | null) {
    return useQuery({
        queryKey: ['run-status', runId],
        queryFn: () => api.get(`/scoring/${runId}/status`).then((r) => r.data),
        enabled: !!runId,
        refetchInterval: (query: any) =>
            query.state.data?.status === 'completed' || query.state.data?.status === 'failed' ? false : 2000,
    })
}

export function useScoringResult(runId: number | null) {
    return useQuery({
        queryKey: ['scoring-result', runId],
        queryFn: () => api.get(`/scoring/${runId}/result`).then((r) => r.data),
        enabled: !!runId,
    })
}
