/**
 * Mock Data for National Incidents and Their Impacts on Companies
 */

import { IncidentImpact, IncidentSeverity } from '../types/companyProfiles';

export const MOCK_INCIDENTS: IncidentImpact[] = [
    {
        incident_id: 'I1',
        incident_name: 'Central Bank Interest Rate Hike +2%',
        date: '2024-12-01',
        category: 'Monetary Policy',
        severity: 'high',
        description: 'Central Bank raised policy rates by 200 basis points to combat inflation',

        affected_companies: [
            { company_id: 'COMB', ticker: 'COMB', name: 'Commercial Bank', stock_impact_percent: 5.2, operational_impact: 'Increased net interest margins', recovery_days: 0, sector: 'Banking & Finance' },
            { company_id: 'HNB', ticker: 'HNB', name: 'Hatton National Bank', stock_impact_percent: 4.8, operational_impact: 'Higher lending margins', recovery_days: 0, sector: 'Banking & Finance' },
            { company_id: 'JKH', ticker: 'JKH', name: 'John Keells Holdings', stock_impact_percent: -2.5, operational_impact: 'Increased borrowing costs', recovery_days: 12, sector: 'Manufacturing' },
            { company_id: 'DIAL', ticker: 'DIAL', name: 'Dialog Axiata', stock_impact_percent: -1.8, operational_impact: 'Higher debt servicing costs', recovery_days: 8, sector: 'Telecommunications' },
            { company_id: 'SPEN', ticker: 'SPEN', name: 'Aitken Spence', stock_impact_percent: -3.2, operational_impact: 'Reduced consumer spending', recovery_days: 15, sector: 'Hospitality & Leisure' },
        ],

        sector_impact: [
            { sector: 'Banking & Finance', avg_impact_percent: 5.0, companies_affected: 5, total_companies: 5 },
            { sector: 'Manufacturing', avg_impact_percent: -2.8, companies_affected: 4, total_companies: 4 },
            { sector: 'Telecommunications', avg_impact_percent: -1.5, companies_affected: 2, total_companies: 2 },
            { sector: 'Hospitality & Leisure', avg_impact_percent: -3.5, companies_affected: 2, total_companies: 2 },
        ],

        national_indicators_changed: [
            { indicator_name: 'Interest Rate', change_percent: 20.0, previous_value: 10.0, current_value: 12.0 },
            { indicator_name: 'Lending Rate', change_percent: 15.0, previous_value: 13.5, current_value: 15.5 },
        ],

        total_companies_affected: 13,
        avg_stock_impact: 0.8,
        max_stock_impact: 5.2,
        min_stock_impact: -3.5,
    },

    {
        incident_id: 'I2',
        incident_name: 'Fuel Price Increase +15%',
        date: '2024-11-15',
        category: 'Energy',
        severity: 'high',
        description: 'Government increased fuel prices by 15% due to global oil price surge',

        affected_companies: [
            { company_id: 'HAYL', ticker: 'HAYL', name: 'Hayleys', stock_impact_percent: -8.2, operational_impact: 'Transportation costs up 22%', recovery_days: 25, sector: 'Agriculture' },
            { company_id: 'JKH', ticker: 'JKH', name: 'John Keells Holdings', stock_impact_percent: -2.8, operational_impact: 'Transport segment costs increased', recovery_days: 15, sector: 'Manufacturing' },
            { company_id: 'DIAL', ticker: 'DIAL', name: 'Dialog Axiata', stock_impact_percent: -3.2, operational_impact: 'Tower operations costs up', recovery_days: 18, sector: 'Telecommunications' },
            { company_id: 'COMB', ticker: 'COMB', name: 'Commercial Bank', stock_impact_percent: -1.8, operational_impact: 'Higher operational costs', recovery_days: 12, sector: 'Banking & Finance' },
            { company_id: 'LGAS', ticker: 'LGAS', name: 'Laugfs Gas', stock_impact_percent: -5.5, operational_impact: 'Import costs increased', recovery_days: 20, sector: 'Energy & Power' },
        ],

        sector_impact: [
            { sector: 'Agriculture', avg_impact_percent: -7.5, companies_affected: 2, total_companies: 2 },
            { sector: 'Manufacturing', avg_impact_percent: -4.2, companies_affected: 4, total_companies: 4 },
            { sector: 'Telecommunications', avg_impact_percent: -3.0, companies_affected: 2, total_companies: 2 },
            { sector: 'Energy & Power', avg_impact_percent: -5.0, companies_affected: 2, total_companies: 2 },
        ],

        national_indicators_changed: [
            { indicator_name: 'Fuel Price Index', change_percent: 15.0, previous_value: 100, current_value: 115 },
            { indicator_name: 'Transportation Cost Index', change_percent: 18.0, previous_value: 100, current_value: 118 },
            { indicator_name: 'Inflation', change_percent: 8.5, previous_value: 6.5, current_value: 7.05 },
        ],

        total_companies_affected: 12,
        avg_stock_impact: -4.2,
        max_stock_impact: -1.8,
        min_stock_impact: -8.2,
    },

    {
        incident_id: 'I3',
        incident_name: 'Tourism Boom +40%',
        date: '2024-11-20',
        category: 'Tourism',
        severity: 'medium',
        description: 'Tourist arrivals surged 40% YoY driven by visa-free policy and marketing campaigns',

        affected_companies: [
            { company_id: 'SPEN', ticker: 'SPEN', name: 'Aitken Spence', stock_impact_percent: 12.5, operational_impact: 'Hotel occupancy at 98%', recovery_days: 0, sector: 'Hospitality & Leisure' },
            { company_id: 'JKH', ticker: 'JKH', name: 'John Keells Holdings', stock_impact_percent: 8.2, operational_impact: 'Hotel segment revenue up 45%', recovery_days: 0, sector: 'Manufacturing' },
            { company_id: 'NEST', ticker: 'NEST', name: 'Nestlé Lanka', stock_impact_percent: 3.5, operational_impact: 'Increased F&B demand', recovery_days: 0, sector: 'Consumer Goods' },
            { company_id: 'DIAL', ticker: 'DIAL', name: 'Dialog Axiata', stock_impact_percent: 2.8, operational_impact: 'Roaming revenue increased', recovery_days: 0, sector: 'Telecommunications' },
        ],

        sector_impact: [
            { sector: 'Hospitality & Leisure', avg_impact_percent: 13.5, companies_affected: 2, total_companies: 2 },
            { sector: 'Consumer Goods', avg_impact_percent: 4.2, companies_affected: 3, total_companies: 3 },
            { sector: 'Telecommunications', avg_impact_percent: 2.5, companies_affected: 2, total_companies: 2 },
        ],

        national_indicators_changed: [
            { indicator_name: 'Tourist Arrivals', change_percent: 40.0, previous_value: 150000, current_value: 210000 },
            { indicator_name: 'Tourism Revenue', change_percent: 45.0, previous_value: 500000000, current_value: 725000000 },
            { indicator_name: 'Hotel Occupancy', change_percent: 35.0, previous_value: 65, current_value: 87.75 },
        ],

        total_companies_affected: 8,
        avg_stock_impact: 6.8,
        max_stock_impact: 13.5,
        min_stock_impact: 2.5,
    },

    {
        incident_id: 'I4',
        incident_name: 'Inflation Spike +2.5%',
        date: '2024-10-28',
        category: 'Economic',
        severity: 'high',
        description: 'Consumer price inflation increased to 9% from 6.5% due to supply chain disruptions',

        affected_companies: [
            { company_id: 'NEST', ticker: 'NEST', name: 'Nestlé Lanka', stock_impact_percent: -4.5, operational_impact: 'Input costs increased 12%', recovery_days: 20, sector: 'Consumer Goods' },
            { company_id: 'HEMS', ticker: 'HEMS', name: 'Hemas Holdings', stock_impact_percent: -3.8, operational_impact: 'Consumer demand softened', recovery_days: 18, sector: 'Manufacturing' },
            { company_id: 'COMB', ticker: 'COMB', name: 'Commercial Bank', stock_impact_percent: -2.2, operational_impact: 'Real returns eroded', recovery_days: 15, sector: 'Banking & Finance' },
        ],

        sector_impact: [
            { sector: 'Consumer Goods', avg_impact_percent: -4.8, companies_affected: 3, total_companies: 3 },
            { sector: 'Manufacturing', avg_impact_percent: -3.5, companies_affected: 4, total_companies: 4 },
            { sector: 'Banking & Finance', avg_impact_percent: -2.0, companies_affected: 5, total_companies: 5 },
        ],

        national_indicators_changed: [
            { indicator_name: 'Inflation Rate', change_percent: 38.5, previous_value: 6.5, current_value: 9.0 },
            { indicator_name: 'Consumer Confidence', change_percent: -15.0, previous_value: 100, current_value: 85 },
        ],

        total_companies_affected: 15,
        avg_stock_impact: -3.5,
        max_stock_impact: -2.0,
        min_stock_impact: -4.8,
    },

    {
        incident_id: 'I5',
        incident_name: 'Currency Depreciation -8%',
        date: '2024-10-15',
        category: 'Currency',
        severity: 'critical',
        description: 'Sri Lankan Rupee depreciated 8% against USD due to forex shortage',

        affected_companies: [
            { company_id: 'LGAS', ticker: 'LGAS', name: 'Laugfs Gas', stock_impact_percent: -12.5, operational_impact: 'Import costs surged', recovery_days: 30, sector: 'Energy & Power' },
            { company_id: 'NEST', ticker: 'NEST', name: 'Nestlé Lanka', stock_impact_percent: -6.8, operational_impact: 'Raw material costs up', recovery_days: 25, sector: 'Consumer Goods' },
            { company_id: 'HEMS', ticker: 'HEMS', name: 'Hemas Holdings', stock_impact_percent: -5.2, operational_impact: 'Pharmaceutical imports expensive', recovery_days: 22, sector: 'Manufacturing' },
            { company_id: 'SPEN', ticker: 'SPEN', name: 'Aitken Spence', stock_impact_percent: 4.5, operational_impact: 'USD earnings increased', recovery_days: 0, sector: 'Hospitality & Leisure' },
            { company_id: 'HAYL', ticker: 'HAYL', name: 'Hayleys', stock_impact_percent: 3.8, operational_impact: 'Export earnings boosted', recovery_days: 0, sector: 'Agriculture' },
        ],

        sector_impact: [
            { sector: 'Energy & Power', avg_impact_percent: -11.5, companies_affected: 2, total_companies: 2 },
            { sector: 'Consumer Goods', avg_impact_percent: -6.0, companies_affected: 3, total_companies: 3 },
            { sector: 'Hospitality & Leisure', avg_impact_percent: 5.2, companies_affected: 2, total_companies: 2 },
            { sector: 'Agriculture', avg_impact_percent: 4.5, companies_affected: 2, total_companies: 2 },
        ],

        national_indicators_changed: [
            { indicator_name: 'USD/LKR Exchange Rate', change_percent: 8.0, previous_value: 300, current_value: 324 },
            { indicator_name: 'Import Costs', change_percent: 8.5, previous_value: 100, current_value: 108.5 },
            { indicator_name: 'Export Competitiveness', change_percent: 8.0, previous_value: 100, current_value: 108 },
        ],

        total_companies_affected: 14,
        avg_stock_impact: -2.8,
        max_stock_impact: 5.2,
        min_stock_impact: -12.5,
    },
];

// Helper functions
export function getIncidentById(id: string): IncidentImpact | undefined {
    return MOCK_INCIDENTS.find(i => i.incident_id === id);
}

export function getRecentIncidents(limit: number = 5): IncidentImpact[] {
    return [...MOCK_INCIDENTS]
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, limit);
}

export function getIncidentsByCategory(category: string): IncidentImpact[] {
    return MOCK_INCIDENTS.filter(i => i.category === category);
}

export function getIncidentsBySeverity(severity: IncidentSeverity): IncidentImpact[] {
    return MOCK_INCIDENTS.filter(i => i.severity === severity);
}

export function getHighImpactIncidents(threshold: number = 5): IncidentImpact[] {
    return MOCK_INCIDENTS.filter(i => Math.abs(i.avg_stock_impact) >= threshold);
}
