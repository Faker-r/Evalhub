/**
 * API Client for EvalHub Backend
 */

const API_BASE = '/api';

interface ApiError {
  detail: string | { msg: string }[];
}

export interface OpenRouterProviderSummary {
  name: string;
  slug: string;
  model_count: number;
  privacy_policy_url?: string | null;
  terms_of_service_url?: string | null;
  status_page_url?: string | null;
}

export interface OpenRouterModelSummary {
  id: string;
  name: string;
  description?: string;
  pricing?: Record<string, unknown>;
  context_length?: number;
  canonical_slug?: string;
  architecture?: Record<string, unknown>;
  top_provider?: Record<string, unknown>;
  supported_parameters?: string[];
  per_request_limits?: Record<string, unknown>;
  provider_slugs?: string[];
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

  async createApiKey(providerId: string, apiKey: string) {
    return this.request<{ provider_id: string; provider_name: string }>(
      '/users/api-keys',
      {
        method: 'POST',
        body: JSON.stringify({ provider_id: providerId, api_key: apiKey }),
      }
    );
  }

  async getApiKeys() {
    return this.request<{
      api_key_providers: { provider_id: string; provider_name: string }[];
    }>('/users/api-keys');
  }

  async deleteApiKey(providerId: string) {
    return this.request(`/users/api-keys/${providerId}`, {
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

  async getDatasetPreview(id: number) {
    return this.request<{ samples: any[] }>(`/datasets/${id}/preview`);
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
    model_completion_config: {
      model_name: string;
      model_id: string;
      api_name: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: string;
      api_base?: string;
    };
    judge_config: {
      model_name: string;
      model_id: string;
      api_name: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: string;
      api_base?: string;
    };
  }) {
    return this.request('/evaluations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createTaskEvaluation(data: {
    task_name: string;
    dataset_config: {
      dataset_name: string;
      n_samples?: number;
      n_fewshots?: number;
    };
    model_completion_config: {
      model_name: string;
      model_id: string;
      api_name: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: string;
      api_base?: string;
    };
    judge_config?: {
      model_name: string;
      model_id: string;
      api_name: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: string;
      api_base?: string;
    };
  }) {
    return this.request('/evaluations/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createFlexibleEvaluation(data: {
    dataset_name: string;
    input_field: string;
    output_type: 'text' | 'multiple_choice';
    text_config?: { gold_answer_field?: string };
    mc_config?: { choices_field: string; gold_answer_field: string };
    judge_type: 'llm_as_judge' | 'f1_score' | 'exact_match';
    guideline_names?: string[];
    model_completion_config: {
      model_name: string;
      model_id: string;
      api_name: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: string;
      api_base?: string;
    };
    judge_config?: {
      model_name: string;
      model_id: string;
      api_name: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: string;
      api_base?: string;
    };
  }) {
    return this.request('/evaluations/flexible', {
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
        judge_model_provider: string;
        status: string;
        summary: any;
        created_at: string;
      }[];
    }>('/evaluations/traces');
  }

  async getTrace(traceId: number) {
    return this.request(`/evaluations/traces/${traceId}`);
  }

  async getTraceDetails(traceId: number) {
    return this.request<{
      trace_id: number;
      status: string;
      created_at: string;
      judge_model_provider: string;
      spec: {
        dataset_name?: string;
        task_name?: string;
        completion_model?: string;
        model_provider?: string;
        judge_model?: string;
        guideline_names?: string[];
        sample_count?: number;
        n_fewshots?: number;
        [key: string]: unknown;
      };
    }>(`/evaluations/trace-details/${traceId}`);
  }

  async getTraceSamples(traceId: number) {
    return this.request<{ samples: any[] }>(`/evaluations/traces/${traceId}/samples`);
  }

  async getEvalProgress(traceId: number) {
    return this.request<{ stage: string; percent: number | null; detail: string } | null>(
      `/evaluations/traces/${traceId}/progress`
    );
  }

  // Leaderboard endpoints
  async getLeaderboard() {
    return this.request<{
      datasets: {
        dataset_name: string;
        sample_count: number;
        entries: {
          trace_id: number;
          dataset_name: string;
          completion_model: string;
          model_provider: string;
          judge_model: string;
          scores: {
            metric_name: string;
            mean: number;
            std: number;
            failed: number;
          }[];
          total_failures: number;
          created_at: string;
        }[];
      }[];
    }>('/leaderboard');
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
        repo_type: string | null;
        created_at_hf: string | null;
        private: boolean | null;
        gated: boolean | null;
        files: string[] | null;
        created_at: string;
        updated_at: string;
        default_dataset_size: number | null;
        default_estimated_input_tokens: number | null;
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
      repo_type: string | null;
      created_at_hf: string | null;
      private: boolean | null;
      gated: boolean | null;
      files: string[] | null;
      created_at: string;
      updated_at: string;
    }>(`/benchmarks/${benchmarkId}`);
  }

  async getBenchmarkTasks(benchmarkId: number) {
    return this.request<{
      tasks: {
        id: number;
        benchmark_id: number;
        task_name: string;
        hf_subset: string | null;
        evaluation_splits: string[] | null;
        dataset_size: number | null;
        estimated_input_tokens: number | null;
        created_at: string;
        updated_at: string;
      }[];
    }>(`/benchmarks/${benchmarkId}/tasks`);
  }

  async getTaskDetails(taskName: string) {
    const response = await this.request<{
      task_name: string;
      task_details_nested_dict: Record<string, any> | null;
    }>(`/benchmarks/task-details/${encodeURIComponent(taskName)}`);
    return response.task_details_nested_dict || {};
  }

  // Models and Providers endpoints
  async getProviders(params?: { page?: number; page_size?: number }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

    const query = queryParams.toString();
    return this.request<{
      providers: {
        id: number;
        name: string;
        slug: string | null;
        base_url: string;
        created_at: string;
      }[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
    }>(`/models-and-providers/providers${query ? '?' + query : ''}`);
  }

  async getModels(params?: { page?: number; page_size?: number; provider_id?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.provider_id) queryParams.append('provider_id', params.provider_id);

    const query = queryParams.toString();
    return this.request<{
      models: {
        id: string;
        display_name: string;
        developer: string;
        api_name: string;
        providers: {
          id: string;
          name: string;
          slug: string | null;
          base_url: string;
        }[];
      }[];
      total: number;
      page: number;
      page_size: number;
    }>(`/models-and-providers/models${query ? '?' + query : ''}`);
  }

  // OpenRouter endpoints
  async getOpenRouterModels(params?: {
    limit?: number;
    offset?: number;
    provider_slug?: string;
    search?: string;
    sort?: string;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.limit != null) searchParams.set('limit', String(params.limit));
    if (params?.offset != null) searchParams.set('offset', String(params.offset));
    if (params?.provider_slug) searchParams.set('provider_slug', params.provider_slug);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.sort) searchParams.set('sort', params.sort);
    const q = searchParams.toString();
    return this.request<{
      models: OpenRouterModelSummary[];
      total: number;
    }>(`/models-and-providers/openrouter/models${q ? '?' + q : ''}`);
  }

  async getOpenRouterProviders(params?: { limit?: number; offset?: number; search?: string; sort?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.limit != null) searchParams.set('limit', String(params.limit));
    if (params?.offset != null) searchParams.set('offset', String(params.offset));
    if (params?.search) searchParams.set('search', params.search);
    if (params?.sort) searchParams.set('sort', params.sort);
    const q = searchParams.toString();
    return this.request<{
      providers: OpenRouterProviderSummary[];
      total: number;
    }>(`/models-and-providers/openrouter/providers${q ? '?' + q : ''}`);
  }

  async getOpenRouterModelsByProvider(providerSlug: string) {
    return this.request<{
      models: OpenRouterModelSummary[];
      total: number;
    }>(`/models-and-providers/openrouter/providers/${encodeURIComponent(providerSlug)}/models`);
  }

  async getOpenRouterProvidersByModel(modelId: string) {
    return this.request<{ model_id: string; providers: string[] }>(
      `/models-and-providers/openrouter/models/${encodeURIComponent(modelId)}/providers`
    );
  }

  async getOverlappingDatasets(modelProviderPairs: { model: string; provider: string }[]) {
    return this.request<{ count: number; dataset_names: string[] }>(
      '/evaluation-comparison/overlapping-datasets',
      {
        method: 'POST',
        body: JSON.stringify({ model_provider_pairs: modelProviderPairs }),
      }
    );
  }

  async getSideBySideReport(modelProviderPairs: { model: string; provider: string }[]) {
    return this.request<{
      entries: {
        model: string;
        provider: string;
        dataset_name: string;
        metric_name: string;
        trace_id: number;
        created_at: string;
        score?: number | Record<string, unknown>;
      }[];
      spec_by_trace: Record<string, { id: number; trace_id: number; event_type: string; data: Record<string, unknown>; created_at: string } | null>;
    }>('/evaluation-comparison/side-by-side-report', {
      method: 'POST',
      body: JSON.stringify({ model_provider_pairs: modelProviderPairs }),
    });
  }

  // Health check
  async health() {
    return this.request<{ status: string }>('/health');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
