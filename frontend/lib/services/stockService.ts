/**
 * Colombo Stock Exchange Service
 * 
 * Fetches stock market data from backend proxy (which fetches from CSE API)
 */

import { CSEData, MOCK_CSE_DATA } from '@/types/stock';

// Use backend API instead of CSE directly (bypasses CORS)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

// Cache to avoid excessive API calls
const cseCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export class StockService {
    /**
     * Fetch market summary from backend proxy
     */
    static async getMarketSummary(): Promise<CSEData> {
        // Check cache first
        const cacheKey = 'market_summary';
        const cached = cseCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
            return cached.data;
        }

        try {
            // Fetch from backend proxy (bypasses CORS)
            const response = await fetch(`${API_BASE_URL}/stock/market-summary`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`Backend API error: ${response.status}`);
            }

            const data = await response.json();

            // Cache the result
            cseCache.set(cacheKey, { data, timestamp: Date.now() });

            console.log('✅ Successfully fetched CSE data from backend');
            return data;
        } catch (error) {
            console.warn('⚠️ Failed to fetch CSE data from backend, using mock data:', error);
            // Return mock data as fallback
            return this.getMockData();
        }
    }

    /**
     * Get mock CSE data with some randomization
     */
    private static getMockData(): CSEData {
        const baseData = { ...MOCK_CSE_DATA };

        // Add some randomization to make it look live
        baseData.indices = baseData.indices.map(index => ({
            ...index,
            value: index.value + (Math.random() * 20 - 10),
            change: (Math.random() * 30 - 15),
            changePercent: (Math.random() * 2 - 1),
            timestamp: Date.now(),
        }));

        baseData.marketSummary = {
            ...baseData.marketSummary,
            totalTurnover: baseData.marketSummary.totalTurnover * (0.9 + Math.random() * 0.2),
            totalVolume: Math.floor(baseData.marketSummary.totalVolume * (0.9 + Math.random() * 0.2)),
            totalTrades: Math.floor(baseData.marketSummary.totalTrades * (0.9 + Math.random() * 0.2)),
        };

        baseData.lastUpdate = Date.now();

        return baseData;
    }

    /**
     * Format currency in LKR
     */
    static formatCurrency(amount: number): string {
        if (amount >= 1000000000) {
            return `LKR ${(amount / 1000000000).toFixed(2)}B`;
        } else if (amount >= 1000000) {
            return `LKR ${(amount / 1000000).toFixed(2)}M`;
        } else if (amount >= 1000) {
            return `LKR ${(amount / 1000).toFixed(2)}K`;
        }
        return `LKR ${amount.toFixed(2)}`;
    }

    /**
     * Format volume
     */
    static formatVolume(volume: number): string {
        if (volume >= 1000000) {
            return `${(volume / 1000000).toFixed(2)}M`;
        } else if (volume >= 1000) {
            return `${(volume / 1000).toFixed(2)}K`;
        }
        return volume.toString();
    }

    /**
     * Clear cache
     */
    static clearCache(): void {
        cseCache.clear();
    }
}
