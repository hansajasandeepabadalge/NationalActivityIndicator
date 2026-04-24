export type Trend = "up" | "down" | "stable";
export type IndicatorStatus = "good" | "warning" | "critical";

export interface Factor {
    name: string;
    score: number;
    trend: Trend;
}

export interface Indicator {
    id: string;
    name: string;
    score: number;
    trend: Trend;
    status: IndicatorStatus;
    factors: Factor[];
}
