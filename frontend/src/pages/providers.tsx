import Layout from "@/components/layout";
import { OpenRouterProviderCatalog } from "@/components/openrouter-catalog";

export default function ProvidersPage() {
  return (
    <Layout>
      <section className="py-10 border-b border-border bg-zinc-50/50">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-display font-bold tracking-tight">Provider Catalog</h1>
          <p className="text-muted-foreground mt-2">
            Compare hosted providers, model coverage, and trust links.
          </p>
        </div>
      </section>

      <section className="py-8">
        <div className="container mx-auto px-4">
          <OpenRouterProviderCatalog />
        </div>
      </section>
    </Layout>
  );
}
