'use client'

import React from 'react'
import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'elevated' | 'subtle'
  spotlight?: boolean
}

export function GlassCard({ 
  children, 
  className, 
  variant = 'default',
  spotlight = false 
}: GlassCardProps) {
  const cardRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (!spotlight || !cardRef.current) return

    const card = cardRef.current
    
    const handleMouseMove = (e: MouseEvent) => {
      const rect = card.getBoundingClientRect()
      const x = ((e.clientX - rect.left) / rect.width) * 100
      const y = ((e.clientY - rect.top) / rect.height) * 100
      card.style.setProperty('--mouse-x', `${x}%`)
      card.style.setProperty('--mouse-y', `${y}%`)
    }

    card.addEventListener('mousemove', handleMouseMove)
    return () => card.removeEventListener('mousemove', handleMouseMove)
  }, [spotlight])

  return (
    <div
      ref={cardRef}
      className={cn(
        'glass-card',
        spotlight && 'spotlight-card',
        variant === 'elevated' && 'shadow-2xl',
        variant === 'subtle' && 'bg-opacity-40 backdrop-blur-md',
        className
      )}
    >
      {children}
    </div>
  )
}
