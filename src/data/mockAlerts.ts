import {Alert} from "@/types/alert";

export const mockAlerts: Alert[] = [
    {
        id: '1',
        severity: 'critical',
        title: 'Fuel Shortage Alert',
        description: 'Critical fuel shortage detected in Western Province affecting your delivery operations.',
        time: '2 hours ago',
        read: false,
        recommendations: [
            'Postpone non-urgent deliveries',
            'Notify customers of potential delays',
            'Coordinate with alternative suppliers'
        ]
    },
    {
        id: '2',
        severity: 'high',
        title: 'Currency Volatility Warning',
        description: 'LKR depreciation accelerating beyond predicted thresholds.',
        time: '5 hours ago',
        read: true,
        recommendations: [
            'Review hedging positions',
            'Accelerate pending payments'
        ]
    },
    {
        id: '3',
        severity: 'medium',
        title: 'Policy Update Notice',
        description: 'New import regulations effective from next month.',
        time: '1 day ago',
        read: true
    }
];