/**
 * API Client for Layer 1 (Data Collection) Dashboard
 * 
 * These functions will call backend API endpoints once they are implemented.
 * Currently returns mock data for frontend development.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

// Data Source Types
export interface DataSource {
    id: number;
    name: string;
    display_name: string;
    source_type: 'news' | 'government' | 'social_media' | 'api';
    status: 'active' | 'inactive' | 'error';
    base_url: string;
    last_scraped?: string;
    total_articles: number;
    articles_24h: number;
    success_rate: number;
    avg_articles_per_scrape: number;
}

export interface ScrapingJob {
    job_id: string;
    source_name: string;
    status: 'running' | 'completed' | 'failed' | 'pending';
    start_time: string;
    end_time?: string;
    duration_seconds?: number;
    articles_found: number;
    articles_processed: number;
    error_message?: string;
}

export interface RawArticle {
    article_id: string;
    title: string;
    source_name: string;
    source_url: string;
    scraped_at: string;
    publish_date?: string;
    author?: string;
    word_count?: number;
    language?: string;
}

export interface PipelineStage {
    name: string;
    count: number;
    processing_rate: number;
    success_rate: number;
    error_count: number;
    avg_processing_time: number;
}

/**
 * Get all data sources with their current status
 * Backend endpoint: GET /api/admin/sources
 */
export async function getDataSources(): Promise<DataSource[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/sources`, {
            headers: {
                'Content-Type': 'application/json',
                // Add auth token when authentication is implemented
                // 'Authorization': `Bearer ${token}`
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching data sources:', error);
        // Return empty array on error - components will handle empty state
        return [];
    }
}

/**
 * Get recent scraping jobs
 * Backend endpoint: GET /api/admin/scraping-jobs?limit={limit}
 */
export async function getScrapingJobs(limit: number = 50): Promise<ScrapingJob[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/scraping-jobs?limit=${limit}`, {
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching scraping jobs:', error);
        return [];
    }
}

/**
 * Get raw articles stream
 * Backend endpoint: GET /api/admin/raw-articles?source={source}&limit={limit}
 */
export async function getRawArticles(params: {
    source?: string;
    limit?: number;
}): Promise<RawArticle[]> {
    try {
        const queryParams = new URLSearchParams();
        if (params.source) queryParams.append('source', params.source);
        if (params.limit) queryParams.append('limit', params.limit.toString());

        const response = await fetch(
            `${API_BASE_URL}/admin/raw-articles?${queryParams.toString()}`,
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching raw articles:', error);
        return [];
    }
}

/**
 * Get processing pipeline status
 * Backend endpoint: GET /api/admin/pipeline-status
 */
export async function getPipelineStatus(): Promise<PipelineStage[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/pipeline-status`, {
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching pipeline status:', error);
        return [];
    }
}

/**
 * Retry a failed scraping job
 * Backend endpoint: POST /api/admin/scraping-jobs/{jobId}/retry
 */
export async function retryScrapingJob(jobId: string): Promise<{ success: boolean; message: string }> {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/scraping-jobs/${jobId}/retry`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error retrying scraping job:', error);
        return { success: false, message: 'Failed to retry job' };
    }
}
