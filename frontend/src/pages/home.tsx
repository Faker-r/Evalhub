import Layout from "@/components/layout";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { Button } from "@/components/ui/button";
import generatedImage from "@assets/evalhub_logo.png";
import { Play } from "lucide-react";
import { Link } from "wouter";

export default function Home() {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative pt-20 pb-24 overflow-hidden">
        <div className="container mx-auto px-4 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="z-10">
            <h1 className="text-5xl md:text-7xl font-display font-bold leading-[0.95] tracking-tight mb-6">
              Benchmarking <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-black to-zinc-600">
                is Clarity.
              </span>
            </h1>
            <p className="text-lg text-muted-foreground mb-8 max-w-lg leading-relaxed">
              EvalHub is the modern standard for evaluating open-source LLMs. 
              Compare performance across providers with rigorous, transparent benchmarks.
            </p>
            
            <div className="flex flex-wrap gap-4">
              <Link href="/submit">
                <Button size="lg" variant="outline" className="border-zinc-300 hover:bg-zinc-50 h-12 px-8 text-base gap-2">
                  <Play className="w-4 h-4" />
                  Run Custom Eval
                </Button>
              </Link>
            </div>
          </div>
          
          <div className="relative h-[400px] lg:h-[500px] w-full flex items-center justify-center">
            <div className="absolute inset-0 bg-gradient-to-tr from-mint-100/20 to-transparent rounded-full blur-3xl -z-10"></div>
            <img 
              src={generatedImage} 
              alt="Abstract geometric visualization of data" 
              className="object-contain h-full w-full drop-shadow-2xl animate-in fade-in zoom-in duration-1000"
            />
          </div>
        </div>
      </section>

      {/* Leaderboard Section */}
      <section className="py-16 bg-zinc-50/50 border-y border-border">
        <div className="container mx-auto px-4">
          <div className="mb-8">
            <h2 className="text-3xl font-display font-bold mb-2">Top Models</h2>
            <p className="text-muted-foreground">Ranked by aggregate performance across key benchmarks.</p>
          </div>
          
          <LeaderboardTable />
        </div>
      </section>

    </Layout>
  );
}
