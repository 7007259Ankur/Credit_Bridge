import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export function getScoreBandColor(score: number): string {
    if (score < 580) return 'text-red-600'
    if (score < 670) return 'text-orange-500'
    if (score < 740) return 'text-yellow-500'
    if (score < 800) return 'text-blue-500'
    return 'text-green-600'
}

export function getScoreBandBg(score: number): string {
    if (score < 580) return 'bg-red-100'
    if (score < 670) return 'bg-orange-100'
    if (score < 740) return 'bg-yellow-100'
    if (score < 800) return 'bg-blue-100'
    return 'bg-green-100'
}
