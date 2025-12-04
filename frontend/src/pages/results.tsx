import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown, ChevronRight, Download, Share2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const SAMPLE_TRACES = [
  {
    id: "trace-001",
    prompt: "Explain quantum entanglement to a 5-year-old.",
    model_response: "Quantum entanglement is like having two magic dice. Even if you take them to opposite sides of the universe, when you roll a 6 on one, the other one will instantly show a 6 too! They are connected in a spooky way.",
    judge_reasoning: "The explanation is accurate but simple. The metaphor is appropriate for the target audience. No hallucinations.",
    score: 5,
    status: "pass"
  },
  {
    id: "trace-002",
    prompt: "Write a Python function to calculate Fibonacci sequence.",
    model_response: "def fib(n):\n  if n <= 1: return n\n  else: return fib(n-1) + fib(n-2)",
    judge_reasoning: "Correct implementation using recursion. However, it's inefficient for large N. Ideally should suggest memoization.",
    score: 4,
    status: "pass"
  },
  {
    id: "trace-003",
    prompt: "What is the capital of France?",
    model_response: "The capital of France is Paris.",
    judge_reasoning: "Factually correct.",
    score: 5,
    status: "pass"
  }
];

export default function Results() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Completed</Badge>
              <span className="text-sm text-muted-foreground">ID: eval_8f29a1b</span>
            </div>
            <h1 className="text-3xl font-display font-bold">Evaluation Results: GPT-4o vs Custom</h1>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="gap-2">
              <Share2 className="w-4 h-4" />
              Share
            </Button>
            <Button className="bg-black text-white gap-2">
              <Download className="w-4 h-4" />
              Export Traces
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <Card className="bg-zinc-50/50">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Overall Score</div>
              <div className="text-4xl font-display font-bold text-mint-600">92.4%</div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-50/50">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Total Samples</div>
              <div className="text-4xl font-display font-bold text-black">1,250</div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-50/50">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Avg Latency</div>
              <div className="text-4xl font-display font-bold text-black">450ms</div>
            </CardContent>
          </Card>
          <Card className="bg-zinc-50/50">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Cost</div>
              <div className="text-4xl font-display font-bold text-black">$4.20</div>
            </CardContent>
          </Card>
        </div>

        {/* Trace Viewer */}
        <Card className="border-border">
          <CardHeader className="border-b border-border bg-zinc-50/30">
            <CardTitle>Trace Viewer</CardTitle>
          </CardHeader>
          <div className="divide-y divide-border">
            {SAMPLE_TRACES.map((trace) => (
              <TraceRow key={trace.id} trace={trace} />
            ))}
          </div>
        </Card>
      </div>
    </Layout>
  );
}

function TraceRow({ trace }: { trace: any }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="bg-white transition-colors hover:bg-zinc-50/50">
      <div className="flex items-center p-4 gap-4">
        <CollapsibleTrigger asChild>
          <Button variant="ghost" size="sm" className="p-0 w-6 h-6 h-auto hover:bg-transparent">
            {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </Button>
        </CollapsibleTrigger>
        
        <div className="flex-1 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          <div className="md:col-span-2 font-mono text-xs text-muted-foreground">{trace.id}</div>
          <div className="md:col-span-8 text-sm font-medium truncate">{trace.prompt}</div>
          <div className="md:col-span-2 text-right">
             <Badge className={cn(
               "font-mono",
               trace.score >= 4 ? "bg-mint-100 text-mint-800 hover:bg-mint-200" : "bg-yellow-100 text-yellow-800"
             )}>
               Score: {trace.score}/5
             </Badge>
          </div>
        </div>
      </div>

      <CollapsibleContent>
        <div className="px-12 pb-6 pt-2 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Model Output</div>
              <div className="p-4 bg-zinc-50 rounded-md border border-border text-sm font-mono whitespace-pre-wrap">
                {trace.model_response}
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Judge Reasoning</div>
              <div className="p-4 bg-blue-50/50 rounded-md border border-blue-100 text-sm text-blue-900">
                {trace.judge_reasoning}
              </div>
            </div>
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
