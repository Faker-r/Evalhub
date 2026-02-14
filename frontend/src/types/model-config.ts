export interface ModelConfig {
  // For standard providers
  provider_id?: string;
  provider_name?: string;
  provider_slug?: string;
  model_id?: string;
  model_name?: string;
  model_developer?: string;
  api_name?: string;
  api_base?: string;
  model_providers?: Array<{
    id: string;
    name: string;
    slug?: string | null;
    base_url: string;
  }>;

  // For OpenRouter
  is_openrouter?: boolean;
  openrouter_model_id?: string;
  openrouter_model_name?: string;
  openrouter_model_description?: string;
  openrouter_model_pricing?: Record<string, unknown>;
  openrouter_model_context_length?: number;
  openrouter_model_canonical_slug?: string;
  openrouter_model_architecture?: Record<string, unknown>;
  openrouter_model_top_provider?: Record<string, unknown>;
  openrouter_model_supported_parameters?: string[];
  openrouter_model_per_request_limits?: Record<string, unknown>;
  openrouter_model_provider_slugs?: string[];
  openrouter_provider_slug?: string;
  openrouter_provider_name?: string;
}
