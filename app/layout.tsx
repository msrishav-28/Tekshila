import type { Metadata } from 'next'
import { AuthProvider } from '@/hooks/useAuth'
import './globals.css'

export const metadata: Metadata = {
  title: 'Tekshila | Documentation, Refracted',
  description: 'AI-powered code documentation with cinematic engineering precision',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="bg-void text-silver-100 antialiased">
        <AuthProvider>
          <div className="noise-overlay" aria-hidden="true" />
          <main className="relative min-h-screen">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  )
}
