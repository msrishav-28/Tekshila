'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { GlassCard } from '@/components/GlassCard'
import { MagneticButton } from '@/components/MagneticButton'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function GitHubCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    const code = searchParams.get('code')
    
    if (!code) {
      setError('No authorization code received from GitHub')
      setIsProcessing(false)
      return
    }

    const exchangeCode = async () => {
      try {
        const response = await fetch(`${API_URL}/auth/github/callback?code=${code}`, {
          method: 'POST'
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.detail || 'Authentication failed')
        }

        const data = await response.json()
        
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        
        router.push('/dashboard')
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Authentication failed')
        setIsProcessing(false)
      }
    }

    exchangeCode()
  }, [searchParams, router])

  return (
    <div className="min-h-screen bg-void flex items-center justify-center p-4">
      <GlassCard className="p-12 max-w-md w-full text-center" spotlight>
        {isProcessing ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="w-16 h-16 mx-auto relative">
              <motion.div
                className="absolute inset-0 border-4 border-crimson/20 rounded-full"
              />
              <motion.div
                className="absolute inset-0 border-4 border-transparent border-t-crimson rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
            </div>
            <div>
              <span className="micro-label text-crimson block mb-2">AUTHENTICATING</span>
              <h2 className="headline-display text-2xl">Connecting to GitHub</h2>
              <p className="text-silver-400 mt-2">Exchanging credentials...</p>
            </div>
          </motion.div>
        ) : error ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="w-16 h-16 mx-auto bg-crimson/10 rounded-full flex items-center justify-center">
              <span className="text-crimson text-3xl">!</span>
            </div>
            <div>
              <span className="micro-label text-crimson block mb-2">ERROR</span>
              <h2 className="headline-display text-2xl">Authentication Failed</h2>
              <p className="text-silver-400 mt-2">{error}</p>
            </div>
            <MagneticButton onClick={() => router.push('/')} variant="secondary">
              Return Home
            </MagneticButton>
          </motion.div>
        ) : null}
      </GlassCard>
    </div>
  )
}
