import {Opportunity} from "@/types/opportunity";

export const mockOpportunities: Opportunity[] = [
    {
        id: '1',
        value: 'high',
        name: 'Export Tax Incentive',
        description: 'Government announced new tax breaks for export-oriented businesses in your sector',
        potentialValue: 8.5,
        feasibility: 75,
        strategicFit: 85,
        timing: 'Next 2 weeks',
        whyNow: 'Registration deadline in 15 days, early applicants get priority processing',
        requirements: [
            { item: 'Export documentation', status: 'have' },
            { item: 'Registration fee: LKR 50,000', status: 'need' }
        ],
        cost: 'LKR 50,000'
    },
    {
        id: '2',
        value: 'medium',
        name: 'Supplier Diversification',
        description: 'Multiple new suppliers entering market with competitive pricing',
        potentialValue: 6.5,
        feasibility: 90,
        strategicFit: 70,
        timing: 'This month',
        whyNow: 'Market conditions favorable for negotiation',
        requirements: [
            { item: 'Supplier evaluation', status: 'need' },
            { item: 'Contract templates', status: 'have' }
        ]
    }
];