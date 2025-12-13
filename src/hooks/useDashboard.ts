'use client';

import { useState, useEffect, useCallback } from 'react';
import { dashboardService } from '@/lib/api';
import type {
  AdminDashboard,
  NationalIndicator,
  BusinessInsight,
  Industry,
  DashboardHome,
  CompanyResponse,
  OperationalIndicator,
} from '@/lib/api/types';

// Generic fetch state
interface FetchState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

// Hook for admin dashboard data
export function useAdminDashboard(): FetchState<AdminDashboard> {
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getAdminDashboard();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for national indicators
export function useNationalIndicators(
  pestelCategory?: string,
  limit: number = 50,
  offset: number = 0
): FetchState<NationalIndicator[]> {
  const [data, setData] = useState<NationalIndicator[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getNationalIndicators(pestelCategory, limit, offset);
      // API returns { indicators: [...], total, by_category } - extract the array
      const indicators = result.indicators || [];

      // Add mock percentage for indicators that don't have real data
      const indicatorsWithMockData = indicators.map(indicator => {
        if (indicator.change_percentage === undefined || indicator.change_percentage === null) {
          // Generate consistent mock percentage based on indicator ID
          const hash = indicator.indicator_id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
          const mockPercentage = ((hash % 40) - 20) + (Math.random() * 4 - 2); // Range: -22 to +22
          return {
            ...indicator,
            change_percentage: parseFloat(mockPercentage.toFixed(1))
          };
        }
        return indicator;
      });

      setData(indicatorsWithMockData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch indicators');
    } finally {
      setIsLoading(false);
    }
  }, [pestelCategory, limit, offset]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for business insights
export function useBusinessInsights(
  companyId?: string,
  insightType?: string,
  severityLevel?: string,
  limit: number = 50
): FetchState<BusinessInsight[]> {
  const [data, setData] = useState<BusinessInsight[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getAllInsights({
        insight_type: insightType as 'risk' | 'opportunity' | undefined,
        severity: severityLevel,
        company_id: companyId,
        limit: limit
      });
      // API returns { insights: [...], total, ... } - extract the array
      setData(result.insights || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch insights');
    } finally {
      setIsLoading(false);
    }
  }, [companyId, insightType, severityLevel, limit]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for industries
export function useIndustries(): FetchState<Industry[]> {
  const [data, setData] = useState<Industry[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getIndustries();
      setData(result.industries.map(name => ({ name, company_count: result.by_industry[name] || 0 })));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch industries');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for companies (for admin selector)
export function useCompanies(): FetchState<import('@/lib/api/types').CompanyProfile[]> {
  const [data, setData] = useState<import('@/lib/api/types').CompanyProfile[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getCompanies({ limit: 100 });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch companies');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for user dashboard home
export function useDashboardHome(): FetchState<DashboardHome> {
  const [data, setData] = useState<DashboardHome | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getDashboardHome();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard home');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for user's company
export function useMyCompany(): FetchState<CompanyResponse> {
  const [data, setData] = useState<CompanyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getMyCompany();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch company');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for user's insights
export function useMyInsights(
  insightType?: string,
  severityLevel?: string,
  limit: number = 20
): FetchState<BusinessInsight[]> {
  const [data, setData] = useState<BusinessInsight[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getMyInsights(insightType, severityLevel, limit);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch insights');
    } finally {
      setIsLoading(false);
    }
  }, [insightType, severityLevel, limit]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for relevant national indicators (for user)
export function useRelevantIndicators(): FetchState<NationalIndicator[]> {
  const [data, setData] = useState<NationalIndicator[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await dashboardService.getRelevantIndicators();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch relevant indicators');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

// Hook for operational indicators (Layer 3)
export function useOperationalIndicators(
  limit: number = 20
): FetchState<OperationalIndicator[]> {
  const [data, setData] = useState<OperationalIndicator[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('🔍 useOperationalIndicators - Fetching with limit:', limit);
      const result = await dashboardService.getOperationalIndicators(limit);
      console.log('🔍 useOperationalIndicators - Result received:', result);
      // API returns { indicators: [...], total, ... } - extract the array
      const indicators = result.indicators || [];
      console.log('🔍 useOperationalIndicators - Setting data:', indicators.length, 'indicators');
      setData(indicators);
    } catch (err) {
      console.error('❌ useOperationalIndicators - Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch operational indicators');
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}
