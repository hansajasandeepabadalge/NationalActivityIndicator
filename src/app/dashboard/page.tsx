'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, ProtectedRoute } from '@/contexts/AuthContext';
import { useAdminDashboard, useNationalIndicators, useBusinessInsights, useOperationalIndicators, useCompanies } from '@/hooks/useDashboard';

// Import new components
import { StatCard } from './components/shared/StatCard';
import { PestelBadge, SeverityBadge, TrendArrow } from './components/shared/Badge';
import { LoadingSkeleton } from './components/shared/LoadingSkeleton';

// Layer 1 Components
import { DataSourcesMonitor } from './components/layer1/DataSourcesMonitor';
import { ScrapingJobsPanel } from './components/layer1/ScrapingJobsPanel';
import { RawArticlesStream } from './components/layer1/RawArticlesStream';
import { ProcessingPipelineStatus } from './components/layer1/ProcessingPipelineStatus';

// Layer 2 Components
import { IndicatorAnalysis } from './components/layer2/IndicatorAnalysis';

// Layer 3 Components
import { OperationalOverview } from './components/layer3/OperationalOverview';

// Tab type
type DashboardTab = 'overview' | 'layer1' | 'layer2' | 'system';

// Main Dashboard Content
function DashboardContent() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview');
  const [selectedCompany, setSelectedCompany] = useState<string | undefined>(undefined);

  const { data: dashboard, isLoading: dashboardLoading, error: dashboardError } = useAdminDashboard();
  const { data: indicators, isLoading: indicatorsLoading, error: indicatorsError } = useNationalIndicators(undefined, 100);
  const { data: insights, isLoading: insightsLoading, error: insightsError } = useBusinessInsights(selectedCompany, undefined, undefined, 10);
  const { data: operationalIndicators, isLoading: operationalLoading, error: operationalError } = useOperationalIndicators(20);
  const { data: companies, isLoading: companiesLoading } = useCompanies();

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

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const tabs = [
    { id: 'overview' as const, label: 'Overview', icon: '📊' },
    { id: 'layer1' as const, label: 'Data Collection (L1)', icon: '🔄' },
    { id: 'layer2' as const, label: 'Indicators & Analysis (L2-4)', icon: '📈' },
    { id: 'system' as const, label: 'System Health', icon: '🏥' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                National Activity Indicator
              </h1>
              <p className="text-sm text-gray-500">Admin Dashboard</p>
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

          {/* Tab Navigation */}
          <div className="mt-4 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm transition
                    ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <span>{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Company Filter */}
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-gray-700">Filter by Company:</span>
                <select
                  value={selectedCompany || ''}
                  onChange={(e) => setSelectedCompany(e.target.value || undefined)}
                  className="block w-64 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  disabled={companiesLoading}
                >
                  <option value="">All Companies</option>
                  {companies?.map((company) => (
                    <option key={company.id} value={company.id}>
                      {company.name} ({company.industry})
                    </option>
                  ))}
                </select>
              </div>
              {selectedCompany && (
                <button
                  onClick={() => setSelectedCompany(undefined)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Clear Filter
                </button>
              )}
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {dashboardLoading ? (
                <>
                  <LoadingSkeleton variant="stat" />
                  <LoadingSkeleton variant="stat" />
                  <LoadingSkeleton variant="stat" />
                  <LoadingSkeleton variant="stat" />
                </>
              ) : (
                <>
                  <StatCard
                    title="Total Indicators"
                    value={dashboard?.total_indicators || 0}
                    icon={<span>📊</span>}
                  />
                  <StatCard
                    title="Active Companies"
                    value={dashboard?.total_companies || 0}
                    icon={<span>🏢</span>}
                  />
                  <StatCard
                    title="Business Insights"
                    value={dashboard?.total_insights || 0}
                    icon={<span>💡</span>}
                  />
                  <StatCard
                    title="Active Risks"
                    value={dashboard?.total_active_risks || 0}
                    icon={<span>⚠️</span>}
                  />
                </>
              )}
            </div>

            {/* National Indicators by PESTEL Category */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">National Indicators (Layer 2)</h2>

              {indicatorsLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <LoadingSkeleton variant="card" rows={3} />
                  <LoadingSkeleton variant="card" rows={3} />
                  <LoadingSkeleton variant="card" rows={3} />
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
                </div>
              )}
            </div>

            {/* Operational & Insights Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Operational Indicators */}
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
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No operational indicators found</p>
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
                          {(insight as any).confidence_score && (
                            <span className="text-xs text-gray-400">
                              • {((insight as any).confidence_score * 100).toFixed(0)}% confidence
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No insights found</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Layer 1: Data Collection Tab */}
        {activeTab === 'layer1' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Layer 1: Data Collection Pipeline</h2>
              <p className="text-gray-600">Monitor data sources, scraping jobs, raw articles, and processing pipeline status</p>
            </div>

            {/* Data Sources Monitor */}
            <DataSourcesMonitor />

            {/* Processing Pipeline Status */}
            <ProcessingPipelineStatus />

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Scraping Jobs */}
              <ScrapingJobsPanel
                onRetry={(jobId) => console.log('Retry job:', jobId)}
              />

              {/* Raw Articles Stream */}
              <RawArticlesStream
                onArticleClick={(article) => console.log('View article:', article)}
              />
            </div>
          </div>
        )}

        {/* Layer 2-4: Indicators & Analysis Tab */}
        {activeTab === 'layer2' && (
          <IndicatorAnalysis />
        )}

        {/* System Health Tab */}
        {activeTab === 'system' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">System Health & Monitoring</h2>
              <p className="text-gray-600">Overall system status and performance metrics</p>
            </div>

            {/* Placeholder for system health components */}
            <div className="bg-green-50 border-2 border-green-200 rounded-xl p-8 text-center">
              <div className="text-4xl mb-4">🏥</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">System Health Dashboard Coming Soon</h3>
              <p className="text-gray-600">
                This section will display system health metrics, database status, API performance, and error logs.
              </p>
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
