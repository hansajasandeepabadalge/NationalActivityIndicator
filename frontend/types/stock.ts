// Colombo Stock Exchange (CSE) data types

export interface StockIndex {
    name: string;
    code: string; // e.g., "ASPI", "S&P SL20"
    value: number;
    change: number;
    changePercent: number;
    high: number;
    low: number;
    timestamp: number;
}

export interface StockQuote {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    volume: number;
    turnover: number;
    trades: number;
}

export interface MarketSummary {
    date: string;
    totalTurnover: number; // LKR
    totalVolume: number; // shares
    totalTrades: number;
    advancers: number; // stocks that went up
    decliners: number; // stocks that went down
    unchanged: number;
    marketCap: number; // LKR billions
}

export interface CSEData {
    indices: StockIndex[];
    marketSummary: MarketSummary;
    topGainers: StockQuote[];
    topLosers: StockQuote[];
    mostActive: StockQuote[];
    lastUpdate: number;
}

// Mock CSE data for fallback
export const MOCK_CSE_DATA: CSEData = {
    indices: [
        {
            name: 'All Share Price Index',
            code: 'ASPI',
            value: 11245.67,
            change: 125.34,
            changePercent: 1.13,
            high: 11289.45,
            low: 11198.23,
            timestamp: Date.now(),
        },
        {
            name: 'S&P Sri Lanka 20',
            code: 'S&P SL20',
            value: 3456.89,
            change: -12.45,
            changePercent: -0.36,
            high: 3478.12,
            low: 3445.67,
            timestamp: Date.now(),
        },
    ],
    marketSummary: {
        date: new Date().toISOString().split('T')[0],
        totalTurnover: 2450000000, // 2.45 billion LKR
        totalVolume: 45678900,
        totalTrades: 5678,
        advancers: 89,
        decliners: 67,
        unchanged: 45,
        marketCap: 3250, // 3.25 trillion LKR
    },
    topGainers: [
        { symbol: 'JKH', name: 'John Keells Holdings PLC', price: 145.50, change: 8.50, changePercent: 6.20, volume: 1234500, turnover: 179621250, trades: 456 },
        { symbol: 'COMB', name: 'Commercial Bank of Ceylon PLC', price: 98.75, change: 5.25, changePercent: 5.61, volume: 987600, turnover: 97525500, trades: 234 },
        { symbol: 'DIAL', name: 'Dialog Axiata PLC', price: 12.30, change: 0.60, changePercent: 5.13, volume: 5678900, turnover: 69850470, trades: 789 },
    ],
    topLosers: [
        { symbol: 'SAMP', name: 'Sampath Bank PLC', price: 87.25, change: -4.75, changePercent: -5.16, volume: 567800, turnover: 49550550, trades: 123 },
        { symbol: 'HNB', name: 'Hatton National Bank PLC', price: 156.00, change: -6.50, changePercent: -4.00, volume: 345600, turnover: 53913600, trades: 98 },
    ],
    mostActive: [
        { symbol: 'DIAL', name: 'Dialog Axiata PLC', price: 12.30, change: 0.60, changePercent: 5.13, volume: 5678900, turnover: 69850470, trades: 789 },
        { symbol: 'JKH', name: 'John Keells Holdings PLC', price: 145.50, change: 8.50, changePercent: 6.20, volume: 1234500, turnover: 179621250, trades: 456 },
    ],
    lastUpdate: Date.now(),
};
