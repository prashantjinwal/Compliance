'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { Upload, X } from 'lucide-react'

const industries = [
  'Financial Services',
  'Healthcare',
  'Technology',
  'Manufacturing',
  'Retail',
  'Energy',
]

const companySizes = [
  '1-100 Employees',
  '101-500 Employees',
  '501-1000 Employees',
  '1000+ Employees',
]

const regulations = [
  'EU AI Act',
  'GDPR',
  'CCPA',
  'HIPAA',
  'SOX',
]

const departments = [
  'Research & Development',
  'Customer Operations',
  'Marketing & Sales',
  'Human Resources',
]

export default function CompanyProfilePage() {
  const [selectedRegulations, setSelectedRegulations] = useState(['EU AI Act', 'GDPR'])
  const [selectedDepartments, setSelectedDepartments] = useState(['Research & Development', 'Customer Operations', 'Human Resources'])
  const [riskTolerance, setRiskTolerance] = useState('moderate')

  const toggleRegulation = (reg) => {
    setSelectedRegulations(prev =>
      prev.includes(reg) ? prev.filter(r => r !== reg) : [...prev, reg]
    )
  }

  const toggleDepartment = (dept) => {
    setSelectedDepartments(prev =>
      prev.includes(dept) ? prev.filter(d => d !== dept) : [...prev, dept]
    )
  }

  const removeRegulation = (reg) => {
    setSelectedRegulations(prev => prev.filter(r => r !== reg))
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 ml-56">
        <Topbar title="Company Profile" />

        <main className="pt-20 px-8 pb-8">
          <p className="text-gray-600 text-sm mb-8">Define your organization&apos;s regulatory perimeter.</p>

          <div className="grid grid-cols-3 gap-8">
            {/* Left: Form */}
            <div className="col-span-2 space-y-6">
              {/* Company Information */}
              <Card className="p-6 bg-white border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Company Information</h3>

                <div className="space-y-6">
                  <div>
                    <Label className="text-sm font-medium text-gray-900 mb-2 block">Company Name</Label>
                    <Input
                      defaultValue="Global Dynamics Inc."
                      className="border-gray-200 bg-white placeholder-gray-400"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <Label className="text-sm font-medium text-gray-900 mb-2 block">Industry</Label>
                      <Select defaultValue="financial">
                        <SelectTrigger className="border-gray-200 bg-white">
                          <SelectValue placeholder="Select industry" />
                        </SelectTrigger>
                        <SelectContent>
                          {industries.map(ind => (
                            <SelectItem key={ind} value={ind.toLowerCase()}>
                              {ind}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="text-sm font-medium text-gray-900 mb-2 block">Organization Size</Label>
                      <Select defaultValue="1000">
                        <SelectTrigger className="border-gray-200 bg-white">
                          <SelectValue placeholder="Select size" />
                        </SelectTrigger>
                        <SelectContent>
                          {companySizes.map(size => (
                            <SelectItem key={size} value={size}>
                              {size}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-gray-900 mb-2 block">Primary Region</Label>
                    <Input
                      defaultValue="North America & European Union"
                      className="border-gray-200 bg-white placeholder-gray-400"
                    />
                  </div>
                </div>
              </Card>

              {/* Regulations */}
              <Card className="p-6 bg-white border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Applicable Regulations</h3>

                <div className="space-y-4 mb-6">
                  {regulations.map(reg => (
                    <div key={reg} className="flex items-center gap-3">
                      <Checkbox
                        id={reg}
                        checked={selectedRegulations.includes(reg)}
                        onCheckedChange={() => toggleRegulation(reg)}
                        className="border-gray-300"
                      />
                      <Label htmlFor={reg} className="text-sm text-gray-700 cursor-pointer font-normal">
                        {reg}
                      </Label>
                    </div>
                  ))}
                </div>

                {selectedRegulations.length > 0 && (
                  <div>
                    <Label className="text-xs font-medium text-gray-600 mb-3 block">+ Add Regulation</Label>
                    <div className="flex flex-wrap gap-2">
                      {selectedRegulations.map(reg => (
                        <Badge key={reg} className="bg-blue-600 text-white pr-2 flex items-center gap-1">
                          {reg}
                          <button
                            onClick={() => removeRegulation(reg)}
                            className="hover:bg-blue-700 rounded ml-1"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </Card>

              {/* Departments */}
              <Card className="p-6 bg-white border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">In-Scope Departments</h3>

                <div className="space-y-4">
                  {departments.map(dept => (
                    <div key={dept} className="flex items-center gap-3">
                      <Checkbox
                        id={dept}
                        checked={selectedDepartments.includes(dept)}
                        onCheckedChange={() => toggleDepartment(dept)}
                        className="border-gray-300"
                      />
                      <Label htmlFor={dept} className="text-sm text-gray-700 cursor-pointer font-normal">
                        {dept}
                      </Label>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Risk Tolerance */}
              <Card className="p-6 bg-white border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Institutional Risk Tolerance</h3>

                <RadioGroup value={riskTolerance} onValueChange={setRiskTolerance}>
                  <div className="grid grid-cols-3 gap-4">
                    <div className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      riskTolerance === 'conservative' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        <RadioGroupItem value="conservative" id="conservative" />
                        <Label htmlFor="conservative" className="font-medium text-sm text-gray-900 cursor-pointer">
                          Conservative
                        </Label>
                      </div>
                      <p className="text-xs text-gray-600">Low appetite for risk</p>
                    </div>

                    <div className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      riskTolerance === 'moderate' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        <RadioGroupItem value="moderate" id="moderate" />
                        <Label htmlFor="moderate" className="font-medium text-sm text-gray-900 cursor-pointer">
                          Moderate
                        </Label>
                      </div>
                      <p className="text-xs text-gray-600">Balanced growth</p>
                    </div>

                    <div className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      riskTolerance === 'progressive' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        <RadioGroupItem value="progressive" id="progressive" />
                        <Label htmlFor="progressive" className="font-medium text-sm text-gray-900 cursor-pointer">
                          Progressive
                        </Label>
                      </div>
                      <p className="text-xs text-gray-600">High innovation focus</p>
                    </div>
                  </div>
                </RadioGroup>
              </Card>

              <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-6 text-base rounded-lg">
                Save Institutional Profile
              </Button>
            </div>

            {/* Right: Summary Card */}
            <div>
              <Card className="p-6 bg-gradient-to-br from-blue-600 to-blue-800 text-white border-none sticky top-24">
                <div className="mb-6">
                  <p className="text-blue-100 text-xs font-semibold uppercase tracking-wide">Entity Preview</p>
                  <h2 className="text-2xl font-bold mt-2">Global Dynamics Inc.</h2>
                </div>

                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-1">INDUSTRY</p>
                    <p className="font-medium">Financial Services</p>
                  </div>

                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-1">REGION</p>
                    <p className="font-medium">EU & NA Markets</p>
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
                    <p className="font-medium">12,450 FTEs</p>
                  </div>

                  <hr className="border-blue-500 my-4" />

                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-3">ACTIVE FRAMEWORKS</p>
                    <div className="space-y-2">
                      {selectedRegulations.map(reg => (
                        <div key={reg} className="flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-blue-300" />
                          <span className="text-sm">{reg}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-blue-100 text-xs font-semibold mb-3 mt-4">ORGANIZATIONAL PROFILE</p>
                    <p className="text-sm leading-relaxed text-blue-50">
                      Your institutional profile is used to calibrate AI-driven compliance insights. Measures now anticipating your specific risk surface across the {selectedRegulations.length} active compliance frameworks with emphasis on internal alignment with risk tolerance.
                    </p>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-blue-500">
                  <button className="w-full bg-white text-blue-600 font-semibold py-2 rounded-lg hover:bg-blue-50 transition-colors">
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
