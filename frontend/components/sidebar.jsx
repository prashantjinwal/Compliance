'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Building2, Cpu, CheckSquare, LogOut } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { clearAuthTokens, getUserDisplayName, getUserInitial, getUserRole } from '@/lib/api'
import { cn } from '@/lib/utils'

export function Sidebar({ user }) {
  const pathname = usePathname()
  const displayName = getUserDisplayName(user)
  const displayRole = getUserRole(user)
  const displayInitial = getUserInitial(user)

  function handleSignOut() {
    clearAuthTokens()
    window.location.href = '/auth'
  }

  const menuItems = [
    {
      href: '/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      href: '/company-profile',
      label: 'Company Profile',
      icon: Building2,
    },
    {
      href: '/ai-interface',
      label: 'AI Interface',
      icon: Cpu,
    },
    {
      href: '/tasks',
      label: 'Tasks',
      icon: CheckSquare,
    },
  ]

  return (
    <aside className="fixed left-0 top-0 h-screen w-56 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <div className="flex flex-col">
            <h1 className="font-semibold text-sm text-gray-900">AI Compliance</h1>
            <p className="text-xs text-gray-500">Institutional Integrity</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-6 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-200',
                isActive
                  ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-6 border-t border-gray-200 space-y-4">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10 ring-1 ring-orange-100">
            <AvatarFallback className="bg-gradient-to-br from-amber-500 to-red-500 text-sm font-bold text-white">
              {displayInitial}
            </AvatarFallback>
          </Avatar>
          <div className="text-sm">
            <p className="font-medium text-gray-900">{displayName}</p>
            <p className="text-xs text-gray-500">{displayRole}</p>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-gray-600 bg-gray-50 border border-gray-200 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  )
}
