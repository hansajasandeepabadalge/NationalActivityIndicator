/**
 * Mock Data for Top 20 CSE Companies
 * Comprehensive company profiles with stock data, correlations, and incident impacts
 */

import {
    CompanyProfile,
    IncidentImpact,
    SectorType,
    SECTOR_COLORS,
} from '../types/companyProfiles';
import { ADDITIONAL_CSE_COMPANIES } from './additionalCompanies';

// Helper to generate realistic price history
function generatePriceHistory(basePrice: number, volatility: number = 0.02): number[] {
    const history: number[] = [];
    let price = basePrice * 0.95; // Start 5% lower

    for (let i = 0; i < 30; i++) {
        const change = (Math.random() - 0.5) * 2 * volatility * price;
        price += change;
        history.push(Number(price.toFixed(2)));
    }

    return history;
}

// Helper to generate quarterly revenue
function generateQuarterlyRevenue(base: number): number[] {
    return [
        base * 0.92,
        base * 0.98,
        base * 1.05,
        base * 1.12,
    ];
}

export const MOCK_COMPANIES: CompanyProfile[] = [
    // Banking & Finance (5 companies)
    {
        company_id: 'COMB',
        ticker: 'COMB',
        name: 'Commercial Bank of Ceylon',
        sector: 'Banking & Finance',
        industry: 'Commercial Banking',
        market_cap: 310_000_000_000,
        description: 'Leading commercial bank offering retail, corporate, and investment banking services across Sri Lanka.',

        stock_data: {
            current_price: 142.50,
            price_change_1d: 2.5,
            price_change_1w: 4.2,
            price_change_1m: -1.8,
            price_change_3m: 8.5,
            price_change_1y: 15.3,
            week_52_high: 158.00,
            week_52_low: 125.00,
            volume: 1_250_000,
            pe_ratio: 8.5,
            dividend_yield: 4.2,
            price_history_30d: generatePriceHistory(142.50),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(25_000_000_000),
            profit_margin: 18.5,
            employee_count: 4_500,
            market_share: 12.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Interest Rate', correlation: 0.85, impact_level: 'high', description: 'Higher rates increase lending margins' },
            { indicator_name: 'Inflation', correlation: -0.42, impact_level: 'medium', description: 'Inflation erodes real returns' },
            { indicator_name: 'GDP Growth', correlation: 0.65, impact_level: 'medium', description: 'Economic growth drives loan demand' },
            { indicator_name: 'Exchange Rate', correlation: -0.28, impact_level: 'low', description: 'Currency volatility affects foreign operations' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R1', title: 'Credit Risk in SME Sector', type: 'risk', severity: 'medium', description: 'Rising default rates in SME lending portfolio due to economic volatility' },
                { insight_id: 'R2', title: 'Digital Banking Competition', type: 'risk', severity: 'high', description: 'Aggressive competition from fintech startups and digital-only banks eroding traditional market share' },
                { insight_id: 'R3', title: 'Interest Rate Sensitivity', type: 'risk', severity: 'medium', description: 'Margin compression risk if policy rates decline rapidly' },
                { insight_id: 'R4', title: 'Regulatory Compliance Costs', type: 'risk', severity: 'low', description: 'Increasing regulatory requirements raising operational costs' },
            ],
            opportunities: [
                { insight_id: 'O1', title: 'Digital Transformation', type: 'opportunity', severity: 'high', description: 'Strong mobile banking platform with 2M+ active users, positioned for digital growth' },
                { insight_id: 'O2', title: 'Regional Expansion', type: 'opportunity', severity: 'medium', description: 'Expanding branch network in underserved rural areas with high growth potential' },
                { insight_id: 'O3', title: 'Corporate Banking Growth', type: 'opportunity', severity: 'high', description: 'Growing demand for trade finance and working capital solutions from export sector' },
                { insight_id: 'O4', title: 'Wealth Management Services', type: 'opportunity', severity: 'medium', description: 'Rising affluent customer base creating demand for investment advisory services' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I1', incident_name: 'Interest Rate Hike +2%', date: '2024-12-01', stock_impact_percent: 5.2, operational_impact: 'Increased lending margins', recovery_days: 0 },
            { incident_id: 'I2', incident_name: 'Fuel Price Increase +15%', date: '2024-11-15', stock_impact_percent: -1.8, operational_impact: 'Higher operational costs', recovery_days: 12 },
        ],
    },

    {
        company_id: 'HNB',
        ticker: 'HNB',
        name: 'Hatton National Bank',
        sector: 'Banking & Finance',
        industry: 'Commercial Banking',
        market_cap: 177_000_000_000,
        description: 'Premier banking institution with strong retail and corporate banking presence.',

        stock_data: {
            current_price: 393.00,
            price_change_1d: 1.8,
            price_change_1w: 3.5,
            price_change_1m: 2.2,
            price_change_3m: 9.8,
            price_change_1y: 18.5,
            week_52_high: 248.00,
            week_52_low: 198.00,
            volume: 850_000,
            pe_ratio: 9.2,
            dividend_yield: 3.8,
            price_history_30d: generatePriceHistory(235.00),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(22_000_000_000),
            profit_margin: 19.2,
            employee_count: 4_200,
            market_share: 11.8,
        },

        sensitivity_indicators: [
            { indicator_name: 'Interest Rate', correlation: 0.82, impact_level: 'high', description: 'Net interest margin sensitivity' },
            { indicator_name: 'GDP Growth', correlation: 0.68, impact_level: 'medium', description: 'Credit growth correlation' },
            { indicator_name: 'Inflation', correlation: -0.38, impact_level: 'medium', description: 'Cost pressures' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R3', title: 'Real Estate Exposure', type: 'risk', severity: 'medium', description: 'High concentration in real estate lending creates sector-specific risk' },
                { insight_id: 'R4', title: 'Foreign Exchange Volatility', type: 'risk', severity: 'medium', description: 'Exposure to currency fluctuations affecting foreign currency loans' },
                { insight_id: 'R5', title: 'Technology Infrastructure', type: 'risk', severity: 'low', description: 'Need for continuous investment in digital banking infrastructure' },
            ],
            opportunities: [
                { insight_id: 'O3', title: 'Treasury Operations', type: 'opportunity', severity: 'high', description: 'Strong government securities portfolio benefiting from yield curve positioning' },
                { insight_id: 'O4', title: 'Retail Banking Expansion', type: 'opportunity', severity: 'high', description: 'Growing middle class creating demand for personal loans and credit cards' },
                { insight_id: 'O5', title: 'Remittance Services', type: 'opportunity', severity: 'medium', description: 'Capturing diaspora remittance flows through digital channels' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I1', incident_name: 'Interest Rate Hike +2%', date: '2024-12-01', stock_impact_percent: 4.8, operational_impact: 'Improved NIM', recovery_days: 0 },
        ],
    },

    // Manufacturing (4 companies)
    {
        company_id: 'JKH',
        ticker: 'JKH',
        name: 'John Keells Holdings',
        sector: 'Manufacturing',
        industry: 'Diversified Conglomerate',
        market_cap: 375_000_000_000,
        description: 'Sri Lanka\'s largest listed conglomerate with interests in transportation, leisure, retail, and property.',

        stock_data: {
            current_price: 185.00,
            price_change_1d: -0.5,
            price_change_1w: 2.8,
            price_change_1m: 5.5,
            price_change_3m: 12.3,
            price_change_1y: 22.8,
            week_52_high: 195.00,
            week_52_low: 148.00,
            volume: 2_100_000,
            pe_ratio: 12.5,
            dividend_yield: 2.8,
            price_history_30d: generatePriceHistory(185.00),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(45_000_000_000),
            profit_margin: 15.8,
            employee_count: 12_500,
            market_share: 8.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Tourism Growth', correlation: 0.82, impact_level: 'high', description: 'Hotel and leisure segment exposure' },
            { indicator_name: 'Fuel Prices', correlation: -0.68, impact_level: 'high', description: 'Transportation costs impact' },
            { indicator_name: 'Consumer Spending', correlation: 0.72, impact_level: 'medium', description: 'Retail operations dependency' },
            { indicator_name: 'GDP Growth', correlation: 0.78, impact_level: 'medium', description: 'Overall business environment' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R4', title: 'Tourism Dependency', type: 'risk', severity: 'high', description: '40% revenue from tourism-related activities vulnerable to external shocks' },
                { insight_id: 'R5', title: 'Fuel Cost Volatility', type: 'risk', severity: 'medium', description: 'Transportation segment exposed to global oil price fluctuations' },
                { insight_id: 'R6', title: 'Retail Competition', type: 'risk', severity: 'medium', description: 'Intense competition in supermarket sector from local and international players' },
                { insight_id: 'R7', title: 'Property Market Cycles', type: 'risk', severity: 'low', description: 'Real estate development exposed to market cyclicality' },
            ],
            opportunities: [
                { insight_id: 'O4', title: 'Tourism Recovery', type: 'opportunity', severity: 'high', description: 'Strong post-pandemic rebound with record tourist arrivals expected in 2025' },
                { insight_id: 'O5', title: 'Retail Expansion', type: 'opportunity', severity: 'medium', description: 'New supermarket locations planned in suburban areas with growing populations' },
                { insight_id: 'O6', title: 'Logistics Growth', type: 'opportunity', severity: 'high', description: 'Expanding port and logistics operations benefiting from regional trade growth' },
                { insight_id: 'O7', title: 'Urban Development', type: 'opportunity', severity: 'medium', description: 'Mixed-use property developments in Colombo creating recurring revenue streams' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I3', incident_name: 'Tourism Boom +40%', date: '2024-11-20', stock_impact_percent: 8.2, operational_impact: 'Hotel occupancy at 95%', recovery_days: 0 },
            { incident_id: 'I2', incident_name: 'Fuel Price Increase +15%', date: '2024-11-15', stock_impact_percent: -2.8, operational_impact: 'Transport costs up 18%', recovery_days: 15 },
        ],
    },

    {
        company_id: 'HEMS',
        ticker: 'HEMS',
        name: 'Hemas Holdings',
        sector: 'Manufacturing',
        industry: 'Healthcare & Consumer',
        market_cap: 42_000_000_000,
        description: 'Diversified group with healthcare, consumer, and transportation businesses.',

        stock_data: {
            current_price: 95.50,
            price_change_1d: 1.2,
            price_change_1w: 3.8,
            price_change_1m: 6.2,
            price_change_3m: 11.5,
            price_change_1y: 19.2,
            week_52_high: 102.00,
            week_52_low: 78.00,
            volume: 450_000,
            pe_ratio: 14.2,
            dividend_yield: 3.2,
            price_history_30d: generatePriceHistory(95.50),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(18_000_000_000),
            profit_margin: 12.5,
            employee_count: 5_800,
            market_share: 6.2,
        },

        sensitivity_indicators: [
            { indicator_name: 'Healthcare Spending', correlation: 0.75, impact_level: 'high', description: 'Pharmaceutical and hospital segments' },
            { indicator_name: 'Consumer Confidence', correlation: 0.62, impact_level: 'medium', description: 'FMCG sales correlation' },
            { indicator_name: 'Exchange Rate', correlation: -0.45, impact_level: 'medium', description: 'Import costs for pharmaceuticals' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R6', title: 'Import Dependency', type: 'risk', severity: 'medium', description: 'Pharmaceutical raw materials imported, vulnerable to currency fluctuations' },
                { insight_id: 'R10', title: 'Healthcare Regulation', type: 'risk', severity: 'low', description: 'Stringent pharmaceutical regulations increasing compliance costs' },
                { insight_id: 'R11', title: 'Generic Competition', type: 'risk', severity: 'medium', description: 'Growing competition from generic drug manufacturers' },
            ],
            opportunities: [
                { insight_id: 'O6', title: 'Healthcare Expansion', type: 'opportunity', severity: 'high', description: 'New hospital projects underway in Colombo and regional cities' },
                { insight_id: 'O10', title: 'Medical Tourism', type: 'opportunity', severity: 'medium', description: 'Growing demand for quality healthcare from regional patients' },
                { insight_id: 'O11', title: 'Consumer Healthcare', type: 'opportunity', severity: 'high', description: 'Expanding OTC and wellness product portfolio for growing middle class' },
            ],
        },

        recent_incidents_impact: [],
    },

    // Telecommunications (2 companies)
    {
        company_id: 'DIAL',
        ticker: 'DIAL',
        name: 'Dialog Axiata',
        sector: 'Telecommunications',
        industry: 'Mobile Telecommunications',
        market_cap: 268_000_000_000,
        description: 'Leading mobile telecommunications provider with 15M+ subscribers.',

        stock_data: {
            current_price: 29.50,
            price_change_1d: -0.8,
            price_change_1w: 1.5,
            price_change_1m: -2.2,
            price_change_3m: 4.8,
            price_change_1y: 8.5,
            week_52_high: 14.20,
            week_52_low: 11.50,
            volume: 8_500_000,
            pe_ratio: 15.8,
            dividend_yield: 2.5,
            price_history_30d: generatePriceHistory(12.80),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(35_000_000_000),
            profit_margin: 14.2,
            employee_count: 3_200,
            market_share: 45.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Data Usage Growth', correlation: 0.88, impact_level: 'high', description: '4G/5G adoption driving revenue' },
            { indicator_name: 'Fuel Prices', correlation: -0.42, impact_level: 'medium', description: 'Network operations costs' },
            { indicator_name: 'Consumer Spending', correlation: 0.55, impact_level: 'medium', description: 'ARPU correlation' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R7', title: 'Regulatory Pressure', type: 'risk', severity: 'medium', description: 'Potential government intervention on mobile tariffs and data pricing' },
                { insight_id: 'R8', title: 'Infrastructure Investment', type: 'risk', severity: 'high', description: 'Heavy capital expenditure required for 5G network rollout' },
                { insight_id: 'R9', title: 'Market Saturation', type: 'risk', severity: 'low', description: 'Mobile penetration above 100% limiting subscriber growth' },
            ],
            opportunities: [
                { insight_id: 'O7', title: '5G Network Rollout', type: 'opportunity', severity: 'high', description: 'First mover advantage in 5G with commercial launch planned for 2025' },
                { insight_id: 'O8', title: 'Digital Services Revenue', type: 'opportunity', severity: 'high', description: 'Growing revenue from digital content, fintech, and enterprise solutions' },
                { insight_id: 'O9', title: 'IoT and Enterprise', type: 'opportunity', severity: 'medium', description: 'Expanding IoT solutions for smart cities and industrial applications' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I2', incident_name: 'Fuel Price Increase +15%', date: '2024-11-15', stock_impact_percent: -3.2, operational_impact: 'Tower operations costs up', recovery_days: 18 },
        ],
    },

    // Consumer Goods (3 companies)
    {
        company_id: 'NEST',
        ticker: 'NEST',
        name: 'Nestlé Lanka',
        sector: 'Consumer Goods',
        industry: 'Food & Beverages',
        market_cap: 68_000_000_000,
        description: 'Leading food and beverage manufacturer with strong brand portfolio.',

        stock_data: {
            current_price: 3_250.00,
            price_change_1d: 0.5,
            price_change_1w: 2.2,
            price_change_1m: 4.8,
            price_change_3m: 8.5,
            price_change_1y: 12.3,
            week_52_high: 3_380.00,
            week_52_low: 2_950.00,
            volume: 15_000,
            pe_ratio: 22.5,
            dividend_yield: 3.8,
            price_history_30d: generatePriceHistory(3250.00, 0.015),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(28_000_000_000),
            profit_margin: 16.8,
            employee_count: 2_100,
            market_share: 18.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Consumer Spending', correlation: 0.72, impact_level: 'high', description: 'Discretionary spending impact' },
            { indicator_name: 'Inflation', correlation: -0.58, impact_level: 'high', description: 'Input cost pressures' },
            { indicator_name: 'Exchange Rate', correlation: -0.48, impact_level: 'medium', description: 'Imported raw materials' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R8', title: 'Commodity Price Volatility', type: 'risk', severity: 'high', description: 'Milk powder and cocoa prices fluctuating due to global supply chain issues' },
                { insight_id: 'R12', title: 'Consumer Spending Pressure', type: 'risk', severity: 'medium', description: 'Economic challenges affecting discretionary spending on premium products' },
                { insight_id: 'R13', title: 'Distribution Costs', type: 'risk', severity: 'low', description: 'Rising transportation and logistics costs impacting margins' },
            ],
            opportunities: [
                { insight_id: 'O8', title: 'Premium Product Growth', type: 'opportunity', severity: 'medium', description: 'Growing middle class demand for premium coffee, chocolate, and nutrition products' },
                { insight_id: 'O12', title: 'Health and Wellness', type: 'opportunity', severity: 'high', description: 'Expanding portfolio of health-focused products aligned with consumer trends' },
                { insight_id: 'O13', title: 'E-commerce Channel', type: 'opportunity', severity: 'medium', description: 'Growing online sales through partnerships with delivery platforms' },
            ],
        },

        recent_incidents_impact: [],
    },

    // Hospitality & Leisure (2 companies)
    {
        company_id: 'SPEN',
        ticker: 'SPEN',
        name: 'Aitken Spence',
        sector: 'Hospitality & Leisure',
        industry: 'Hotels & Resorts',
        market_cap: 52_000_000_000,
        description: 'Diversified conglomerate with strong presence in tourism and hospitality.',

        stock_data: {
            current_price: 128.00,
            price_change_1d: 2.8,
            price_change_1w: 8.5,
            price_change_1m: 15.2,
            price_change_3m: 28.5,
            price_change_1y: 42.8,
            week_52_high: 135.00,
            week_52_low: 88.00,
            volume: 620_000,
            pe_ratio: 18.5,
            dividend_yield: 2.2,
            price_history_30d: generatePriceHistory(128.00, 0.025),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(15_000_000_000),
            profit_margin: 11.5,
            employee_count: 6_500,
            market_share: 14.2,
        },

        sensitivity_indicators: [
            { indicator_name: 'Tourism Arrivals', correlation: 0.92, impact_level: 'high', description: 'Direct hotel occupancy impact' },
            { indicator_name: 'Exchange Rate', correlation: 0.68, impact_level: 'high', description: 'Foreign currency earnings' },
            { indicator_name: 'Fuel Prices', correlation: -0.35, impact_level: 'low', description: 'Operational costs' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R9', title: 'Seasonal Dependency', type: 'risk', severity: 'medium', description: 'Revenue concentrated in peak tourist seasons (Dec-Mar, Jul-Aug)' },
                { insight_id: 'R14', title: 'Geopolitical Events', type: 'risk', severity: 'high', description: 'Tourism vulnerable to regional security concerns and travel advisories' },
                { insight_id: 'R15', title: 'Labor Costs', type: 'risk', severity: 'low', description: 'Rising hospitality sector wages affecting profitability' },
            ],
            opportunities: [
                { insight_id: 'O9', title: 'Tourism Boom', type: 'opportunity', severity: 'high', description: 'Record tourist arrivals expected with visa-free entry for 35+ countries' },
                { insight_id: 'O14', title: 'MICE Segment', type: 'opportunity', severity: 'medium', description: 'Growing meetings, incentives, conferences, and events business' },
                { insight_id: 'O15', title: 'Sustainable Tourism', type: 'opportunity', severity: 'medium', description: 'Eco-friendly resorts attracting premium sustainability-focused travelers' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I3', incident_name: 'Tourism Boom +40%', date: '2024-11-20', stock_impact_percent: 12.5, operational_impact: '98% occupancy rates', recovery_days: 0 },
        ],
    },

    // Energy & Power (2 companies)
    {
        company_id: 'LGAS',
        ticker: 'LGAS',
        name: 'Laugfs Gas',
        sector: 'Energy & Power',
        industry: 'LPG Distribution',
        market_cap: 28_000_000_000,
        description: 'Leading LPG distributor with nationwide network.',

        stock_data: {
            current_price: 82.50,
            price_change_1d: -1.5,
            price_change_1w: -3.2,
            price_change_1m: 2.8,
            price_change_3m: 5.5,
            price_change_1y: 8.2,
            week_52_high: 92.00,
            week_52_low: 72.00,
            volume: 380_000,
            pe_ratio: 11.2,
            dividend_yield: 4.5,
            price_history_30d: generatePriceHistory(82.50),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(12_000_000_000),
            profit_margin: 8.5,
            employee_count: 1_800,
            market_share: 32.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Oil Prices', correlation: -0.75, impact_level: 'high', description: 'LPG import costs' },
            { indicator_name: 'Exchange Rate', correlation: -0.82, impact_level: 'high', description: 'USD denominated imports' },
            { indicator_name: 'Consumer Demand', correlation: 0.45, impact_level: 'medium', description: 'Household consumption' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R10', title: 'Global LPG Price Volatility', type: 'risk', severity: 'high', description: 'International LPG prices fluctuating with crude oil markets' },
                { insight_id: 'R16', title: 'Regulatory Price Controls', type: 'risk', severity: 'medium', description: 'Government price controls limiting ability to pass through cost increases' },
                { insight_id: 'R17', title: 'Alternative Energy', type: 'risk', severity: 'low', description: 'Growing adoption of electric cooking reducing LPG demand long-term' },
            ],
            opportunities: [
                { insight_id: 'O10', title: 'Rural Market Expansion', type: 'opportunity', severity: 'medium', description: 'Untapped rural markets with low LPG penetration rates' },
                { insight_id: 'O16', title: 'Industrial Segment', type: 'opportunity', severity: 'high', description: 'Growing demand from industrial and commercial customers' },
                { insight_id: 'O17', title: 'Distribution Network', type: 'opportunity', severity: 'medium', description: 'Expanding dealer network and home delivery services' },
            ],
        },

        recent_incidents_impact: [],
    },

    // Agriculture (2 companies)
    {
        company_id: 'HAYL',
        ticker: 'HAYL',
        name: 'Hayleys',
        sector: 'Agriculture',
        industry: 'Diversified Agriculture',
        market_cap: 48_000_000_000,
        description: 'Diversified conglomerate with plantations, agriculture, and industrial sectors.',

        stock_data: {
            current_price: 92.00,
            price_change_1d: -2.2,
            price_change_1w: -4.5,
            price_change_1m: -8.2,
            price_change_3m: -5.8,
            price_change_1y: 2.5,
            week_52_high: 105.00,
            week_52_low: 85.00,
            volume: 520_000,
            pe_ratio: 10.5,
            dividend_yield: 5.2,
            price_history_30d: generatePriceHistory(92.00, 0.025),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(38_000_000_000),
            profit_margin: 9.8,
            employee_count: 18_500,
            market_share: 15.8,
        },

        sensitivity_indicators: [
            { indicator_name: 'Commodity Prices', correlation: 0.78, impact_level: 'high', description: 'Tea, rubber, palm oil prices' },
            { indicator_name: 'Weather Patterns', correlation: 0.65, impact_level: 'high', description: 'Crop yield dependency' },
            { indicator_name: 'Fuel Prices', correlation: -0.72, impact_level: 'high', description: 'Transportation and processing costs' },
            { indicator_name: 'Exchange Rate', correlation: 0.58, impact_level: 'medium', description: 'Export earnings' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R11', title: 'Climate Vulnerability', type: 'risk', severity: 'high', description: 'Drought and flood risks to tea, rubber, and palm oil plantations' },
                { insight_id: 'R12', title: 'Fuel Cost Impact', type: 'risk', severity: 'high', description: 'High transportation costs for moving produce from estates to ports' },
                { insight_id: 'R18', title: 'Labor Availability', type: 'risk', severity: 'medium', description: 'Shortage of plantation workers affecting harvesting operations' },
                { insight_id: 'R19', title: 'Global Commodity Prices', type: 'risk', severity: 'medium', description: 'Tea and rubber prices subject to international market fluctuations' },
            ],
            opportunities: [
                { insight_id: 'O11', title: 'Organic Products', type: 'opportunity', severity: 'medium', description: 'Growing global demand for organic Ceylon tea commanding premium prices' },
                { insight_id: 'O18', title: 'Value Addition', type: 'opportunity', severity: 'high', description: 'Processing and packaging tea locally to capture higher margins' },
                { insight_id: 'O19', title: 'Sustainable Agriculture', type: 'opportunity', severity: 'medium', description: 'Rainforest Alliance certification attracting environmentally conscious buyers' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I2', incident_name: 'Fuel Price Increase +15%', date: '2024-11-15', stock_impact_percent: -8.2, operational_impact: 'Transport costs up 22%', recovery_days: 25 },
        ],
    },
];

export const ALL_COMPANIES = [...MOCK_COMPANIES, ...ADDITIONAL_CSE_COMPANIES];

// Helper functions
export function getCompanyByTicker(ticker: string): CompanyProfile | undefined {
    return ALL_COMPANIES.find(c => c.ticker === ticker);
}

export function getCompaniesBySector(sector: SectorType): CompanyProfile[] {
    return ALL_COMPANIES.filter(c => c.sector === sector);
}

export function getTopPerformers(limit: number = 5): CompanyProfile[] {
    return [...ALL_COMPANIES]
        .sort((a, b) => b.stock_data.price_change_1m - a.stock_data.price_change_1m)
        .slice(0, limit);
}

export function getTopLosers(limit: number = 5): CompanyProfile[] {
    return [...ALL_COMPANIES]
        .sort((a, b) => a.stock_data.price_change_1m - b.stock_data.price_change_1m)
        .slice(0, limit);
}
