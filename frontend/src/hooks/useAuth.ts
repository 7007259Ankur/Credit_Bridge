import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { jwtDecode } from 'jwt-decode'

interface DecodedToken {
    sub: string
    role: string
}

function extractUser(token: string) {
    const decoded = jwtDecode<DecodedToken>(token)
    return { id: parseInt(decoded.sub), role: decoded.role as any }
}

export function useLogin() {
    const { setTokens } = useAuthStore()
    const navigate = useNavigate()

    return useMutation({
        mutationFn: (data: { email: string; password: string }) =>
            api.post('/auth/login', data).then((r) => r.data),
        onSuccess: (data) => {
            const user = extractUser(data.access_token)
            setTokens(data.access_token, data.refresh_token, user)
            if (user.role === 'admin') navigate('/admin')
            else if (user.role === 'bank_officer') navigate('/bank')
            else navigate('/applicant/consent')
        },
    })
}

export function useRegister() {
    const { setTokens } = useAuthStore()
    const navigate = useNavigate()

    return useMutation({
        mutationFn: (data: { email: string; password: string; full_name: string; role: string }) =>
            api.post('/auth/register', data).then((r) => r.data),
        onSuccess: (data) => {
            const user = extractUser(data.access_token)
            setTokens(data.access_token, data.refresh_token, user)
            navigate('/applicant/consent')
        },
    })
}
