/**
 * Weather and Disaster Impact Incidents for Sri Lankan Companies
 * Focus on how natural events affect business operations
 */

import { IncidentImpact } from '../types/companyProfiles';

export const WEATHER_DISASTER_INCIDENTS: IncidentImpact[] = [
    {
        incident_id: 'W1',
        incident_name: 'Heavy Monsoon Rains & Flooding',
        date: '2024-11-25',
        category: 'Weather',
        severity: 'critical',
        description: 'Severe monsoon rains caused widespread flooding in Western and Southern provinces, disrupting transportation and agriculture',

        affected_companies: [
            { company_id: 'HAYL', ticker: 'HAYL', name: 'Hayleys', stock_impact_percent: -12.5, operational_impact: 'Tea and rubber plantations flooded, harvesting suspended for 2 weeks', recovery_days: 35, sector: 'Agriculture' },
            { company_id: 'WATA', ticker: 'WATA', name: 'Watawala Plantations', stock_impact_percent: -10.8, operational_impact: 'Crop damage in low-lying estates, soil erosion affecting yields', recovery_days: 40, sector: 'Agriculture' },
            { company_id: 'JKH', ticker: 'JKH', name: 'John Keells Holdings', stock_impact_percent: -5.2, operational_impact: 'Transportation delays affecting logistics and retail distribution', recovery_days: 15, sector: 'Manufacturing' },
            { company_id: 'SPEN', ticker: 'SPEN', name: 'Aitken Spence', stock_impact_percent: -8.5, operational_impact: 'Tourist cancellations, resort access roads damaged', recovery_days: 20, sector: 'Hospitality & Leisure' },
            { company_id: 'CARG', ticker: 'CARG', name: 'Cargills Ceylon', stock_impact_percent: -4.2, operational_impact: 'Supply chain disruptions, store closures in affected areas', recovery_days: 12, sector: 'Consumer Goods' },
        ],

        sector_impact: [
            { sector: 'Agriculture', avg_impact_percent: -11.5, companies_affected: 2, total_companies: 2 },
            { sector: 'Hospitality & Leisure', avg_impact_percent: -8.5, companies_affected: 2, total_companies: 2 },
            { sector: 'Manufacturing', avg_impact_percent: -5.0, companies_affected: 3, total_companies: 4 },
            { sector: 'Consumer Goods', avg_impact_percent: -4.2, companies_affected: 2, total_companies: 3 },
        ],

        national_indicators_changed: [
            { indicator_name: 'Agricultural Output', change_percent: -15.0, previous_value: 100, current_value: 85 },
            { indicator_name: 'Transportation Index', change_percent: -25.0, previous_value: 100, current_value: 75 },
            { indicator_name: 'Tourism Arrivals', change_percent: -12.0, previous_value: 200000, current_value: 176000 },
        ],

        total_companies_affected: 12,
        avg_stock_impact: -7.2,
        max_stock_impact: -4.2,
        min_stock_impact: -12.5,
    },

    {
        incident_id: 'W2',
        incident_name: 'Landslides in Central Highlands',
        date: '2024-10-18',
        category: 'Disaster',
        severity: 'high',
        description: 'Multiple landslides in central hill country disrupted tea plantations and blocked major transportation routes',

        affected_companies: [
            { company_id: 'HAYL', ticker: 'HAYL', name: 'Hayleys', stock_impact_percent: -15.2, operational_impact: 'Major tea estates inaccessible, production halted in affected regions', recovery_days: 45, sector: 'Agriculture' },
            { company_id: 'WATA', ticker: 'WATA', name: 'Watawala Plantations', stock_impact_percent: -14.5, operational_impact: 'Estate infrastructure damaged, replanting required', recovery_days: 50, sector: 'Agriculture' },
            { company_id: 'JKH', ticker: 'JKH', name: 'John Keells Holdings', stock_impact_percent: -6.8, operational_impact: 'Transportation network disrupted, delivery delays', recovery_days: 25, sector: 'Manufacturing' },
        ],

        sector_impact: [
            { sector: 'Agriculture', avg_impact_percent: -14.8, companies_affected: 2, total_companies: 2 },
            { sector: 'Manufacturing', avg_impact_percent: -6.5, companies_affected: 2, total_companies: 4 },
        ],

        national_indicators_changed: [
            { indicator_name: 'Tea Production', change_percent: -22.0, previous_value: 100, current_value: 78 },
            { indicator_name: 'Road Connectivity', change_percent: -18.0, previous_value: 100, current_value: 82 },
        ],

        total_companies_affected: 8,
        avg_stock_impact: -10.5,
        max_stock_impact: -6.8,
        min_stock_impact: -15.2,
    },

    {
        incident_id: 'W3',
        incident_name: 'Drought Conditions',
        date: '2024-09-10',
        category: 'Weather',
        severity: 'high',
        description: 'Prolonged drought in North-Central and Eastern provinces affecting agriculture and hydropower generation',

        affected_companies: [
            { company_id: 'HAYL', ticker: 'HAYL', name: 'Hayleys', stock_impact_percent: -8.5, operational_impact: 'Reduced crop yields, irrigation challenges', recovery_days: 60, sector: 'Agriculture' },
            { company_id: 'WATA', ticker: 'WATA', name: 'Watawala Plantations', stock_impact_percent: -7.2, operational_impact: 'Water scarcity affecting tea quality', recovery_days: 55, sector: 'Agriculture' },
            { company_id: 'CEB', ticker: 'CEB', name: 'Ceylon Electricity Board', stock_impact_percent: -10.5, operational_impact: 'Hydropower generation down 40%, increased thermal generation costs', recovery_days: 90, sector: 'Energy & Power' },
            { company_id: 'LGAS', ticker: 'LGAS', name: 'Laugfs Gas', stock_impact_percent: 5.5, operational_impact: 'Increased demand for LPG as alternative to electricity', recovery_days: 0, sector: 'Energy & Power' },
        ],

        sector_impact: [
            { sector: 'Agriculture', avg_impact_percent: -7.8, companies_affected: 2, total_companies: 2 },
            { sector: 'Energy & Power', avg_impact_percent: -2.5, companies_affected: 2, total_companies: 2 },
        ],

        national_indicators_changed: [
            { indicator_name: 'Agricultural Output', change_percent: -12.0, previous_value: 100, current_value: 88 },
            { indicator_name: 'Electricity Generation', change_percent: -18.0, previous_value: 100, current_value: 82 },
            { indicator_name: 'Water Availability Index', change_percent: -35.0, previous_value: 100, current_value: 65 },
        ],

        total_companies_affected: 10,
        avg_stock_impact: -5.2,
        max_stock_impact: 5.5,
        min_stock_impact: -10.5,
    },
];

// Helper functions
export function getWeatherIncidents(): IncidentImpact[] {
    return WEATHER_DISASTER_INCIDENTS;
}

export function getIncidentsByCompany(companyId: string): IncidentImpact[] {
    return WEATHER_DISASTER_INCIDENTS.filter(incident =>
        incident.affected_companies.some(c => c.company_id === companyId)
    );
}
