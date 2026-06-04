import { getScoreBandColor } from '@/lib/utils'

interface ScoreGaugeProps {
    score: number
    band: string
}

export default function ScoreGauge({ score, band }: ScoreGaugeProps) {
    const percentage = ((score - 300) / 550) * 100
    const colorClass = getScoreBandColor(score)

    return (
        <div className="flex flex-col items-center">
            <div className="relative w-48 h-48">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                    {/* Background arc */}
                    <circle
                        cx="50" cy="50" r="40"
                        fill="none" stroke="#e5e7eb" strokeWidth="10"
                        strokeDasharray="188 251"
                        strokeLinecap="round"
                    />
                    {/* Score arc */}
                    <circle
                        cx="50" cy="50" r="40"
                        fill="none"
                        stroke={score < 580 ? '#dc2626' : score < 670 ? '#f97316' : score < 740 ? '#eab308' : score < 800 ? '#3b82f6' : '#16a34a'}
                        strokeWidth="10"
                        strokeDasharray={`${(percentage / 100) * 188} 251`}
                        strokeLinecap="round"
                        className="transition-all duration-1000"
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-4xl font-bold ${colorClass}`}>{score}</span>
                    <span className="text-xs text-gray-500 uppercase tracking-wide">{band.replace('_', ' ')}</span>
                </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">300 – 850</p>
        </div>
    )
}
