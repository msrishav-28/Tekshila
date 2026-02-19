import { GlassSidebar } from '@/components/GlassSidebar'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-void">
      <GlassSidebar />
      <main className="ml-72 min-h-screen">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
