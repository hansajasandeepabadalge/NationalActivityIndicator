/**
 * Auth Service
 * 
 * Handles authentication operations: login, logout, registration, etc.
 */

import { apiClient } from './client';
import type {
  UserLogin,
  UserCreate,
  TokenResponse,
  UserResponse,
  PasswordChange,
} from './types';

export const authService = {
  /**
   * Login with email and password
   */
  async login(credentials: UserLogin): Promise<TokenResponse> {
    const tokens = await apiClient.post<TokenResponse>('/auth/login', credentials, false);
    apiClient.setTokens(tokens);
    return tokens;
  },
  
  /**
   * Register a new user
   */
  async register(userData: UserCreate): Promise<UserResponse> {
    return apiClient.post<UserResponse>('/auth/register', userData, false);
  },
  
  /**
   * Register a new admin (requires admin auth)
   */
  async registerAdmin(userData: UserCreate): Promise<UserResponse> {
    return apiClient.post<UserResponse>('/auth/register/admin', userData);
  },
  
  /**
   * Get current user profile
   */
  async getMe(): Promise<UserResponse> {
    return apiClient.get<UserResponse>('/auth/me');
  },
  
  /**
   * Logout the current user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      apiClient.clearTokens();
    }
  },
  
  /**
   * Change password
   */
  async changePassword(data: PasswordChange): Promise<void> {
    await apiClient.post('/auth/change-password', data);
  },
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return apiClient.isAuthenticated();
  },
  
  /**
   * Clear tokens (local logout)
   */
  clearAuth(): void {
    apiClient.clearTokens();
  },
};

export default authService;
