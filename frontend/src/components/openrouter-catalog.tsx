import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ExternalLink } from "lucide-react";
import { Link } from "wouter";

import { apiClient, type OpenRouterModelSummary, type OpenRouterProviderSummary } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const DEFAULT_PAGE_SIZE = 24;

export type OpenRouterModelSort = "name" | "context" | "input" | "output";
export type OpenRouterProviderSort = "models" | "name";

function toNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return null;
}

function formatUsdPerMillion(raw: unknown): string {
  const perToken = toNumber(raw);
  if (perToken === null) return "-";
  const perMillion = perToken * 1_000_000;
  if (perMillion < 0.01) return `$${perMillion.toFixed(4)}`;
  if (perMillion < 1) return `$${perMillion.toFixed(3)}`;
  return `$${perMillion.toFixed(2)}`;
}

function getAuthor(modelId: string): string {
  const [author] = modelId.split("/", 1);
  return author || "unknown";
}

function getProviderNames(model: OpenRouterModelSummary, providers: OpenRouterProviderSummary[]): string[] {
  const slugs = model.provider_slugs || [];
  const names: string[] = [];
  for (const slug of slugs) {
    const provider = providers.find((candidate) => candidate.slug === slug);
    if (provider) names.push(provider.name);
  }
  return names;
}

interface OpenRouterModelCatalogProps {
  pageSize?: number;
  fixedProviderSlug?: string;
  initialProviderSlug?: string;
  selectable?: boolean;
  selectedModelId?: string;
  onSelectModel?: (model: OpenRouterModelSummary | null) => void;
  showExploreProvidersLink?: boolean;
  className?: string;
}

export function OpenRouterModelCatalog({
  pageSize = DEFAULT_PAGE_SIZE,
  fixedProviderSlug,
  initialProviderSlug = "all",
  selectable = false,
  selectedModelId,
  onSelectModel,
  showExploreProvidersLink = false,
  className,
}: OpenRouterModelCatalogProps) {
  const [search, setSearch] = useState("");
  const [providerFilter, setProviderFilter] = useState(initialProviderSlug);
  const [sortBy, setSortBy] = useState<OpenRouterModelSort>("name");
  const [page, setPage] = useState(0);

  const effectiveProviderSlug = fixedProviderSlug || (providerFilter === "all" ? undefined : providerFilter);

  const { data: modelsData, isLoading: modelsLoading } = useQuery({
    queryKey: ["openrouter-models-catalog", page, search, effectiveProviderSlug, sortBy, pageSize],
    queryFn: () =>
      apiClient.getOpenRouterModels({
        limit: pageSize,
        offset: page * pageSize,
        search: search.trim() || undefined,
        provider_slug: effectiveProviderSlug,
        sort: sortBy,
      }),
  });

  const { data: providersData } = useQuery({
    queryKey: ["openrouter-providers-catalog-all"],
    queryFn: () => apiClient.getOpenRouterProviders({ limit: 500 }),
  });

  const models = modelsData?.models || [];
  const total = modelsData?.total ?? 0;
  const providers = providersData?.providers || [];
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const goToPage = (target: number) => {
    setPage(Math.max(0, Math.min(target, totalPages - 1)));
  };

  const canSelect = selectable && typeof onSelectModel === "function";

  return (
    <div className={cn("space-y-4", className)}>
      <div className={cn("grid gap-3", fixedProviderSlug ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1 md:grid-cols-3")}>
        <Input
          placeholder="Search model name, ID, or description"
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPage(0);
          }}
        />
        {!fixedProviderSlug && (
          <select
            value={providerFilter}
            onChange={(event) => {
              setProviderFilter(event.target.value);
              setPage(0);
            }}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="all">All Providers</option>
            {providers.map((provider) => (
              <option key={provider.slug} value={provider.slug}>
                {provider.name}
              </option>
            ))}
          </select>
        )}
        <select
          value={sortBy}
          onChange={(event) => {
            setSortBy(event.target.value as OpenRouterModelSort);
            setPage(0);
          }}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="name">Sort: Name</option>
          <option value="context">Sort: Context (high to low)</option>
          <option value="input">Sort: Input price (low to high)</option>
          <option value="output">Sort: Output price (low to high)</option>
        </select>
      </div>

      <div className="flex items-center justify-between gap-4">
        <span className="text-sm text-muted-foreground">
          {total === 0 ? "0 models" : `${page * pageSize + 1}-${Math.min(page * pageSize + pageSize, total)} of ${total} models`}
        </span>
        {totalPages > 1 && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => goToPage(page - 1)}
              disabled={page <= 0}
              className="rounded border border-input bg-background px-3 py-1 text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-muted-foreground">
              Page {page + 1} of {totalPages}
            </span>
            <button
              type="button"
              onClick={() => goToPage(page + 1)}
              disabled={page >= totalPages - 1}
              className="rounded border border-input bg-background px-3 py-1 text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {modelsLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-52 w-full" />
          ))}
        </div>
      )}

      {!modelsLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {models.map((model) => {
            const providerNames = getProviderNames(model, providers);
            const topProvider = (model.top_provider || {}) as Record<string, unknown>;
            const architecture = (model.architecture || {}) as Record<string, unknown>;
            const pricing = (model.pricing || {}) as Record<string, unknown>;
            const contextLength = toNumber(topProvider.context_length) ?? model.context_length;
            const maxCompletion = toNumber(topProvider.max_completion_tokens);
            const modality = String(architecture.modality || "text");
            const isSelected = selectedModelId === model.id;

            return (
              <Card
                key={model.id}
                className={cn(
                  "h-full",
                  canSelect && "cursor-pointer transition-colors",
                  isSelected && "border-emerald-600 bg-emerald-50/40"
                )}
                onClick={canSelect ? () => onSelectModel(isSelected ? null : model) : undefined}
              >
                <CardHeader className="pb-3">
                  <div className="min-w-0">
                    <CardTitle className="text-base leading-tight truncate">{model.name}</CardTitle>
                    <p className="text-xs text-muted-foreground truncate mt-1">{model.id}</p>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">{modality}</Badge>
                    <Badge variant="outline">{getAuthor(model.id)}</Badge>
                    {contextLength ? <Badge variant="outline">{contextLength.toLocaleString()} ctx</Badge> : null}
                  </div>

                  {model.description ? <p className="text-sm text-muted-foreground line-clamp-2">{model.description}</p> : null}

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="rounded-md border p-2">
                      <div className="text-muted-foreground">Input / 1M</div>
                      <div className="font-semibold">{formatUsdPerMillion(pricing.prompt)}</div>
                    </div>
                    <div className="rounded-md border p-2">
                      <div className="text-muted-foreground">Output / 1M</div>
                      <div className="font-semibold">{formatUsdPerMillion(pricing.completion)}</div>
                    </div>
                    <div className="rounded-md border p-2">
                      <div className="text-muted-foreground">Request</div>
                      <div className="font-semibold">{formatUsdPerMillion(pricing.request)}</div>
                    </div>
                    <div className="rounded-md border p-2">
                      <div className="text-muted-foreground">Max Output</div>
                      <div className="font-semibold">{maxCompletion ? maxCompletion.toLocaleString() : "-"}</div>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground">
                    {providerNames.length > 0 ? `Providers: ${providerNames.join(", ")}` : "Providers: -"}
                  </div>

                  <div className="flex items-center justify-between gap-2">
                    <a
                      href={`https://openrouter.ai/${model.id}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                      onClick={(event) => event.stopPropagation()}
                    >
                      OpenRouter <ExternalLink className="h-3 w-3" />
                    </a>
                    {canSelect && (
                      <span className="text-xs text-muted-foreground">
                        {isSelected ? "Selected" : "Click card to select"}
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {!modelsLoading && models.length === 0 && (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">No models match your filters.</CardContent>
        </Card>
      )}

      {showExploreProvidersLink && (
        <div>
          <Link href="/providers" className="text-sm underline text-muted-foreground hover:text-foreground">
            Explore providers
          </Link>
        </div>
      )}
    </div>
  );
}

interface OpenRouterProviderCatalogProps {
  pageSize?: number;
  selectable?: boolean;
  selectedProviderSlug?: string;
  onSelectProvider?: (provider: OpenRouterProviderSummary | null) => void;
  onlyProviderSlugs?: string[];
  showHostedModelsLink?: boolean;
  className?: string;
}

export function OpenRouterProviderCatalog({
  pageSize = DEFAULT_PAGE_SIZE,
  selectable = false,
  selectedProviderSlug,
  onSelectProvider,
  onlyProviderSlugs,
  showHostedModelsLink = true,
  className,
}: OpenRouterProviderCatalogProps) {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<OpenRouterProviderSort>("models");
  const [page, setPage] = useState(0);
  const hasRestrictedProviders = Boolean(onlyProviderSlugs?.length);

  const { data, isLoading } = useQuery({
    queryKey: ["openrouter-providers-catalog", page, search, sortBy, pageSize, hasRestrictedProviders],
    queryFn: () =>
      apiClient.getOpenRouterProviders({
        limit: hasRestrictedProviders ? 500 : pageSize,
        offset: hasRestrictedProviders ? 0 : page * pageSize,
        search: hasRestrictedProviders ? undefined : search.trim() || undefined,
        sort: sortBy,
      }),
  });

  const providers = data?.providers || [];

  const allowedSlugs = useMemo(() => {
    if (!onlyProviderSlugs?.length) return null;
    return new Set(onlyProviderSlugs);
  }, [onlyProviderSlugs]);

  const visibleProviders = useMemo(() => {
    const filteredByAllowed = allowedSlugs
      ? providers.filter((provider) => allowedSlugs.has(provider.slug) || allowedSlugs.has(provider.name))
      : providers;

    if (!hasRestrictedProviders || !search.trim()) return filteredByAllowed;

    const loweredSearch = search.trim().toLowerCase();
    return filteredByAllowed.filter(
      (provider) =>
        provider.name.toLowerCase().includes(loweredSearch) ||
        provider.slug.toLowerCase().includes(loweredSearch)
    );
  }, [allowedSlugs, hasRestrictedProviders, providers, search]);
  const total = hasRestrictedProviders ? visibleProviders.length : data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const pagedProviders = hasRestrictedProviders
    ? visibleProviders.slice(page * pageSize, page * pageSize + pageSize)
    : visibleProviders;

  useEffect(() => {
    if (page <= totalPages - 1) return;
    setPage(Math.max(0, totalPages - 1));
  }, [page, totalPages]);

  const canSelect = selectable && typeof onSelectProvider === "function";

  const goToPage = (target: number) => {
    setPage(Math.max(0, Math.min(target, totalPages - 1)));
  };

  return (
    <div className={cn("space-y-4", className)}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Input
          placeholder="Search provider name or slug"
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPage(0);
          }}
        />
        <select
          value={sortBy}
          onChange={(event) => {
            setSortBy(event.target.value as OpenRouterProviderSort);
            setPage(0);
          }}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        >
          <option value="models">Sort: Most models</option>
          <option value="name">Sort: Name</option>
        </select>
      </div>

      <div className="flex items-center justify-between gap-4">
        <span className="text-sm text-muted-foreground">
          {total === 0 ? "0 providers" : `${page * pageSize + 1}-${Math.min(page * pageSize + pageSize, total)} of ${total} providers`}
        </span>
        {totalPages > 1 && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => goToPage(page - 1)}
              disabled={page <= 0}
              className="rounded border border-input bg-background px-3 py-1 text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-muted-foreground">
              Page {page + 1} of {totalPages}
            </span>
            <button
              type="button"
              onClick={() => goToPage(page + 1)}
              disabled={page >= totalPages - 1}
              className="rounded border border-input bg-background px-3 py-1 text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-44 w-full" />
          ))}
        </div>
      )}

      {!isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {pagedProviders.map((provider) => {
            const isSelected = selectedProviderSlug === provider.slug;

            return (
              <Card
                key={provider.slug}
                className={cn(
                  canSelect && "cursor-pointer transition-colors",
                  isSelected && "border-emerald-600 bg-emerald-50/40"
                )}
                onClick={canSelect ? () => onSelectProvider(isSelected ? null : provider) : undefined}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between gap-4">
                    <div className="min-w-0">
                      <CardTitle className="text-base truncate">{provider.name}</CardTitle>
                      <p className="text-xs text-muted-foreground truncate">{provider.slug}</p>
                    </div>
                    <Badge variant="outline">{provider.model_count} models</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex flex-wrap gap-2 text-xs">
                    <a
                      href={`https://openrouter.ai/provider/${encodeURIComponent(provider.slug)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 rounded-md border px-2 py-1 hover:bg-muted"
                      onClick={(event) => event.stopPropagation()}
                    >
                      OpenRouter <ExternalLink className="h-3 w-3" />
                    </a>
                    {provider.status_page_url ? (
                      <a
                        href={provider.status_page_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 rounded-md border px-2 py-1 hover:bg-muted"
                        onClick={(event) => event.stopPropagation()}
                      >
                        Status <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : null}
                    {provider.terms_of_service_url ? (
                      <a
                        href={provider.terms_of_service_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 rounded-md border px-2 py-1 hover:bg-muted"
                        onClick={(event) => event.stopPropagation()}
                      >
                        Terms <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : null}
                    {provider.privacy_policy_url ? (
                      <a
                        href={provider.privacy_policy_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 rounded-md border px-2 py-1 hover:bg-muted"
                        onClick={(event) => event.stopPropagation()}
                      >
                        Privacy <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : null}
                  </div>

                  {canSelect ? (
                    <p className="text-xs text-muted-foreground">
                      {isSelected ? "Selected" : "Click card to select provider"}
                    </p>
                  ) : (
                    showHostedModelsLink && (
                      <Link href={`/models?provider=${encodeURIComponent(provider.slug)}`}>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full"
                          onClick={(event) => event.stopPropagation()}
                        >
                          View hosted models
                        </Button>
                      </Link>
                    )
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {!isLoading && total === 0 && (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No providers match your filters.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
