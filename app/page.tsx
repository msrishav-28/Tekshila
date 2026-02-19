'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'
import { GlassCard } from '@/components/GlassCard'
import { MagneticButton } from '@/components/MagneticButton'
import { Code2, FileText, Sparkles, ArrowRight, Zap, Shield, Github } from 'lucide-react'

// Dynamic import for Three.js scene to avoid SSR issues
const HeroScene = dynamic(() => import('@/components/HeroScene'), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="w-32 h-32 rounded-full bg-gradient-to-br from-crimson to-crimson-dark animate-pulse" />
    </div>
  )
})

export default function LandingPage() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2
      })
    }

    const handleScroll = () => {
      setScrolled(window.scrollY > 100)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('scroll', handleScroll)
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const features = [
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'AI-Powered Analysis',
      description: 'Gemini-powered code intelligence that understands context and generates precise documentation.'
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Lightning Fast',
      description: 'Sub-second documentation generation with streaming responses and real-time preview.'
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Enterprise Security',
      description: 'Your code never leaves your environment. Local processing with optional cloud acceleration.'
    },
    {
      icon: <Github className="w-6 h-6" />,
      title: 'GitHub Integration',
      description: 'Seamlessly connect repositories and automatically sync documentation with code changes.'
    }
  ]

  return (
    <div className="relative min-h-screen bg-void overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center">
        {/* 3D Scene Background */}
        <HeroScene mousePosition={mousePosition} />
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-void/50 to-void pointer-events-none z-10" />
        
        {/* Hero Content */}
        <div className="relative z-20 text-center px-4 max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="micro-label block mb-6 text-crimson">
              SYSTEM READY // V.3.0
            </span>
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="headline-display text-5xl sm:text-7xl md:text-8xl lg:text-9xl mb-6"
          >
            Documentation,
            <br />
            <span className="text-gradient-crimson">Refracted.</span>
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="font-ui text-lg sm:text-xl text-silver-400 max-w-2xl mx-auto mb-10"
          >
            Transform your codebase into cinematic documentation with AI precision.
            <br className="hidden sm:block" />
            Built for engineers who demand excellence.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <MagneticButton size="lg" onClick={() => window.location.href = '/dashboard'}>
              <span className="flex items-center gap-2">
                Enter the Lab
                <ArrowRight className="w-4 h-4" />
              </span>
            </MagneticButton>
            
            <MagneticButton variant="secondary" size="lg">
              <span className="flex items-center gap-2">
                <Github className="w-4 h-4" />
                Connect GitHub
              </span>
            </MagneticButton>
          </motion.div>
        </div>
        
        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="w-6 h-10 rounded-full border-2 border-silver-600 flex justify-center pt-2"
          >
            <div className="w-1 h-2 bg-crimson rounded-full" />
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative py-32 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-20"
          >
            <span className="micro-label text-crimson mb-4 block">CAPABILITIES</span>
            <h2 className="headline-display text-4xl sm:text-5xl md:text-6xl">
              Precision Engineering
            </h2>
          </motion.div>
          
          {/* Bento Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <GlassCard 
                  spotlight 
                  className="p-8 h-full hover:bg-surface/80 transition-colors duration-300"
                >
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-crimson/10 text-crimson">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="font-display text-xl font-semibold mb-2 text-silver-100">
                        {feature.title}
                      </h3>
                      <p className="font-ui text-silver-400 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-32 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <GlassCard className="p-12 sm:p-16" spotlight>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <span className="micro-label text-crimson mb-6 block">BEGIN TRANSFORMATION</span>
              <h2 className="headline-display text-3xl sm:text-4xl md:text-5xl mb-6">
                Ready to refract your code?
              </h2>
              <p className="font-ui text-silver-400 text-lg mb-10 max-w-xl mx-auto">
                Join thousands of engineers who have elevated their documentation to an art form.
              </p>
              <MagneticButton size="lg" onClick={() => window.location.href = '/dashboard'}>
                <span className="flex items-center gap-2">
                  <Code2 className="w-5 h-5" />
                  Start Generating
                </span>
              </MagneticButton>
            </motion.div>
          </GlassCard>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-12 px-4 border-t border-glass-stroke">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-crimson to-crimson-dark flex items-center justify-center">
              <FileText className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-semibold text-lg">Tekshila</span>
          </div>
          <p className="font-ui text-silver-500 text-sm">
            © 2024 Tekshila. Documentation, refracted.
          </p>
        </div>
      </footer>
    </div>
  )
}
