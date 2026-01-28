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
  provider_id?: number;
  provider_name?: string;
  provider_slug?: string;
  model_id?: number; // Database ID as integer
  model_name?: string;
  model_slug?: string;
  api_base?: string;

  // For OpenRouter
  is_openrouter?: boolean;
  openrouter_model_id?: string;
  openrouter_model_name?: string;
  openrouter_provider_slug?: string;
}

interface ModelSelectionProps {
  value: ModelConfig;
  onChange: (value: ModelConfig) => void;
  label?: string;
}

type ApiSource = 'standard' | 'openrouter';
type OpenRouterTab = 'by-provider' | 'by-model';

export function ModelSelection({ value, onChange, label = 'Model Selection' }: ModelSelectionProps) {
  // API Source selection
  const [apiSource, setApiSource] = useState<ApiSource>('standard');
  const [openRouterTab, setOpenRouterTab] = useState<OpenRouterTab>('by-provider');

  // Standard providers state
  const [standardProviders, setStandardProviders] = useState<any[]>([]);
  const [standardModels, setStandardModels] = useState<any[]>([]);
  const [selectedStandardProvider, setSelectedStandardProvider] = useState<number | null>(null);
  const [selectedStandardModel, setSelectedStandardModel] = useState<number | null>(null);

  // OpenRouter state
  const [openRouterProviders, setOpenRouterProviders] = useState<any[]>([]);
  const [openRouterModels, setOpenRouterModels] = useState<any[]>([]);
  const [selectedOpenRouterProvider, setSelectedOpenRouterProvider] = useState<string>('');
  const [selectedOpenRouterModel, setSelectedOpenRouterModel] = useState<string>('');
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
    if (apiSource === 'openrouter' && openRouterTab === 'by-provider') {
      fetchOpenRouterProviders();
    }
  }, [apiSource, openRouterTab]);

  // Fetch all OpenRouter models when selecting by model
  useEffect(() => {
    if (apiSource === 'openrouter' && openRouterTab === 'by-model') {
      fetchAllOpenRouterModels();
    }
  }, [apiSource, openRouterTab]);

  // Fetch standard models when provider changes
  useEffect(() => {
    if (selectedStandardProvider) {
      fetchStandardModels(selectedStandardProvider);
    }
  }, [selectedStandardProvider]);

  // Fetch OpenRouter models when provider changes
  useEffect(() => {
    if (selectedOpenRouterProvider && openRouterTab === 'by-provider') {
      fetchOpenRouterModelsByProvider(selectedOpenRouterProvider);
    }
  }, [selectedOpenRouterProvider]);

  // Fetch providers by model when OpenRouter model changes
  useEffect(() => {
    if (selectedOpenRouterModel && openRouterTab === 'by-model') {
      fetchOpenRouterProvidersByModel(selectedOpenRouterModel);
    }
  }, [selectedOpenRouterModel]);

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

  const fetchStandardModels = async (providerId: number) => {
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
      setOpenRouterModels(response.models);
    } catch (error) {
      toast.error('Failed to load OpenRouter models. Check if API key is configured.');
      console.error('Error fetching OpenRouter models:', error);
    } finally {
      setLoadingOpenRouterModels(false);
    }
  };

  const fetchOpenRouterModelsByProvider = async (providerName: string) => {
    setLoadingOpenRouterModels(true);
    try {
      const response = await apiClient.getOpenRouterModelsByProvider(providerName);
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
      const response = await apiClient.getOpenRouterProvidersByModel(modelId);
      setOpenRouterProvidersByModel(response.providers);
    } catch (error) {
      console.error('Error fetching OpenRouter providers by model:', error);
      setOpenRouterProvidersByModel([]);
    } finally {
      setLoadingOpenRouterProvidersByModel(false);
    }
  };

  const handleStandardProviderChange = (providerId: string) => {
    const id = parseInt(providerId);
    setSelectedStandardProvider(id);
    setSelectedStandardModel(null);
    setStandardModels([]);
  };

  const handleStandardModelChange = (modelId: string) => {
    const id = parseInt(modelId);
    setSelectedStandardModel(id);

    // Find the selected model
    const model = standardModels.find((m) => m.id === id);

    if (model) {
      // Find the provider for this model from the model's providers array
      const provider = model.providers.find((p: any) => p.id === selectedStandardProvider);

      if (provider) {
        onChange({
          provider_id: provider.id,
          provider_name: provider.name,
          provider_slug: provider.slug || provider.name,
          model_id: model.id,
          model_name: model.api_name,
          model_slug: model.slug || model.api_name,
          api_base: provider.base_url,
          is_openrouter: false,
        });
      }
    }
  };

  const handleOpenRouterProviderChange = (providerName: string) => {
    setSelectedOpenRouterProvider(providerName);
    setSelectedOpenRouterModel('');
    setOpenRouterModels([]);
  };

  const handleOpenRouterModelChange = (modelId: string) => {
    setSelectedOpenRouterModel(modelId);

    // Find the model to get its name
    const model = openRouterModels.find((m) => m.id === modelId);

    // Set the config for OpenRouter
    onChange({
      is_openrouter: true,
      openrouter_model_id: modelId,
      openrouter_model_name: model?.name || modelId,
      openrouter_provider_slug: selectedOpenRouterProvider || undefined,
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
          <RadioGroup value={apiSource} onValueChange={(val) => setApiSource(val as ApiSource)}>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="standard" id="standard" />
              <Label htmlFor="standard" className="font-normal cursor-pointer">
                Standard Providers
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="openrouter" id="openrouter" />
              <Label htmlFor="openrouter" className="font-normal cursor-pointer">
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
                  value={selectedStandardProvider?.toString() || ''}
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
                        <SelectItem key={provider.id} value={provider.id.toString()}>
                          {provider.name}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              )}
            </div>

            {/* Model Selection */}
            {selectedStandardProvider && (
              <div className="space-y-2">
                <Label>Model</Label>
                {loadingStandardModels ? (
                  <Skeleton className="h-10 w-full" />
                ) : (
                  <Select
                    value={selectedStandardModel?.toString() || ''}
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
                          <SelectItem key={model.id} value={model.id.toString()}>
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
                    value={selectedOpenRouterProvider}
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
              {selectedOpenRouterProvider && (
                <div className="space-y-2">
                  <Label>Model</Label>
                  {loadingOpenRouterModels ? (
                    <Skeleton className="h-10 w-full" />
                  ) : (
                    <Select
                      value={selectedOpenRouterModel}
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
                    value={selectedOpenRouterModel}
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
              {selectedOpenRouterModel && (
                <div className="space-y-2">
                  <Label>Available Providers</Label>
                  {loadingOpenRouterProvidersByModel ? (
                    <Skeleton className="h-10 w-full" />
                  ) : (
                    <div className="text-sm text-muted-foreground p-3 border rounded-md">
                      {openRouterProvidersByModel.length === 0 ? (
                        <span>Provider information not available</span>
                      ) : (
                        <span>
                          This model is available from {openRouterProvidersByModel.length} provider(s)
                        </span>
                      )}
                    </div>
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
                    ? (value.openrouter_provider_slug || 'OpenRouter')
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
