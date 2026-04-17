'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'

const DEPARTMENTS = ['Finance', 'HR', 'Legal', 'IT', 'Marketing', 'Operations']
const REGULATIONS = ['RBI', 'SEBI', 'GDPR', 'HIPAA', 'PCI-DSS', 'SOX']

export default function CompanyProfilePage() {
  const [form, setForm] = useState({
    name: 'Global Dynamics Inc.',
    industry: 'financial_services',
    size: '1000+',
    country: 'India',
    region: 'EU & NA Markets',
    headcount: '12,450',
    email: 'compliance@globaldynamics.com',
    regulations: ['RBI', 'SEBI', 'GDPR'],
    departments: ['Finance', 'HR', 'Legal'],
    risk: 'medium',
  })
  const [saved, setSaved] = useState(false)

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))

  const toggleList = (key, val) =>
    set(key, form[key].includes(val)
      ? form[key].filter(x => x !== val)
      : [...form[key], val]
    )

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-56">
        <Topbar title="Company Profile" />

        <main className="pt-20 px-8 pb-8">
          <p className="text-gray-500 text-sm mb-8">Define your organization&apos;s regulatory perimeter.</p>

          <div className="grid grid-cols-3 gap-8">

            {/* Left: Form (col-span-2) */}
            <div className="col-span-2 space-y-6">

              {/* Basic Info */}
              <Card className="p-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Basic Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label className="text-sm text-gray-600">Company Name</Label>
                    <Input value={form.name} onChange={e => set('name', e.target.value)} />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-sm text-gray-600">Industry</Label>
                    <Select value={form.industry} onValueChange={v => set('industry', v)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="financial_services">Financial Services</SelectItem>
                        <SelectItem value="fintech">Fintech</SelectItem>
                        <SelectItem value="healthcare">Healthcare</SelectItem>
                        <SelectItem value="ecommerce">E-commerce</SelectItem>
                        <SelectItem value="manufacturing">Manufacturing</SelectItem>
                        <SelectItem value="legal">Legal</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-sm text-gray-600">Country / Region</Label>
                    <Input value={form.country} onChange={e => set('country', e.target.value)} />
                  </div>
                  
                  <div className="space-y-1">
                    <Label className="text-sm text-gray-600">Headcount (FTEs)</Label>
                    <Input value={form.headcount} onChange={e => set('headcount', e.target.value)} />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-sm text-gray-600">Compliance Contact Email</Label>
                    <Input type="email" value={form.email} onChange={e => set('email', e.target.value)} />
                  </div>
                </div>
              </Card>

              {/* Compliance Scope */}
              <Card className="p-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Compliance Scope</h3>

                <div className="mb-5">
                  <Label className="text-sm text-gray-600 mb-2 block">Applicable Regulations</Label>
                  <div className="flex flex-wrap gap-2">
                    {REGULATIONS.map(reg => (
                      <button
                        key={reg}
                        onClick={() => toggleList('regulations', reg)}
                        className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                          form.regulations.includes(reg)
                            ? 'bg-blue-600 text-white border-blue-600'
                            : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'
                        }`}
                      >
                        {reg}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <Label className="text-sm text-gray-600 mb-2 block">Departments</Label>
                  <div className="grid grid-cols-3 gap-2">
                    {DEPARTMENTS.map(dept => (
                      <div key={dept} className="flex items-center gap-2">
                        <Checkbox
                          id={dept}
                          checked={form.departments.includes(dept)}
                          onCheckedChange={() => toggleList('departments', dept)}
                        />
                        <Label htmlFor={dept} className="text-sm text-gray-700 cursor-pointer">{dept}</Label>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>

              {/* Risk Preferences */}
              <Card className="p-6">
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Risk Preferences</h3>
                <Label className="text-sm text-gray-600 mb-2 block">Risk Tolerance</Label>
                <div className="flex gap-2">
                  {['low', 'medium', 'high'].map(level => {
                    const colors = {
                      low:    form.risk === 'low'    ? 'bg-green-600 text-white border-green-600' : 'bg-white text-gray-600 border-gray-200 hover:border-green-300',
                      medium: form.risk === 'medium' ? 'bg-amber-500 text-white border-amber-500' : 'bg-white text-gray-600 border-gray-200 hover:border-amber-300',
                      high:   form.risk === 'high'   ? 'bg-red-600 text-white border-red-600'     : 'bg-white text-gray-600 border-gray-200 hover:border-red-300',
                    }
                    return (
                      <button
                        key={level}
                        onClick={() => set('risk', level)}
                        className={`px-5 py-2 rounded-lg text-sm border font-medium capitalize transition-colors ${colors[level]}`}
                      >
                        {level.charAt(0).toUpperCase() + level.slice(1)}
                      </button>
                    )
                  })}
                </div>
              </Card>

              {/* Save */}
              <div className="flex items-center gap-3">
                <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700 text-white px-6">
                  {saved ? '✓ Saved' : 'Save Profile'}
                </Button>
                {saved && <span className="text-sm text-green-600">Profile updated successfully</span>}
              </div>
            </div>

            {/* Right: Summary Card */}
            <div>
              <Card className="p-6 bg-gradient-to-br from-blue-600 to-blue-800 text-white border-none sticky top-24">
                <div className="mb-6">
                  <p className="text-blue-100 text-xs font-semibold uppercase tracking-wide">Entity Preview</p>
                  <h2 className="text-2xl font-bold mt-2">{form.name || 'Your Company'}</h2>
                </div>

                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-1">INDUSTRY</p>
                    <p className="font-medium capitalize">{form.industry.replace('_', ' ') || '—'}</p>
                  </div>
                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-1">REGION</p>
                    <p className="font-medium">{form.country || '—'}</p>
                  </div>
                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-1">COMPLIANCE STATUS</p>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-green-400" />
                      <p className="font-medium">Audit Ready</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-1">HEADCOUNT</p>
                    <p className="font-medium">{form.headcount ? `${form.headcount} FTEs` : '—'}</p>
                  </div>

                  <hr className="border-blue-500 my-4" />

                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-3">ACTIVE FRAMEWORKS</p>
                    <div className="flex flex-wrap gap-1">
                      {form.regulations.length > 0
                        ? form.regulations.map(r => (
                            <span key={r} className="px-2 py-0.5 bg-blue-500 rounded text-xs font-medium">{r}</span>
                          ))
                        : <span className="text-blue-200 text-xs">None selected</span>
                      }
                    </div>
                  </div>

                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-3 mt-4">ORGANIZATIONAL PROFILE</p>
                    <p className="text-sm leading-relaxed text-blue-50">
                      Your institutional profile is used to calibrate AI-driven compliance insights across{' '}
                      {form.regulations.length} active framework{form.regulations.length !== 1 ? 's' : ''} with emphasis
                      on internal alignment with <span className="font-medium capitalize">{form.risk}</span> risk tolerance.
                    </p>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-blue-500">
                  <button className="w-full bg-white text-blue-600 font-semibold py-2 rounded-lg hover:bg-blue-50 transition-colors text-sm">
                    Upload Supplemental Documentation
                  </button>
                </div>
              </Card>
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}