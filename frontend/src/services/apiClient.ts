import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

// Environment variable for API URL (fallback for dev)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Defined API Error Interface
export interface ApiError {
  message: string;
  code?: string;
  field?: string;
}

class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 120000, // 2 minutes for slow model loading/generation
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request Interceptor: Attach Token
    this.instance.interceptors.request.use(
      (config) => {
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('auth_token');
          console.log('[API Client] Token from localStorage:', token ? token.substring(0, 50) + '...' : 'NO TOKEN');
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('[API Client] Authorization header set:', config.headers.Authorization.substring(0, 70) + '...');
          } else {
            console.warn('[API Client] No token found in localStorage!');
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response Interceptor: Handle Errors (401, etc.)
    this.instance.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const customError: ApiError = {
          message: 'An unexpected error occurred',
        };

        if (error.response) {
          // Server responded with non-2xx code
          if (error.response.status === 401) {
            // Handle unauthorized (redirect to login or refresh token)
            // For now, we will just let the app handle the redirect
            if (typeof window !== 'undefined') {
              // event bus or callback could go here
            }
          }
          // Handle various response data formats
          if (typeof error.response.data === 'string') {
            customError.message = error.response.data;
          } else if (error.response.data && typeof error.response.data === 'object') {
            customError.message = (error.response.data as any)?.message || (error.response.data as any)?.detail || JSON.stringify(error.response.data);
          } else {
            customError.message = error.message || 'Server error';
          }
        } else if (error.request) {
          // Request made but no response
          customError.message = 'Network Error. Please check your connection.';
        } else {
          // Something else happened
          customError.message = error.message || 'Request failed';
        }

        return Promise.reject(customError);
      }
    );
  }

  // Generic request wrappers
  public get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get<T>(url, config)
      .then((res) => res.data)
      .catch((error) => {
        console.error(`GET request failed: ${url}`, error.response || error.message || error);
        throw error;
      });
  }

  public post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post<T>(url, data, config)
      .then((res) => res.data)
      .catch((error) => {
        console.error(`POST request failed: ${url}`, error.response || error.message || error);
        throw error;
      });
  }

  public put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put<T>(url, data, config)
      .then((res) => res.data)
      .catch((error) => {
        console.error(`PUT request failed: ${url}`, error.response || error.message || error);
        throw error;
      });
  }

  public delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete<T>(url, config)
      .then((res) => res.data)
      .catch((error) => {
        console.error(`DELETE request failed: ${url}`, error.response || error.message || error);
        throw error;
      });
  }

  // Expose instance for specific needs
  public getAxiosInstance() {
    return this.instance;
  }
}

export const apiClient = new ApiClient();
