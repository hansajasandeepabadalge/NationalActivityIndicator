'use client';

/**
 * National Incidents Impact Dashboard
 * Main dashboard showing how national incidents affect CSE companies
 */

import React, { useState, useMemo } from 'react';
import { AlertCircle, TrendingUp, TrendingDown, Building2, Calendar, Filter } from 'lucide-react';
import { CompanyImpactCard } from './CompanyImpactCard';
import { ALL_COMPANIES } from '@/data/mockCompanies';
import { MOCK_INCIDENTS, getRecentIncidents } from '@/data/mockIncidents';
import { WEATHER_DISASTER_INCIDENTS } from '@/data/weatherIncidents';
import {
    CompanyProfile,
    SectorType,
    IncidentImpact,
    formatPercent,
    getSeverityColor,
    SECTOR_COLORS,
    SECTOR_ICONS,
} from '@/types/companyProfiles';

type SortOption = 'impact' | 'name' | 'price' | 'sector';

export function NationalIncidentsImpactDashboard() {
    const [selectedSector, setSelectedSector] = useState<SectorType | 'All'>('All');
    const [sortBy, setSortBy] = useState<SortOption>('impact');
    const [selectedIncident, setSelectedIncident] = useState<string | null>(null);

    const sectors: Array<SectorType | 'All'> = [
        'All',
        'Banking & Finance',
        'Manufacturing',
        'Telecommunications',
        'Consumer Goods',
        'Hospitality & Leisure',
        'Energy & Power',
        'Agriculture',
    ];

    // Filter and sort companies
    const filteredCompanies = useMemo(() => {
        let companies = [...ALL_COMPANIES];

        // Filter by sector
        if (selectedSector !== 'All') {
            companies = companies.filter(c => c.sector === selectedSector);
        }

        // Sort
        switch (sortBy) {
            case 'impact':
                companies.sort((a, b) => {
                    const aImpact = a.recent_incidents_impact[0]?.stock_impact_percent || 0;
                    const bImpact = b.recent_incidents_impact[0]?.stock_impact_percent || 0;
                    return Math.abs(bImpact) - Math.abs(aImpact);
                });
                break;
            case 'name':
                companies.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case 'price':
                companies.sort((a, b) => b.stock_data.current_price - a.stock_data.current_price);
                break;
            case 'sector':
                companies.sort((a, b) => a.sector.localeCompare(b.sector));
                break;
        }

        return companies;
    }, [selectedSector, sortBy]);

    // Get recent incidents (including weather)
    const allIncidents = [...MOCK_INCIDENTS, ...WEATHER_DISASTER_INCIDENTS];
    const recentIncidents = allIncidents
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, 5);

    // Calculate summary stats
    const stats = useMemo(() => {
        const activeIncidents = recentIncidents.length;
        const highImpactCompanies = ALL_COMPANIES.filter(c =>
            c.recent_incidents_impact.some(i => Math.abs(i.stock_impact_percent) > 5)
        ).length;
        const sectorsMonitored = new Set(ALL_COMPANIES.map(c => c.sector)).size;

        return { activeIncidents, highImpactCompanies, sectorsMonitored };
    }, [recentIncidents]);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl shadow-xl p-8 text-white">
                <h1 className="text-3xl font-bold mb-2">National Indicators Impact Analysis</h1>
                <p className="text-blue-100 text-lg">
                    How national events, weather, and economic indicators affect CSE companies
                </p>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-red-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Active Incidents</p>
                            <p className="text-4xl font-bold text-red-600">{stats.activeIncidents}</p>
                        </div>
                        <AlertCircle className="w-12 h-12 text-red-400" />
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-orange-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">High Impact Companies</p>
                            <p className="text-4xl font-bold text-orange-600">{stats.highImpactCompanies}</p>
                        </div>
                        <Building2 className="w-12 h-12 text-orange-400" />
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600 mb-1">Monitored Sectors</p>
                            <p className="text-4xl font-bold text-blue-600">{stats.sectorsMonitored}</p>
                        </div>
                        <Filter className="w-12 h-12 text-blue-400" />
                    </div>
                </div>
            </div>

            {/* Recent Incidents */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <Calendar className="w-6 h-6 text-blue-600" />
                    Recent National Incidents
                </h2>
                <div className="space-y-3">
                    {recentIncidents.map((incident: IncidentImpact) => (
                        <div
                            key={incident.incident_id}
                            className="p-4 bg-gray-50 rounded-lg border-2 border-gray-200 hover:border-blue-400 transition-colors cursor-pointer"
                            onClick={() => setSelectedIncident(incident.incident_id)}
                        >
                            <div className="flex items-start justify-between mb-2">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getSeverityColor(incident.severity)}`}>
                                            {incident.severity.toUpperCase()}
                                        </span>
                                        <span className="text-xs text-gray-500">{incident.category}</span>
                                        <span className="text-xs text-gray-400">•</span>
                                        <span className="text-xs text-gray-500">{new Date(incident.date).toLocaleDateString()}</span>
                                    </div>
                                    <h3 className="font-semibold text-gray-900">{incident.incident_name}</h3>
                                    <p className="text-sm text-gray-600 mt-1">{incident.description}</p>
                                </div>
                                <div className="text-right ml-4">
                                    <p className="text-sm text-gray-500">Avg Impact</p>
                                    <p className={`text-2xl font-bold ${incident.avg_stock_impact >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatPercent(incident.avg_stock_impact)}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                                <span>📊 {incident.total_companies_affected} companies affected</span>
                                <span>📈 Max: {formatPercent(incident.max_stock_impact)}</span>
                                <span>📉 Min: {formatPercent(incident.min_stock_impact)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <div className="flex items-center justify-between flex-wrap gap-4">
                    <div className="flex items-center gap-3">
                        <label className="text-sm font-semibold text-gray-700">Sector:</label>
                        <select
                            value={selectedSector}
                            onChange={(e) => setSelectedSector(e.target.value as SectorType | 'All')}
                            className="px-4 py-2 border-2 border-gray-300 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            {sectors.map((sector) => (
                                <option key={sector} value={sector}>
                                    {sector !== 'All' && SECTOR_ICONS[sector as SectorType]} {sector}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="flex items-center gap-3">
                        <label className="text-sm font-semibold text-gray-700">Sort by:</label>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as SortOption)}
                            className="px-4 py-2 border-2 border-gray-300 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="impact">Impact</option>
                            <option value="name">Name</option>
                            <option value="price">Price</option>
                            <option value="sector">Sector</option>
                        </select>
                    </div>

                    <div className="text-sm text-gray-600">
                        Showing <span className="font-semibold">{filteredCompanies.length}</span> companies
                    </div>
                </div>
            </div>

            {/* Company Grid */}
            <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Company Impact Analysis</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {filteredCompanies.map((company) => (
                        <CompanyImpactCard
                            key={company.company_id}
                            company={company}
                            onClick={() => {
                                // TODO: Open detailed view
                                console.log('View company:', company.ticker);
                            }}
                        />
                    ))}
                </div>
            </div>

            {/* Empty State */}
            {filteredCompanies.length === 0 && (
                <div className="text-center py-12 bg-white rounded-xl shadow-lg">
                    <p className="text-gray-500 text-lg">No companies found for the selected filters</p>
                </div>
            )}
        </div>
    );
}
