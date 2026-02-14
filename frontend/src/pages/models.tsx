import Layout from "@/components/layout";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { apiClient, type OpenRouterModelSummary, type OpenRouterProviderSummary } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ExternalLink } from "lucide-react";
import { Link } from "wouter";

function getAuthor(modelId: string): string {
  const [author] = modelId.split("/", 1);
  return author || "unknown";
}

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

function getProviderNames(
  model: OpenRouterModelSummary,
  providers: OpenRouterProviderSummary[]
): string[] {
  const slugs = model.provider_slugs || [];
  const names: string[] = [];
  for (const slug of slugs) {
    const p = providers.find((x) => x.slug === slug);
    if (p) names.push(p.name);
  }
  return names;
}

const PAGE_SIZE = 24;

export default function ModelsPage() {
  const defaultProvider = new URLSearchParams(window.location.search).get("provider") || "all";
  const [search, setSearch] = useState("");
  const [providerFilter, setProviderFilter] = useState(defaultProvider);
  const [sortBy, setSortBy] = useState<"name" | "context" | "input" | "output">("name");
  const [page, setPage] = useState(0);

  const { data: modelsData, isLoading: modelsLoading } = useQuery({
    queryKey: ["openrouter-models-catalog", page, search, providerFilter, sortBy],
    queryFn: () =>
      apiClient.getOpenRouterModels({
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        search: search.trim() || undefined,
        provider_slug: providerFilter === "all" ? undefined : providerFilter,
        sort: sortBy,
      }),
  });

  const { data: providersData } = useQuery({
    queryKey: ["openrouter-providers-catalog"],
    queryFn: () => apiClient.getOpenRouterProviders({ limit: 500 }),
  });

  const models = modelsData?.models || [];
  const total = modelsData?.total ?? 0;
  const providers = providersData?.providers || [];
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const goToPage = (p: number) => {
    setPage(Math.max(0, Math.min(p, totalPages - 1)));
  };

  return (
    <Layout>
      <section className="py-10 border-b border-border bg-zinc-50/50">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-display font-bold tracking-tight">Model Catalog</h1>
          <p className="text-muted-foreground mt-2">
            Browse model pricing, context windows, token limits, and provider coverage.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-6">
            <Input
              placeholder="Search model name, ID, or description"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
            />
            <select
              value={providerFilter}
              onChange={(e) => {
                setProviderFilter(e.target.value);
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
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value as typeof sortBy);
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
        </div>
      </section>

      <section className="py-8">
        <div className="container mx-auto px-4">
          <div className="mb-4 flex items-center justify-between gap-4">
            <span className="text-sm text-muted-foreground">
              {total === 0
                ? "0 models"
                : `${page * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE + PAGE_SIZE, total)} of ${total} models`}
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
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-52 w-full" />
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
                const contextLength =
                  toNumber(topProvider.context_length) ?? model.context_length;
                const maxCompletion = toNumber(topProvider.max_completion_tokens);
                const modality = String(architecture.modality || "text");

                return (
                  <Card key={model.id} className="h-full">
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

                      {model.description ? (
                        <p className="text-sm text-muted-foreground line-clamp-2">{model.description}</p>
                      ) : null}

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
                        {providerNames.length > 0
                          ? `Providers: ${providerNames.join(", ")}`
                          : "Providers: —"}
                      </div>
                      <a
                        href={`https://openrouter.ai/${model.id}`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                      >
                        OpenRouter <ExternalLink className="h-3 w-3" />
                      </a>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}

          {!modelsLoading && models.length === 0 && (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                No models match your filters.
              </CardContent>
            </Card>
          )}

          <div className="mt-8">
            <Link href="/providers" className="text-sm underline text-muted-foreground hover:text-foreground">
              Explore providers
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
}
