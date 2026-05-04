/**
 * Additional 10 CSE Companies from S&P Sri Lanka 20 Index
 * Completing the dataset to 20 companies total
 */

import { CompanyProfile } from '../types/companyProfiles';

// Helper functions from mockCompanies
function generatePriceHistory(basePrice: number, volatility: number = 0.02): number[] {
    const history: number[] = [];
    let price = basePrice * 0.95;
    for (let i = 0; i < 30; i++) {
        const change = (Math.random() - 0.5) * 2 * volatility * price;
        price += change;
        history.push(Number(price.toFixed(2)));
    }
    return history;
}

function generateQuarterlyRevenue(base: number): number[] {
    return [base * 0.92, base * 0.98, base * 1.05, base * 1.12];
}

export const ADDITIONAL_CSE_COMPANIES: CompanyProfile[] = [
    // Banking & Finance (3 companies)
    {
        company_id: 'SAMP',
        ticker: 'SAMP',
        name: 'Sampath Bank',
        sector: 'Banking & Finance',
        industry: 'Commercial Banking',
        market_cap: 145_000_000_000,
        description: 'Leading retail-focused commercial bank with strong SME and personal banking presence.',

        stock_data: {
            current_price: 125.00,
            price_change_1d: 1.2,
            price_change_1w: 2.8,
            price_change_1m: 5.5,
            price_change_3m: 10.2,
            price_change_1y: 16.8,
            week_52_high: 135.00,
            week_52_low: 108.00,
            volume: 950_000,
            pe_ratio: 8.8,
            dividend_yield: 4.5,
            price_history_30d: generatePriceHistory(125.00),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(20_000_000_000),
            profit_margin: 17.5,
            employee_count: 3_800,
            market_share: 10.2,
        },

        sensitivity_indicators: [
            { indicator_name: 'Interest Rate', correlation: 0.80, impact_level: 'high', description: 'Lending margin sensitivity' },
            { indicator_name: 'GDP Growth', correlation: 0.70, impact_level: 'medium', description: 'Credit demand correlation' },
            { indicator_name: 'Inflation', correlation: -0.40, impact_level: 'medium', description: 'Real return erosion' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R20', title: 'SME Credit Risk', type: 'risk', severity: 'medium', description: 'High exposure to SME sector vulnerable to economic downturns' },
                { insight_id: 'R21', title: 'Digital Disruption', type: 'risk', severity: 'high', description: 'Need to accelerate digital transformation to compete' },
            ],
            opportunities: [
                { insight_id: 'O20', title: 'Retail Banking Growth', type: 'opportunity', severity: 'high', description: 'Strong brand in retail segment with expansion potential' },
                { insight_id: 'O21', title: 'SME Financing', type: 'opportunity', severity: 'medium', description: 'Growing SME market with financing needs' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I1', incident_name: 'Interest Rate Hike +2%', date: '2024-12-01', stock_impact_percent: 4.5, operational_impact: 'Improved lending margins', recovery_days: 0 },
        ],
    },

    {
        company_id: 'NTB',
        ticker: 'NTB',
        name: 'Nations Trust Bank',
        sector: 'Banking & Finance',
        industry: 'Commercial Banking',
        market_cap: 95_000_000_000,
        description: 'Technology-focused commercial bank with strong digital banking capabilities.',

        stock_data: {
            current_price: 165.00,
            price_change_1d: 0.8,
            price_change_1w: 3.2,
            price_change_1m: 6.8,
            price_change_3m: 11.5,
            price_change_1y: 19.2,
            week_52_high: 175.00,
            week_52_low: 142.00,
            volume: 720_000,
            pe_ratio: 9.5,
            dividend_yield: 3.9,
            price_history_30d: generatePriceHistory(165.00),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(18_000_000_000),
            profit_margin: 18.2,
            employee_count: 3_200,
            market_share: 8.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Interest Rate', correlation: 0.78, impact_level: 'high', description: 'Net interest margin impact' },
            { indicator_name: 'Technology Adoption', correlation: 0.85, impact_level: 'high', description: 'Digital banking leader' },
            { indicator_name: 'GDP Growth', correlation: 0.65, impact_level: 'medium', description: 'Corporate lending growth' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R22', title: 'Cybersecurity Threats', type: 'risk', severity: 'high', description: 'Digital-first model increases cyber risk exposure' },
                { insight_id: 'R23', title: 'Technology Investment', type: 'risk', severity: 'medium', description: 'Continuous tech investment required' },
            ],
            opportunities: [
                { insight_id: 'O22', title: 'Digital Banking Leadership', type: 'opportunity', severity: 'high', description: 'First-mover advantage in digital services' },
                { insight_id: 'O23', title: 'Fintech Partnerships', type: 'opportunity', severity: 'medium', description: 'Collaborations with fintech startups' },
            ],
        },

        recent_incidents_impact: [],
    },

    {
        company_id: 'DFCC',
        ticker: 'DFCC',
        name: 'DFCC Bank',
        sector: 'Banking & Finance',
        industry: 'Development Banking',
        market_cap: 88_000_000_000,
        description: 'Development finance institution providing long-term financing for infrastructure and industry.',

        stock_data: {
            current_price: 92.00,
            price_change_1d: 1.5,
            price_change_1w: 4.2,
            price_change_1m: 7.8,
            price_change_3m: 12.5,
            price_change_1y: 18.5,
            week_52_high: 98.00,
            week_52_low: 78.00,
            volume: 650_000,
            pe_ratio: 7.8,
            dividend_yield: 5.2,
            price_history_30d: generatePriceHistory(92.00),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(16_000_000_000),
            profit_margin: 16.8,
            employee_count: 2_900,
            market_share: 7.2,
        },

        sensitivity_indicators: [
            { indicator_name: 'Infrastructure Investment', correlation: 0.88, impact_level: 'high', description: 'Project financing focus' },
            { indicator_name: 'Interest Rate', correlation: 0.72, impact_level: 'high', description: 'Long-term lending rates' },
            { indicator_name: 'GDP Growth', correlation: 0.82, impact_level: 'high', description: 'Development project demand' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R24', title: 'Project Concentration', type: 'risk', severity: 'medium', description: 'Large exposure to infrastructure projects' },
                { insight_id: 'R25', title: 'Long-term Funding', type: 'risk', severity: 'medium', description: 'Dependency on long-term funding sources' },
            ],
            opportunities: [
                { insight_id: 'O24', title: 'Infrastructure Boom', type: 'opportunity', severity: 'high', description: 'Government infrastructure push creating demand' },
                { insight_id: 'O25', title: 'Green Financing', type: 'opportunity', severity: 'high', description: 'Growing demand for sustainable project financing' },
            ],
        },

        recent_incidents_impact: [],
    },

    // Manufacturing (2 companies)
    {
        company_id: 'CTC',
        ticker: 'CTC',
        name: 'Ceylon Tobacco Company',
        sector: 'Manufacturing',
        industry: 'Tobacco Products',
        market_cap: 220_000_000_000,
        description: 'Leading tobacco manufacturer with dominant market position in cigarettes.',

        stock_data: {
            current_price: 1_450.00,
            price_change_1d: -0.5,
            price_change_1w: 1.2,
            price_change_1m: 3.5,
            price_change_3m: 6.8,
            price_change_1y: 10.2,
            week_52_high: 1_520.00,
            week_52_low: 1_320.00,
            volume: 25_000,
            pe_ratio: 18.5,
            dividend_yield: 6.2,
            price_history_30d: generatePriceHistory(1450.00, 0.012),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(32_000_000_000),
            profit_margin: 22.5,
            employee_count: 1_200,
            market_share: 68.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Excise Tax', correlation: -0.92, impact_level: 'high', description: 'Government taxation policy' },
            { indicator_name: 'Consumer Spending', correlation: 0.45, impact_level: 'medium', description: 'Discretionary spending' },
            { indicator_name: 'Health Regulations', correlation: -0.75, impact_level: 'high', description: 'Smoking restrictions' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R26', title: 'Regulatory Pressure', type: 'risk', severity: 'high', description: 'Increasing tobacco control measures and taxation' },
                { insight_id: 'R27', title: 'Health Awareness', type: 'risk', severity: 'high', description: 'Declining smoking rates due to health concerns' },
                { insight_id: 'R28', title: 'Illicit Trade', type: 'risk', severity: 'medium', description: 'Competition from smuggled cigarettes' },
            ],
            opportunities: [
                { insight_id: 'O26', title: 'Premium Segment', type: 'opportunity', severity: 'medium', description: 'Growing demand for premium cigarette brands' },
                { insight_id: 'O27', title: 'Alternative Products', type: 'opportunity', severity: 'low', description: 'Potential for reduced-risk products' },
            ],
        },

        recent_incidents_impact: [],
    },

    {
        company_id: 'TEJA',
        ticker: 'TEJA',
        name: 'Teejay Lanka',
        sector: 'Manufacturing',
        industry: 'Textile Manufacturing',
        market_cap: 62_000_000_000,
        description: 'Leading textile manufacturer specializing in knit fabric production for global brands.',

        stock_data: {
            current_price: 48.00,
            price_change_1d: 2.5,
            price_change_1w: 5.8,
            price_change_1m: 12.5,
            price_change_3m: 18.2,
            price_change_1y: 25.5,
            week_52_high: 52.00,
            week_52_low: 38.00,
            volume: 1_200_000,
            pe_ratio: 12.8,
            dividend_yield: 2.5,
            price_history_30d: generatePriceHistory(48.00, 0.025),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(24_000_000_000),
            profit_margin: 11.5,
            employee_count: 8_500,
            market_share: 15.2,
        },

        sensitivity_indicators: [
            { indicator_name: 'Exchange Rate', correlation: 0.82, impact_level: 'high', description: 'Export earnings in USD' },
            { indicator_name: 'Global Apparel Demand', correlation: 0.75, impact_level: 'high', description: 'International buyer orders' },
            { indicator_name: 'Cotton Prices', correlation: -0.68, impact_level: 'high', description: 'Raw material costs' },
            { indicator_name: 'Fuel Prices', correlation: -0.55, impact_level: 'medium', description: 'Energy and logistics costs' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R29', title: 'Global Competition', type: 'risk', severity: 'high', description: 'Competition from Bangladesh, Vietnam, and India' },
                { insight_id: 'R30', title: 'Buyer Concentration', type: 'risk', severity: 'medium', description: 'Dependency on few large international buyers' },
                { insight_id: 'R31', title: 'Energy Costs', type: 'risk', severity: 'medium', description: 'High electricity consumption affecting margins' },
            ],
            opportunities: [
                { insight_id: 'O28', title: 'Sustainable Textiles', type: 'opportunity', severity: 'high', description: 'Growing demand for eco-friendly fabrics from global brands' },
                { insight_id: 'O29', title: 'Vertical Integration', type: 'opportunity', severity: 'medium', description: 'Expanding into garment manufacturing' },
                { insight_id: 'O30', title: 'New Markets', type: 'opportunity', severity: 'medium', description: 'Diversifying customer base to new regions' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'I2', incident_name: 'Fuel Price Increase +15%', date: '2024-11-15', stock_impact_percent: -4.5, operational_impact: 'Energy costs up 18%', recovery_days: 20 },
        ],
    },

    // Telecommunications (1 company)
    {
        company_id: 'SLT',
        ticker: 'SLT',
        name: 'Sri Lanka Telecom',
        sector: 'Telecommunications',
        industry: 'Fixed-line & Broadband',
        market_cap: 125_000_000_000,
        description: 'National telecommunications provider with dominant fixed-line and broadband market share.',

        stock_data: {
            current_price: 38.50,
            price_change_1d: 0.5,
            price_change_1w: 2.2,
            price_change_1m: 4.8,
            price_change_3m: 8.5,
            price_change_1y: 12.2,
            week_52_high: 42.00,
            week_52_low: 34.00,
            volume: 2_500_000,
            pe_ratio: 14.5,
            dividend_yield: 3.8,
            price_history_30d: generatePriceHistory(38.50),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(28_000_000_000),
            profit_margin: 13.5,
            employee_count: 4_500,
            market_share: 55.2,
        },

        sensitivity_indicators: [
            { indicator_name: 'Broadband Adoption', correlation: 0.88, impact_level: 'high', description: 'Fiber optic expansion' },
            { indicator_name: 'Work From Home Trend', correlation: 0.72, impact_level: 'high', description: 'Home internet demand' },
            { indicator_name: 'GDP Growth', correlation: 0.58, impact_level: 'medium', description: 'Business connectivity demand' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R32', title: 'Mobile Substitution', type: 'risk', severity: 'medium', description: 'Fixed-line decline as mobile data improves' },
                { insight_id: 'R33', title: 'Infrastructure Investment', type: 'risk', severity: 'high', description: 'Heavy capex required for fiber rollout' },
            ],
            opportunities: [
                { insight_id: 'O31', title: 'Fiber Expansion', type: 'opportunity', severity: 'high', description: 'Growing demand for high-speed broadband' },
                { insight_id: 'O32', title: 'Enterprise Solutions', type: 'opportunity', severity: 'medium', description: 'Cloud and data center services for businesses' },
                { insight_id: 'O33', title: 'Smart City Projects', type: 'opportunity', severity: 'medium', description: 'Government digitalization initiatives' },
            ],
        },

        recent_incidents_impact: [],
    },

    // Consumer Goods (1 company)
    {
        company_id: 'CARG',
        ticker: 'CARG',
        name: 'Cargills Ceylon',
        sector: 'Consumer Goods',
        industry: 'Food & Retail',
        market_cap: 78_000_000_000,
        description: 'Leading supermarket chain and FMCG company with diverse retail and food operations.',

        stock_data: {
            current_price: 285.00,
            price_change_1d: 1.8,
            price_change_1w: 4.5,
            price_change_1m: 8.2,
            price_change_3m: 14.5,
            price_change_1y: 22.8,
            week_52_high: 298.00,
            week_52_low: 232.00,
            volume: 180_000,
            pe_ratio: 16.5,
            dividend_yield: 2.8,
            price_history_30d: generatePriceHistory(285.00, 0.018),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(42_000_000_000),
            profit_margin: 8.5,
            employee_count: 12_000,
            market_share: 22.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Consumer Spending', correlation: 0.85, impact_level: 'high', description: 'Retail sales dependency' },
            { indicator_name: 'Inflation', correlation: -0.62, impact_level: 'high', description: 'Purchasing power impact' },
            { indicator_name: 'Tourism', correlation: 0.45, impact_level: 'medium', description: 'Tourist spending in stores' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R34', title: 'Competition Intensity', type: 'risk', severity: 'high', description: 'Aggressive competition from Keells and Arpico' },
                { insight_id: 'R35', title: 'Supply Chain Disruptions', type: 'risk', severity: 'medium', description: 'Weather and transport affecting product availability' },
                { insight_id: 'R36', title: 'Real Estate Costs', type: 'risk', severity: 'medium', description: 'High rental costs for prime locations' },
            ],
            opportunities: [
                { insight_id: 'O34', title: 'Store Expansion', type: 'opportunity', severity: 'high', description: 'Opening new outlets in suburban areas' },
                { insight_id: 'O35', title: 'Private Label Growth', type: 'opportunity', severity: 'high', description: 'Own-brand products with higher margins' },
                { insight_id: 'O36', title: 'Online Grocery', type: 'opportunity', severity: 'medium', description: 'E-commerce and home delivery services' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'W1', incident_name: 'Heavy Monsoon Rains & Flooding', date: '2024-11-25', stock_impact_percent: -4.2, operational_impact: 'Supply chain disruptions, store closures in affected areas', recovery_days: 12 },
        ],
    },

    // Agriculture (1 company)
    {
        company_id: 'WATA',
        ticker: 'WATA',
        name: 'Watawala Plantations',
        sector: 'Agriculture',
        industry: 'Tea & Rubber Plantations',
        market_cap: 32_000_000_000,
        description: 'Major plantation company with tea and rubber estates across central highlands.',

        stock_data: {
            current_price: 68.00,
            price_change_1d: -1.8,
            price_change_1w: -3.5,
            price_change_1m: -6.8,
            price_change_3m: -4.2,
            price_change_1y: 5.5,
            week_52_high: 78.00,
            week_52_low: 62.00,
            volume: 420_000,
            pe_ratio: 9.5,
            dividend_yield: 5.8,
            price_history_30d: generatePriceHistory(68.00, 0.028),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(12_000_000_000),
            profit_margin: 8.2,
            employee_count: 6_500,
            market_share: 12.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Weather Patterns', correlation: 0.88, impact_level: 'high', description: 'Rainfall and temperature critical for crops' },
            { indicator_name: 'Tea Prices', correlation: 0.82, impact_level: 'high', description: 'Global commodity prices' },
            { indicator_name: 'Rubber Prices', correlation: 0.75, impact_level: 'high', description: 'International rubber market' },
            { indicator_name: 'Fuel Prices', correlation: -0.68, impact_level: 'high', description: 'Transportation to auctions' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R37', title: 'Weather Vulnerability', type: 'risk', severity: 'high', description: 'Extreme weather events damaging crops and infrastructure' },
                { insight_id: 'R38', title: 'Labor Shortage', type: 'risk', severity: 'high', description: 'Difficulty finding plantation workers' },
                { insight_id: 'R39', title: 'Commodity Price Volatility', type: 'risk', severity: 'medium', description: 'Tea and rubber prices fluctuate with global demand' },
            ],
            opportunities: [
                { insight_id: 'O37', title: 'Premium Ceylon Tea', type: 'opportunity', severity: 'high', description: 'Growing global demand for high-quality Ceylon tea' },
                { insight_id: 'O38', title: 'Organic Certification', type: 'opportunity', severity: 'medium', description: 'Premium prices for organic tea' },
                { insight_id: 'O39', title: 'Diversification', type: 'opportunity', severity: 'medium', description: 'Adding spices and other crops to portfolio' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'W1', incident_name: 'Heavy Monsoon Rains & Flooding', date: '2024-11-25', stock_impact_percent: -10.8, operational_impact: 'Crop damage in low-lying estates, soil erosion affecting yields', recovery_days: 40 },
            { incident_id: 'W2', incident_name: 'Landslides in Central Highlands', date: '2024-10-18', stock_impact_percent: -14.5, operational_impact: 'Estate infrastructure damaged, replanting required', recovery_days: 50 },
        ],
    },

    // Energy & Power (2 companies)
    {
        company_id: 'CEB',
        ticker: 'CEB',
        name: 'Ceylon Electricity Board',
        sector: 'Energy & Power',
        industry: 'Electricity Generation',
        market_cap: 180_000_000_000,
        description: 'National electricity utility providing power generation and distribution across Sri Lanka.',

        stock_data: {
            current_price: 95.00,
            price_change_1d: -0.8,
            price_change_1w: -2.2,
            price_change_1m: 1.5,
            price_change_3m: 4.8,
            price_change_1y: 8.5,
            week_52_high: 105.00,
            week_52_low: 85.00,
            volume: 850_000,
            pe_ratio: 11.2,
            dividend_yield: 4.2,
            price_history_30d: generatePriceHistory(95.00),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(65_000_000_000),
            profit_margin: 6.5,
            employee_count: 15_000,
            market_share: 92.0,
        },

        sensitivity_indicators: [
            { indicator_name: 'Rainfall', correlation: 0.85, impact_level: 'high', description: 'Hydropower generation dependency' },
            { indicator_name: 'Fuel Prices', correlation: -0.88, impact_level: 'high', description: 'Thermal power generation costs' },
            { indicator_name: 'Industrial Activity', correlation: 0.72, impact_level: 'medium', description: 'Electricity demand from industries' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R40', title: 'Drought Impact', type: 'risk', severity: 'high', description: 'Reduced hydropower forcing expensive thermal generation' },
                { insight_id: 'R41', title: 'Fuel Cost Volatility', type: 'risk', severity: 'high', description: 'Oil price fluctuations affecting thermal plants' },
                { insight_id: 'R42', title: 'Tariff Regulation', type: 'risk', severity: 'medium', description: 'Government control on electricity pricing' },
            ],
            opportunities: [
                { insight_id: 'O40', title: 'Renewable Energy', type: 'opportunity', severity: 'high', description: 'Expanding solar and wind power capacity' },
                { insight_id: 'O41', title: 'Grid Modernization', type: 'opportunity', severity: 'medium', description: 'Smart grid technology reducing losses' },
            ],
        },

        recent_incidents_impact: [
            { incident_id: 'W3', incident_name: 'Drought Conditions', date: '2024-09-10', stock_impact_percent: -10.5, operational_impact: 'Hydropower generation down 40%, increased thermal generation costs', recovery_days: 90 },
        ],
    },

    {
        company_id: 'LOLC',
        ticker: 'LOLC',
        name: 'LOLC Holdings',
        sector: 'Banking & Finance',
        industry: 'Diversified Finance',
        market_cap: 165_000_000_000,
        description: 'Diversified financial services group with microfinance, leasing, insurance, and banking operations.',

        stock_data: {
            current_price: 245.00,
            price_change_1d: 2.2,
            price_change_1w: 5.5,
            price_change_1m: 10.8,
            price_change_3m: 18.5,
            price_change_1y: 28.2,
            week_52_high: 258.00,
            week_52_low: 192.00,
            volume: 680_000,
            pe_ratio: 10.5,
            dividend_yield: 3.2,
            price_history_30d: generatePriceHistory(245.00, 0.022),
        },

        operational_metrics: {
            revenue_quarterly: generateQuarterlyRevenue(35_000_000_000),
            profit_margin: 14.5,
            employee_count: 8_500,
            market_share: 18.5,
        },

        sensitivity_indicators: [
            { indicator_name: 'Interest Rate', correlation: 0.75, impact_level: 'high', description: 'Lending and leasing margins' },
            { indicator_name: 'SME Growth', correlation: 0.82, impact_level: 'high', description: 'Microfinance and SME lending' },
            { indicator_name: 'GDP Growth', correlation: 0.78, impact_level: 'high', description: 'Overall economic activity' },
        ],

        business_insights: {
            risks: [
                { insight_id: 'R43', title: 'Credit Risk', type: 'risk', severity: 'high', description: 'High exposure to SME and micro-segment defaults' },
                { insight_id: 'R44', title: 'Regulatory Changes', type: 'risk', severity: 'medium', description: 'Microfinance sector regulations' },
            ],
            opportunities: [
                { insight_id: 'O42', title: 'Microfinance Expansion', type: 'opportunity', severity: 'high', description: 'Growing unbanked population needing financial services' },
                { insight_id: 'O43', title: 'Digital Finance', type: 'opportunity', severity: 'high', description: 'Mobile-based lending and payments' },
                { insight_id: 'O44', title: 'Regional Expansion', type: 'opportunity', severity: 'medium', description: 'Expanding operations to other South Asian markets' },
            ],
        },

        recent_incidents_impact: [],
    },
];
