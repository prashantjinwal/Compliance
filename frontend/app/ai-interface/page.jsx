'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, CheckCircle2, AlertCircle, TrendingUp, Zap, Send, Upload } from 'lucide-react'

const suggestedActions = [
  {
    icon: CheckCircle2,
    title: 'Update Data Retention Policy',
    description: 'Implement new data retention requirements',
  },
  {
    icon: Zap,
    title: 'Conduct Module Audit v3.1',
    description: 'Verify compliance across systems',
  },
  {
    icon: TrendingUp,
    title: 'Draft Disclosure Statement',
    description: 'Document technical implementation steps',
  },
  {
    icon: AlertCircle,
    title: 'Schedule Board Review',
    description: 'Present findings to leadership',
  },
]

const chatMessages = [
  {
    id: 1,
    role: 'ai',
    content: 'Hello! I\'m the Institutional Agent for your compliance team. I\'ve analyzed the GDPR Audit task. Based on previous cycles, I recommend starting the vendor review phase 2 days early.',
  },
  {
    id: 2,
    role: 'user',
    content: 'What are the key compliance gaps we need to address?',
  },
  {
    id: 3,
    role: 'ai',
    content: 'Based on the latest regulatory updates, I\'ve identified 3 critical compliance gaps across your technical infrastructure. Notably, your data processing agreements need immediate attention for GDPR compliance.',
    isExpanded: true,
  },
]

export default function AIInterfacePage() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [chatInput, setChatInput] = useState('')
  const [messages, setMessages] = useState(chatMessages)

  const handleAnalyze = () => {
    setAnalysisResult('analysis')
  }

  const handleSendMessage = () => {
    if (chatInput.trim()) {
      const newMessage = {
        id: messages.length + 1,
        role: 'user',
        content: chatInput,
      }
      setMessages([...messages, newMessage])
      setChatInput('')

      // Simulate AI response
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: prev.length + 1,
          role: 'ai',
          content: 'I understand. Let me analyze this further and provide comprehensive recommendations based on your regulatory framework.',
        }])
      }, 1000)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-56">
        <Topbar title="Regulation Analyzer" />

        <main className="pt-20 px-8 pb-8 overflow-y-auto max-h-[calc(100vh-80px)]">
          <p className="text-gray-600 text-sm mb-8">Paste regulatory text or upload a document for instant institutional mapping.</p>

          {/* Analyzer Section */}
          <Card className="p-8 bg-white border-gray-200 mb-8">
            <div className="space-y-6">
              <div>
                <label className="text-sm font-medium text-gray-900 mb-3 block">Enter regulatory text, legal documentation, or corporate policy here for AI synthesis.</label>
                <Textarea
                  placeholder="Paste regulation text or upload a directive for analysis..."
                  className="min-h-32 border-gray-200 bg-gray-50 placeholder-gray-500 text-gray-900"
                />
              </div>

              <div className="flex gap-3">
                <Button className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-gray-900">
                  <Upload className="w-4 h-4" />
                  Upload PDF
                </Button>
                <Button onClick={handleAnalyze} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8">
                  Analyze
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>

          {analysisResult && (
            <div className="grid grid-cols-2 gap-6 mb-8">
              {/* Left: Analysis Results */}
              <div className="space-y-6">
                {/* Executive Summary */}
                <Card className="p-6 bg-white border-gray-200">
                  <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-4">Executive Summary</h3>
                  <p className="text-gray-900 text-sm leading-relaxed mb-4">
                    The submitted document (Directive 2024/NC) mandates new transparency reporting for cross-border implementations. Primarily impacts our algorithmic trading modules and requires updated disclosure by Q1 2024.
                  </p>
                  <button className="text-blue-600 text-sm font-medium hover:underline">
                    Expand Details <ArrowRight className="inline w-3 h-3 ml-1" />
                  </button>
                </Card>

                {/* Impact Analysis */}
                <Card className="p-6 bg-white border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">Impact Analysis</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Operational</span>
                        <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full w-2/3 bg-blue-600" />
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Technical</span>
                        <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full w-1/2 bg-blue-600" />
                        </div>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Financial</span>
                        <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div className="h-full w-1/3 bg-blue-600" />
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Suggested Actions */}
                <Card className="p-6 bg-white border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">Suggested Actions</h3>
                  <div className="space-y-3">
                    {suggestedActions.map((action, idx) => {
                      const Icon = action.icon
                      return (
                        <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer">
                          <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                            <Icon className="w-4 h-4 text-blue-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900">{action.title}</p>
                            <p className="text-xs text-gray-600 mt-1">{action.description}</p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  <button className="mt-4 text-blue-600 text-sm font-medium hover:underline flex items-center gap-1">
                    Expand Task List <ArrowRight className="w-3 h-3" />
                  </button>
                </Card>
              </div>

              {/* Right: Risk Score */}
              <div>
                <Card className="p-6 bg-white border-gray-200 mb-6">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-6">Compliance Risk</h3>
                  <div className="flex flex-col items-center justify-center py-8">
                    <div className="relative w-32 h-32 mb-6">
                      <svg className="w-full h-full" style={{ transform: 'rotateZ(-90deg)' }}>
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          fill="none"
                          stroke="#e5e7eb"
                          strokeWidth="8"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          fill="none"
                          stroke="#ea580c"
                          strokeWidth="8"
                          strokeDasharray={`${(70 / 100) * 351.8} 351.8`}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                          <p className="text-4xl font-bold text-gray-900">70</p>
                          <p className="text-xs text-gray-600">Medium-High Risk</p>
                        </div>
                      </div>
                    </div>

                    <Badge className="bg-orange-100 text-orange-800 border-orange-200 mb-6">
                      MEDIUM-HIGH RISK
                    </Badge>

                    <p className="text-sm text-gray-600 text-center leading-relaxed">
                      Based on current institutional baseline. Risk assessment may be escalated within 14 days pending implementation of recommended actions.
                    </p>
                  </div>
                </Card>

                <Card className="p-4 bg-gray-50 border-gray-200">
                  <p className="text-xs text-gray-600">
                    <strong>Note:</strong> This analysis integrates current compliance posture with regulatory updates. Recommendations prioritize feasibility and strategic alignment.
                  </p>
                </Card>
              </div>
            </div>
          )}

          {/* AI Chat Section */}
          <Card className="bg-white border-gray-200 mb-8 flex flex-col" style={{ height: '500px' }}>
            <div className="border-b border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-600" />
                AI Chat Assistant
              </h3>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'ai' && (
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3 flex-shrink-0">
                      <Zap className="w-4 h-4 text-blue-600" />
                    </div>
                  )}
                  <div
                    className={`max-w-md p-4 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-gray-100 text-gray-900 rounded-bl-none'
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about compliance..."
                  className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <Button
                  onClick={handleSendMessage}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2"
                  size="sm"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        </main>
      </div>
    </div>
  )
}
