import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from "recharts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowRightLeft, Check, ChevronRight, Code2, Copy, MessageSquare, RefreshCw, ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const RADAR_DATA = [
  { subject: 'Reasoning', A: 120, B: 110, fullMark: 150 },
  { subject: 'Coding', A: 98, B: 130, fullMark: 150 },
  { subject: 'Math', A: 86, B: 130, fullMark: 150 },
  { subject: 'Creativity', A: 99, B: 100, fullMark: 150 },
  { subject: 'Instruction', A: 85, B: 90, fullMark: 150 },
  { subject: 'Factuality', A: 65, B: 85, fullMark: 150 },
];

const COMPARISON_SCENARIOS = [
  {
    id: "coding-bfs",
    title: "Algorithm: BFS Implementation",
    category: "Coding",
    prompt: "Write a TypeScript function to perform a Breadth-First Search on a binary tree. Include type definitions.",
    model_a_output: `type TreeNode<T> = {
  val: T;
  left: TreeNode<T> | null;
  right: TreeNode<T> | null;
};

function bfs<T>(root: TreeNode<T> | null): T[] {
  if (!root) return [];
  
  const result: T[] = [];
  const queue: TreeNode<T>[] = [root];
  
  while (queue.length > 0) {
    const node = queue.shift()!;
    result.push(node.val);
    
    if (node.left) queue.push(node.left);
    if (node.right) queue.push(node.right);
  }
  
  return result;
}`,
    model_b_output: `interface Node<T> {
  value: T;
  left: Node<T> | null;
  right: Node<T> | null;
}

// Standard iterative BFS using a queue
const breadthFirstSearch = <T>(startNode: Node<T> | null): T[] => {
  if (startNode === null) return [];

  const values: T[] = [];
  const queue: Node<T>[] = [startNode];

  while (queue.length > 0) {
    // Shift is O(n) in JS arrays, technically O(1) with a real Queue
    const current = queue.shift(); 
    if (current) {
      values.push(current.value);
      if (current.left) queue.push(current.left);
      if (current.right) queue.push(current.right);
    }
  }
  return values;
};`,
    diff_notes: "Model A uses a simpler type definition. Model B includes a comment about the time complexity of array.shift()."
  },
  {
    id: "creative-haiku",
    title: "Creative: Tech Haiku",
    category: "Creative Writing",
    prompt: "Write a haiku about a database migration failing in production.",
    model_a_output: `Data flows like streams,
Schema change breaks the silence,
Pager duty screams.`,
    model_b_output: `Tables locked in fear,
Migration script has failed us,
Rollback is not clear.`,
    diff_notes: "Model A focuses on the alerting aspect. Model B focuses on the technical state (locks)."
  },
  {
    id: "logic-riddle",
    title: "Logic: The Two Doors",
    category: "Reasoning",
    prompt: "You are in a room with two doors. One leads to freedom, the other to death. There are two guards. One always tells the truth, the other always lies. You can ask one question to one guard. What do you ask?",
    model_a_output: "You should ask either guard: 'If I were to ask the other guard which door leads to freedom, what would he say?' \n\nThen, you pick the door OPPOSITE to what the guard tells you.",
    model_b_output: "Ask one guard: 'Which door would the other guard say leads to freedom?'\n\nThen choose the door that he does NOT point to. This works because the double negative (one truth, one lie) ensures the answer is always the false path.",
    diff_notes: "Both models correctly identify the classic solution. Model B explains the 'why' slightly more clearly."
  }
];

export default function Compare() {
  const [selectedScenario, setSelectedScenario] = useState(COMPARISON_SCENARIOS[0]);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-12">
        <div className="mb-10">
          <h1 className="text-4xl font-display font-bold mb-4">Model Comparison</h1>
          <p className="text-muted-foreground max-w-2xl">
            Analyze performance differences between models using quantitative benchmarks and qualitative side-by-side output comparisons.
          </p>
        </div>

        {/* Model Selectors - Sticky-ish or prominent */}
        <div className="flex flex-col md:flex-row gap-4 md:gap-8 items-center justify-center mb-12 bg-zinc-50/50 p-6 rounded-xl border border-border">
          <div className="w-full md:w-[300px]">
            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 block">Model A (Baseline)</label>
            <Select defaultValue="gpt4">
              <SelectTrigger className="h-12 text-lg font-bold bg-white">
                <SelectValue placeholder="Model A" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gpt4">GPT-4o</SelectItem>
                <SelectItem value="claude3">Claude 3.5 Sonnet</SelectItem>
                <SelectItem value="llama3">Llama 3 70B</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="bg-white p-2 rounded-full border border-border shadow-sm z-10 -my-3 md:my-0">
            <ArrowRightLeft className="w-5 h-5 text-muted-foreground" />
          </div>

          <div className="w-full md:w-[300px]">
            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 block">Model B (Candidate)</label>
            <Select defaultValue="claude3">
              <SelectTrigger className="h-12 text-lg font-bold bg-white">
                <SelectValue placeholder="Model B" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gpt4">GPT-4o</SelectItem>
                <SelectItem value="claude3">Claude 3.5 Sonnet</SelectItem>
                <SelectItem value="llama3">Llama 3 70B</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Tabs defaultValue="visual" className="w-full">
          <TabsList className="mb-8 bg-zinc-100 p-1 h-12 w-full md:w-auto flex md:inline-flex">
            <TabsTrigger value="visual" className="flex-1 md:flex-none h-10 px-6 font-medium">Output Comparison</TabsTrigger>
            <TabsTrigger value="metrics" className="flex-1 md:flex-none h-10 px-6 font-medium">Benchmark Metrics</TabsTrigger>
          </TabsList>

          {/* VISUAL / OUTPUT COMPARISON TAB */}
          <TabsContent value="visual" className="space-y-8 animate-in fade-in-50 duration-500">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Sidebar Scenario List */}
              <div className="lg:col-span-3 space-y-4">
                <div className="font-bold text-sm text-muted-foreground uppercase tracking-wider mb-2">Test Scenarios</div>
                <div className="space-y-2">
                  {COMPARISON_SCENARIOS.map((scenario) => (
                    <button
                      key={scenario.id}
                      onClick={() => setSelectedScenario(scenario)}
                      className={cn(
                        "w-full text-left p-4 rounded-lg border transition-all duration-200 flex flex-col gap-1",
                        selectedScenario.id === scenario.id 
                          ? "bg-mint-50 border-mint-200 ring-1 ring-mint-200" 
                          : "bg-white border-transparent hover:bg-zinc-50 hover:border-zinc-200"
                      )}
                    >
                      <span className={cn("font-bold text-sm", selectedScenario.id === scenario.id ? "text-mint-900" : "text-black")}>
                        {scenario.title}
                      </span>
                      <Badge variant="secondary" className="w-fit text-[10px] h-5 px-1.5 bg-white/50 border-zinc-200">
                        {scenario.category}
                      </Badge>
                    </button>
                  ))}
                </div>
                <Button variant="outline" className="w-full border-dashed border-zinc-300 text-muted-foreground hover:text-black hover:border-zinc-400">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Generate New Prompt
                </Button>
              </div>

              {/* Main Comparison Area */}
              <div className="lg:col-span-9">
                <Card className="h-full flex flex-col border-border shadow-sm">
                  <CardHeader className="pb-4 border-b border-border bg-zinc-50/30">
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-white rounded-md border border-border shadow-sm">
                        <MessageSquare className="w-5 h-5 text-mint-600" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">Prompt</div>
                        <CardTitle className="text-base font-medium leading-relaxed">{selectedScenario.prompt}</CardTitle>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="flex-1 p-0 grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border">
                    {/* Model A Output */}
                    <div className="flex flex-col min-h-[400px]">
                      <div className="p-3 border-b border-border bg-zinc-50/10 flex justify-between items-center sticky top-0">
                        <Badge variant="outline" className="bg-white font-mono text-xs">GPT-4o</Badge>
                        <Button variant="ghost" size="icon" className="h-6 w-6"><Copy className="w-3 h-3" /></Button>
                      </div>
                      <ScrollArea className="flex-1 p-6">
                        <pre className="font-mono text-sm whitespace-pre-wrap text-zinc-700 leading-relaxed">
                          {selectedScenario.model_a_output}
                        </pre>
                      </ScrollArea>
                      <div className="p-4 border-t border-border bg-zinc-50/30 flex justify-center gap-2">
                        <Button variant="outline" size="sm" className="h-8 hover:bg-red-50 hover:text-red-600 hover:border-red-200"><ThumbsDown className="w-3 h-3 mr-1" /> Worse</Button>
                        <Button variant="outline" size="sm" className="h-8 hover:bg-mint-50 hover:text-mint-700 hover:border-mint-200"><ThumbsUp className="w-3 h-3 mr-1" /> Better</Button>
                      </div>
                    </div>

                    {/* Model B Output */}
                    <div className="flex flex-col min-h-[400px]">
                      <div className="p-3 border-b border-border bg-zinc-50/10 flex justify-between items-center sticky top-0">
                        <Badge variant="outline" className="bg-white font-mono text-xs">Claude 3.5 Sonnet</Badge>
                        <Button variant="ghost" size="icon" className="h-6 w-6"><Copy className="w-3 h-3" /></Button>
                      </div>
                      <ScrollArea className="flex-1 p-6">
                        <pre className="font-mono text-sm whitespace-pre-wrap text-zinc-700 leading-relaxed">
                          {selectedScenario.model_b_output}
                        </pre>
                      </ScrollArea>
                      <div className="p-4 border-t border-border bg-zinc-50/30 flex justify-center gap-2">
                        <Button variant="outline" size="sm" className="h-8 hover:bg-red-50 hover:text-red-600 hover:border-red-200"><ThumbsDown className="w-3 h-3 mr-1" /> Worse</Button>
                        <Button variant="outline" size="sm" className="h-8 hover:bg-mint-50 hover:text-mint-700 hover:border-mint-200"><ThumbsUp className="w-3 h-3 mr-1" /> Better</Button>
                      </div>
                    </div>
                  </CardContent>
                  
                  <div className="p-4 bg-mint-50/30 border-t border-border text-sm flex gap-2 items-start">
                    <div className="mt-0.5 p-1 rounded-full bg-mint-100 text-mint-700">
                      <Check className="w-3 h-3" />
                    </div>
                    <div>
                      <span className="font-bold text-mint-900 block text-xs uppercase tracking-wider mb-0.5">Automated Analysis</span>
                      <span className="text-muted-foreground">{selectedScenario.diff_notes}</span>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* METRICS TAB */}
          <TabsContent value="metrics" className="animate-in fade-in-50 duration-500">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              {/* Radar Chart */}
              <Card className="border-border">
                <CardHeader>
                  <CardTitle>Guideline Performance</CardTitle>
                  <CardDescription>Visualizing strengths across 6 key dimensions</CardDescription>
                </CardHeader>
                <CardContent className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={RADAR_DATA}>
                      <PolarGrid stroke="#e5e7eb" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 12 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 150]} tick={false} axisLine={false} />
                      <Radar
                        name="GPT-4o"
                        dataKey="A"
                        stroke="#39E29D"
                        strokeWidth={3}
                        fill="#39E29D"
                        fillOpacity={0.2}
                      />
                      <Radar
                        name="Claude 3.5"
                        dataKey="B"
                        stroke="#000000"
                        strokeWidth={2}
                        fill="#000000"
                        fillOpacity={0.1}
                      />
                      <Legend />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Comparison Table */}
              <Card className="border-border">
                <CardHeader>
                  <CardTitle>Direct Benchmark Comparison</CardTitle>
                  <CardDescription>Head-to-head scores on standard open datasets</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Benchmark</TableHead>
                        <TableHead className="text-right text-mint-600 font-bold">GPT-4o</TableHead>
                        <TableHead className="text-right font-bold">Claude 3.5</TableHead>
                        <TableHead className="text-right">Diff</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell className="font-medium">MMLU-Pro</TableCell>
                        <TableCell className="text-right font-mono">88.7%</TableCell>
                        <TableCell className="text-right font-mono">85.4%</TableCell>
                        <TableCell className="text-right font-mono text-green-600 bg-green-50 rounded px-2">+3.3%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="font-medium">HumanEval+</TableCell>
                        <TableCell className="text-right font-mono">90.2%</TableCell>
                        <TableCell className="text-right font-mono">92.0%</TableCell>
                        <TableCell className="text-right font-mono text-red-500 bg-red-50 rounded px-2">-1.8%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="font-medium">GSM8K</TableCell>
                        <TableCell className="text-right font-mono">95.8%</TableCell>
                        <TableCell className="text-right font-mono">95.0%</TableCell>
                        <TableCell className="text-right font-mono text-green-600 bg-green-50 rounded px-2">+0.8%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="font-medium">MATH</TableCell>
                        <TableCell className="text-right font-mono">76.6%</TableCell>
                        <TableCell className="text-right font-mono">71.2%</TableCell>
                        <TableCell className="text-right font-mono text-green-600 bg-green-50 rounded px-2">+5.4%</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="font-medium">IFEval</TableCell>
                        <TableCell className="text-right font-mono">88.0%</TableCell>
                        <TableCell className="text-right font-mono">89.1%</TableCell>
                        <TableCell className="text-right font-mono text-red-500 bg-red-50 rounded px-2">-1.1%</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
