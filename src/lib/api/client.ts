/**
 * API Client
 * 
 * Core HTTP client for communicating with the backend API.
 * Handles token management, authentication, and request/response processing.
 */

import { API_CONFIG } from './config';
import type { TokenResponse, ApiError } from './types';

class ApiClient {
  private baseUrl: string;
  
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }
  
  // ============== Token Management ==============
  
  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(API_CONFIG.ACCESS_TOKEN_KEY);
  }
  
  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(API_CONFIG.REFRESH_TOKEN_KEY);
  }
  
  setTokens(tokens: TokenResponse): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(API_CONFIG.ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(API_CONFIG.REFRESH_TOKEN_KEY, tokens.refresh_token);
  }
  
  clearTokens(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(API_CONFIG.ACCESS_TOKEN_KEY);
    localStorage.removeItem(API_CONFIG.REFRESH_TOKEN_KEY);
  }
  
  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
  
  // ============== HTTP Methods ==============
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    requiresAuth: boolean = true
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    // Add auth header if required
    if (requiresAuth) {
      const token = this.getAccessToken();
      if (token) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
      }
    }
    
    const config: RequestInit = {
      ...options,
      headers,
    };
    
    try {
      const response = await fetch(url, config);
      
      // Handle 401 - try to refresh token
      if (response.status === 401 && requiresAuth) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Retry with new token
          const newToken = this.getAccessToken();
          (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
          const retryResponse = await fetch(url, { ...config, headers });
          if (!retryResponse.ok) {
            throw await this.handleError(retryResponse);
          }
          return retryResponse.json();
        } else {
          // Refresh failed, clear tokens
          this.clearTokens();
          throw { detail: 'Session expired. Please login again.', status: 401 } as ApiError;
        }
      }
      
      if (!response.ok) {
        throw await this.handleError(response);
      }
      
      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }
      
      return response.json();
    } catch (error) {
      if ((error as ApiError).detail) {
        throw error;
      }
      throw { detail: 'Network error. Please check your connection.', status: 0 } as ApiError;
    }
  }
  
  private async handleError(response: Response): Promise<ApiError> {
    try {
      const data = await response.json();
      return { detail: data.detail || 'An error occurred', status: response.status };
    } catch {
      return { detail: response.statusText || 'An error occurred', status: response.status };
    }
  }
  
  private async refreshToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;
    
    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!response.ok) return false;
      
      const tokens: TokenResponse = await response.json();
      this.setTokens(tokens);
      return true;
    } catch {
      return false;
    }
  }
  
  // ============== Public API Methods ==============
  
  async get<T>(endpoint: string, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, requiresAuth);
  }
  
  async post<T>(endpoint: string, data?: unknown, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }, requiresAuth);
  }
  
  async put<T>(endpoint: string, data?: unknown, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }, requiresAuth);
  }
  
  async delete<T>(endpoint: string, requiresAuth: boolean = true): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' }, requiresAuth);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
