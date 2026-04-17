'use client'

import { Bell, Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export function Topbar({ title }) {
  return (
    <div className="fixed top-0 left-56 right-0 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 z-40">
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>

      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search tasks, regulations, or users..."
            className="pl-10 bg-gray-50 border-gray-200 placeholder-gray-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="w-5 h-5 text-gray-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">Notifications</h3>
            </div>
            <div className="p-2 space-y-2 max-h-96 overflow-y-auto">
              <DropdownMenuItem className="flex items-start gap-3 py-3 px-3 hover:bg-gray-50 cursor-pointer rounded">
                <div className="w-2 h-2 rounded-full bg-red-500 mt-2 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">GDPR Audit Deadline</p>
                  <p className="text-xs text-gray-500">Due in 2 days</p>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem className="flex items-start gap-3 py-3 px-3 hover:bg-gray-50 cursor-pointer rounded">
                <div className="w-2 h-2 rounded-full bg-yellow-500 mt-2 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Risk Assessment Due</p>
                  <p className="text-xs text-gray-500">Vendor review status update</p>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem className="flex items-start gap-3 py-3 px-3 hover:bg-gray-50 cursor-pointer rounded">
                <div className="w-2 h-2 rounded-full bg-green-500 mt-2 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Privacy Training Completed</p>
                  <p className="text-xs text-gray-500">3 hours ago</p>
                </div>
              </DropdownMenuItem>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        <button className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 hover:opacity-90 transition-opacity" />
      </div>
    </div>
  )
}
