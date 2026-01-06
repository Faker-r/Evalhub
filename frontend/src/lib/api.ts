/**
 * API Client for EvalHub Backend
 */

const API_BASE = '/api';

interface ApiError {
  detail: string | { msg: string }[];
}

class ApiClient {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage on initialization
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      ...options.headers,
    };

    // Add auth token if available
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    // Add Content-Type for JSON bodies
    if (options.body && typeof options.body === 'string') {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: 'An error occurred',
      }));
      throw new Error(
        typeof error.detail === 'string'
          ? error.detail
          : error.detail[0]?.msg || 'Request failed'
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth endpoints
  async register(email: string, password: string) {
    return this.request<{ id: number; email: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await this.request<{
      access_token: string;
      token_type: string;
    }>('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    this.setToken(response.access_token);
    return response;
  }

  logout() {
    this.setToken(null);
  }

  // User endpoints
  async getCurrentUser() {
    return this.request<{ id: number; email: string }>('/users/me');
  }

  async createApiKey(provider: string, apiKey: string) {
    return this.request<{ provider: string }>('/users/api-keys', {
      method: 'POST',
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
  }

  async getApiKeys() {
    return this.request<{
      api_key_providers: { provider: string }[];
    }>('/users/api-keys');
  }

  async deleteApiKey(provider: string) {
    return this.request(`/users/api-keys/${provider}`, {
      method: 'DELETE',
    });
  }

  // Dataset endpoints
  async createDataset(name: string, category: string, file: File) {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('category', category);
    formData.append('file', file);

    const headers: HeadersInit = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}/datasets`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create dataset');
    }

    return response.json();
  }

  async getDatasets() {
    return this.request<{
      datasets: {
        id: number;
        name: string;
        category: string;
        sample_count: number;
      }[];
    }>('/datasets');
  }

  // Guideline endpoints
  async createGuideline(data: {
    name: string;
    prompt: string;
    category: string;
    max_score: number;
  }) {
    return this.request<{
      id: number;
      name: string;
      prompt: string;
      category: string;
      max_score: number;
    }>('/guidelines', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getGuidelines() {
    return this.request<{
      guidelines: {
        id: number;
        name: string;
        prompt: string;
        category: string;
        max_score: number;
      }[];
    }>('/guidelines');
  }

  // Evaluation endpoints
  async createEvaluation(data: {
    dataset_name: string;
    guideline_names: string[];
    completion_model: string;
    model_provider: string;
    judge_model: string;
    api_base?: string;
  }) {
    return this.request('/evaluations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTraces() {
    return this.request<{
      traces: {
        id: number;
        user_id: number;
        dataset_name: string;
        guideline_names: string[];
        completion_model: string;
        model_provider: string;
        judge_model: string;
        status: string;
        summary: any;
        created_at: string;
      }[];
    }>('/evaluations/traces');
  }

  async getTrace(traceId: number) {
    return this.request(`/evaluations/traces/${traceId}`);
  }

  // Health check
  async health() {
    return this.request<{ status: string }>('/health');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

