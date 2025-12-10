/**
 * API Module Index
 * 
 * Export all API-related functionality.
 */

export { API_CONFIG } from './config';
export { apiClient } from './client';
export { authService } from './auth';
export { dashboardService } from './dashboard';

// Export all types
export type {
  // Auth types
  UserLogin,
  UserCreate,
  TokenResponse,
  UserResponse,
  PasswordChange,
  
  // Dashboard types
  TrendDirection,
  SeverityLevel,
  InsightType,
  HealthScore,
  NationalIndicator,
  NationalIndicatorList,
  BusinessInsight,
  BusinessInsightList,
  RiskSummary,
  OpportunitySummary,
  DashboardHome,
  OperationalIndicator,
  
  // Admin types
  IndustryOverview,
  AdminDashboard,
  
  // Company types
  CompanyProfile,
  CompanyProfileUpdate,
  
  // Error type
  ApiError,
} from './types';
