/**
 * API Configuration
 * 
 * Central configuration for backend API connection.
 */

export const API_CONFIG = {
  // Base URL for the backend API
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1',
  
  // Token storage keys
  ACCESS_TOKEN_KEY: 'nai_access_token',
  REFRESH_TOKEN_KEY: 'nai_refresh_token',
  
  // Token expiry buffer (refresh 5 minutes before expiry)
  TOKEN_REFRESH_BUFFER: 5 * 60 * 1000, // 5 minutes in ms
};

export default API_CONFIG;
