import { useNavigate } from 'react-router-dom'
import { useConsentStatus, useGrantConsent, useRevokeConsent } from '@/hooks/useConsent'
import { useInitiateScoring } from '@/hooks/useScoring'
import { Card, CardHeader, CardTitle } from '@/components/Card'
import Button from '@/components/Button'

const SOURCE_LABELS: Record<string, { label: string; description: string }> = {
    phone: { label: 'Phone Bills', description: 'Telecom payment history for consistency scoring' },
    ecommerce: { label: 'E-Commerce', description: 'Purchase patterns from online shopping platforms' },
    bank: { label: 'Bank Statements', description: 'Transaction history for cashflow analysis' },
    merchant: { label: 'Merchant Data', description: 'Point-of-sale transactions and disputes' },
    geo: { label: 'Geolocation', description: 'Residence stability and location history' },
    psychometric: { label: 'Psychometric', description: 'Financial behaviour questionnaire results' },
}

export default function ConsentPage() {
    const navigate = useNavigate()
    const { data, isLoading } = useConsentStatus()
    const grant = useGrantConsent()
    const revoke = useRevokeConsent()
    const initiate = useInitiateScoring()

    const handleStartScoring = () => {
        initiate.mutate(undefined, {
            onSuccess: (res) => navigate(`/applicant/score/${res.run_id}`),
        })
    }

    if (isLoading) return <div className="text-center py-12 text-gray-500">Loading...</div>

    const consents: any[] = data?.consents ?? []
    const grantedCount = consents.filter((c) => c.granted).length

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Data Consent</h1>
                <p className="text-gray-500 text-sm mt-1">
                    Grant access to data sources for your credit score. You can revoke consent at any time.
                </p>
            </div>

            <div className="grid gap-4">
                {consents.map((consent) => {
                    const info = SOURCE_LABELS[consent.source_type] ?? { label: consent.source_type, description: '' }
                    return (
                        <Card key={consent.source_type} className="flex items-center justify-between">
                            <div>
                                <p className="font-medium text-gray-900">{info.label}</p>
                                <p className="text-sm text-gray-500">{info.description}</p>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className={`text-xs font-medium px-2 py-1 rounded-full ${consent.granted ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                                    {consent.granted ? 'Granted' : 'Not granted'}
                                </span>
                                {consent.granted ? (
                                    <Button
                                        variant="danger"
                                        size="sm"
                                        loading={revoke.isPending}
                                        onClick={() => revoke.mutate(consent.source_type)}
                                    >
                                        Revoke
                                    </Button>
                                ) : (
                                    <Button
                                        size="sm"
                                        loading={grant.isPending}
                                        onClick={() => grant.mutate(consent.source_type)}
                                    >
                                        Grant
                                    </Button>
                                )}
                            </div>
                        </Card>
                    )
                })}
            </div>

            <div className="flex items-center justify-between pt-4 border-t">
                <p className="text-sm text-gray-500">{grantedCount} of {consents.length} sources granted</p>
                <Button
                    size="lg"
                    onClick={handleStartScoring}
                    loading={initiate.isPending}
                    disabled={grantedCount === 0}
                >
                    Generate Credit Score
                </Button>
            </div>
        </div>
    )
}
