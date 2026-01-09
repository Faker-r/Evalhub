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
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
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
    const response = await this.request<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
      user_id: string;
      email: string;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
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
    scoring_scale: string;
    scoring_scale_config: any;
  }) {
    return this.request<{
      id: number;
      name: string;
      prompt: string;
      category: string;
      scoring_scale: string;
      scoring_scale_config: any;
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
        scoring_scale: string;
        scoring_scale_config: any;
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
    judge_model_provider: string;
    api_base?: string;
    judge_api_base?: string;
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

  // Leaderboard endpoints
  async getLeaderboard(datasetName: string) {
    return this.request<{
      dataset_name: string;
      sample_count: number;
      entries: {
        trace_id: number;
        completion_model: string;
        model_provider: string;
        judge_model: string;
        scores: {
          guideline_name: string;
          mean: number;
          max_score: number;
          normalized: number;
          failed: number;
        }[];
        total_failures: number;
        normalized_avg_score: number;
        created_at: string;
      }[];
    }>(`/leaderboard?dataset_name=${encodeURIComponent(datasetName)}`);
  }

  // Benchmark endpoints
  async getBenchmarks(params?: {
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    tags?: string[];
    author?: string;
    search?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params?.tags) {
        params.tags.forEach(tag => queryParams.append('tag', tag));
    }
    if (params?.author) queryParams.append('author', params.author);
    if (params?.search) queryParams.append('search', params.search);

    const query = queryParams.toString();
    return this.request<{
      benchmarks: {
        id: number;
        tasks: string[] | null;
        dataset_name: string;
        hf_repo: string;
        description: string | null;
        author: string | null;
        downloads: number | null;
        tags: string[] | null;
        estimated_input_tokens: number | null;
        repo_type: string | null;
        created_at_hf: string | null;
        private: boolean | null;
        gated: boolean | null;
        files: string[] | null;
        created_at: string;
        updated_at: string;
      }[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
    }>(`/benchmarks${query ? '?' + query : ''}`);
  }

  async getBenchmark(benchmarkId: number) {
    return this.request<{
      id: number;
      tasks: string[] | null;
      dataset_name: string;
      hf_repo: string;
      description: string | null;
      author: string | null;
      downloads: number | null;
      tags: string[] | null;
      estimated_input_tokens: number | null;
      repo_type: string | null;
      created_at_hf: string | null;
      private: boolean | null;
      gated: boolean | null;
      files: string[] | null;
      created_at: string;
      updated_at: string;
    }>(`/benchmarks/${benchmarkId}`);
  }

  // Health check
  async health() {
    return this.request<{ status: string }>('/health');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

