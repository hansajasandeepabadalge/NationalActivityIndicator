import {Indicator} from "@/types/indicator";

export const mockIndicators: Indicator[] = [
    {
        id: '1',
        name: 'Supply Chain Health',
        score: 85,
        trend: 'up',
        status: 'good',
        factors: [
            { name: 'Supplier Reliability', score: 90, trend: 'up' },
            { name: 'Import Clearance Time', score: 78, trend: 'stable' },
            { name: 'Transport Availability', score: 88, trend: 'up' }
        ]
    },
    {
        id: '2',
        name: 'Workforce Readiness',
        score: 68,
        trend: 'down',
        status: 'warning',
        factors: [
            { name: 'Transport Accessibility', score: 55, trend: 'down' },
            { name: 'Power Availability', score: 72, trend: 'down' },
            { name: 'Safety Conditions', score: 85, trend: 'stable' }
        ]
    },
    {
        id: '3',
        name: 'Financial Stability',
        score: 74,
        trend: 'stable',
        status: 'good',
        factors: [
            { name: 'Cash Flow', score: 70, trend: 'stable' },
            { name: 'Credit Access', score: 80, trend: 'up' },
            { name: 'Currency Exposure', score: 65, trend: 'down' }
        ]
    }
];