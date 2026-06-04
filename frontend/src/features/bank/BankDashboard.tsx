import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { Card, CardHeader, CardTitle } from '@/components/Card'
import Button from '@/components/Button'
import Input from '@/components/Input'
import ScoreGauge from '@/components/ScoreGauge'

export default function BankDashboard() {
    const { logout } = useAuthStore()
    const [searchId, setSearchId] = useState('')
    const [userId, setUserId] = useState<number | null>(null)

    const { data: scores, isLoading, error } = useQuery({
        queryKey: ['bank-score', userId],
        queryFn: () => api.get(`/scoring/user/${userId}/latest`).then((r) => r.data),
        enabled: !!userId,
    })

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <span className="font-bold text-blue-600 text-lg">CreditBridge — Bank Officer</span>
                <Button variant="ghost" size="sm" onClick={logout}>Sign out</Button>
            </nav>

            <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
                <h1 className="text-2xl font-bold text-gray-900">Applicant Score Lookup</h1>

                <Card>
                    <div className="flex gap-3">
                        <Input
                            placeholder="Enter applicant user ID"
                            value={searchId}
                            onChange={(e) => setSearchId(e.target.value)}
                            className="max-w-xs"
                        />
                        <Button onClick={() => setUserId(parseInt(searchId))} disabled={!searchId}>
                            Lookup
                        </Button>
                    </div>
                </Card>

                {isLoading && <div className="text-center text-gray-500 py-8">Loading...</div>}
                {error && <div className="text-center text-red-500 py-8">No score found for this user.</div>}

                {scores && (
                    <div className="space-y-6">
                        <Card className="flex flex-col md:flex-row items-center gap-8">
                            <ScoreGauge score={scores.final_score} band={scores.score_band} />
                            <div className="space-y-2">
                                <p className="text-sm text-gray-500">User ID: {userId}</p>
                                <p className="font-semibold text-lg">
                                    Score Band: <span className="capitalize">{scores.score_band?.replace('_', ' ')}</span>
                                </p>
                                <p className="text-gray-700">{scores.recommendation}</p>
                            </div>
                        </Card>

                        <Card>
                            <CardHeader><CardTitle>Agent Breakdown</CardTitle></CardHeader>
                            <div className="space-y-3">
                                {scores.agent_scores?.map((a: any) => (
                                    <div key={a.agent_name} className="border-b pb-3 last:border-0">
                                        <div className="flex justify-between mb-1">
                                            <span className="text-sm font-medium">{a.agent_name}</span>
                                            <span className="text-sm font-bold text-blue-600">{a.raw_score.toFixed(0)}/100</span>
                                        </div>
                                        <p className="text-xs text-gray-500">{a.explanation}</p>
                                        <div className="bg-gray-100 rounded-full h-1.5 mt-2">
                                            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${a.raw_score}%` }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    </div>
                )}
            </main>
        </div>
    )
}
