/**
 * API Types
 * 
 * TypeScript interfaces matching the backend Layer 5 schemas.
 */

// ============== Auth Types ==============

export interface UserLogin {
  email: string;
  password: string;
}

// Alias for UserLogin (used in auth context)
export type LoginCredentials = UserLogin;

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string;
  company_id?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: number;
  email: string;
  full_name: string | null;
  role: 'admin' | 'user';
  company_id: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

// ============== Dashboard Types ==============

export type TrendDirection = 'up' | 'down' | 'stable';
export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low';
export type InsightType = 'risk' | 'opportunity' | 'recommendation';

export interface HealthScore {
  overall_score: number;
  trend: TrendDirection;
  components: Record<string, number>;
  last_calculated: string;
}

export interface NationalIndicator {
  indicator_id: string;
  indicator_name: string;
  pestel_category: string;
  description: string | null;
  current_value: number | null;
  previous_value: number | null;
  change_percentage: number | null;
  trend: TrendDirection;
  threshold_high: number | null;
  threshold_low: number | null;
  status: 'normal' | 'warning' | 'critical';
  last_updated: string | null;
  confidence: number | null;
  source_count: number | null;
}

export interface NationalIndicatorList {
  indicators: NationalIndicator[];
  total: number;
  by_category: Record<string, number>;
}

export interface BusinessInsight {
  insight_id: number;
  company_id: string;
  insight_type: InsightType;
  category: string;
  title: string;
  description: string;
  probability: number | null;
  impact: number | null;
  urgency: number | null;
  final_score: number | null;
  severity_level: SeverityLevel | null;
  confidence: number | null;
  detected_at: string;
  expected_impact_time: string | null;
  expected_duration_hours: number | null;
  status: string;
  is_urgent: boolean;
  requires_immediate_action: boolean;
  priority_rank: number | null;
  triggering_indicators: string[] | null;
  affected_operations: string[] | null;
}

export interface BusinessInsightList {
  insights: BusinessInsight[];
  total: number;
  risks_count: number;
  opportunities_count: number;
  critical_count: number;
  by_category: Record<string, number>;
}

export interface RiskSummary {
  total_active: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  recent_risks: BusinessInsight[];
  trend: TrendDirection;
}

export interface OpportunitySummary {
  total_active: number;
  high_potential: number;
  medium_potential: number;
  low_potential: number;
  recent_opportunities: BusinessInsight[];
  trend: TrendDirection;
}

export interface DashboardHome {
  company_id: string;
  company_name: string;
  health_score: HealthScore;
  risk_summary: RiskSummary;
  opportunity_summary: OpportunitySummary;
  key_indicators: OperationalIndicator[];
  last_updated: string;
}

export interface OperationalIndicator {
  indicator_id: string;
  indicator_name: string;
  category: string;
  current_value: number;
  baseline_value?: number;
  deviation?: number;
  impact_score?: number;
  trend: TrendDirection;
  is_above_threshold?: boolean;
  is_below_threshold?: boolean;
  company_id?: string;
  calculated_at?: string | Date;
  status?: string;
}

export interface OperationalIndicatorListResponse {
  company_id: string;
  indicators: OperationalIndicator[];
  total: number;
  critical_count: number;
  warning_count: number;
}

// ============== Admin Types ==============

export interface IndustryOverview {
  industry: string;
  company_count: number;
  average_health_score: number;
  total_active_risks: number;
  total_active_opportunities: number;
  critical_risks: number;
  top_risk_indicators: string[];
  top_opportunity_indicators: string[];
}

export interface AdminDashboard {
  total_companies: number;
  total_active_users: number;
  total_indicators: number;
  total_insights: number;
  total_active_risks: number;
  total_active_opportunities: number;
  critical_alerts: number;
  industries: IndustryOverview[];
  last_updated: string;
}

// ============== Company Types ==============

export interface CompanyProfile {
  company_id: string;
  company_name: string;
  industry: string | null;
  sub_industry: string | null;
  business_scale: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CompanyProfileUpdate {
  company_name?: string;
  industry?: string;
  sub_industry?: string;
  business_scale?: string;
  description?: string;
}

// ============== Chart Types ==============

export interface PestelDistribution {
  category: string;
  count: number;
  color: string;
}

export interface IndicatorHistoryPoint {
  timestamp: string;
  value: number;
  confidence: number;
  source_count: number;
}

export interface IndicatorHistory {
  indicator_id: string;
  indicator_name: string;
  days: number;
  history: IndicatorHistoryPoint[];
}

export interface IndicatorHistoryBatch {
  [indicator_id: string]: IndicatorHistory;
}

// ============== API Error ==============

export interface ApiError {
  detail: string;
  status?: number;
}
