import Layout from "@/components/layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { apiClient } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { ExternalLink } from "lucide-react";
import { useState } from "react";
import { Link } from "wouter";

const PAGE_SIZE = 24;

export default function ProvidersPage() {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"models" | "name">("models");
  const [page, setPage] = useState(0);

  const { data, isLoading } = useQuery({
    queryKey: ["openrouter-providers-page", page, search, sortBy],
    queryFn: () =>
      apiClient.getOpenRouterProviders({
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        search: search.trim() || undefined,
        sort: sortBy,
      }),
  });

  const providers = data?.providers || [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const goToPage = (p: number) => {
    setPage(Math.max(0, Math.min(p, totalPages - 1)));
  };

  return (
    <Layout>
      <section className="py-10 border-b border-border bg-zinc-50/50">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-display font-bold tracking-tight">Provider Catalog</h1>
          <p className="text-muted-foreground mt-2">
            Compare hosted providers, model coverage, and trust links.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-6">
            <Input
              placeholder="Search provider name or slug"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
            />
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value as typeof sortBy);
                setPage(0);
              }}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="models">Sort: Most models</option>
              <option value="name">Sort: Name</option>
            </select>
          </div>
        </div>
      </section>

      <section className="py-8">
        <div className="container mx-auto px-4">
          <div className="mb-4 flex items-center justify-between gap-4">
            <span className="text-sm text-muted-foreground">
              {total === 0
                ? "0 providers"
                : `${page * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE + PAGE_SIZE, total)} of ${total} providers`}
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
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-44 w-full" />
              ))}
            </div>
          )}

          {!isLoading && (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {providers.map((provider) => (
                <Card key={provider.slug}>
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
                      >
                        OpenRouter <ExternalLink className="h-3 w-3" />
                      </a>
                      {provider.status_page_url ? (
                        <a
                          href={provider.status_page_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 rounded-md border px-2 py-1 hover:bg-muted"
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
                        >
                          Privacy <ExternalLink className="h-3 w-3" />
                        </a>
                      ) : null}
                    </div>
                    <Link href={`/models?provider=${encodeURIComponent(provider.slug)}`}>
                      <Button variant="outline" size="sm" className="w-full">
                        View hosted models
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {!isLoading && providers.length === 0 && (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                No providers match your filters.
              </CardContent>
            </Card>
          )}
        </div>
      </section>
    </Layout>
  );
}
