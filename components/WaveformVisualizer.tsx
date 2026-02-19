'use client'

import React, { useEffect, useRef } from 'react'

interface WaveformVisualizerProps {
  isActive: boolean
  className?: string
}

export function WaveformVisualizer({ isActive, className }: WaveformVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const timeRef = useRef(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }
    resize()
    window.addEventListener('resize', resize)

    const bars = 64
    const barWidth = canvas.offsetWidth / bars

    const animate = () => {
      if (!isActive) {
        // Draw idle state - subtle pulse
        ctx.fillStyle = 'rgba(5, 5, 5, 0.8)'
        ctx.fillRect(0, 0, canvas.offsetWidth, canvas.offsetHeight)
        
        for (let i = 0; i < bars; i++) {
          const x = i * barWidth
          const baseHeight = canvas.offsetHeight * 0.1
          const pulse = Math.sin(timeRef.current * 2 + i * 0.1) * 5
          const height = baseHeight + pulse
          
          const gradient = ctx.createLinearGradient(0, canvas.offsetHeight - height, 0, canvas.offsetHeight)
          gradient.addColorStop(0, 'rgba(244, 63, 94, 0.3)')
          gradient.addColorStop(1, 'rgba(244, 63, 94, 0.05)')
          
          ctx.fillStyle = gradient
          ctx.fillRect(x + 1, canvas.offsetHeight - height, barWidth - 2, height)
        }
      } else {
        // Draw active analyzing state
        ctx.fillStyle = 'rgba(5, 5, 5, 0.8)'
        ctx.fillRect(0, 0, canvas.offsetWidth, canvas.offsetHeight)
        
        for (let i = 0; i < bars; i++) {
          const x = i * barWidth
          
          // Multiple sine waves for complex motion
          const wave1 = Math.sin(timeRef.current * 3 + i * 0.2) * 0.5 + 0.5
          const wave2 = Math.sin(timeRef.current * 5 + i * 0.15) * 0.3 + 0.3
          const wave3 = Math.sin(timeRef.current * 2 + i * 0.3) * 0.2 + 0.2
          
          const amplitude = wave1 + wave2 + wave3
          const height = (canvas.offsetHeight * 0.8) * amplitude * (0.3 + Math.random() * 0.1)
          
          const gradient = ctx.createLinearGradient(0, canvas.offsetHeight - height, 0, canvas.offsetHeight)
          gradient.addColorStop(0, '#F43F5E')
          gradient.addColorStop(0.5, 'rgba(244, 63, 94, 0.5)')
          gradient.addColorStop(1, 'rgba(244, 63, 94, 0.1)')
          
          ctx.fillStyle = gradient
          ctx.fillRect(x + 1, canvas.offsetHeight - height, barWidth - 2, height)
        }
        
        // Add glow effect
        ctx.shadowBlur = 20
        ctx.shadowColor = 'rgba(244, 63, 94, 0.5)'
      }
      
      timeRef.current += 0.016
      animationRef.current = requestAnimationFrame(animate)
    }
    
    animate()
    
    return () => {
      window.removeEventListener('resize', resize)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isActive])

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{ width: '100%', height: '100%' }}
    />
  )
}
