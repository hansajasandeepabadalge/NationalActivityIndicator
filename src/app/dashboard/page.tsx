'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, ProtectedRoute } from '@/contexts/AuthContext';
import { useAdminDashboard, useNationalIndicators, useBusinessInsights, useOperationalIndicators } from '@/hooks/useDashboard';

// Dashboard Stats Card Component
function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color = 'blue' 
}: { 
  title: string; 
  value: string | number; 
  subtitle?: string;
  icon: React.ReactNode;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    yellow: 'from-yellow-500 to-yellow-600',
    red: 'from-red-500 to-red-600',
    purple: 'from-purple-500 to-purple-600',
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className={`bg-gradient-to-r ${colorClasses[color]} p-4`}>
        <div className="flex items-center justify-between">
          <div className="text-white">
            <p className="text-sm opacity-80">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
            {subtitle && <p className="text-sm opacity-80">{subtitle}</p>}
          </div>
          <div className="text-white/80 text-3xl">
            {icon}
          </div>
        </div>
      </div>
    </div>
  );
}

// PESTEL Category Badge
function PestelBadge({ category }: { category: string }) {
  const colors: Record<string, string> = {
    Political: 'bg-red-100 text-red-800',
    Economic: 'bg-blue-100 text-blue-800',
    Social: 'bg-green-100 text-green-800',
    Technological: 'bg-purple-100 text-purple-800',
    Environmental: 'bg-emerald-100 text-emerald-800',
    Legal: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[category] || 'bg-gray-100 text-gray-800'}`}>
      {category}
    </span>
  );
}

// Trend Arrow Component
function TrendArrow({ trend }: { trend: string }) {
  if (trend === 'up') {
    return <span className="text-green-500">↑</span>;
  } else if (trend === 'down') {
    return <span className="text-red-500">↓</span>;
  }
  return <span className="text-gray-400">→</span>;
}

// Severity Badge
function SeverityBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    high: 'bg-red-100 text-red-800 border-red-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200',
  };

  return (
    <span className={`px-2 py-1 rounded-md text-xs font-medium border ${colors[level] || 'bg-gray-100 text-gray-800'}`}>
      {level.toUpperCase()}
    </span>
  );
}

// Loading Skeleton
function LoadingSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="animate-pulse space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-12 bg-gray-200 rounded"></div>
      ))}
    </div>
  );
}

// Main Dashboard Content
function DashboardContent() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { data: dashboard, isLoading: dashboardLoading, error: dashboardError } = useAdminDashboard();
  const { data: indicators, isLoading: indicatorsLoading, error: indicatorsError } = useNationalIndicators(undefined, 100);
  const { data: insights, isLoading: insightsLoading, error: insightsError } = useBusinessInsights(undefined, undefined, undefined, 10);
  const { data: operationalIndicators, isLoading: operationalLoading, error: operationalError } = useOperationalIndicators(20);

  // Group indicators by PESTEL category
  const indicatorsByCategory = React.useMemo(() => {
    if (!indicators) return {};
    return indicators.reduce((acc, indicator) => {
      const category = indicator.pestel_category || 'Other';
      if (!acc[category]) acc[category] = [];
      acc[category].push(indicator);
      return acc;
    }, {} as Record<string, typeof indicators>);
  }, [indicators]);

  // Debug logging
  React.useEffect(() => {
    console.log('Dashboard state:', { 
      dashboard, dashboardError,
      indicators: indicators?.length, indicatorsError,
      insights: insights?.length, insightsError 
    });
  }, [dashboard, dashboardError, indicators, indicatorsError, insights, insightsError]);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                National Activity Indicator
              </h1>
              <p className="text-sm text-gray-500">Dashboard</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.full_name || user?.email}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardLoading ? (
            <>
              <div className="h-24 bg-gray-200 rounded-xl animate-pulse"></div>
              <div className="h-24 bg-gray-200 rounded-xl animate-pulse"></div>
              <div className="h-24 bg-gray-200 rounded-xl animate-pulse"></div>
              <div className="h-24 bg-gray-200 rounded-xl animate-pulse"></div>
            </>
          ) : (
            <>
              <StatCard
                title="Total Indicators"
                value={dashboard?.total_indicators || 0}
                icon={<span>📊</span>}
                color="blue"
              />
              <StatCard
                title="Active Companies"
                value={dashboard?.total_companies || 0}
                icon={<span>🏢</span>}
                color="green"
              />
              <StatCard
                title="Business Insights"
                value={dashboard?.total_insights || 0}
                icon={<span>💡</span>}
                color="purple"
              />
              <StatCard
                title="Active Risks"
                value={dashboard?.total_active_risks || 0}
                icon={<span>⚠️</span>}
                color="red"
              />
            </>
          )}
        </div>

        {/* National Indicators by PESTEL Category */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">National Indicators (Layer 2)</h2>

          {indicatorsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <LoadingSkeleton rows={3} />
              <LoadingSkeleton rows={3} />
              <LoadingSkeleton rows={3} />
            </div>
          ) : indicators && indicators.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(indicatorsByCategory).map(([category, categoryIndicators]) => (
                <div key={category} className="bg-white rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <PestelBadge category={category} />
                      <span className="text-sm text-gray-500">({categoryIndicators.length})</span>
                    </div>
                  </div>

                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {categoryIndicators.map((indicator) => (
                      <div
                        key={indicator.indicator_id}
                        className="p-2 bg-gray-50 rounded hover:bg-gray-100 transition"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0 pr-2">
                            <p className="text-sm font-medium text-gray-900 truncate" title={indicator.indicator_name}>
                              {indicator.indicator_name}
                            </p>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <p className="text-sm font-semibold text-gray-900">
                              {indicator.current_value?.toFixed(1) || 'N/A'}
                              <TrendArrow trend={indicator.trend || 'stable'} />
                            </p>
                          </div>
                        </div>
                        {indicator.change_percentage !== undefined && indicator.change_percentage !== null && (
                          <p className={`text-xs mt-1 ${indicator.change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {indicator.change_percentage >= 0 ? '+' : ''}{indicator.change_percentage.toFixed(1)}%
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 bg-white rounded-xl shadow-lg">
              <p className="text-gray-500">No indicators found</p>
              {indicatorsError && (
                <p className="text-red-500 text-sm mt-2">Error: {indicatorsError}</p>
              )}
            </div>
          )}
        </div>

        {/* Two Column Layout for Operational & Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Operational Indicators (Layer 3) */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Operational Indicators</h2>
              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded">Layer 3</span>
            </div>

            {operationalLoading ? (
              <LoadingSkeleton rows={8} />
            ) : operationalIndicators && operationalIndicators.length > 0 ? (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {operationalIndicators.map((indicator) => (
                  <div
                    key={indicator.indicator_id}
                    className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0 pr-2">
                        <p className="font-medium text-gray-900 text-sm">{indicator.indicator_name}</p>
                        <p className="text-xs text-gray-500 mt-1">{indicator.category}</p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="text-base font-semibold text-gray-900">
                          {indicator.current_value?.toFixed(1) || 'N/A'}
                          <TrendArrow trend={indicator.trend || 'stable'} />
                        </p>
                        {indicator.deviation !== undefined && indicator.deviation !== null && (
                          <p className={`text-xs mt-1 ${Math.abs(indicator.deviation) > 10 ? 'text-red-600 font-medium' : 'text-gray-600'}`}>
                            {indicator.deviation >= 0 ? '+' : ''}{indicator.deviation.toFixed(1)}% baseline
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No operational indicators found</p>
                {operationalError && (
                  <p className="text-red-500 text-sm mt-2">Error: {operationalError}</p>
                )}
              </div>
            )}
          </div>

          {/* Business Insights */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Business Insights</h2>
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">Layer 4</span>
            </div>

            {insightsLoading ? (
              <LoadingSkeleton rows={8} />
            ) : insights && insights.length > 0 ? (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {insights.map((insight) => (
                  <div
                    key={insight.insight_id}
                    className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{insight.title}</p>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {insight.description}
                        </p>
                      </div>
                      <SeverityBadge level={insight.severity_level || 'medium'} />
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-gray-500 capitalize">{insight.insight_type}</span>
                      {insight.confidence_score && (
                        <span className="text-xs text-gray-400">
                          • {(insight.confidence_score * 100).toFixed(0)}% confidence
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No insights found</p>
                {insightsError && (
                  <p className="text-red-500 text-sm mt-2">Error: {insightsError}</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity Summary */}
        {dashboard?.recent_activity && (
          <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">
                  {dashboard.recent_activity.new_articles_24h || 0}
                </p>
                <p className="text-sm text-gray-600">New Articles (24h)</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">
                  {dashboard.recent_activity.updated_indicators_24h || 0}
                </p>
                <p className="text-sm text-gray-600">Updated Indicators (24h)</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">
                  {dashboard.recent_activity.new_insights_24h || 0}
                </p>
                <p className="text-sm text-gray-600">New Insights (24h)</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// Dashboard Page with Protection
export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
