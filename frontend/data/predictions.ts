/**
 * Predictive Impact Analysis Types
 * Mock prediction data showing how national indicators might affect companies
 */

export interface PredictionScenario {
    scenario_id: string;
    scenario_name: string;
    description: string;
    probability: number; // 0-100
    timeframe_days: number;
    national_indicators_change: {
        indicator_name: string;
        current_value: number;
        predicted_value: number;
        change_percent: number;
    }[];
}

export interface CompanyPrediction {
    company_id: string;
    ticker: string;
    name: string;
    current_price: number;
    predictions: {
        scenario_id: string;
        scenario_name: string;
        predicted_price: number;
        price_change_percent: number;
        confidence_level: 'high' | 'medium' | 'low';
        confidence_score: number; // 0-100
        timeline: {
            day: number;
            predicted_price: number;
        }[];
        key_drivers: string[];
    }[];
}

// Mock prediction scenarios
export const PREDICTION_SCENARIOS: PredictionScenario[] = [
    {
        scenario_id: 'S1',
        scenario_name: 'Interest Rate Hike +1.5%',
        description: 'Central Bank increases policy rates by 1.5% to control inflation',
        probability: 65,
        timeframe_days: 90,
        national_indicators_change: [
            { indicator_name: 'Interest Rate', current_value: 9.0, predicted_value: 10.5, change_percent: 16.7 },
            { indicator_name: 'Inflation', current_value: 5.2, predicted_value: 4.5, change_percent: -13.5 },
            { indicator_name: 'GDP Growth', current_value: 4.5, predicted_value: 4.0, change_percent: -11.1 },
        ],
    },
    {
        scenario_id: 'S2',
        scenario_name: 'Tourism Boom',
        description: 'Tourist arrivals increase 40% due to visa-free entry expansion',
        probability: 75,
        timeframe_days: 180,
        national_indicators_change: [
            { indicator_name: 'Tourism Arrivals', current_value: 200000, predicted_value: 280000, change_percent: 40.0 },
            { indicator_name: 'GDP Growth', current_value: 4.5, predicted_value: 5.2, change_percent: 15.6 },
            { indicator_name: 'Employment Rate', current_value: 92.0, predicted_value: 93.5, change_percent: 1.6 },
        ],
    },
    {
        scenario_id: 'S3',
        scenario_name: 'Fuel Price Reduction -20%',
        description: 'Global oil prices drop, reducing domestic fuel costs by 20%',
        probability: 45,
        timeframe_days: 60,
        national_indicators_change: [
            { indicator_name: 'Fuel Prices', current_value: 350, predicted_value: 280, change_percent: -20.0 },
            { indicator_name: 'Inflation', current_value: 5.2, predicted_value: 4.0, change_percent: -23.1 },
            { indicator_name: 'Transportation Index', current_value: 100, predicted_value: 115, change_percent: 15.0 },
        ],
    },
    {
        scenario_id: 'S4',
        scenario_name: 'Heavy Monsoon Season',
        description: 'Above-average rainfall predicted for next monsoon season',
        probability: 55,
        timeframe_days: 120,
        national_indicators_change: [
            { indicator_name: 'Weather Patterns', current_value: 100, predicted_value: 140, change_percent: 40.0 },
            { indicator_name: 'Agricultural Output', current_value: 100, predicted_value: 85, change_percent: -15.0 },
            { indicator_name: 'Hydropower Generation', current_value: 100, predicted_value: 125, change_percent: 25.0 },
        ],
    },
];

// Generate mock prediction timeline
function generatePredictionTimeline(
    currentPrice: number,
    targetPrice: number,
    days: number
): { day: number; predicted_price: number }[] {
    const timeline: { day: number; predicted_price: number }[] = [];
    const priceChange = targetPrice - currentPrice;

    for (let day = 0; day <= days; day += Math.ceil(days / 10)) {
        // S-curve progression for realistic prediction
        const progress = day / days;
        const sCurve = 1 / (1 + Math.exp(-10 * (progress - 0.5)));
        const predictedPrice = currentPrice + (priceChange * sCurve);

        // Add some noise
        const noise = (Math.random() - 0.5) * (currentPrice * 0.02);

        timeline.push({
            day,
            predicted_price: Number((predictedPrice + noise).toFixed(2)),
        });
    }

    return timeline;
}

// Mock company predictions
export const COMPANY_PREDICTIONS: CompanyPrediction[] = [
    {
        company_id: 'COMB',
        ticker: 'COMB',
        name: 'Commercial Bank',
        current_price: 144.75,
        predictions: [
            {
                scenario_id: 'S1',
                scenario_name: 'Interest Rate Hike +1.5%',
                predicted_price: 158.20,
                price_change_percent: 9.3,
                confidence_level: 'high',
                confidence_score: 85,
                timeline: generatePredictionTimeline(144.75, 158.20, 90),
                key_drivers: [
                    'Higher lending margins increase profitability',
                    'Improved net interest income',
                    'Strong correlation (0.85) with interest rates',
                ],
            },
            {
                scenario_id: 'S3',
                scenario_name: 'Fuel Price Reduction -20%',
                predicted_price: 149.50,
                price_change_percent: 3.3,
                confidence_level: 'medium',
                confidence_score: 65,
                timeline: generatePredictionTimeline(144.75, 149.50, 60),
                key_drivers: [
                    'Lower inflation boosts consumer spending',
                    'Reduced operational costs',
                ],
            },
        ],
    },
    {
        company_id: 'JKH',
        ticker: 'JKH',
        name: 'John Keells Holdings',
        current_price: 185.00,
        predictions: [
            {
                scenario_id: 'S2',
                scenario_name: 'Tourism Boom',
                predicted_price: 215.50,
                price_change_percent: 16.5,
                confidence_level: 'high',
                confidence_score: 88,
                timeline: generatePredictionTimeline(185.00, 215.50, 180),
                key_drivers: [
                    '40% revenue from tourism-related activities',
                    'Hotel occupancy rates increase',
                    'Retail and logistics benefit from tourist spending',
                ],
            },
            {
                scenario_id: 'S3',
                scenario_name: 'Fuel Price Reduction -20%',
                predicted_price: 198.75,
                price_change_percent: 7.4,
                confidence_level: 'high',
                confidence_score: 82,
                timeline: generatePredictionTimeline(185.00, 198.75, 60),
                key_drivers: [
                    'Transportation costs reduced significantly',
                    'Logistics division margins improve',
                    'Lower fuel costs for shipping operations',
                ],
            },
        ],
    },
    {
        company_id: 'SPEN',
        ticker: 'SPEN',
        name: 'Aitken Spence',
        current_price: 125.00,
        predictions: [
            {
                scenario_id: 'S2',
                scenario_name: 'Tourism Boom',
                predicted_price: 152.50,
                price_change_percent: 22.0,
                confidence_level: 'high',
                confidence_score: 90,
                timeline: generatePredictionTimeline(125.00, 152.50, 180),
                key_drivers: [
                    'Resort bookings increase 45%',
                    'Premium pricing power in peak season',
                    'Expansion of hospitality portfolio',
                ],
            },
            {
                scenario_id: 'S4',
                scenario_name: 'Heavy Monsoon Season',
                predicted_price: 112.50,
                price_change_percent: -10.0,
                confidence_level: 'medium',
                confidence_score: 70,
                timeline: generatePredictionTimeline(125.00, 112.50, 120),
                key_drivers: [
                    'Tourist cancellations during heavy rains',
                    'Resort access disruptions',
                    'Seasonal revenue impact',
                ],
            },
        ],
    },
    {
        company_id: 'HAYL',
        ticker: 'HAYL',
        name: 'Hayleys',
        current_price: 95.00,
        predictions: [
            {
                scenario_id: 'S4',
                scenario_name: 'Heavy Monsoon Season',
                predicted_price: 82.50,
                price_change_percent: -13.2,
                confidence_level: 'high',
                confidence_score: 85,
                timeline: generatePredictionTimeline(95.00, 82.50, 120),
                key_drivers: [
                    'Tea plantation flooding risk',
                    'Crop damage from excessive rainfall',
                    'Harvesting delays and quality issues',
                ],
            },
            {
                scenario_id: 'S3',
                scenario_name: 'Fuel Price Reduction -20%',
                predicted_price: 102.50,
                price_change_percent: 7.9,
                confidence_level: 'medium',
                confidence_score: 72,
                timeline: generatePredictionTimeline(95.00, 102.50, 60),
                key_drivers: [
                    'Lower transportation costs to auctions',
                    'Reduced operational expenses',
                ],
            },
        ],
    },
    {
        company_id: 'DIAL',
        ticker: 'DIAL',
        name: 'Dialog Axiata',
        current_price: 29.50,
        predictions: [
            {
                scenario_id: 'S2',
                scenario_name: 'Tourism Boom',
                predicted_price: 32.25,
                price_change_percent: 9.3,
                confidence_level: 'medium',
                confidence_score: 68,
                timeline: generatePredictionTimeline(29.50, 32.25, 180),
                key_drivers: [
                    'Increased roaming revenue from tourists',
                    'Higher data usage',
                ],
            },
        ],
    },
    {
        company_id: 'CEB',
        ticker: 'CEB',
        name: 'Ceylon Electricity Board',
        current_price: 95.00,
        predictions: [
            {
                scenario_id: 'S4',
                scenario_name: 'Heavy Monsoon Season',
                predicted_price: 105.50,
                price_change_percent: 11.1,
                confidence_level: 'high',
                confidence_score: 88,
                timeline: generatePredictionTimeline(95.00, 105.50, 120),
                key_drivers: [
                    'Hydropower generation increases 25%',
                    'Reduced reliance on expensive thermal power',
                    'Lower fuel costs improve margins',
                ],
            },
            {
                scenario_id: 'S3',
                scenario_name: 'Fuel Price Reduction -20%',
                predicted_price: 102.00,
                price_change_percent: 7.4,
                confidence_level: 'high',
                confidence_score: 85,
                timeline: generatePredictionTimeline(95.00, 102.00, 60),
                key_drivers: [
                    'Thermal power generation costs reduced',
                    'Improved profitability',
                ],
            },
        ],
    },
];

// Helper functions
export function getPredictionsByCompany(companyId: string): CompanyPrediction | undefined {
    return COMPANY_PREDICTIONS.find(p => p.company_id === companyId);
}

export function getPredictionsByScenario(scenarioId: string): CompanyPrediction[] {
    return COMPANY_PREDICTIONS.filter(cp =>
        cp.predictions.some(p => p.scenario_id === scenarioId)
    );
}

export function getConfidenceColor(level: 'high' | 'medium' | 'low'): string {
    switch (level) {
        case 'high': return 'text-green-600';
        case 'medium': return 'text-yellow-600';
        case 'low': return 'text-red-600';
    }
}
