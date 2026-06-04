import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

// Auth
import LoginPage from '@/features/auth/LoginPage'
import RegisterPage from '@/features/auth/RegisterPage'

// Applicant
import ApplicantLayout from '@/features/applicant/ApplicantLayout'
import ConsentPage from '@/features/applicant/ConsentPage'
import PsychometricPage from '@/features/applicant/PsychometricPage'
import ScoreResultPage from '@/features/applicant/ScoreResultPage'

// Bank
import BankDashboard from '@/features/bank/BankDashboard'

// Admin
import AdminPanel from '@/features/admin/AdminPanel'

function RequireAuth({ children, role }: { children: JSX.Element; role?: string }) {
    const { token, user } = useAuthStore()
    if (!token) return <Navigate to="/login" replace />
    if (role && user?.role !== role) return <Navigate to="/" replace />
    return children
}

export default function App() {
    const { user } = useAuthStore()

    const homeRedirect = () => {
        if (!user) return <Navigate to="/login" replace />
        if (user.role === 'admin') return <Navigate to="/admin" replace />
        if (user.role === 'bank_officer') return <Navigate to="/bank" replace />
        return <Navigate to="/applicant/consent" replace />
    }

    return (
        <Routes>
            <Route path="/" element={homeRedirect()} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route path="/applicant" element={
                <RequireAuth role="applicant"><ApplicantLayout /></RequireAuth>
            }>
                <Route path="consent" element={<ConsentPage />} />
                <Route path="psychometric" element={<PsychometricPage />} />
                <Route path="score/:runId" element={<ScoreResultPage />} />
                <Route index element={<Navigate to="consent" replace />} />
            </Route>

            <Route path="/bank" element={
                <RequireAuth role="bank_officer"><BankDashboard /></RequireAuth>
            } />

            <Route path="/admin" element={
                <RequireAuth role="admin"><AdminPanel /></RequireAuth>
            } />
        </Routes>
    )
}
