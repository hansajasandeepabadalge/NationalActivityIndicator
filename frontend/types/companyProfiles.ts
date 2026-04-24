/**
 * Company Profiles and Incident Impact Analysis Types
 * Connects national incidents to CSE company stock performance
 */

export type SectorType =
    | 'Banking & Finance'
    | 'Manufacturing'
    | 'Telecommunications'
    | 'Consumer Goods'
    | 'Hospitality & Leisure'
    | 'Energy & Power'
    | 'Agriculture';

export type ImpactLevel = 'high' | 'medium' | 'low';
export type IncidentSeverity = 'critical' | 'high' | 'medium' | 'low';

export interface StockData {
    current_price: number;
    price_change_1d: number;
    price_change_1w: number;
    price_change_1m: number;
    price_change_3m: number;
    price_change_1y: number;
    week_52_high: number;
    week_52_low: number;
    volume: number;
    pe_ratio: number;
    dividend_yield: number;
    price_history_30d: number[]; // Last 30 days for sparkline
}

export interface OperationalMetrics {
    revenue_quarterly: number[];
    profit_margin: number;
    employee_count: number;
    market_share: number;
    production_capacity?: number;
}

export interface SensitivityIndicator {
    indicator_name: string;
    correlation: number; // -1 to +1
    impact_level: ImpactLevel;
    description: string;
}

export interface BusinessInsightSummary {
    insight_id: string;
    title: string;
    type: 'risk' | 'opportunity';
    severity: string;
    description: string;
}

export interface IncidentImpactRecord {
    incident_id: string;
    incident_name: string;
    date: string;
    stock_impact_percent: number;
    operational_impact: string;
    recovery_days: number;
}

export interface CompanyProfile {
    company_id: string;
    ticker: string;
    name: string;
    sector: SectorType;
    industry: string;
    market_cap: number;
    description: string;
    logo_url?: string;
    website?: string;

    stock_data: StockData;
    operational_metrics: OperationalMetrics;
    sensitivity_indicators: SensitivityIndicator[];
    business_insights: {
        risks: BusinessInsightSummary[];
        opportunities: BusinessInsightSummary[];
    };
    recent_incidents_impact: IncidentImpactRecord[];
}

export interface AffectedCompany {
    company_id: string;
    ticker: string;
    name: string;
    stock_impact_percent: number;
    operational_impact: string;
    recovery_days: number;
    sector: SectorType;
}

export interface SectorImpact {
    sector: SectorType;
    avg_impact_percent: number;
    companies_affected: number;
    total_companies: number;
}

export interface NationalIndicatorChange {
    indicator_name: string;
    change_percent: number;
    previous_value: number;
    current_value: number;
}

export interface IncidentImpact {
    incident_id: string;
    incident_name: string;
    date: string;
    category: string;
    severity: IncidentSeverity;
    description: string;

    affected_companies: AffectedCompany[];
    sector_impact: SectorImpact[];
    national_indicators_changed: NationalIndicatorChange[];

    total_companies_affected: number;
    avg_stock_impact: number;
    max_stock_impact: number;
    min_stock_impact: number;
}

export interface CorrelationData {
    company_ticker: string;
    company_name: string;
    sector: SectorType;
    correlations: {
        [indicator: string]: number;
    };
}

// Sector colors for consistent UI
export const SECTOR_COLORS: Record<SectorType, string> = {
    'Banking & Finance': '#10b981',
    'Manufacturing': '#3b82f6',
    'Telecommunications': '#8b5cf6',
    'Consumer Goods': '#f59e0b',
    'Hospitality & Leisure': '#ec4899',
    'Energy & Power': '#ef4444',
    'Agriculture': '#059669',
};

// Sector icons
export const SECTOR_ICONS: Record<SectorType, string> = {
    'Banking & Finance': '🏦',
    'Manufacturing': '🏭',
    'Telecommunications': '📡',
    'Consumer Goods': '🛒',
    'Hospitality & Leisure': '🏨',
    'Energy & Power': '⚡',
    'Agriculture': '🌾',
};

// Helper function to get impact color
export function getImpactColor(impact: number): string {
    if (impact > 5) return 'text-green-600 bg-green-50';
    if (impact > 0) return 'text-green-500 bg-green-50';
    if (impact > -5) return 'text-red-500 bg-red-50';
    return 'text-red-600 bg-red-50';
}

// Helper function to get severity color
export function getSeverityColor(severity: IncidentSeverity): string {
    switch (severity) {
        case 'critical': return 'bg-red-100 text-red-800 border-red-200';
        case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
        case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
    }
}

// Helper to format currency
export function formatCurrency(value: number): string {
    if (value >= 1_000_000_000) {
        return `LKR ${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (value >= 1_000_000) {
        return `LKR ${(value / 1_000_000).toFixed(1)}M`;
    }
    return `LKR ${value.toLocaleString()}`;
}

// Helper to format percentage
export function formatPercent(value: number, decimals: number = 1): string {
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(decimals)}%`;
}
