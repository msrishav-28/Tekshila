'use client'

import React, { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface MagneticButtonProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  magneticStrength?: number
}

export function MagneticButton({
  children,
  className,
  onClick,
  variant = 'primary',
  size = 'md',
  magneticStrength = 0.3
}: MagneticButtonProps) {
  const ref = useRef<HTMLButtonElement>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!ref.current) return
    
    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    
    const x = (e.clientX - centerX) * magneticStrength
    const y = (e.clientY - centerY) * magneticStrength
    
    setPosition({ x, y })
  }

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 })
  }

  const variants = {
    primary: 'bg-gradient-to-br from-crimson to-crimson-dark text-white shadow-[0_0_0_0_rgba(244,63,94,0.4)] hover:shadow-[0_0_30px_rgba(244,63,94,0.4)]',
    secondary: 'bg-surface border border-glass-stroke text-silver-200 hover:border-glass-highlight',
    ghost: 'bg-transparent text-silver-400 hover:text-silver-200'
  }

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-sm',
    lg: 'px-8 py-4 text-base'
  }

  return (
    <motion.button
      ref={ref}
      className={cn(
        'relative inline-flex items-center justify-center font-ui font-medium rounded-lg transition-all duration-300 ease-out',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-crimson focus-visible:ring-offset-2 focus-visible:ring-offset-void',
        variants[variant],
        sizes[size],
        className
      )}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: 'spring', stiffness: 350, damping: 15, mass: 0.5 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.button>
  )
}
