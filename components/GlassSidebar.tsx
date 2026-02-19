'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  FileText, 
  Code2, 
  GitBranch, 
  Settings, 
  Sparkles,
  LogOut,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  className?: string
}

const navItems = [
  { icon: FileText, label: 'Documentation', href: '/dashboard' },
  { icon: Code2, label: 'Code Analysis', href: '/dashboard/analyze' },
  { icon: GitBranch, label: 'GitHub', href: '/dashboard/github' },
  { icon: Sparkles, label: 'AI Studio', href: '/dashboard/ai' },
  { icon: Settings, label: 'Settings', href: '/dashboard/settings' },
]

export function GlassSidebar({ className }: SidebarProps) {
  const pathname = usePathname()

  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        'fixed left-0 top-0 h-full w-72 z-50',
        'glass-card border-r-0 rounded-r-2xl rounded-l-none',
        className
      )}
    >
      {/* Logo */}
      <div className="p-6 border-b border-glass-stroke">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-crimson to-crimson-dark flex items-center justify-center shadow-lg shadow-crimson/20 group-hover:shadow-crimson/40 transition-shadow">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-display font-bold text-xl tracking-tight">Tekshila</h1>
            <span className="micro-label text-crimson">V.3.0 PRISM</span>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1">
        {navItems.map((item, index) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Link
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group',
                  'hover:bg-white/5',
                  isActive && 'bg-crimson/10 text-crimson'
                )}
              >
                <Icon className={cn(
                  'w-5 h-5 transition-colors',
                  isActive ? 'text-crimson' : 'text-silver-400 group-hover:text-silver-200'
                )} />
                <span className={cn(
                  'font-ui font-medium transition-colors',
                  isActive ? 'text-crimson' : 'text-silver-300 group-hover:text-silver-100'
                )}>
                  {item.label}
                </span>
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-crimson"
                  />
                )}
              </Link>
            </motion.div>
          )
        })}
      </nav>

      {/* Status */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-glass-stroke">
        <div className="glass-card p-4 rounded-xl bg-surface/50">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="micro-label text-silver-400">SYSTEM ONLINE</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-silver-500">API Latency</span>
            <span className="font-mono text-emerald-400">12ms</span>
          </div>
        </div>

        <button className="mt-4 flex items-center gap-3 px-4 py-3 w-full rounded-xl hover:bg-white/5 transition-colors group">
          <LogOut className="w-5 h-5 text-silver-400 group-hover:text-silver-200" />
          <span className="font-ui font-medium text-silver-300 group-hover:text-silver-100">
            Disconnect
          </span>
        </button>
      </div>
    </motion.aside>
  )
}
