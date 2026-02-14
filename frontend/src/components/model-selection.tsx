/**
 * ModelSelection Component
 *
 * Multi-step model selection supporting:
 * 1. Standard Providers (from database)
 * 2. OpenRouter (by provider or by model)
 */

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';

interface ModelConfig {
  // For standard providers
  provider_id?: string;
  provider_name?: string;
  provider_slug?: string;
  model_id?: string;
  model_name?: string;
  api_name?: string;
  api_base?: string;

  // For OpenRouter
  is_openrouter?: boolean;
  openrouter_model_id?: string;
  openrouter_model_name?: string;
  openrouter_provider_slug?: string;
  openrouter_provider_name?: string;
}

interface ModelSelectionProps {
  value: ModelConfig;
  onChange: (value: ModelConfig) => void;
  label?: string;
}

type ApiSource = 'standard' | 'openrouter';
type OpenRouterTab = 'by-provider' | 'by-model';

export function ModelSelection({ value, onChange, label = 'Model Selection' }: ModelSelectionProps) {
  // Derive API source from value prop
  const apiSource: ApiSource = value.is_openrouter ? 'openrouter' : 'standard';
  const [openRouterTab, setOpenRouterTab] = useState<OpenRouterTab>('by-provider');

  // Standard providers state
  const [standardProviders, setStandardProviders] = useState<any[]>([]);
  const [standardModels, setStandardModels] = useState<any[]>([]);

  // OpenRouter state
  const [openRouterProviders, setOpenRouterProviders] = useState<any[]>([]);
  const [openRouterModels, setOpenRouterModels] = useState<any[]>([]);
  const [openRouterProvidersByModel, setOpenRouterProvidersByModel] = useState<any[]>([]);

  // Loading states
  const [loadingStandardProviders, setLoadingStandardProviders] = useState(false);
  const [loadingStandardModels, setLoadingStandardModels] = useState(false);
  const [loadingOpenRouterProviders, setLoadingOpenRouterProviders] = useState(false);
  const [loadingOpenRouterModels, setLoadingOpenRouterModels] = useState(false);
  const [loadingOpenRouterProvidersByModel, setLoadingOpenRouterProvidersByModel] = useState(false);

  // Fetch standard providers on mount
  useEffect(() => {
    if (apiSource === 'standard') {
      fetchStandardProviders();
    }
  }, [apiSource]);

  // Fetch OpenRouter providers on mount
  useEffect(() => {
    if (apiSource === 'openrouter') {
      fetchOpenRouterProviders();
    }
  }, [apiSource]);

  // Fetch all OpenRouter models when selecting by model
  useEffect(() => {
    if (apiSource === 'openrouter' && openRouterTab === 'by-model') {
      fetchAllOpenRouterModels();
    }
  }, [apiSource, openRouterTab]);

  // Fetch standard models when provider changes
  useEffect(() => {
    if (value.provider_id && !value.is_openrouter) {
      fetchStandardModels(value.provider_id);
    }
  }, [value.provider_id]);

  // Fetch OpenRouter models when provider changes
  useEffect(() => {
    if (value.openrouter_provider_slug && openRouterTab === 'by-provider' && value.is_openrouter) {
      fetchOpenRouterModelsByProvider(value.openrouter_provider_slug);
    }
  }, [value.openrouter_provider_slug, openRouterTab]);

  // Fetch providers by model when OpenRouter model changes
  useEffect(() => {
    if (value.openrouter_model_id && openRouterTab === 'by-model' && value.is_openrouter) {
      fetchOpenRouterProvidersByModel(value.openrouter_model_id);
    }
  }, [value.openrouter_model_id, openRouterTab]);

  const fetchStandardProviders = async () => {
    setLoadingStandardProviders(true);
    try {
      const response = await apiClient.getProviders({ page_size: 100 });
      setStandardProviders(response.providers.filter((p) => p.name !== 'OpenRouter'));
    } catch (error) {
      toast.error('Failed to load providers');
      console.error('Error fetching standard providers:', error);
    } finally {
      setLoadingStandardProviders(false);
    }
  };

  const fetchStandardModels = async (providerId: string) => {
    setLoadingStandardModels(true);
    try {
      const response = await apiClient.getModels({ provider_id: providerId, page_size: 100 });
      setStandardModels(response.models);
    } catch (error) {
      toast.error('Failed to load models');
      console.error('Error fetching standard models:', error);
    } finally {
      setLoadingStandardModels(false);
    }
  };

  const fetchOpenRouterProviders = async () => {
    setLoadingOpenRouterProviders(true);
    try {
      const response = await apiClient.getOpenRouterProviders();
      setOpenRouterProviders(response.providers);
    } catch (error) {
      toast.error('Failed to load OpenRouter providers. Check if API key is configured.');
      console.error('Error fetching OpenRouter providers:', error);
    } finally {
      setLoadingOpenRouterProviders(false);
    }
  };

  const fetchAllOpenRouterModels = async () => {
    setLoadingOpenRouterModels(true);
    try {
      const response = await apiClient.getOpenRouterModels();
      const modelsWithProviderCounts = await Promise.all(
        response.models.map(async (model) => {
          try {
            const providerResponse = await apiClient.getOpenRouterProvidersByModel(model.id);
            return { ...model, providerCount: providerResponse.providers.length };
          } catch {
            return { ...model, providerCount: 0 };
          }
        })
      );
      const sortedModels = modelsWithProviderCounts.sort((a, b) => b.providerCount - a.providerCount);
      setOpenRouterModels(sortedModels);
    } catch (error) {
      toast.error('Failed to load OpenRouter models. Check if API key is configured.');
      console.error('Error fetching OpenRouter models:', error);
    } finally {
      setLoadingOpenRouterModels(false);
    }
  };

  const fetchOpenRouterModelsByProvider = async (providerSlug: string) => {
    setLoadingOpenRouterModels(true);
    try {
      const response = await apiClient.getOpenRouterModelsByProvider(providerSlug);
      setOpenRouterModels(response.models);
    } catch (error) {
      toast.error('Failed to load models for provider');
      console.error('Error fetching OpenRouter models by provider:', error);
    } finally {
      setLoadingOpenRouterModels(false);
    }
  };

  const fetchOpenRouterProvidersByModel = async (modelId: string) => {
    setLoadingOpenRouterProvidersByModel(true);
    try {
      const [providersResponse, providerNamesResponse] = await Promise.all([
        apiClient.getOpenRouterProviders(),
        apiClient.getOpenRouterProvidersByModel(modelId),
      ]);
      
      const providerNameToSlug = new Map(
        providersResponse.providers.map((p) => [p.name, p.slug])
      );
      
      const providerSlugs = providerNamesResponse.providers
        .map((name) => providerNameToSlug.get(name))
        .filter((slug): slug is string => Boolean(slug));
      
      setOpenRouterProvidersByModel(providerSlugs);
    } catch (error) {
      console.error('Error fetching OpenRouter providers by model:', error);
      setOpenRouterProvidersByModel([]);
    } finally {
      setLoadingOpenRouterProvidersByModel(false);
    }
  };

  const handleStandardProviderChange = (providerId: string) => {
    const provider = standardProviders.find((p) => p.id === providerId);

    if (provider) {
      onChange({
        provider_id: provider.id,
        provider_name: provider.name,
        provider_slug: provider.slug ?? undefined,
        is_openrouter: false,
      });
    }
    setStandardModels([]);
  };

  const handleStandardModelChange = (modelId: string) => {
    const model = standardModels.find((m) => m.id === modelId);

    if (model) {
      // Find the provider for this model from the model's providers array
      const provider = model.providers.find((p: any) => p.id === value.provider_id);

      if (provider) {
        onChange({
          provider_id: provider.id,
          provider_name: provider.name,
          provider_slug: provider.slug ?? undefined,
          model_id: model.id,
          model_name: model.display_name,
          api_name: model.api_name,
          api_base: provider.base_url,
          is_openrouter: false,
        });
      }
    }
  };

  const handleOpenRouterProviderChange = (providerSlug: string) => {
    const provider = openRouterProviders.find((p) => p.slug === providerSlug);
    onChange({
      is_openrouter: true,
      openrouter_provider_slug: providerSlug,
      openrouter_provider_name: provider?.name,
    });
    setOpenRouterModels([]);
  };

  const handleOpenRouterModelChange = (modelId: string) => {
    // Find the model to get its name
    const model = openRouterModels.find((m) => m.id === modelId);

    // Set the config for OpenRouter
    onChange({
      is_openrouter: true,
      openrouter_model_id: modelId,
      openrouter_model_name: model?.name || modelId,
      openrouter_provider_slug: openRouterTab === 'by-provider' ? value.openrouter_provider_slug : undefined,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
        <CardDescription>Select the model configuration for this evaluation</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Step 1: API Source Selection */}
        <div className="space-y-3">
          <Label>API Source</Label>
          <RadioGroup
            value={apiSource}
            onValueChange={(val) => {
              // Reset config when switching API source
              if (val === 'openrouter') {
                onChange({ is_openrouter: true });
              } else {
                onChange({ is_openrouter: false });
              }
            }}
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="standard" id={`standard-${label}`} />
              <Label htmlFor={`standard-${label}`} className="font-normal cursor-pointer">
                Standard Providers
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="openrouter" id={`openrouter-${label}`} />
              <Label htmlFor={`openrouter-${label}`} className="font-normal cursor-pointer">
                OpenRouter
              </Label>
            </div>
          </RadioGroup>
        </div>

        {/* Step 2a: Standard Provider Flow */}
        {apiSource === 'standard' && (
          <div className="space-y-4">
            {/* Provider Selection */}
            <div className="space-y-2">
              <Label>Provider</Label>
              {loadingStandardProviders ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <Select
                  value={value.provider_id || ''}
                  onValueChange={handleStandardProviderChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a provider" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[300px] overflow-y-auto">
                    {standardProviders.length === 0 ? (
                      <div className="p-2 text-sm text-muted-foreground">
                        No providers available. Contact admin to add providers.
                      </div>
                    ) : (
                      standardProviders.map((provider) => (
                        <SelectItem key={provider.id} value={String(provider.id)}>
                          {provider.name}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              )}
            </div>

            {/* Model Selection */}
            {value.provider_id && (
              <div className="space-y-2">
                <Label>Model</Label>
                {loadingStandardModels ? (
                  <Skeleton className="h-10 w-full" />
                ) : (
                  <Select
                    value={value.model_id || ''}
                    onValueChange={handleStandardModelChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a model" />
                    </SelectTrigger>
                    <SelectContent className="max-h-[300px] overflow-y-auto">
                      {standardModels.length === 0 ? (
                        <div className="p-2 text-sm text-muted-foreground">
                          No models available for this provider.
                        </div>
                      ) : (
                        standardModels.map((model) => (
                          <SelectItem key={model.id} value={String(model.id)}>
                            {model.display_name}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                )}
              </div>
            )}
          </div>
        )}

        {/* Step 2b: OpenRouter Flow */}
        {apiSource === 'openrouter' && (
          <Tabs value={openRouterTab} onValueChange={(val) => setOpenRouterTab(val as OpenRouterTab)}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="by-provider">By Provider</TabsTrigger>
              <TabsTrigger value="by-model">By Model</TabsTrigger>
            </TabsList>

            {/* By Provider Tab */}
            <TabsContent value="by-provider" className="space-y-4 mt-4">
              {/* Provider Selection */}
              <div className="space-y-2">
                <Label>Provider</Label>
                {loadingOpenRouterProviders ? (
                  <Skeleton className="h-10 w-full" />
                ) : (
                  <Select
                    value={value.openrouter_provider_slug || ''}
                    onValueChange={handleOpenRouterProviderChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a provider" />
                    </SelectTrigger>
                    <SelectContent className="max-h-[300px] overflow-y-auto">
                      {openRouterProviders.length === 0 ? (
                        <div className="p-2 text-sm text-muted-foreground">
                          No providers available. Check OpenRouter API key configuration.
                        </div>
                      ) : (
                        openRouterProviders.map((provider) => (
                          <SelectItem key={provider.slug} value={provider.slug}>
                            {provider.name} ({provider.model_count} models)
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                )}
              </div>

              {/* Model Selection */}
              {value.openrouter_provider_slug && (
                <div className="space-y-2">
                  <Label>Model</Label>
                  {loadingOpenRouterModels ? (
                    <Skeleton className="h-10 w-full" />
                  ) : (
                    <Select
                      value={value.openrouter_model_id || ''}
                      onValueChange={handleOpenRouterModelChange}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a model" />
                      </SelectTrigger>
                      <SelectContent className="max-h-[300px] overflow-y-auto">
                        {openRouterModels.length === 0 ? (
                          <div className="p-2 text-sm text-muted-foreground">
                            No models available for this provider.
                          </div>
                        ) : (
                          openRouterModels.map((model) => (
                            <SelectItem key={model.id} value={model.id}>
                              <div className="flex flex-col">
                                <span>{model.name}</span>
                                {model.description && (
                                  <span className="text-xs text-muted-foreground truncate max-w-md">
                                    {model.description}
                                  </span>
                                )}
                              </div>
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                  )}
                </div>
              )}
            </TabsContent>

            {/* By Model Tab */}
            <TabsContent value="by-model" className="space-y-4 mt-4">
              {/* Model Selection */}
              <div className="space-y-2">
                <Label>Model</Label>
                {loadingOpenRouterModels ? (
                  <Skeleton className="h-10 w-full" />
                ) : (
                  <Select
                    value={value.openrouter_model_id || ''}
                    onValueChange={handleOpenRouterModelChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Search and select a model" />
                    </SelectTrigger>
                    <SelectContent className="max-h-[300px]">
                      {openRouterModels.length === 0 ? (
                        <div className="p-2 text-sm text-muted-foreground">
                          No models available. Check OpenRouter API key configuration.
                        </div>
                      ) : (
                        openRouterModels.map((model) => (
                          <SelectItem key={model.id} value={model.id}>
                            <div className="flex flex-col">
                              <span>{model.name}</span>
                              <span className="text-xs text-muted-foreground">{model.id}</span>
                            </div>
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                )}
              </div>

              {/* Show available providers for selected model */}
              {value.openrouter_model_id && (
                <div className="space-y-2">
                  <Label>Provider</Label>
                  {loadingOpenRouterProvidersByModel ? (
                    <Skeleton className="h-10 w-full" />
                  ) : (
                    <Select
                      value={value.openrouter_provider_slug || ''}
                      onValueChange={(providerSlug) => {
                        const provider = openRouterProviders.find((p) => p.slug === providerSlug);
                        onChange({
                          ...value,
                          openrouter_provider_slug: providerSlug,
                          openrouter_provider_name: provider?.name,
                        });
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a provider" />
                      </SelectTrigger>
                      <SelectContent className="max-h-[300px] overflow-y-auto">
                        {openRouterProvidersByModel.length === 0 ? (
                          <div className="p-2 text-sm text-muted-foreground">
                            Provider information not available
                          </div>
                        ) : (
                          openRouterProvidersByModel.map((providerSlug) => {
                            const provider = openRouterProviders.find((p) => p.slug === providerSlug);
                            return (
                              <SelectItem key={providerSlug} value={providerSlug}>
                                {provider?.name || providerSlug}
                              </SelectItem>
                            );
                          })
                        )}
                      </SelectContent>
                    </Select>
                  )}
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}

        {/* Current Selection Display */}
        {(value.model_name || value.openrouter_model_id) && (
          <div className="pt-4 border-t space-y-2">
            <Label>Current Selection</Label>
            <div className="text-sm space-y-1 p-3 bg-muted rounded-md">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Provider:</span>
                <span className="font-medium">
                  {value.is_openrouter
                    ? (value.openrouter_provider_name || value.openrouter_provider_slug || 'OpenRouter')
                    : value.provider_name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Model:</span>
                <span className="font-medium">
                  {value.is_openrouter
                    ? (value.openrouter_model_name || value.openrouter_model_id)
                    : value.model_name}
                </span>
              </div>
              {value.api_base && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">API Base:</span>
                  <span className="font-medium text-xs truncate max-w-[200px]">{value.api_base}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
