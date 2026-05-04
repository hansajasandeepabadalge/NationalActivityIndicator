export type AlertSeverity = "critical" | "high" | "medium";

export interface Alert {
    id: string;
    severity: AlertSeverity;
    title: string;
    description: string;
    time: string;
    read: boolean;
    recommendations?: string[];
}
