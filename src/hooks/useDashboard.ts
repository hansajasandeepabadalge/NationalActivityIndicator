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
      setData(result.indicators || []);
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
  companyId?: number,
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
      setData(result);
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
      const result = await dashboardService.getOperationalIndicators(limit);
      // API returns { indicators: [...], total, ... } - extract the array
      setData(result.indicators || []);
    } catch (err) {
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
