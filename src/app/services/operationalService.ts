import { apiClient } from '../../lib/api/client';
import { API_CONFIG } from '../../lib/api/config';

export interface OperationalIndicator {
    indicator_id: string;
    indicator_name: string;
    category: string;
    current_value: number;
    baseline_value: number;
    deviation: number | null;
    impact_score: number;
    trend: 'up' | 'down' | 'stable';
    is_above_threshold: boolean;
    is_below_threshold: boolean;
    company_id: string;
    calculated_at: string;
}

export interface OperationalIndicatorListResponse {
    company_id: string;
    indicators: OperationalIndicator[];
    total: number;
    critical_count: number;
    warning_count: number;
}

export class OperationalService {
    private static instance: OperationalService;

    private constructor() { }

    public static getInstance(): OperationalService {
        if (!OperationalService.instance) {
            OperationalService.instance = new OperationalService();
        }
        return OperationalService.instance;
    }

    public async getOperationalIndicators(limit: number = 20): Promise<OperationalIndicatorListResponse> {
        try {
            // Use apiClient which handles token automatically
            return await apiClient.get<OperationalIndicatorListResponse>(`/user/operations-data?limit=${limit}`);
        } catch (error) {
            console.error('Error fetching operational indicators:', error);
            throw error;
        }
    }

    public calculateOverallHealth(indicators: OperationalIndicator[]): number {
        if (!indicators || indicators.length === 0) return 100;

        // Calculate health based on average impact score
        // Impact score ranges from -1 (good) to 1 (bad). We only care about positive (bad) impact.
        const avgImpact = indicators.reduce((acc, ind) => acc + (ind.impact_score > 0 ? ind.impact_score : 0), 0) / indicators.length;

        // Map average impact (0 to 1) to health score (100 to 0)
        return Math.max(0, Math.round(100 - (avgImpact * 100)));
    }
}

export const operationalService = OperationalService.getInstance();
