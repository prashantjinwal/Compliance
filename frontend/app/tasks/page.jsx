'use client'

import { useEffect, useMemo, useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { AlertCircle, Clock, CheckCircle2, Plus } from 'lucide-react'
import { useProtectedUser } from '@/hooks/use-protected-user'
import { optionalAuthApiRequest } from '@/lib/api'

function normalizeTasksResponse(payload) {
  if (!payload) {
    return []
  }

  if (Array.isArray(payload)) {
    return payload
  }

  if (Array.isArray(payload.results)) {
    return payload.results
  }

  if (Array.isArray(payload.tasks)) {
    return payload.tasks
  }

  if (Array.isArray(payload.items)) {
    return payload.items
  }

  return []
}

function normalizeTask(task, index) {
  const status = task.status || 'Pending'
  const riskLevel = task.priority || task.risk_level || task.riskLevel || 'Unknown'
  const riskKey = riskLevel.toString().toLowerCase()

  const badgeMap = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800',
    unknown: 'bg-gray-100 text-gray-800',
  }

  return {
    id: task.id || index + 1,
    name: task.name || task.title || 'Untitled Task',
    department: task.department || task.assignee || 'Unassigned',
    riskLevel,
    deadline: task.due_date || task.deadline || 'No due date',
    status,
    badgeColor: badgeMap[riskKey] || badgeMap.unknown,
  }
}

export default function TasksPage() {
  const { user, loading, error } = useProtectedUser()
  const [activeTab, setActiveTab] = useState('all')
  const [tasks, setTasks] = useState([])
  const [tasksLoading, setTasksLoading] = useState(true)
  const [tasksError, setTasksError] = useState('')
  const [tasksEndpointPath, setTasksEndpointPath] = useState(null)

  useEffect(() => {
    if (!user) {
      return
    }

    let isActive = true

    async function loadTasks() {
      setTasksLoading(true)
      setTasksError('')

      try {
        const result = await optionalAuthApiRequest(['/api/tasks/'])

        if (!isActive) {
          return
        }

        setTasksEndpointPath(result.path)

        if (!result.path) {
          setTasks([])
          setTasksError('Task list endpoint is not available yet. The UI is ready to consume /api/tasks/ when it is added.')
          return
        }

        setTasks(normalizeTasksResponse(result.data).map(normalizeTask))
      } catch (requestError) {
        if (!isActive) {
          return
        }

        setTasks([])
        setTasksError(requestError.message || 'Unable to load tasks.')
      } finally {
        if (isActive) {
          setTasksLoading(false)
        }
      }
    }

    loadTasks()

    return () => {
      isActive = false
    }
  }, [user])

  const filteredTasks = useMemo(() => {
    if (activeTab === 'all') {
      return tasks
    }

    return tasks.filter(task => task.status.toLowerCase() === activeTab.toLowerCase())
  }, [activeTab, tasks])

  const completedCount = tasks.filter(task => task.status === 'Completed').length
  const completionPercentage = tasks.length > 0 ? (completedCount / tasks.length) * 100 : 0
  const urgentCount = tasks.filter(task => task.status === 'Pending').length

  const departmentDistribution = useMemo(() => {
    const counts = {}

    tasks.forEach(task => {
      counts[task.department] = (counts[task.department] || 0) + 1
    })

    return Object.entries(counts).map(([department, count], index) => {
      const colors = ['bg-blue-200', 'bg-green-200', 'bg-yellow-200', 'bg-purple-200']

      return {
        dept: department,
        count,
        color: colors[index % colors.length],
      }
    })
  }, [tasks])

  const riskDistribution = useMemo(() => {
    const counts = {
      'High Risk': 0,
      'Medium Risk': 0,
      'Low Risk': 0,
    }

    tasks.forEach(task => {
      const normalizedRisk = task.riskLevel.toString().toLowerCase()

      if (normalizedRisk === 'high') {
        counts['High Risk'] += 1
      } else if (normalizedRisk === 'medium') {
        counts['Medium Risk'] += 1
      } else if (normalizedRisk === 'low') {
        counts['Low Risk'] += 1
      }
    })

    return [
      { level: 'High Risk', count: counts['High Risk'], color: 'bg-red-500' },
      { level: 'Medium Risk', count: counts['Medium Risk'], color: 'bg-yellow-500' },
      { level: 'Low Risk', count: counts['Low Risk'], color: 'bg-green-500' },
    ]
  }, [tasks])

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-800'
      case 'In Progress':
        return 'bg-blue-100 text-blue-800'
      case 'Pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Completed':
        return <CheckCircle2 className="w-4 h-4" />
      case 'In Progress':
        return <Clock className="w-4 h-4" />
      case 'Pending':
        return <AlertCircle className="w-4 h-4" />
      default:
        return null
    }
  }

  if (loading) {
    return null
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar user={user} />

      <div className="flex-1 ml-56">
        <Topbar title="Tasks" user={user} />

        <main className="pt-20 px-8 pb-8 overflow-y-auto max-h-[calc(100vh-80px)]">
          {error ? (
            <Card className="p-4 bg-red-50 border-red-200 mb-6">
              <p className="text-sm text-red-700">{error}</p>
            </Card>
          ) : null}

          {tasksError ? (
            <Card className="p-4 bg-amber-50 border-amber-200 mb-6">
              <p className="text-sm text-amber-700">{tasksError}</p>
            </Card>
          ) : null}

          <div className="mb-8">
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">
              Quarterly Compliance Progress
            </h3>
            <div className="flex items-end gap-4 mb-4">
              <div className="flex-1">
                <p className="text-4xl font-bold text-gray-900">{Math.round(completionPercentage)}%</p>
                <Progress value={completionPercentage} className="mt-4 h-2" />
                <p className="text-sm text-gray-600 mt-2">
                  {completedCount} of {tasks.length} tasks completed
                </p>
              </div>
              <div className="bg-blue-600 text-white rounded-lg p-6 min-w-max">
                <p className="text-sm font-medium text-blue-100 mb-1">Urgent Actions</p>
                <p className="text-4xl font-bold">{urgentCount.toString().padStart(2, '0')}</p>
                <p className="text-xs text-blue-100 mt-1">
                  {tasksEndpointPath ? 'Pending items loaded from backend' : 'Waiting for task endpoint'}
                </p>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="bg-white border border-gray-200 p-1">
                <TabsTrigger value="all" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-600">
                  All Tasks
                </TabsTrigger>
                <TabsTrigger value="pending" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-600">
                  Pending
                </TabsTrigger>
                <TabsTrigger value="in progress" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-600">
                  In Progress
                </TabsTrigger>
                <TabsTrigger value="completed" className="data-[state=active]:bg-blue-50 data-[state=active]:text-blue-600">
                  Completed
                </TabsTrigger>
              </TabsList>

              <div className="mt-6 bg-white rounded-lg border border-gray-200 overflow-hidden">
                <div className="grid grid-cols-5 gap-4 px-6 py-4 border-b border-gray-200 bg-gray-50 font-semibold text-sm text-gray-700">
                  <div>Task Name</div>
                  <div>Department</div>
                  <div>Risk Level</div>
                  <div>Deadline</div>
                  <div>Status</div>
                </div>

                <TabsContent value={activeTab} className="m-0">
                  {tasksLoading ? (
                    <div className="px-6 py-10 text-sm text-gray-500">Loading tasks...</div>
                  ) : filteredTasks.length > 0 ? (
                    <div className="divide-y divide-gray-200">
                      {filteredTasks.map(task => (
                        <div
                          key={task.id}
                          className="grid grid-cols-5 gap-4 px-6 py-4 hover:bg-gray-50 transition-colors cursor-pointer items-center"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                            <span className="font-medium text-gray-900 text-sm">{task.name}</span>
                          </div>

                          <span className="text-sm text-gray-600">{task.department}</span>

                          <Badge className={`${task.badgeColor} w-fit text-xs font-semibold`}>
                            {task.riskLevel} Risk
                          </Badge>

                          <span className="text-sm text-gray-600">{task.deadline}</span>

                          <div className="flex items-center gap-2">
                            {getStatusIcon(task.status)}
                            <Badge className={`${getStatusBadge(task.status)} text-xs font-semibold`}>
                              {task.status}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="px-6 py-10 text-sm text-gray-500">
                      {tasksEndpointPath
                        ? 'No tasks are available for this account yet.'
                        : 'No task endpoint is currently configured in the backend.'}
                    </div>
                  )}
                </TabsContent>
              </div>
            </Tabs>

            <p className="text-sm text-gray-600 mt-4">
              Showing {filteredTasks.length} of {tasks.length} tasks
            </p>
          </div>

          <div className="flex gap-3 mb-8">
            <Button
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center gap-2"
              disabled={!tasksEndpointPath}
            >
              <Plus className="w-4 h-4" />
              New Task
            </Button>
            <Button variant="outline" className="border-gray-200">
              Export Report
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <Card className="p-6 bg-white border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Distribution by Department</h3>
              <div className="space-y-3">
                {departmentDistribution.length > 0 ? departmentDistribution.map(item => (
                  <div key={item.dept} className="flex items-center gap-3">
                    <div className={`${item.color} h-3 rounded-full flex-1`} />
                    <span className="text-sm text-gray-600 w-24">{item.dept}</span>
                    <span className="font-semibold text-gray-900">{item.count}</span>
                  </div>
                )) : (
                  <p className="text-sm text-gray-500">Department distribution will appear once task data is available.</p>
                )}
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance By Risk Level</h3>
              <div className="space-y-3">
                {riskDistribution.map(item => (
                  <div key={item.level} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${item.color}`} />
                      <span className="text-sm text-gray-600">{item.level}</span>
                    </div>
                    <span className="font-semibold text-gray-900">{item.count} tasks</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
