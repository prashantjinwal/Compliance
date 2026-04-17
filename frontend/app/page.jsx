'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    router.push('/dashboard')
  }, [router])

  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <div className="text-center">
        <div className="w-12 h-12 rounded-lg bg-blue-600 flex items-center justify-center mx-auto mb-4">
          <span className="text-white font-bold text-lg">AI</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">AI Compliance</h1>
        <p className="text-gray-600 mt-2">Loading dashboard...</p>
      </div>
    </div>
  )
}
