/**
 * API Client for EvalHub Backend
 */

const API_BASE = '/api';

interface ApiError {
  detail: string | { msg: string }[];
}

type OpenRouterModel = {
  id: string;
  name: string;
  description?: string;
  pricing?: unknown;
  context_length?: number;
  canonical_slug?: string;
  top_provider?: unknown;
};

type OpenRouterProvider = {
  name: string;
  slug: string;
  privacy_policy_url?: string | null;
  terms_of_service_url?: string | null;
  status_page_url?: string | null;
};

type OpenRouterModelsResponse = { data: OpenRouterModel[] };
type OpenRouterProvidersResponse = { data: OpenRouterProvider[] };
type OpenRouterModelEndpointsResponse = {
  data: {
    endpoints: {
      provider_name?: string;
    }[];
  };
};

class ApiClient {
  private token: string | null = null;
  private openRouterHostedModelsByProviderSlugPromise: Promise<
    Record<string, OpenRouterModel[]>
  > | null = null;

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

  private async getOpenRouterHostedModelsByProviderSlug(): Promise<Record<string, OpenRouterModel[]>> {
    if (!this.openRouterHostedModelsByProviderSlugPromise) {
      this.openRouterHostedModelsByProviderSlugPromise = (async () => {
        const [providersResp, modelsResp] = await Promise.all([
          fetch('https://openrouter.ai/api/v1/providers'),
          fetch('https://openrouter.ai/api/v1/models'),
        ]);
        if (!providersResp.ok) throw new Error('Failed to fetch OpenRouter providers');
        if (!modelsResp.ok) throw new Error('Failed to fetch OpenRouter models');

        const providersJson = (await providersResp.json()) as OpenRouterProvidersResponse;
        const modelsJson = (await modelsResp.json()) as OpenRouterModelsResponse;

        const normalize = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, '');

        const slugByNormalizedName: Record<string, string> = {};
        for (const p of providersJson.data) {
          slugByNormalizedName[normalize(p.name)] = p.slug;
          slugByNormalizedName[normalize(p.slug)] = p.slug;
        }

        const modelIdsByProviderSlug: Record<string, Set<string>> = {};

        await Promise.all(
          modelsJson.data.map(async (m) => {
            const modelId = m.id;
            const [author, slug] = modelId.split('/', 2);
            if (!author || !slug) return;

            const resp = await fetch(
              `https://openrouter.ai/api/v1/models/${encodeURIComponent(
                author
              )}/${encodeURIComponent(slug)}/endpoints`
            );
            if (!resp.ok) return;

            const json = (await resp.json()) as OpenRouterModelEndpointsResponse;
            for (const endpoint of json.data.endpoints) {
              const providerName = endpoint.provider_name;
              if (!providerName) continue;
              const providerSlug = slugByNormalizedName[normalize(providerName)];
              if (!providerSlug) continue;
              (modelIdsByProviderSlug[providerSlug] ||= new Set()).add(modelId);
            }
          })
        );

        const modelById: Record<string, OpenRouterModel> = {};
        for (const m of modelsJson.data) modelById[m.id] = m;

        const modelsByProviderSlug: Record<string, OpenRouterModel[]> = {};
        for (const [providerSlug, ids] of Object.entries(modelIdsByProviderSlug)) {
          modelsByProviderSlug[providerSlug] = Array.from(ids)
            .map((id) => modelById[id])
            .filter(Boolean);
        }

        return modelsByProviderSlug;
      })();
    }

    return this.openRouterHostedModelsByProviderSlugPromise;
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

  async createApiKey(providerId: number, apiKey: string) {
    return this.request<{ provider_id: number; provider_name: string }>(
      '/users/api-keys',
      {
      method: 'POST',
        body: JSON.stringify({ provider_id: providerId, api_key: apiKey }),
      }
    );
  }

  async getApiKeys() {
    return this.request<{
      api_key_providers: { provider_id: number; provider_name: string }[];
    }>('/users/api-keys');
  }

  async deleteApiKey(providerId: number) {
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
      model_slug: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: number;
      api_base?: string;
    };
    judge_config: {
      model_name: string;
      model_id: string;
      model_slug: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: number;
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
      model_slug: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: number;
      api_base?: string;
    };
    judge_config?: {
      model_name: string;
      model_id: string;
      model_slug: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: number;
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
      model_slug: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: number;
      api_base?: string;
    };
    judge_config?: {
      model_name: string;
      model_id: string;
      model_slug: string;
      model_provider: string;
      model_provider_slug: string;
      model_provider_id: number;
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

  async getModels(params?: { page?: number; page_size?: number; provider_id?: number }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.provider_id) queryParams.append('provider_id', params.provider_id.toString());

    const query = queryParams.toString();
    return this.request<{
      models: {
        id: number;
        display_name: string;
        developer: string;
        api_name: string;
        slug: string | null;
        providers: {
          id: number;
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
  async getOpenRouterModels() {
    const response = await fetch('https://openrouter.ai/api/v1/models');
    if (!response.ok) throw new Error('Failed to fetch OpenRouter models');

    const json = (await response.json()) as OpenRouterModelsResponse;
    return {
      models: json.data.map((m) => ({
        id: m.id,
        name: m.name,
        description: m.description,
        pricing: m.pricing,
        context_length: m.context_length,
      })),
    };
  }

  async getOpenRouterProviders() {
    const providersResp = await fetch('https://openrouter.ai/api/v1/providers');
    if (!providersResp.ok) throw new Error('Failed to fetch OpenRouter providers');
    const providersJson = (await providersResp.json()) as OpenRouterProvidersResponse;

    const hostedModelsByProviderSlug = await this.getOpenRouterHostedModelsByProviderSlug();
    const providers = providersJson.data
      .map((p) => ({
        name: p.name,
        slug: p.slug,
        model_count: hostedModelsByProviderSlug[p.slug]?.length || 0,
      }))
      .filter((p) => p.model_count > 0)
      .sort((a, b) => b.model_count - a.model_count);
    return {
      providers,
    };
  }

  async getOpenRouterModelsByProvider(providerName: string) {
    const hostedModelsByProviderSlug = await this.getOpenRouterHostedModelsByProviderSlug();
    const models = (hostedModelsByProviderSlug[providerName] || []).map((m) => ({
      id: m.id,
      name: m.name,
      description: m.description,
      pricing: m.pricing,
      context_length: m.context_length,
    }));

    return { models };
  }

  async getOpenRouterProvidersByModel(modelId: string) {
    const [author, slug] = modelId.split('/', 2);
    if (!author || !slug) return { model_id: modelId, providers: [] };

    const response = await fetch(
      `https://openrouter.ai/api/v1/models/${encodeURIComponent(author)}/${encodeURIComponent(
        slug
      )}/endpoints`
    );
    if (!response.ok) return { model_id: modelId, providers: [] };

    const json = (await response.json()) as OpenRouterModelEndpointsResponse;
    return {
      model_id: modelId,
      providers: json.data.endpoints
        .map((e) => e.provider_name)
        .filter((x): x is string => Boolean(x)),
    };
  }

  // Health check
  async health() {
    return this.request<{ status: string }>('/health');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

