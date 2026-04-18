'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, CheckCircle2, Zap, Send, Upload } from 'lucide-react'
import { useProtectedUser } from '@/hooks/use-protected-user'
import { chatWithCopilotDocument, getOrganizationName, uploadCopilotDocument } from '@/lib/api'

export default function AIInterfacePage() {
  const { user, loading, error } = useProtectedUser()
  const [analysisInput, setAnalysisInput] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState('')
  const [currentDocumentId, setCurrentDocumentId] = useState('')
  const [chatSessionId, setChatSessionId] = useState('')
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [messages, setMessages] = useState([])

  useEffect(() => {
    if (!user) {
      return
    }

    setMessages([
      {
        id: 1,
        role: 'ai',
        content:
          'Hello ' +
          (user.full_name || user.email) +
          '. I am ready to analyze compliance content for ' +
          getOrganizationName(user) +
          '. Upload a document or paste regulatory text to start a DRF-backed compliance analysis.',
      },
    ])
  }, [user])

  async function handleAnalyze() {
    if (!analysisInput.trim() && !selectedFile) {
      setAnalysisError('Enter regulatory text or upload a file before starting analysis.')
      return
    }

    setAnalysisLoading(true)
    setAnalysisError('')
    setAnalysisResult(null)
    setChatSessionId('')

    try {
      const result = await uploadCopilotDocument({
        file: selectedFile,
        text: analysisInput.trim(),
      })

      const payload = result.data || result

      setAnalysisResult(payload)
      setCurrentDocumentId(payload.doc_id)
      setMessages(prev => [
        prev[0],
        {
          id: prev.length + 1,
          role: 'ai',
          content: 'Analysis complete. You can now ask follow-up questions about this document.',
        },
      ])
    } catch (requestError) {
      setAnalysisError(requestError.message || 'Unable to analyze the submitted text.')
    } finally {
      setAnalysisLoading(false)
    }
  }

  async function handleSendMessage() {
    if (!chatInput.trim()) {
      return
    }

    if (!currentDocumentId) {
      setMessages(prev => [
        ...prev,
        {
          id: prev.length + 1,
          role: 'ai',
          content: 'Analyze a document first so I have a document context to query.',
        },
      ])
      return
    }

    const nextUserMessage = {
      id: messages.length + 1,
      role: 'user',
      content: chatInput,
    }

    setMessages(prev => [...prev, nextUserMessage])
    setChatInput('')
    setChatLoading(true)

    try {
      const result = await chatWithCopilotDocument(currentDocumentId, {
        question: nextUserMessage.content,
        ...(chatSessionId ? { session_id: chatSessionId } : {}),
      })

      const payload = result.data || result

      setChatSessionId(payload.session_id || '')
      setMessages(prev => [
        ...prev,
        {
          id: prev.length + 1,
          role: 'ai',
          content: payload.answer || 'No answer was returned by the AI service.',
        },
      ])
    } catch (requestError) {
      setMessages(prev => [
        ...prev,
        {
          id: prev.length + 1,
          role: 'ai',
          content: requestError.message || 'Unable to reach the AI service.',
        },
      ])
    } finally {
      setChatLoading(false)
    }
  }

  if (loading) {
    return null
  }

  const suggestedTasks = Array.isArray(analysisResult?.tasks) ? analysisResult.tasks : []

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar user={user} />

      <div className="flex-1 ml-56">
        <Topbar title="Regulation Analyzer" user={user} />

        <main className="pt-20 px-8 pb-8 overflow-y-auto max-h-[calc(100vh-80px)]">
          <p className="text-gray-600 text-sm mb-8">Paste regulatory text or upload a document for instant institutional mapping.</p>

          {error ? (
            <Card className="p-4 bg-red-50 border-red-200 mb-6">
              <p className="text-sm text-red-700">{error}</p>
            </Card>
          ) : null}

          <Card className="p-8 bg-white border-gray-200 mb-8">
            <div className="space-y-6">
              <div>
                <label className="text-sm font-medium text-gray-900 mb-3 block">Enter regulatory text, legal documentation, or corporate policy here for AI synthesis.</label>
                <Textarea
                  value={analysisInput}
                  onChange={e => setAnalysisInput(e.target.value)}
                  placeholder="Paste regulation text or upload a directive for analysis..."
                  className="min-h-32 border-gray-200 bg-gray-50 placeholder-gray-500 text-gray-900"
                />
              </div>

              <div className="flex gap-3">
                <label className="inline-flex">
                  <input
                    type="file"
                    accept=".pdf,.txt"
                    className="hidden"
                    onChange={e => {
                      const file = e.target.files && e.target.files[0] ? e.target.files[0] : null
                      setSelectedFile(file)
                    }}
                  />
                  <Button asChild className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-gray-900">
                    <span>
                      <Upload className="w-4 h-4" />
                      Upload PDF
                    </span>
                  </Button>
                </label>
                {selectedFile ? (
                  <span className="self-center text-sm text-gray-600">{selectedFile.name}</span>
                ) : null}
                <Button onClick={handleAnalyze} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8" disabled={analysisLoading}>
                  {analysisLoading ? 'Analyzing...' : 'Analyze'}
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>

          {analysisError ? (
            <Card className="p-4 bg-amber-50 border-amber-200 mb-8">
              <p className="text-sm text-amber-700">{analysisError}</p>
            </Card>
          ) : null}

          {analysisResult && (
            <div className="grid grid-cols-2 gap-6 mb-8">
              <div className="space-y-6">
                <Card className="p-6 bg-white border-gray-200">
                  <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-4">Executive Summary</h3>
                  <p className="text-gray-900 text-sm leading-relaxed mb-4">
                    {analysisResult.analysis?.summary || analysisResult.summary || 'No summary was returned by the backend.'}
                  </p>
                  <p className="text-xs text-gray-500">
                    Document ID: {analysisResult.doc_id}
                  </p>
                </Card>

                <Card className="p-6 bg-white border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">Impact Analysis</h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Key Changes</p>
                      <p className="text-sm text-gray-600">
                        {analysisResult.analysis?.key_changes || 'No key-change narrative was returned.'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Obligations</p>
                      <ul className="space-y-2 text-sm text-gray-600">
                        {Array.isArray(analysisResult.analysis?.obligations) && analysisResult.analysis.obligations.length > 0 ? (
                          analysisResult.analysis.obligations.map((obligation, index) => (
                            <li key={index}>{obligation}</li>
                          ))
                        ) : (
                          <li>No obligations were returned.</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 bg-white border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">Suggested Actions</h3>
                  <div className="space-y-3">
                    {suggestedTasks.length > 0 ? suggestedTasks.map((task, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer">
                        <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <CheckCircle2 className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">{task.title || `Action ${idx + 1}`}</p>
                          <p className="text-xs text-gray-600 mt-1">{task.suggested_action || task.description}</p>
                        </div>
                      </div>
                    )) : (
                      <p className="text-sm text-gray-500">No suggested actions were returned by the backend.</p>
                    )}
                  </div>
                </Card>
              </div>

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
                          strokeDasharray={`${((analysisResult.analysis?.relevance_score || 0) * 351.8)} 351.8`}
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                          <p className="text-4xl font-bold text-gray-900">
                            {Math.round((analysisResult.analysis?.relevance_score || 0) * 100)}
                          </p>
                          <p className="text-xs text-gray-600">Relevance Score</p>
                        </div>
                      </div>
                    </div>

                    <Badge className="bg-orange-100 text-orange-800 border-orange-200 mb-6">
                      {(analysisResult.risk?.risk_level || 'unknown').toUpperCase()}
                    </Badge>

                    <p className="text-sm text-gray-600 text-center leading-relaxed">
                      {analysisResult.risk?.description || 'The backend did not return a risk description.'}
                    </p>
                    <p className="text-xs text-gray-500 mt-3">
                      Responsible role: {analysisResult.risk?.responsible_role || 'Compliance'}
                    </p>
                  </div>
                </Card>

                <Card className="p-4 bg-gray-50 border-gray-200">
                  <p className="text-xs text-gray-600">
                    <strong>Note:</strong> This panel is backed by the existing DRF copilot upload endpoint and document chat endpoint.
                  </p>
                </Card>
              </div>
            </div>
          )}

          <Card className="bg-white border-gray-200 mb-8 flex flex-col" style={{ height: '500px' }}>
            <div className="border-b border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-600" />
                AI Chat Assistant
              </h3>
            </div>

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

            <div className="border-t border-gray-200 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about compliance..."
                  className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <Button
                  onClick={handleSendMessage}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2"
                  size="sm"
                  disabled={chatLoading}
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
