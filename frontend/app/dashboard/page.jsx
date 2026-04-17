'use client'

import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { AlertCircle, CheckCircle2, Clock, Bell, TrendingUp } from 'lucide-react'

const complianceData = [
  { month: 'JAN', compliance: 78 },
  { month: 'FEB', compliance: 82 },
  { month: 'MAR', compliance: 85 },
  { month: 'APR', compliance: 88 },
  { month: 'MAY', compliance: 87 },
  { month: 'JUN', compliance: 90 },
  { month: 'JUL', compliance: 92 },
  { month: 'AUG', compliance: 91 },
  { month: 'SEP', compliance: 94 },
  { month: 'OCT', compliance: 96 },
  { month: 'NOV', compliance: 97 },
  { month: 'DEC', compliance: 98 },
]

const regulations = [
  {
    id: 1,
    title: 'Compliance Engine v2.0',
    description: 'New mandatory reporting requirements for algorithmic decision-making systems operating within the EU jurisdiction.',
    date: 'Dec 20, 2023',
    type: 'CRITICAL',
  },
  {
    id: 2,
    title: 'Cross-Border Data Governance Framework',
    description: 'New mandatory reporting requirements for cross-border digital infrastructure operations.',
    date: 'Dec 15, 2023',
    type: 'IMPORTANT',
  },
  {
    id: 3,
    title: 'California Privacy Rights Act (CPRA) Amendment',
    description: 'Clarification on the definition of sensitive personal information and updated compliance obligations.',
    date: 'Dec 10, 2023',
    type: 'IMPORTANT',
  },
]

const alerts = [
  {
    id: 1,
    title: 'Critical Integrity Mismatch',
    description: 'New GDPR audit data integrity violation detected. Action required immediately.',
    risk: 'critical',
    date: 'Dec 14, 2023',
  },
  {
    id: 2,
    title: 'Upcoming Compliance Expiry',
    description: 'GDPR Compliance certificate expires in 14 days. Annual validation in progress.',
    risk: 'warning',
    date: 'Dec 12, 2023',
  },
  {
    id: 3,
    title: 'System Optimization Completed',
    description: 'Automated compliance monitoring system successfully upgraded.',
    risk: 'info',
    date: 'Dec 10, 2023',
  },
]

export default function DashboardPage() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-56">
        <Topbar title="Executive Dashboard" />

        <main className="pt-20 px-8 pb-8">
          {/* Subtitle */}
          <p className="text-gray-600 text-sm mb-8">Real-time institutional oversight and regulatory monitoring.</p>

          {/* KPI Cards */}
          <div className="grid grid-cols-4 gap-6 mb-8">
            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Compliance Score</p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">98.2%</p>
                  <p className="text-gray-500 text-xs mt-1">Outstanding across all audits</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Active Alerts</p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">14</p>
                  <p className="text-gray-500 text-xs mt-1">Requiring immediate action</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Pending Tasks</p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">27</p>
                  <p className="text-gray-500 text-xs mt-1">Across departments</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-yellow-100 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">Recent Updates</p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">08</p>
                  <p className="text-gray-500 text-xs mt-1">Last 24 hours</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </Card>
          </div>

          {/* Chart Section */}
          {/* <Card className="p-6 bg-white border-gray-200 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Compliance Trend</h3>
              <div className="flex gap-2">
                <button className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors">Monthly</button>
                <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded transition-colors">Quarterly</button>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={complianceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                  formatter={(value) => `${value}%`}
                />
                <Bar dataKey="compliance" fill="#2563eb" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card> */}

          {/* Bottom Section */}
          {/* <div className="grid grid-cols-3 gap-6"> */}
            {/* Recent Regulations */}
            {/* <div className="col-span-2 space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recent Regulations</h3>
                <button className="text-blue-600 text-sm font-medium hover:underline">View Intelligence Hub</button>
              </div>
              <div className="space-y-3">
                {regulations.map((reg) => (
                  <Card key={reg.id} className="p-4 bg-white border-gray-200 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="flex items-start gap-4">
                      <div className="w-2 h-2 rounded-full bg-red-500 mt-2 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 text-sm">{reg.title}</h4>
                        <p className="text-gray-600 text-xs mt-1">{reg.description}</p>
                        <p className="text-gray-500 text-xs mt-2">{reg.date}</p>
                      </div>
                      <Badge variant={reg.type === 'CRITICAL' ? 'default' : 'secondary'} className="flex-shrink-0">
                        {reg.type}
                      </Badge>
                    </div>
                  </Card>
                ))}
              </div>
            </div> */}

            {/* Alerts Panel */}
            {/* <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Alerts Panel</h3>
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <Card 
                    key={alert.id} 
                    className={`p-4 bg-white border-l-4 hover:shadow-md transition-shadow cursor-pointer ${
                      alert.risk === 'critical' ? 'border-l-red-500' : alert.risk === 'warning' ? 'border-l-yellow-500' : 'border-l-blue-500'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                        alert.risk === 'critical' ? 'bg-red-500' : alert.risk === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 text-sm">{alert.title}</p>
                        <p className="text-gray-600 text-xs mt-1">{alert.description}</p>
                        <p className="text-gray-500 text-xs mt-2">{alert.date}</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div> */}
          {/* </div> */}
        </main>
      </div>
    </div>
  )
}
