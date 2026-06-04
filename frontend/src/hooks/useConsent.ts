import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'

export function useConsentStatus() {
    return useQuery({
        queryKey: ['consent-status'],
        queryFn: () => api.get('/consent/status').then((r) => r.data),
    })
}

export function useGrantConsent() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: (sourceType: string) => api.post(`/consent/${sourceType}`).then((r) => r.data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['consent-status'] }),
    })
}

export function useRevokeConsent() {
    const qc = useQueryClient()
    return useMutation({
        mutationFn: (sourceType: string) => api.delete(`/consent/${sourceType}`).then((r) => r.data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['consent-status'] }),
    })
}
