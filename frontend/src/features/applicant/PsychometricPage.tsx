import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { Card } from '@/components/Card'
import Button from '@/components/Button'

const LIKERT_LABELS = ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree']

export default function PsychometricPage() {
    const navigate = useNavigate()
    const [answers, setAnswers] = useState<Record<number, number>>({})

    const { data: questionsData, isLoading } = useQuery({
        queryKey: ['psychometric-questions'],
        queryFn: () => api.get('/psychometric/questions').then((r) => r.data),
    })

    const submit = useMutation({
        mutationFn: (payload: any) => api.post('/psychometric/submit', payload).then((r) => r.data),
        onSuccess: () => navigate('/applicant/consent'),
    })

    const questions = questionsData?.questions ?? []
    const allAnswered = questions.length > 0 && Object.keys(answers).length === questions.length

    const handleSubmit = () => {
        const formatted = Object.entries(answers).map(([qid, answer]) => ({
            question_id: parseInt(qid),
            answer,
        }))
        submit.mutate({ answers: formatted })
    }

    if (isLoading) return <div className="text-center py-12 text-gray-500">Loading questions...</div>

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Financial Behaviour Questionnaire</h1>
                <p className="text-gray-500 text-sm mt-1">
                    Answer honestly — this helps us understand your financial mindset. {questions.length} questions.
                </p>
            </div>

            <div className="space-y-4">
                {questions.map((q: any) => (
                    <Card key={q.id}>
                        <p className="font-medium text-gray-800 mb-4">{q.id}. {q.text}</p>
                        <div className="flex gap-2 flex-wrap">
                            {LIKERT_LABELS.map((label, i) => {
                                const val = i + 1
                                const selected = answers[q.id] === val
                                return (
                                    <button
                                        key={val}
                                        onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: val }))}
                                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selected
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                            }`}
                                    >
                                        {val} — {label}
                                    </button>
                                )
                            })}
                        </div>
                    </Card>
                ))}
            </div>

            <div className="flex items-center justify-between pt-4 border-t">
                <p className="text-sm text-gray-500">{Object.keys(answers).length} / {questions.length} answered</p>
                <Button
                    size="lg"
                    onClick={handleSubmit}
                    loading={submit.isPending}
                    disabled={!allAnswered}
                >
                    Submit Answers
                </Button>
            </div>
        </div>
    )
}
