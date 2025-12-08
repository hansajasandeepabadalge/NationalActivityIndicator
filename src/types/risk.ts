export type Severity = "critical" | "high" | "medium" | "low";

export type OperationImpact = "critical" | "high" | "medium" | "low";

export interface AffectedOperation {
    name: string;
    impact: OperationImpact;
}

export interface Risk {
    id: string;
    severity: Severity;
    name: string;
    description: string;
    probability: number;
    impact: string;
    timeHorizon: string;
    confidence: number;
    affectedOperations?: AffectedOperation[];
    financialImpact?: string;
    acknowledged: boolean;
}
