export type OpportunityValue = "high" | "medium" | "low";
export type RequirementStatus = "have" | "need";

export interface Requirement {
    item: string;
    status: RequirementStatus;
}

export interface Opportunity {
    id: string;
    value: OpportunityValue;
    name: string;
    description: string;
    potentialValue: number;
    feasibility: number;
    strategicFit: number;
    timing: string;
    whyNow: string;
    requirements: Requirement[];
    cost?: string;
}
