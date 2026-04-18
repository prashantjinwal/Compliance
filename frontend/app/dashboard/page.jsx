"use client";

import { useEffect, useState } from "react";

import { Sidebar } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";
import { Card } from "@/components/ui/card";
import { useProtectedUser } from "@/hooks/use-protected-user";
import { fetchDashboardSummary, getOrganizationName } from "@/lib/api";
import { AlertCircle, CheckCircle2, Clock, TrendingUp } from "lucide-react";

function buildDashboardMetrics(summary) {
  const totalTasks = Number(summary?.total_tasks || 0);
  const byStatus = summary?.by_status || {};
  const completedTasks = Number(byStatus.completed || 0);
  const pendingTasks =
    Number(byStatus.pending || 0) +
    Number(byStatus.in_progress || 0) +
    Number(byStatus.blocked || 0);

  return {
    complianceScore:
      totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0,
    activeAlerts:
      Number(summary?.open_risks || 0) +
      Number(summary?.overdue_tasks?.length || 0),
    pendingTasks,
    recentUpdates: Number(summary?.new_regulations || 0),
  };
}

export default function DashboardPage() {
  const { user, loading, error } = useProtectedUser();
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [dashboardError, setDashboardError] = useState("");

  useEffect(() => {
    if (!user) {
      return;
    }

    let isActive = true;

    async function loadDashboard() {
      try {
        const summary = await fetchDashboardSummary();

        if (!isActive) {
          return;
        }

        setDashboardSummary(summary);
        setDashboardError("");
      } catch (requestError) {
        if (!isActive) {
          return;
        }

        setDashboardSummary(null);
        setDashboardError(
          requestError.message || "Unable to load dashboard summary."
        );
      }
    }

    loadDashboard();

    return () => {
      isActive = false;
    };
  }, [user]);

  if (loading) {
    return null;
  }

  const metrics = buildDashboardMetrics(dashboardSummary);
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

          {error || dashboardError ? (
            <Card className="p-4 bg-red-50 border-red-200 mb-6">
              <p className="text-sm text-red-700">{dashboardError || error}</p>
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
                    Based on completed compliance tasks
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
                    Open risks and overdue tasks
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
                    Pending, in progress, and blocked tasks
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
                    New regulations added in the last 7 days
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
