import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { apiClient, type OpenRouterModelSummary, type OpenRouterProviderSummary } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { OpenRouterModelCatalog, OpenRouterProviderCatalog } from "@/components/openrouter-catalog";
import type { ModelConfig } from "@/types/model-config";

interface ModelSelectionProps {
  value: ModelConfig;
  onChange: (value: ModelConfig) => void;
  label?: string;
}

type OpenRouterTab = "by-provider" | "by-model";

export function ModelSelection({ value, onChange, label = "Model Selection" }: ModelSelectionProps) {
  const [openRouterTab, setOpenRouterTab] = useState<OpenRouterTab>("by-provider");
  const byProviderStep2Ref = useRef<HTMLDivElement | null>(null);
  const byModelStep2Ref = useRef<HTMLDivElement | null>(null);

  // Temporarily force OpenRouter-only selection flow.
  useEffect(() => {
    if (value.is_openrouter === false) {
      onChange({ is_openrouter: true });
    }
  }, [value.is_openrouter, onChange]);

  const { data: openRouterProviderSlugsByModelData, isLoading: loadingOpenRouterProvidersByModel } = useQuery({
    queryKey: ["openrouter-providers-by-model-selection", value.openrouter_model_id],
    queryFn: () => apiClient.getOpenRouterProvidersByModel(value.openrouter_model_id || ""),
    enabled: openRouterTab === "by-model" && !!value.openrouter_model_id,
  });

  const openRouterProviderSlugsByModel = openRouterProviderSlugsByModelData?.providers || [];

  const handleOpenRouterProviderChange = (provider: OpenRouterProviderSummary | null) => {
    if (!provider) {
      onChange({
        is_openrouter: true,
        openrouter_provider_slug: undefined,
        openrouter_provider_name: undefined,
        openrouter_model_id: undefined,
        openrouter_model_name: undefined,
        openrouter_model_description: undefined,
        openrouter_model_pricing: undefined,
        openrouter_model_context_length: undefined,
        openrouter_model_canonical_slug: undefined,
        openrouter_model_architecture: undefined,
        openrouter_model_top_provider: undefined,
        openrouter_model_supported_parameters: undefined,
        openrouter_model_per_request_limits: undefined,
        openrouter_model_provider_slugs: undefined,
      });
      return;
    }

    onChange({
      is_openrouter: true,
      openrouter_provider_slug: provider.slug,
      openrouter_provider_name: provider.name,
      openrouter_model_id: undefined,
      openrouter_model_name: undefined,
      openrouter_model_description: undefined,
      openrouter_model_pricing: undefined,
      openrouter_model_context_length: undefined,
      openrouter_model_canonical_slug: undefined,
      openrouter_model_architecture: undefined,
      openrouter_model_top_provider: undefined,
      openrouter_model_supported_parameters: undefined,
      openrouter_model_per_request_limits: undefined,
      openrouter_model_provider_slugs: undefined,
    });
    setTimeout(() => byProviderStep2Ref.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 0);
  };

  const handleOpenRouterModelChange = (model: OpenRouterModelSummary | null) => {
    if (!model) {
      onChange({
        ...value,
        is_openrouter: true,
        openrouter_model_id: undefined,
        openrouter_model_name: undefined,
        openrouter_model_description: undefined,
        openrouter_model_pricing: undefined,
        openrouter_model_context_length: undefined,
        openrouter_model_canonical_slug: undefined,
        openrouter_model_architecture: undefined,
        openrouter_model_top_provider: undefined,
        openrouter_model_supported_parameters: undefined,
        openrouter_model_per_request_limits: undefined,
        openrouter_model_provider_slugs: undefined,
        ...(openRouterTab === "by-model"
          ? { openrouter_provider_slug: undefined, openrouter_provider_name: undefined }
          : {}),
      });
      return;
    }

    onChange({
      is_openrouter: true,
      openrouter_model_id: model.id,
      openrouter_model_name: model.name || model.id,
      openrouter_model_description: model.description,
      openrouter_model_pricing: model.pricing,
      openrouter_model_context_length: model.context_length,
      openrouter_model_canonical_slug: model.canonical_slug,
      openrouter_model_architecture: model.architecture,
      openrouter_model_top_provider: model.top_provider,
      openrouter_model_supported_parameters: model.supported_parameters,
      openrouter_model_per_request_limits: model.per_request_limits,
      openrouter_model_provider_slugs: model.provider_slugs,
      openrouter_provider_slug: value.openrouter_provider_slug,
      openrouter_provider_name: value.openrouter_provider_name,
    });
    if (openRouterTab === "by-model") {
      setTimeout(() => byModelStep2Ref.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 0);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
        <CardDescription>Select the model configuration for this evaluation</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <Tabs value={openRouterTab} onValueChange={(tab) => setOpenRouterTab(tab as OpenRouterTab)}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="by-provider">By Provider</TabsTrigger>
            <TabsTrigger value="by-model">By Model</TabsTrigger>
          </TabsList>

          <TabsContent value="by-provider" className="space-y-6 mt-4">
            <div className="space-y-2">
              <Label>1. Choose Provider</Label>
              <OpenRouterProviderCatalog
                pageSize={12}
                selectable
                selectedProviderSlug={value.openrouter_provider_slug}
                onSelectProvider={handleOpenRouterProviderChange}
                showHostedModelsLink={false}
              />
            </div>

            {value.openrouter_provider_slug && (
              <div ref={byProviderStep2Ref} className="space-y-2">
                <Label>2. Choose Model</Label>
                <p className="text-xs text-muted-foreground">
                  Provider selected. Pick one hosted model below to complete the pair.
                </p>
                <OpenRouterModelCatalog
                  pageSize={12}
                  selectable
                  fixedProviderSlug={value.openrouter_provider_slug}
                  selectedModelId={value.openrouter_model_id}
                  onSelectModel={handleOpenRouterModelChange}
                />
              </div>
            )}
          </TabsContent>

          <TabsContent value="by-model" className="space-y-6 mt-4">
            <div className="space-y-2">
              <Label>1. Choose Model</Label>
              <OpenRouterModelCatalog
                pageSize={12}
                selectable
                selectedModelId={value.openrouter_model_id}
                onSelectModel={handleOpenRouterModelChange}
              />
            </div>

            {value.openrouter_model_id && (
              <div ref={byModelStep2Ref} className="space-y-2">
                <Label>2. Choose Provider</Label>
                <p className="text-xs text-muted-foreground">
                  Model selected. Choose one provider from the compatible hosts below.
                </p>
                {loadingOpenRouterProvidersByModel ? (
                  <Skeleton className="h-10 w-full" />
                ) : (
                  <OpenRouterProviderCatalog
                    pageSize={12}
                    selectable
                    selectedProviderSlug={value.openrouter_provider_slug}
                    onSelectProvider={(provider) => {
                      if (!provider) {
                        onChange({
                          ...value,
                          is_openrouter: true,
                          openrouter_provider_slug: undefined,
                          openrouter_provider_name: undefined,
                        });
                        return;
                      }
                      onChange({
                        ...value,
                        is_openrouter: true,
                        openrouter_provider_slug: provider.slug,
                        openrouter_provider_name: provider.name,
                      });
                    }}
                    onlyProviderSlugs={openRouterProviderSlugsByModel}
                    showHostedModelsLink={false}
                  />
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {(value.model_name || value.openrouter_model_id) && (
          <div className="pt-4 border-t space-y-2">
            <Label>Current Selection</Label>
            <div className="text-sm space-y-1 p-3 bg-muted rounded-md">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Provider:</span>
                <span className="font-medium">
                  {value.is_openrouter
                    ? value.openrouter_provider_name || value.openrouter_provider_slug || "OpenRouter"
                    : value.provider_name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Model:</span>
                <span className="font-medium">
                  {value.is_openrouter ? value.openrouter_model_name || value.openrouter_model_id : value.model_name}
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
