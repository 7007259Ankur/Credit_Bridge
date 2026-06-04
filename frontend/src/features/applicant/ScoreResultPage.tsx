import { useParams } from 'react-router-dom'
import { useRunStatus, useScoringResult } from '@/hooks/useScoring'
import ScoreGauge from '@/components/ScoreGauge'
import { Card, CardHeader, CardTitle } from '@/components/Card'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts'

export default function ScoreResultPage() {
    const { runId } = useParams<{ runId: string }>()
    const id = runId ? parseInt(runId) : null

    const { data: status } = useRunStatus(id)
    const { data: result } = useScoringResult(
        status?.status === 'completed' ? id : null
    )

    if (!status || status.status === 'pending' || status.status === 'running') {
        return (
            <div className="flex flex-col items-center justify-center py-24 space-y-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-gray-600 font-medium">Analysing your credit profile...</p>
                <p className="text-sm text-gray-400">Our 7-agent pipeline is working. This takes ~10 seconds.</p>
            </div>
        )
    }

    if (status.status === 'failed') {
        return <div className="text-center py-12 text-red-600">Scoring failed. Please try again.</div>
    }

    if (!result) return null

    const radarData = result.agent_scores.map((a: any) => ({
        subject: a.agent_name.replace('Agent', ''),
        score: a.raw_score,
    }))

    return (
        <div className="space-y-8">
            <h1 className="text-2xl font-bold text-gray-900">Your Credit Score</h1>

            {/* Score + Gauge */}
            <Card className="flex flex-col md:flex-row items-center gap-8">
                <ScoreGauge score={result.final_score} band={result.score_band} />
                <div>
                    <p className="text-sm text-gray-500 uppercase tracking-wide mb-1">Recommendation</p>
                    <p className="text-gray-800 font-medium">{result.recommendation}</p>
                </div>
            </Card>

            {/* Radar Chart */}
            <Card>
                <CardHeader><CardTitle>Agent Score Breakdown</CardTitle></CardHeader>
                <ResponsiveContainer width="100%" height={280}>
                    <RadarChart data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
                        <Radar dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} strokeWidth={2} />
                    </RadarChart>
                </ResponsiveContainer>
            </Card>

            {/* Per-agent details */}
            <div className="space-y-3">
                {result.agent_scores.map((a: any) => (
                    <Card key={a.agent_name}>
                        <div className="flex items-start justify-between mb-2">
                            <p className="font-semibold text-gray-900">{a.agent_name}</p>
                            <span className="text-2xl font-bold text-blue-600">{a.raw_score.toFixed(0)}<span className="text-sm text-gray-400">/100</span></span>
                        </div>
                        <p className="text-sm text-gray-600">{a.explanation}</p>
                        <div className="mt-3 flex gap-2 flex-wrap">
                            {a.signals?.map((s: string) => (
                                <span key={s} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">{s.replace(/_/g, ' ')}</span>
                            ))}
                        </div>
                        <div className="mt-3 bg-gray-100 rounded-full h-2">
                            <div
                                className="bg-blue-500 h-2 rounded-full transition-all duration-700"
                                style={{ width: `${a.raw_score}%` }}
                            />
                        </div>
                        <p className="text-xs text-gray-400 mt-1">Weight: {(a.weight * 100).toFixed(0)}% | Confidence: {(a.confidence * 100).toFixed(0)}%</p>
                    </Card>
                ))}
            </div>
        </div>
    )
}
