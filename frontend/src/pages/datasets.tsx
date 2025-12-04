import Layout from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Database, Search, Filter, Download, FileText, ArrowRight, Layers, Calendar, Info } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

// Mock Data for Datasets List
const DATASETS = [
  {
    id: "mmlu-pro",
    title: "MMLU-Pro",
    category: "General Knowledge",
    samples: 12000,
    description: "Massive Multitask Language Understanding with professional-grade questions across 57 subjects.",
    lastUpdated: "2 days ago",
    tags: ["academic", "reasoning", "multiple-choice"]
  },
  {
    id: "humaneval-plus",
    title: "HumanEval+",
    category: "Coding",
    samples: 164,
    description: "Enhanced version of HumanEval with more rigorous test cases to prevent overfitting.",
    lastUpdated: "1 week ago",
    tags: ["code", "python", "generation"]
  },
  {
    id: "gsm8k-hard",
    title: "GSM8K-Hard",
    category: "Math",
    samples: 8500,
    description: "Grade School Math 8K dataset with increased difficulty and reasoning steps.",
    lastUpdated: "3 weeks ago",
    tags: ["math", "chain-of-thought"]
  },
  {
    id: "truthful-qa",
    title: "TruthfulQA",
    category: "Safety",
    samples: 817,
    description: "Benchmark to measure whether a language model is truthful in generating answers to questions.",
    lastUpdated: "1 month ago",
    tags: ["safety", "hallucination"]
  }
];

// Mock Data for Dataset Samples (Table View)
const SAMPLES = [
  {
    id: "sample_001",
    prompt: "You are an auditor and as part of an audit engagement, you are tasked with reviewing and...",
    category: "Professional",
    difficulty: "Hard",
    reference: "[Reference Files Link]",
    tokens: 1420
  },
  {
    id: "sample_002",
    prompt: "You are the Finance Lead for an advisory client and are responsible for managing and controlling...",
    category: "Finance",
    difficulty: "Medium",
    reference: "[Reference Files Link]",
    tokens: 890
  },
  {
    id: "sample_003",
    prompt: "You are a Senior Staff Accountant at Aurisic. You have been tasked with preparing a detailed...",
    category: "Accounting",
    difficulty: "Hard",
    reference: "[Reference Files Link]",
    tokens: 2100
  },
  {
    id: "sample_004",
    prompt: "You are a mid-level Tax Preparer at an accounting firm. You have been given the task to complete an...",
    category: "Tax",
    difficulty: "Medium",
    reference: "[Reference Files Link]",
    tokens: 1250
  },
  {
    id: "sample_005",
    prompt: "As our Senior Staff Accountant in Financial Reporting & Assembly, you've been a critical part...",
    category: "Reporting",
    difficulty: "Easy",
    reference: "[Reference Files Link]",
    tokens: 650
  },
  {
    id: "sample_006",
    prompt: "You are an administrative operations lead in a government department responsible for citizen-...",
    category: "Government",
    difficulty: "Medium",
    reference: "[]",
    tokens: 980
  }
];

export default function Datasets() {
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const activeDataset = DATASETS.find(d => d.id === selectedDataset) || DATASETS[0];

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 h-[calc(100vh-64px)] flex flex-col">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-display font-bold">Dataset Viewer</h1>
            <p className="text-muted-foreground">Browse and inspect evaluation datasets.</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="gap-2">
              <FileText className="w-4 h-4" /> API Docs
            </Button>
            <Button className="bg-black text-white gap-2">
              <Database className="w-4 h-4" /> New Dataset
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">
          {/* Left Sidebar: Dataset List */}
          <div className="col-span-3 flex flex-col gap-4 h-full overflow-hidden">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Search datasets..." className="pl-9 bg-white" />
            </div>
            
            <div className="flex-1 overflow-y-auto pr-2 space-y-3">
              {DATASETS.map((dataset) => (
                <div 
                  key={dataset.id}
                  onClick={() => setSelectedDataset(dataset.id)}
                  className={cn(
                    "p-4 rounded-lg border cursor-pointer transition-all hover:shadow-sm group",
                    selectedDataset === dataset.id || (!selectedDataset && dataset.id === DATASETS[0].id)
                      ? "bg-mint-50/50 border-mint-200 ring-1 ring-mint-200" 
                      : "bg-white border-border hover:border-zinc-300"
                  )}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className={cn("font-bold text-sm", selectedDataset === dataset.id ? "text-mint-900" : "text-black")}>
                      {dataset.title}
                    </h3>
                    <Badge variant="secondary" className="text-[10px] h-5 px-1.5 bg-zinc-100 text-zinc-600">
                      {dataset.category}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
                    {dataset.description}
                  </p>
                  <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Layers className="w-3 h-3" /> {dataset.samples.toLocaleString()}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" /> {dataset.lastUpdated}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel: Dataset Details & Data Table */}
          <div className="col-span-9 flex flex-col gap-6 h-full overflow-hidden">
            {/* Dataset Header Info */}
            <Card className="shrink-0 bg-zinc-50/30 border-border">
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-bold font-display">{activeDataset.title}</h2>
                      <Badge variant="outline" className="bg-white border-zinc-200 text-zinc-700">
                        v1.2.0
                      </Badge>
                    </div>
                    <p className="text-muted-foreground max-w-2xl mb-4 text-sm">
                      {activeDataset.description}
                    </p>
                    <div className="flex gap-2">
                      {activeDataset.tags.map(tag => (
                        <Badge key={tag} variant="secondary" className="bg-white border border-zinc-200 text-zinc-600 hover:bg-zinc-50">
                          #{tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="flex flex-col gap-2 items-end">
                     <Button variant="outline" size="sm" className="h-8 gap-2 text-xs">
                        <Download className="w-3 h-3" /> Export CSV
                     </Button>
                     <div className="text-xs text-muted-foreground font-mono">
                        ID: {activeDataset.id}
                     </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Data Viewer Table */}
            <Card className="flex-1 border-border flex flex-col min-h-0 shadow-sm">
              <div className="p-3 border-b border-border flex justify-between items-center bg-zinc-50/30">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase text-muted-foreground tracking-wider">Split</span>
                    <Select defaultValue="train">
                      <SelectTrigger className="h-8 w-[120px] bg-white">
                        <SelectValue placeholder="Select split" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="train">train (80%)</SelectItem>
                        <SelectItem value="test">test (10%)</SelectItem>
                        <SelectItem value="val">validation (10%)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="h-4 w-px bg-border"></div>
                  <span className="text-xs text-muted-foreground font-mono">
                    {activeDataset.samples} rows
                  </span>
                </div>
                
                <div className="flex gap-2">
                   <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Filter className="w-4 h-4 text-muted-foreground" /></Button>
                   <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Info className="w-4 h-4 text-muted-foreground" /></Button>
                </div>
              </div>

              <div className="flex-1 overflow-auto bg-white">
                <Table>
                  <TableHeader className="sticky top-0 z-10 bg-zinc-50">
                    <TableRow className="border-b border-border hover:bg-transparent">
                      <TableHead className="w-[100px] text-muted-foreground font-mono text-xs h-10">
                        <div className="flex flex-col gap-0.5 py-2">
                          <span className="font-bold text-black">ID</span>
                          <span className="text-[10px]">string</span>
                        </div>
                      </TableHead>
                      <TableHead className="min-w-[300px] text-muted-foreground font-mono text-xs h-10">
                        <div className="flex flex-col gap-0.5 py-2">
                          <span className="font-bold text-black">Prompt</span>
                          <span className="text-[10px] flex items-center gap-1">
                            string <div className="h-1 w-16 bg-zinc-200 rounded-full overflow-hidden"><div className="h-full w-1/3 bg-zinc-400"></div></div>
                          </span>
                        </div>
                      </TableHead>
                      <TableHead className="w-[150px] text-muted-foreground font-mono text-xs h-10">
                        <div className="flex flex-col gap-0.5 py-2">
                          <span className="font-bold text-black">Category</span>
                          <span className="text-[10px]">string • classes</span>
                        </div>
                      </TableHead>
                      <TableHead className="w-[150px] text-muted-foreground font-mono text-xs h-10">
                        <div className="flex flex-col gap-0.5 py-2">
                           <span className="font-bold text-black">Reference</span>
                           <span className="text-[10px]">list</span>
                        </div>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {SAMPLES.map((row, i) => (
                      <TableRow key={row.id} className="border-b border-border hover:bg-mint-50/30 group cursor-pointer transition-colors">
                        <TableCell className="font-mono text-xs text-muted-foreground align-top py-3 group-hover:text-black">
                          {row.id}
                        </TableCell>
                        <TableCell className="text-xs text-black align-top py-3 leading-relaxed">
                          {row.prompt}
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground align-top py-3">
                          <span className="px-2 py-0.5 rounded bg-zinc-100 text-zinc-700 border border-zinc-200 inline-block mb-1">
                            {row.category}
                          </span>
                          <div className="w-full h-1.5 bg-zinc-100 rounded-full overflow-hidden mt-1" title="Difficulty">
                            <div 
                              className={cn(
                                "h-full", 
                                row.difficulty === "Hard" ? "bg-red-500 w-[90%]" : 
                                row.difficulty === "Medium" ? "bg-yellow-500 w-[60%]" : "bg-green-500 w-[30%]"
                              )}
                            />
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground align-top py-3">
                          {row.reference === "[]" ? "[]" : (
                            <span className="text-blue-600 hover:underline">{row.reference}</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              {/* Pagination Footer */}
              <div className="p-2 border-t border-border bg-zinc-50/30 flex justify-center items-center gap-4 text-xs text-muted-foreground">
                <Button variant="ghost" size="sm" disabled className="h-7 px-2 text-xs">Previous</Button>
                <span className="text-black font-medium">Page 1 of 12</span>
                <Button variant="ghost" size="sm" className="h-7 px-2 text-xs">Next</Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
}
