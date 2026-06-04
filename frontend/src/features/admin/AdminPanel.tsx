import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import api from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { Card, CardHeader, CardTitle } from '@/components/Card'
import Button from '@/components/Button'
import Input from '@/components/Input'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const WEIGHT_FIELDS = [
    { key: 'cashflow', label: 'Cashflow Agent' },
    { key: 'phone_bill', label: 'Phone Bill Agent' },
    { key: 'ecommerce', label: 'E-commerce Agent' },
    { key: 'psychometric', label: 'Psychometric Agent' },
    { key: 'merchant', label: 'Merchant Agent' },
    { key: 'geolocation', label: 'Geolocation Agent' },
    { key: 'risk_synthesizer', label: 'Risk Synthesizer' },
]

export default function AdminPanel() {
    const { logout } = useAuthStore()
    const qc = useQueryClient()

    const { data: weights } = useQuery({
        queryKey: ['admin-weights'],
        queryFn: () => api.get('/admin/weights').then((r) => r.data),
    })

    const { data: analytics } = useQuery({
        queryKey: ['admin-analytics'],
        queryFn: () => api.get('/admin/analytics').then((r) => r.data),
    })

    const { register, handleSubmit, watch } = useForm({ values: weights })

    const updateWeights = useMutation({
        mutationFn: (data: any) => api.put('/admin/weights', data).then((r) => r.data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-weights'] }),
    })

    const currentValues = watch()
    const total = WEIGHT_FIELDS.reduce((sum, f) => sum + (parseFloat(currentValues[f.key]) || 0), 0)

    const chartData = WEIGHT_FIELDS.map((f) => ({
        name: f.label.replace(' Agent', ''),
        weight: parseFloat(currentValues?.[f.key] ?? 0),
    }))

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <span className="font-bold text-blue-600 text-lg">CreditBridge — Admin</span>
                <Button variant="ghost" size="sm" onClick={logout}>Sign out</Button>
            </nav>

            <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
                <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>

                {/* Analytics */}
                {analytics && (
                    <div className="grid grid-cols-3 gap-4">
                        <Card className="text-center">
                            <p className="text-3xl font-bold text-blue-600">{analytics.total_runs}</p>
                            <p className="text-sm text-gray-500 mt-1">Total Runs</p>
                        </Card>
                        <Card className="text-center">
                            <p className="text-3xl font-bold text-green-600">{analytics.completed_runs}</p>
                            <p className="text-sm text-gray-500 mt-1">Completed</p>
                        </Card>
                        <Card className="text-center">
                            <p className="text-3xl font-bold text-indigo-600">{analytics.average_score ?? '—'}</p>
                            <p className="text-sm text-gray-500 mt-1">Avg Score</p>
                        </Card>
                    </div>
                )}

                {/* Weight Configuration */}
                <Card>
                    <CardHeader>
                        <CardTitle>Agent Weight Configuration</CardTitle>
                        <p className="text-sm text-gray-500 mt-1">
                            Adjust scoring weights. Total must equal 1.00. Current: <span className={Math.abs(total - 1) > 0.01 ? 'text-red-600 font-bold' : 'text-green-600 font-bold'}>{total.toFixed(2)}</span>
                        </p>
                    </CardHeader>

                    <form onSubmit={handleSubmit((d) => updateWeights.mutate(d))} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            {WEIGHT_FIELDS.map((f) => (
                                <Input
                                    key={f.key}
                                    id={f.key}
                                    label={f.label}
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    max="1"
                                    {...register(f.key, { valueAsNumber: true })}
                                />
                            ))}
                        </div>

                        <Button
                            type="submit"
                            loading={updateWeights.isPending}
                            disabled={Math.abs(total - 1) > 0.01}
                        >
                            Save Weights
                        </Button>
                        {updateWeights.isSuccess && <span className="text-sm text-green-600 ml-3">Saved</span>}
                    </form>
                </Card>

                {/* Weight chart */}
                <Card>
                    <CardHeader><CardTitle>Weight Distribution</CardTitle></CardHeader>
                    <ResponsiveContainer width="100%" height={220}>
                        <BarChart data={chartData}>
                            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                            <YAxis domain={[0, 0.4]} />
                            <Tooltip formatter={(v: any) => `${(v * 100).toFixed(0)}%`} />
                            <Bar dataKey="weight" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </Card>
            </main>
        </div>
    )
}
