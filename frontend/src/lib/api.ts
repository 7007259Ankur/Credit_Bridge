import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({
    baseURL: '/api',
    headers: { 'Content-Type': 'application/json' },
})

// Attach JWT
api.interceptors.request.use((config) => {
    const token = useAuthStore.getState().token
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

// Auto-refresh on 401
api.interceptors.response.use(
    (res) => res,
    async (error) => {
        const original = error.config
        if (error.response?.status === 401 && !original._retry) {
            original._retry = true
            try {
                const refreshToken = useAuthStore.getState().refreshToken
                const res = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
                useAuthStore.getState().setTokens(res.data.access_token, res.data.refresh_token, useAuthStore.getState().user!)
                original.headers.Authorization = `Bearer ${res.data.access_token}`
                return api(original)
            } catch {
                useAuthStore.getState().logout()
            }
        }
        return Promise.reject(error)
    }
)

export default api
