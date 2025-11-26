import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// API Base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// ============================================================================
// Type Definitions for API Responses
// ============================================================================

// Authentication Types
export interface LoginRequest {
  username: string; // FastAPI OAuth2PasswordRequestForm uses 'username' field
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  email: string;
  created_at: string;
  updated_at?: string;
}

// Panel Types
export interface Panel {
  id: number;
  key: string;
  display_name: string;
}

export interface PanelsResponse {
  panels: Panel[];
}

// Test Types
export interface TestType {
  id: number;
  key: string;
  display_name: string;
  unit: string;
  ref_low: number | null;
  ref_high: number | null;
  panel_id: number;
}

export interface PanelTestsResponse {
  panel_key: string;
  panel_display_name: string;
  tests: TestType[];
}

// Test Result Types
export interface TestResult {
  id: number;
  value: number;
  unit: string;
  status: string;
  created_at: string;
  confidence?: number;
}

export interface TestHistoryResponse {
  test_key: string;
  display_name: string;
  unit: string;
  panel_key: string;
  data: TestResult[];
}

// Insight Types
export interface Guidance {
  message: string;
  trend: string | null;
  suggestions: string[];
  disclaimer: string;
}

export interface LatestInsight {
  test_key: string;
  display_name: string;
  unit: string;
  panel_key: string;
  latest: TestResult | null;
  previous: TestResult | null;
  guidance: Guidance | null;
}

// Report Upload Types
export interface ParsedTest {
  test_name: string;
  value: number;
  unit: string;
  status: string;
}

export interface UploadReportResponse {
  report_id: number;
  filename: string;
  uploaded_at: string;
  parsed_success: boolean;
  parsed_tests: ParsedTest[];
  message: string;
}

// Error Response Type
export interface ErrorResponse {
  detail: string;
}
