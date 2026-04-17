"use client";

import { Sidebar } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";
import { Card } from "@/components/ui/card";
import { useProtectedUser } from "@/hooks/use-protected-user";
import { getOrganizationName, getSafeOrganizationValue } from "@/lib/api";
import { AlertCircle, CheckCircle2, Clock, TrendingUp } from "lucide-react";

function buildDashboardMetrics(user) {
  const profileChecks = [
    user && user.full_name,
    user && user.email,
    user && user.role && user.role.name,
    user && user.organization && user.organization.name,
    user &&
      user.organization &&
      getSafeOrganizationValue(user.organization.industry),
    user &&
      user.organization &&
      getSafeOrganizationValue(user.organization.country),
  ];

  const completedChecks = profileChecks.filter(Boolean).length;
  const totalChecks = profileChecks.length;
  const missingFields = totalChecks - completedChecks;

  return {
    complianceScore: Math.round((completedChecks / totalChecks) * 100),
    activeAlerts: missingFields,
    pendingTasks: 0,
    recentUpdates: completedChecks,
  };
}

export default function DashboardPage() {
  const { user, loading, error } = useProtectedUser();

  if (loading) {
    return null;
  }

  const metrics = buildDashboardMetrics(user);
  const organizationName = getOrganizationName(user);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar user={user} />

      <div className="flex-1 ml-56">
        <Topbar title="Executive Dashboard" user={user} />

        <main className="pt-20 px-8 pb-8">
          <p className="text-gray-600 text-sm mb-8">
            Real-time institutional oversight and regulatory monitoring for{" "}
            {organizationName}.
          </p>

          {error ? (
            <Card className="p-4 bg-red-50 border-red-200 mb-6">
              <p className="text-sm text-red-700">
                {error}
              </p>
            </Card>
          ) : null}

          <div className="grid grid-cols-4 gap-6 mb-8">
            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">
                    Compliance Score
                  </p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">
                    {metrics.complianceScore}%
                  </p>
                  <p className="text-gray-500 text-xs mt-1">
                    Based on current profile completeness
                  </p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">
                    Active Alerts
                  </p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">
                    {metrics.activeAlerts}
                  </p>
                  <p className="text-gray-500 text-xs mt-1">
                    Missing profile fields need attention
                  </p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">
                    Pending Tasks
                  </p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">
                    {metrics.pendingTasks}
                  </p>
                  <p className="text-gray-500 text-xs mt-1">
                    Waiting for task API integration
                  </p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-yellow-100 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 bg-white border-gray-200">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">
                    Recent Updates
                  </p>
                  <p className="text-4xl font-bold text-gray-900 mt-2">
                    {metrics.recentUpdates}
                  </p>
                  <p className="text-gray-500 text-xs mt-1">
                    Available account and organization fields
                  </p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
