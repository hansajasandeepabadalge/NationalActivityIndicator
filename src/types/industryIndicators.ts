/**
 * Industry-wise Operational Indicators Types and Mock Data
 */

export type IndustryType = 'Manufacturing' | 'Technology' | 'Finance' | 'Healthcare' | 'Retail' | 'Agriculture';

export type TrendDirection = 'up' | 'down' | 'stable';
export type StatusType = 'good' | 'warning' | 'critical';

export interface IndustryIndicator {
    industry: IndustryType;
    indicator_name: string;
    current_value: number;
    baseline_value: number;
    change_percentage: number;
    trend: TrendDirection;
    status: StatusType;
    unit: string;
    category: string;
    sparkline_data?: number[]; // 7-day trend data
}

export interface IndustryPerformance {
    industry: IndustryType;
    dimensions: {
        efficiency: number;
        quality: number;
        growth: number;
        innovation: number;
        sustainability: number;
    };
}

export const INDUSTRY_COLORS: Record<IndustryType, string> = {
    Manufacturing: '#3b82f6',
    Technology: '#8b5cf6',
    Finance: '#10b981',
    Healthcare: '#ef4444',
    Retail: '#f97316',
    Agriculture: '#059669',
};

export const INDUSTRY_ICONS: Record<IndustryType, string> = {
    Manufacturing: '🏭',
    Technology: '💻',
    Finance: '💰',
    Healthcare: '🏥',
    Retail: '🛒',
    Agriculture: '🌾',
};

// Mock data generator
function generateSparkline(): number[] {
    const base = 70 + Math.random() * 20;
    return Array.from({ length: 7 }, (_, i) => base + Math.sin(i) * 5 + (Math.random() - 0.5) * 3);
}

export const MOCK_INDUSTRY_INDICATORS: IndustryIndicator[] = [
    // Manufacturing
    {
        industry: 'Manufacturing',
        indicator_name: 'Production Efficiency',
        current_value: 87.5,
        baseline_value: 82.0,
        change_percentage: 6.7,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Efficiency',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Manufacturing',
        indicator_name: 'Quality Score',
        current_value: 94.2,
        baseline_value: 91.5,
        change_percentage: 3.0,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Quality',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Manufacturing',
        indicator_name: 'Equipment Uptime',
        current_value: 91.8,
        baseline_value: 89.0,
        change_percentage: 3.1,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Efficiency',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Manufacturing',
        indicator_name: 'Defect Rate',
        current_value: 2.3,
        baseline_value: 3.5,
        change_percentage: -34.3,
        trend: 'down',
        status: 'good',
        unit: '%',
        category: 'Quality',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Manufacturing',
        indicator_name: 'On-Time Delivery',
        current_value: 96.1,
        baseline_value: 93.0,
        change_percentage: 3.3,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Performance',
        sparkline_data: generateSparkline(),
    },

    // Technology
    {
        industry: 'Technology',
        indicator_name: 'Innovation Index',
        current_value: 8.7,
        baseline_value: 7.5,
        change_percentage: 16.0,
        trend: 'up',
        status: 'good',
        unit: '/10',
        category: 'Innovation',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Technology',
        indicator_name: 'R&D Investment',
        current_value: 15.2,
        baseline_value: 12.8,
        change_percentage: 18.8,
        trend: 'up',
        status: 'good',
        unit: '% of revenue',
        category: 'Investment',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Technology',
        indicator_name: 'Product Launch Rate',
        current_value: 12,
        baseline_value: 9,
        change_percentage: 33.3,
        trend: 'up',
        status: 'good',
        unit: 'per year',
        category: 'Innovation',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Technology',
        indicator_name: 'Customer Satisfaction',
        current_value: 4.6,
        baseline_value: 4.2,
        change_percentage: 9.5,
        trend: 'up',
        status: 'good',
        unit: '/5',
        category: 'Quality',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Technology',
        indicator_name: 'Market Share Growth',
        current_value: 5.8,
        baseline_value: 3.2,
        change_percentage: 81.3,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Growth',
        sparkline_data: generateSparkline(),
    },

    // Finance
    {
        industry: 'Finance',
        indicator_name: 'Capital Adequacy Ratio',
        current_value: 14.5,
        baseline_value: 12.0,
        change_percentage: 20.8,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Stability',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Finance',
        indicator_name: 'Liquidity Ratio',
        current_value: 1.8,
        baseline_value: 1.5,
        change_percentage: 20.0,
        trend: 'up',
        status: 'good',
        unit: 'ratio',
        category: 'Stability',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Finance',
        indicator_name: 'NPL Ratio',
        current_value: 2.1,
        baseline_value: 3.5,
        change_percentage: -40.0,
        trend: 'down',
        status: 'good',
        unit: '%',
        category: 'Risk',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Finance',
        indicator_name: 'Return on Equity',
        current_value: 18.3,
        baseline_value: 15.0,
        change_percentage: 22.0,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Performance',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Finance',
        indicator_name: 'Cost-to-Income',
        current_value: 42.5,
        baseline_value: 48.0,
        change_percentage: -11.5,
        trend: 'down',
        status: 'good',
        unit: '%',
        category: 'Efficiency',
        sparkline_data: generateSparkline(),
    },

    // Healthcare
    {
        industry: 'Healthcare',
        indicator_name: 'Patient Satisfaction',
        current_value: 4.7,
        baseline_value: 4.3,
        change_percentage: 9.3,
        trend: 'up',
        status: 'good',
        unit: '/5',
        category: 'Quality',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Healthcare',
        indicator_name: 'Bed Occupancy',
        current_value: 78.5,
        baseline_value: 82.0,
        change_percentage: -4.3,
        trend: 'down',
        status: 'warning',
        unit: '%',
        category: 'Utilization',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Healthcare',
        indicator_name: 'Average Wait Time',
        current_value: 23,
        baseline_value: 35,
        change_percentage: -34.3,
        trend: 'down',
        status: 'good',
        unit: 'minutes',
        category: 'Efficiency',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Healthcare',
        indicator_name: 'Treatment Success Rate',
        current_value: 92.4,
        baseline_value: 89.0,
        change_percentage: 3.8,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Quality',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Healthcare',
        indicator_name: 'Staff-to-Patient Ratio',
        current_value: 4.2,
        baseline_value: 5.0,
        change_percentage: -16.0,
        trend: 'down',
        status: 'good',
        unit: 'patients per staff',
        category: 'Resources',
        sparkline_data: generateSparkline(),
    },

    // Retail
    {
        industry: 'Retail',
        indicator_name: 'Same-Store Sales Growth',
        current_value: 6.2,
        baseline_value: 3.5,
        change_percentage: 77.1,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Growth',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Retail',
        indicator_name: 'Inventory Turnover',
        current_value: 8.5,
        baseline_value: 7.2,
        change_percentage: 18.1,
        trend: 'up',
        status: 'good',
        unit: 'times',
        category: 'Efficiency',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Retail',
        indicator_name: 'Customer Footfall',
        current_value: 12.3,
        baseline_value: 8.0,
        change_percentage: 53.8,
        trend: 'up',
        status: 'good',
        unit: '% increase',
        category: 'Traffic',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Retail',
        indicator_name: 'Average Transaction Value',
        current_value: 45.8,
        baseline_value: 42.0,
        change_percentage: 9.0,
        trend: 'up',
        status: 'good',
        unit: '$',
        category: 'Revenue',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Retail',
        indicator_name: 'Online Sales Percentage',
        current_value: 28.5,
        baseline_value: 22.0,
        change_percentage: 29.5,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Digital',
        sparkline_data: generateSparkline(),
    },

    // Agriculture
    {
        industry: 'Agriculture',
        indicator_name: 'Crop Yield Index',
        current_value: 112,
        baseline_value: 100,
        change_percentage: 12.0,
        trend: 'up',
        status: 'good',
        unit: 'index',
        category: 'Productivity',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Agriculture',
        indicator_name: 'Water Efficiency',
        current_value: 85.3,
        baseline_value: 78.0,
        change_percentage: 9.4,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Sustainability',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Agriculture',
        indicator_name: 'Soil Health Score',
        current_value: 7.8,
        baseline_value: 7.2,
        change_percentage: 8.3,
        trend: 'up',
        status: 'good',
        unit: '/10',
        category: 'Sustainability',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Agriculture',
        indicator_name: 'Organic Farming Percentage',
        current_value: 18.5,
        baseline_value: 12.0,
        change_percentage: 54.2,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Sustainability',
        sparkline_data: generateSparkline(),
    },
    {
        industry: 'Agriculture',
        indicator_name: 'Export Growth',
        current_value: 9.2,
        baseline_value: 5.5,
        change_percentage: 67.3,
        trend: 'up',
        status: 'good',
        unit: '%',
        category: 'Growth',
        sparkline_data: generateSparkline(),
    },
];

export const MOCK_INDUSTRY_PERFORMANCE: IndustryPerformance[] = [
    {
        industry: 'Manufacturing',
        dimensions: {
            efficiency: 87,
            quality: 92,
            growth: 78,
            innovation: 72,
            sustainability: 68,
        },
    },
    {
        industry: 'Technology',
        dimensions: {
            efficiency: 82,
            quality: 88,
            growth: 95,
            innovation: 94,
            sustainability: 75,
        },
    },
    {
        industry: 'Finance',
        dimensions: {
            efficiency: 85,
            quality: 90,
            growth: 82,
            innovation: 78,
            sustainability: 80,
        },
    },
    {
        industry: 'Healthcare',
        dimensions: {
            efficiency: 76,
            quality: 93,
            growth: 70,
            innovation: 82,
            sustainability: 85,
        },
    },
    {
        industry: 'Retail',
        dimensions: {
            efficiency: 88,
            quality: 85,
            growth: 90,
            innovation: 80,
            sustainability: 72,
        },
    },
    {
        industry: 'Agriculture',
        dimensions: {
            efficiency: 80,
            quality: 86,
            growth: 85,
            innovation: 70,
            sustainability: 92,
        },
    },
];

// Utility functions
export function getIndicatorsByIndustry(industry: IndustryType | 'All'): IndustryIndicator[] {
    if (industry === 'All') {
        return MOCK_INDUSTRY_INDICATORS;
    }
    return MOCK_INDUSTRY_INDICATORS.filter(ind => ind.industry === industry);
}

export function getTopIndicators(limit: number = 10): IndustryIndicator[] {
    return MOCK_INDUSTRY_INDICATORS
        .sort((a, b) => Math.abs(b.change_percentage) - Math.abs(a.change_percentage))
        .slice(0, limit);
}

export function getIndustryPerformance(industry: IndustryType): IndustryPerformance | undefined {
    return MOCK_INDUSTRY_PERFORMANCE.find(perf => perf.industry === industry);
}
