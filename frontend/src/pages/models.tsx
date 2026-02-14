import Layout from "@/components/layout";
import { OpenRouterModelCatalog } from "@/components/openrouter-catalog";

export default function ModelsPage() {
  const defaultProvider = new URLSearchParams(window.location.search).get("provider") || "all";

  return (
    <Layout>
      <section className="py-10 border-b border-border bg-zinc-50/50">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-display font-bold tracking-tight">Model Catalog</h1>
          <p className="text-muted-foreground mt-2">
            Browse model pricing, context windows, token limits, and provider coverage.
          </p>
        </div>
      </section>

      <section className="py-8">
        <div className="container mx-auto px-4">
          <OpenRouterModelCatalog
            initialProviderSlug={defaultProvider}
            showExploreProvidersLink
          />
        </div>
      </section>
    </Layout>
  );
}
