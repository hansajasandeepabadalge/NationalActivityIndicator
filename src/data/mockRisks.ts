import {Risk} from "@/types/risk";

export const mockRisks: Risk[] = [
    {
        id: '1',
        severity: 'critical',
        name: 'Supply Chain Disruption',
        description: 'Fuel shortage expected in Western Province affecting deliveries and operations',
        probability: 85,
        impact: 'CRITICAL',
        timeHorizon: '24-48 hours',
        confidence: 82,
        affectedOperations: [
            { name: 'Deliveries', impact: 'critical' },
            { name: 'Warehouse operations', impact: 'high' },
            { name: 'Customer service', impact: 'medium' }
        ],
        acknowledged: false
    },
    {
        id: '2',
        severity: 'high',
        name: 'Currency Volatility Risk',
        description: 'LKR depreciation accelerating, affecting import costs for raw materials',
        probability: 78,
        impact: 'HIGH',
        timeHorizon: 'This week',
        confidence: 75,
        financialImpact: '+15-20% costs',
        acknowledged: true
    },
    {
        id: '3',
        severity: 'medium',
        name: 'Regulatory Compliance Update',
        description: 'New import documentation requirements coming into effect',
        probability: 65,
        impact: 'MEDIUM',
        timeHorizon: 'Next 2 weeks',
        confidence: 88,
        acknowledged: false
    }
];