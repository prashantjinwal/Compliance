'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { AlertCircle, Clock, CheckCircle2, Plus } from 'lucide-react'

const tasks = [
  {
    id: 1,
    name: 'GDPR Data Audit Q3',
    department: 'Data Privacy',
    riskLevel: 'High',
    deadline: 'Oct 12, 2023',
    status: 'Pending',
    riskColor: 'text-red-600',
    badgeColor: 'bg-red-100 text-red-800',
  },
  {
    id: 2,
    name: 'AI Transparency Report',
    department: 'Product',
    riskLevel: 'Low',
    deadline: 'Oct 15, 2023',
    status: 'Completed',
    riskColor: 'text-green-600',
    badgeColor: 'bg-green-100 text-green-800',
  },
  {
    id: 3,
    name: 'Vendor Risk Assessment',
    department: 'Operations',
    riskLevel: 'Medium',
    deadline: 'Oct 18, 2023',
    status: 'Pending',
    riskColor: 'text-yellow-600',
    badgeColor: 'bg-yellow-100 text-yellow-800',
  },
  {
    id: 4,
    name: 'Ethics Board Review',
    department: 'Legal',
    riskLevel: 'High',
    deadline: 'Oct 20, 2023',
    status: 'Pending',
    riskColor: 'text-red-600',
    badgeColor: 'bg-red-100 text-red-800',
  },
  {
    id: 5,
    name: 'Employee Privacy Training',
    department: 'Human Resources',
    riskLevel: 'Low',
    deadline: 'Oct 25, 2023',
    status: 'Completed',
    riskColor: 'text-green-600',
    badgeColor: 'bg-green-100 text-green-800',
  },
  {
    id: 6,
    name: 'API Security Compliance',
    department: 'Engineering',
    riskLevel: 'High',
    deadline: 'Oct 28, 2023',
    status: 'In Progress',
    riskColor: 'text-red-600',
    badgeColor: 'bg-red-100 text-red-800',
  },
]

export default function TasksPage() {
  const [activeTab, setActiveTab] = useState('all')

  const filteredTasks = activeTab === 'all'
    ? tasks
    : tasks.filter(task => task.status.toLowerCase() === activeTab.toLowerCase())

  const completedCount = tasks.filter(t => t.status === 'Completed').length
  const completionPercentage = (completedCount / tasks.length) * 100

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

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-56">
        <Topbar title="Tasks" />

        <main className="pt-20 px-8 pb-8 overflow-y-auto max-h-[calc(100vh-80px)]">
          {/* Header Section with Progress */}
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
                <p className="text-4xl font-bold">03</p>
                <p className="text-xs text-blue-100 mt-1">Regulatory trips due within 48 hours</p>
              </div>
            </div>
          </div>

          {/* Filter Tabs */}
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
                {/* Table Header */}
                <div className="grid grid-cols-5 gap-4 px-6 py-4 border-b border-gray-200 bg-gray-50 font-semibold text-sm text-gray-700">
                  <div>Task Name</div>
                  <div>Department</div>
                  <div>Risk Level</div>
                  <div>Deadline</div>
                  <div>Status</div>
                </div>

                {/* Table Body */}
                <TabsContent value={activeTab} className="m-0">
                  <div className="divide-y divide-gray-200">
                    {filteredTasks.map((task, idx) => (
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
                </TabsContent>
              </div>
            </Tabs>

            <p className="text-sm text-gray-600 mt-4">
              Showing {filteredTasks.length} of {tasks.length} tasks
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mb-8">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Task
            </Button>
            <Button variant="outline" className="border-gray-200">
              Export Report
            </Button>
          </div>

          {/* Additional Info Cards */}
          <div className="grid grid-cols-2 gap-6">
            <Card className="p-6 bg-white border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Distribution by Department</h3>
              <div className="space-y-3">
                {[
                  { dept: 'Data Privacy', count: 8, color: 'bg-blue-200' },
                  { dept: 'Product', count: 6, color: 'bg-green-200' },
                  { dept: 'Legal', count: 5, color: 'bg-yellow-200' },
                  { dept: 'Operations', count: 4, color: 'bg-purple-200' },
                ].map(item => (
                  <div key={item.dept} className="flex items-center gap-3">
                    <div className={`${item.color} h-3 rounded-full flex-1`} />
                    <span className="text-sm text-gray-600 w-24">{item.dept}</span>
                    <span className="font-semibold text-gray-900">{item.count}</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance By Risk Level</h3>
              <div className="space-y-3">
                {[
                  { level: 'High Risk', count: 8, color: 'text-red-600' },
                  { level: 'Medium Risk', count: 6, color: 'text-yellow-600' },
                  { level: 'Low Risk', count: 5, color: 'text-green-600' },
                ].map(item => (
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
