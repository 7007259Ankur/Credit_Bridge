import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    id: number
    role: 'applicant' | 'bank_officer' | 'admin'
}

interface AuthState {
    token: string | null
    refreshToken: string | null
    user: User | null
    setTokens: (token: string, refreshToken: string, user: User) => void
    logout: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            token: null,
            refreshToken: null,
            user: null,
            setTokens: (token, refreshToken, user) => set({ token, refreshToken, user }),
            logout: () => set({ token: null, refreshToken: null, user: null }),
        }),
        { name: 'cb-auth' }
    )
)
