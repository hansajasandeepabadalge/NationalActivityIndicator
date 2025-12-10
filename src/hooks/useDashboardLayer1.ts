/**
 * React Hooks for Layer 1 (Data Collection) Dashboard
 * 
 * Custom hooks for fetching and managing Layer 1 data with SWR for caching and revalidation
 */

import useSWR from 'swr';
import {
    getDataSources,
    getScrapingJobs,
    getRawArticles,
    getPipelineStatus,
    retryScrapingJob,
    type DataSource,
    type ScrapingJob,
    type RawArticle,
    type PipelineStage,
} from '@/lib/api/dashboard-layer1';

/**
 * Hook to fetch all data sources
 * Refreshes every 30 seconds
 */
export function useDataSources() {
    const { data, error, isLoading, mutate } = useSWR<DataSource[]>(
        '/api/admin/sources',
        getDataSources,
        {
            refreshInterval: 30000, // Refresh every 30 seconds
            revalidateOnFocus: true,
        }
    );

    return {
        data,
        error: error?.message,
        isLoading,
        refresh: mutate,
    };
}

/**
 * Hook to fetch scraping jobs
 * Refreshes every 10 seconds to show live job status
 */
export function useScrapingJobs(limit: number = 50) {
    const { data, error, isLoading, mutate } = useSWR<ScrapingJob[]>(
        `/api/admin/scraping-jobs?limit=${limit}`,
        () => getScrapingJobs(limit),
        {
            refreshInterval: 10000, // Refresh every 10 seconds
            revalidateOnFocus: true,
        }
    );

    return {
        data,
        error: error?.message,
        isLoading,
        refresh: mutate,
    };
}

/**
 * Hook to fetch raw articles
 * Refreshes every 30 seconds
 */
export function useRawArticles(source?: string, limit: number = 50) {
    const { data, error, isLoading, mutate } = useSWR<RawArticle[]>(
        `/api/admin/raw-articles?source=${source || 'all'}&limit=${limit}`,
        () => getRawArticles({ source, limit }),
        {
            refreshInterval: 30000, // Refresh every 30 seconds
            revalidateOnFocus: true,
        }
    );

    return {
        data,
        error: error?.message,
        isLoading,
        refresh: mutate,
    };
}

/**
 * Hook to fetch pipeline status
 * Refreshes every 60 seconds
 */
export function usePipelineStatus() {
    const { data, error, isLoading, mutate } = useSWR<PipelineStage[]>(
        '/api/admin/pipeline-status',
        getPipelineStatus,
        {
            refreshInterval: 60000, // Refresh every 60 seconds
            revalidateOnFocus: true,
        }
    );

    return {
        data,
        error: error?.message,
        isLoading,
        refresh: mutate,
    };
}

/**
 * Hook to retry a scraping job
 * Returns a function that can be called to retry a job
 */
export function useRetryScrapingJob() {
    const { mutate: refreshJobs } = useScrapingJobs();

    const retry = async (jobId: string) => {
        try {
            const result = await retryScrapingJob(jobId);

            if (result.success) {
                // Refresh the jobs list after successful retry
                await refreshJobs();
            }

            return result;
        } catch (error) {
            console.error('Error retrying job:', error);
            return { success: false, message: 'Failed to retry job' };
        }
    };

    return { retry };
}
