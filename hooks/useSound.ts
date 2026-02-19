'use client'

import { useEffect, useRef, useCallback } from 'react'

// Subtle UI sound effects using Web Audio API
// These are high-quality synthesized sounds (no external files needed)

export function useSound() {
  const audioContextRef = useRef<AudioContext | null>(null)

  useEffect(() => {
    // Initialize audio context on first user interaction
    const initAudio = () => {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      }
    }

    window.addEventListener('click', initAudio, { once: true })
    return () => window.removeEventListener('click', initAudio)
  }, [])

  // Camera shutter-like click sound
  const playClick = useCallback(() => {
    if (!audioContextRef.current) return
    
    const ctx = audioContextRef.current
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    
    osc.connect(gain)
    gain.connect(ctx.destination)
    
    // Short high-pitch click
    osc.frequency.setValueAtTime(800, ctx.currentTime)
    osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.02)
    
    gain.gain.setValueAtTime(0.1, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.05)
    
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + 0.05)
  }, [])

  // Luxury car switch-like toggle sound
  const playToggle = useCallback(() => {
    if (!audioContextRef.current) return
    
    const ctx = audioContextRef.current
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    
    osc.connect(gain)
    gain.connect(ctx.destination)
    
    // Satisfying mechanical click
    osc.type = 'sine'
    osc.frequency.setValueAtTime(200, ctx.currentTime)
    osc.frequency.linearRampToValueAtTime(100, ctx.currentTime + 0.1)
    
    gain.gain.setValueAtTime(0.05, ctx.currentTime)
    gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.1)
    
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + 0.1)
  }, [])

  // Soft swoosh for transitions
  const playSwoosh = useCallback(() => {
    if (!audioContextRef.current) return
    
    const ctx = audioContextRef.current
    
    // Create noise buffer
    const bufferSize = ctx.sampleRate * 0.2
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate)
    const data = buffer.getChannelData(0)
    
    for (let i = 0; i < bufferSize; i++) {
      data[i] = Math.random() * 2 - 1
    }
    
    const noise = ctx.createBufferSource()
    noise.buffer = buffer
    
    const filter = ctx.createBiquadFilter()
    filter.type = 'lowpass'
    filter.frequency.setValueAtTime(1000, ctx.currentTime)
    filter.frequency.linearRampToValueAtTime(100, ctx.currentTime + 0.2)
    
    const gain = ctx.createGain()
    gain.gain.setValueAtTime(0.03, ctx.currentTime)
    gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.2)
    
    noise.connect(filter)
    filter.connect(gain)
    gain.connect(ctx.destination)
    
    noise.start(ctx.currentTime)
  }, [])

  // Success chime
  const playSuccess = useCallback(() => {
    if (!audioContextRef.current) return
    
    const ctx = audioContextRef.current
    const frequencies = [523.25, 659.25, 783.99] // C major chord
    
    frequencies.forEach((freq, i) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      
      osc.connect(gain)
      gain.connect(ctx.destination)
      
      osc.type = 'sine'
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.05)
      
      gain.gain.setValueAtTime(0, ctx.currentTime + i * 0.05)
      gain.gain.linearRampToValueAtTime(0.08, ctx.currentTime + i * 0.05 + 0.01)
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.05 + 0.3)
      
      osc.start(ctx.currentTime + i * 0.05)
      osc.stop(ctx.currentTime + i * 0.05 + 0.3)
    })
  }, [])

  return { playClick, playToggle, playSwoosh, playSuccess }
}
