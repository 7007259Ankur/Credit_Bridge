import { Outlet, NavLink } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import Button from '@/components/Button'

const navItems = [
    { to: '/applicant/consent', label: 'Data Consent' },
    { to: '/applicant/psychometric', label: 'Questionnaire' },
]

export default function ApplicantLayout() {
    const { logout } = useAuthStore()

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <span className="font-bold text-blue-600 text-lg">CreditBridge</span>
                <div className="flex items-center gap-6">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={({ isActive }) =>
                                `text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'}`
                            }
                        >
                            {item.label}
                        </NavLink>
                    ))}
                    <Button variant="ghost" size="sm" onClick={logout}>Sign out</Button>
                </div>
            </nav>
            <main className="max-w-3xl mx-auto px-4 py-8">
                <Outlet />
            </main>
        </div>
    )
}
