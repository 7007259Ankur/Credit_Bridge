import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { useRegister } from '@/hooks/useAuth'
import Input from '@/components/Input'
import Button from '@/components/Button'

const schema = z.object({
    full_name: z.string().min(2, 'Required'),
    email: z.string().email('Invalid email'),
    password: z.string().min(8, 'Min 8 characters'),
})
type Form = z.infer<typeof schema>

export default function RegisterPage() {
    const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema) })
    const registerMutation = useRegister()

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
            <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
                    <p className="text-gray-500 text-sm mt-1">Start your credit journey</p>
                </div>

                <form onSubmit={handleSubmit((d) => registerMutation.mutate({ ...d, role: 'applicant' }))} className="space-y-4">
                    <Input id="full_name" label="Full Name" placeholder="Your Name" error={errors.full_name?.message} {...register('full_name')} />
                    <Input id="email" label="Email" type="email" placeholder="you@example.com" error={errors.email?.message} {...register('email')} />
                    <Input id="password" label="Password" type="password" placeholder="••••••••" error={errors.password?.message} {...register('password')} />

                    {registerMutation.isError && (
                        <p className="text-sm text-red-600 text-center">Registration failed. Email may already exist.</p>
                    )}

                    <Button type="submit" className="w-full" loading={registerMutation.isPending} size="lg">
                        Create account
                    </Button>
                </form>

                <p className="text-center text-sm text-gray-500 mt-6">
                    Already have an account?{' '}
                    <Link to="/login" className="text-blue-600 hover:underline">Sign in</Link>
                </p>
            </div>
        </div>
    )
}
