import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { useLogin } from '@/hooks/useAuth'
import Input from '@/components/Input'
import Button from '@/components/Button'

const schema = z.object({
    email: z.string().email('Invalid email'),
    password: z.string().min(6, 'Min 6 characters'),
})
type Form = z.infer<typeof schema>

export default function LoginPage() {
    const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema) })
    const login = useLogin()

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
            <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">CreditBridge</h1>
                    <p className="text-gray-500 text-sm mt-1">Explainable credit scoring</p>
                </div>

                <form onSubmit={handleSubmit((d) => login.mutate(d))} className="space-y-4">
                    <Input
                        id="email"
                        label="Email"
                        type="email"
                        placeholder="you@example.com"
                        error={errors.email?.message}
                        {...register('email')}
                    />
                    <Input
                        id="password"
                        label="Password"
                        type="password"
                        placeholder="••••••••"
                        error={errors.password?.message}
                        {...register('password')}
                    />

                    {login.isError && (
                        <p className="text-sm text-red-600 text-center">Invalid credentials</p>
                    )}

                    <Button type="submit" className="w-full" loading={login.isPending} size="lg">
                        Sign in
                    </Button>
                </form>

                <p className="text-center text-sm text-gray-500 mt-6">
                    No account?{' '}
                    <Link to="/register" className="text-blue-600 hover:underline">Register here</Link>
                </p>
            </div>
        </div>
    )
}
