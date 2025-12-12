/**
 * Dashboard Service
 * 
 * API calls for dashboard data from Layers 2-4.
 */

import { apiClient } from './client';
import type {
  NationalIndicatorList,
  BusinessInsightList,
  DashboardHome,
  AdminDashboard,
  IndustryOverview,
  CompanyProfile,
  OperationalIndicatorListResponse,
} from './types';

export const dashboardService = {
  // ============== Admin Endpoints ==============

  /**
   * Get admin dashboard overview
   */
  async getAdminDashboard(): Promise<AdminDashboard> {
    return apiClient.get<AdminDashboard>('/admin/dashboard');
  },

  /**
   * Get all national indicators (Layer 2)
   */
  async getNationalIndicators(category?: string, limit: number = 20): Promise<NationalIndicatorList> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    params.append('limit', limit.toString());
    return apiClient.get<NationalIndicatorList>(`/admin/indicators/national?${params}`);
  },

  /**
   * Get indicator history
   */
  async getIndicatorHistory(indicatorId: string, days: number = 30): Promise<{
    indicator_id: string;
    days: number;
    history: Array<{ timestamp: string; value: number; confidence: number; source_count: number }>;
  }> {
    return apiClient.get(`/admin/indicators/national/${indicatorId}/history?days=${days}`);
  },

  /**
   * List all industries
   */
  async getIndustries(): Promise<{ industries: string[]; by_industry: Record<string, number> }> {
    return apiClient.get('/admin/industries');
  },

  /**
   * Get industry overview
   */
  async getIndustryOverview(industry: string): Promise<IndustryOverview> {
    return apiClient.get<IndustryOverview>(`/admin/industries/${encodeURIComponent(industry)}/overview`);
  },

  /**
   * List all companies
   */
  async getCompanies(params?: {
    industry?: string;
    business_scale?: string;
    limit?: number;
    offset?: number;
  }): Promise<CompanyProfile[]> {
    const searchParams = new URLSearchParams();
    if (params?.industry) searchParams.append('industry', params.industry);
    if (params?.business_scale) searchParams.append('business_scale', params.business_scale);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());
    return apiClient.get<CompanyProfile[]>(`/admin/companies?${searchParams}`);
  },

  /**
   * Get all business insights (admin view)
   */
  async getAllInsights(params?: {
    insight_type?: 'risk' | 'opportunity';
    severity?: string;
    status?: string;
    company_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<BusinessInsightList> {
    const searchParams = new URLSearchParams();
    if (params?.insight_type) searchParams.append('insight_type', params.insight_type);
    if (params?.severity) searchParams.append('severity', params.severity);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.company_id) searchParams.append('company_id', params.company_id);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());
    return apiClient.get<BusinessInsightList>(`/admin/insights?${searchParams}`);
  },

  /**
   * Get all risks (admin view)
   */
  async getAllRisks(severity?: string, limit: number = 20): Promise<BusinessInsightList> {
    const params = new URLSearchParams();
    if (severity) params.append('severity', severity);
    params.append('limit', limit.toString());
    return apiClient.get<BusinessInsightList>(`/admin/insights/risks?${params}`);
  },

  /**
   * Get all opportunities (admin view)
   */
  async getAllOpportunities(limit: number = 20): Promise<BusinessInsightList> {
    return apiClient.get<BusinessInsightList>(`/admin/insights/opportunities?limit=${limit}`);
  },

  // ============== User Endpoints ==============

  /**
   * Get user's dashboard home
   */
  async getDashboardHome(): Promise<DashboardHome> {
    return apiClient.get<DashboardHome>('/user/dashboard/home');
  },

  /**
   * Get user's company profile
   */
  async getMyCompany(): Promise<CompanyProfile> {
    return apiClient.get<CompanyProfile>('/user/company');
  },

  /**
   * Get user's business insights
   */
  async getMyInsights(params?: {
    insight_type?: 'risk' | 'opportunity';
    severity?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<BusinessInsightList> {
    const searchParams = new URLSearchParams();
    if (params?.insight_type) searchParams.append('insight_type', params.insight_type);
    if (params?.severity) searchParams.append('severity', params.severity);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());
    return apiClient.get<BusinessInsightList>(`/user/insights?${searchParams}`);
  },

  /**
   * Get user's risks
   */
  async getMyRisks(severity?: string, limit: number = 20): Promise<BusinessInsightList> {
    const params = new URLSearchParams();
    if (severity) params.append('severity', severity);
    params.append('limit', limit.toString());
    return apiClient.get<BusinessInsightList>(`/user/risks?${params}`);
  },

  /**
   * Get user's opportunities
   */
  async getMyOpportunities(limit: number = 20): Promise<BusinessInsightList> {
    return apiClient.get<BusinessInsightList>(`/user/opportunities?limit=${limit}`);
  },

  /**
   * Get operational indicators (Layer 3)
   */
  async getOperationalIndicators(limit: number = 20): Promise<OperationalIndicatorListResponse> {
    return apiClient.get<OperationalIndicatorListResponse>(`/user/operations-data?limit=${limit}`);
  },

  /**
   * Acknowledge an insight
   */
  async acknowledgeInsight(insightId: number): Promise<{ message: string; insight_id: number }> {
    return apiClient.post(`/user/insights/${insightId}/acknowledge`);
  },

  /**
   * Resolve an insight
   */
  async resolveInsight(insightId: number, notes?: string): Promise<{ message: string; insight_id: number }> {
    const params = notes ? `?resolution_notes=${encodeURIComponent(notes)}` : '';
    return apiClient.post(`/user/insights/${insightId}/resolve${params}`);
  },
};

export default dashboardService;
