import Layout from "@/components/layout";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { Button } from "@/components/ui/button";
import { DatasetCard, GuidelineCard } from "@/components/cards";
import generatedImage from "@assets/generated_images/abstract_geometric_composition_with_mint_accents.png";
import { ArrowRight, Play } from "lucide-react";
import { Link } from "wouter";

export default function Home() {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative pt-20 pb-24 overflow-hidden">
        <div className="container mx-auto px-4 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-mint-50 border border-mint-200 text-mint-800 text-xs font-bold uppercase tracking-widest mb-6">
              <span className="w-2 h-2 rounded-full bg-mint-500 animate-pulse"></span>
              v2.0 Live Now
            </div>
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
              <Button size="lg" className="bg-black hover:bg-zinc-800 text-white rounded-md h-12 px-8 text-base">
                View Leaderboard
              </Button>
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
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-3xl font-display font-bold mb-2">Top Models</h2>
              <p className="text-muted-foreground">Ranked by aggregate performance across key benchmarks.</p>
            </div>
            <Button variant="link" className="text-black font-bold gap-1">
              View Full Rankings <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
          
          <LeaderboardTable />
        </div>
      </section>

      {/* Datasets Preview */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-3xl font-display font-bold mb-2">Featured Datasets</h2>
              <p className="text-muted-foreground">High-quality evaluation sets for robust testing.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <DatasetCard 
              title="MMLU-Pro" 
              category="General Knowledge" 
              samples={12000} 
              tokens="4.2M"
              description="Massive Multitask Language Understanding with professional-grade questions across 57 subjects."
            />
            <DatasetCard 
              title="HumanEval+" 
              category="Coding" 
              samples={164} 
              tokens="450K"
              description="Enhanced version of HumanEval with more rigorous test cases to prevent overfitting."
            />
            <DatasetCard 
              title="GSM8K-Hard" 
              category="Math" 
              samples={8500} 
              tokens="2.1M"
              description="Grade School Math 8K dataset with increased difficulty and reasoning steps."
            />
          </div>
        </div>
      </section>

       {/* Guidelines Preview */}
       <section className="py-16 bg-zinc-50 border-t border-border">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h2 className="text-3xl font-display font-bold mb-2">Evaluation Guidelines</h2>
              <p className="text-muted-foreground">Standardized rubrics for consistent judging.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GuidelineCard 
              title="Helpfulness" 
              category="General"
              description="Evaluates how well the model addresses the user's intent and provides useful information."
            />
             <GuidelineCard 
              title="Factuality" 
              category="Accuracy"
              description="Checks if the information provided is factually correct and free of hallucinations."
            />
             <GuidelineCard 
              title="Code Safety" 
              category="Security"
              description="Ensures generated code does not contain vulnerabilities or malicious patterns."
            />
             <GuidelineCard 
              title="Conciseness" 
              category="Style"
              description="Rewards brevity and directness without sacrificing necessary detail."
            />
          </div>
        </div>
      </section>
    </Layout>
  );
}
