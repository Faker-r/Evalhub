import Layout from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ExternalLink, Search, ChevronLeft, ChevronRight, ChevronDown, Download, Box, ChevronUp, Database } from "lucide-react";
import { useState, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { cn } from "@/lib/utils";

const VALID_BENCHMARK_TAGS = [
  "bias", "biology", "biomedical", "chemistry", "classification", "code-generation",
  "commonsense", "conversational", "dialog", "dialogue", "emotion", "ethics", "factuality",
  "general-knowledge", "generation", "geography", "graduate-level", "health", "history",
  "instruction-following", "justice", "knowledge", "language", "language-modeling",
  "language-understanding", "legal", "long-context", "math", "medical", "morality",
  "multi-turn", "multilingual", "multimodal", "multiple-choice", "narrative", "nli",
  "physical-commonsense", "physics", "qa", "question-answering", "reading-comprehension",
  "reasoning", "safety", "science", "scientific", "summarization", "symbolic", "translation",
  "utilitarianism", "virtue", "coding", "information-retrieval", "retrieval",
  "text-generation", "text-classification", "token-classification", "causal-lm",
].sort();

const LANGUAGE_FILTERS = [
  { code: "en", label: "english", color: "bg-blue-100 text-blue-800" },
  { code: "zh", label: "chinese", color: "bg-red-100 text-red-800" },
  { code: "ar", label: "arabic", color: "bg-green-100 text-green-800" },
  { code: "fr", label: "french", color: "bg-purple-100 text-purple-800" },
  { code: "ru", label: "russian", color: "bg-pink-100 text-pink-800" },
  { code: "es", label: "spanish", color: "bg-yellow-100 text-yellow-800" },
  { code: "de", label: "german", color: "bg-indigo-100 text-indigo-800" },
  { code: "hi", label: "hindi", color: "bg-orange-100 text-orange-800" },
  { code: "ja", label: "japanese", color: "bg-rose-100 text-rose-800" },
  { code: "ko", label: "korean", color: "bg-cyan-100 text-cyan-800" },
  { code: "pt", label: "portuguese", color: "bg-lime-100 text-lime-800" },
  { code: "it", label: "italian", color: "bg-teal-100 text-teal-800" },
  { code: "nl", label: "dutch", color: "bg-amber-100 text-amber-800" },
  { code: "pl", label: "polish", color: "bg-fuchsia-100 text-fuchsia-800" },
  { code: "tr", label: "turkish", color: "bg-emerald-100 text-emerald-800" },
  { code: "vi", label: "vietnamese", color: "bg-sky-100 text-sky-800" },
  { code: "th", label: "thai", color: "bg-violet-100 text-violet-800" },
  { code: "id", label: "indonesian", color: "bg-stone-100 text-stone-800" },
  { code: "uk", label: "ukrainian", color: "bg-blue-100 text-blue-800" },
  { code: "he", label: "hebrew", color: "bg-indigo-100 text-indigo-800" },
  { code: "fa", label: "persian", color: "bg-purple-100 text-purple-800" },
  { code: "bn", label: "bengali", color: "bg-green-100 text-green-800" },
  { code: "te", label: "telugu", color: "bg-orange-100 text-orange-800" },
  { code: "ta", label: "tamil", color: "bg-red-100 text-red-800" },
  { code: "sw", label: "swahili", color: "bg-teal-100 text-teal-800" },
];

const TAG_STYLE = "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-transparent";

function parseTags(tags: string[] | null) {
  if (!tags) return { benchmarkTags: [], languageTags: [], arxivId: null };
  
  const benchmarkTags: string[] = [];
  const languageTags: string[] = [];
  let arxivId: string | null = null;
  
  tags.forEach(tag => {
    if (tag.startsWith('language:')) {
      const langCode = tag.split(':')[1];
      const langFilter = LANGUAGE_FILTERS.find(l => l.code === langCode);
      languageTags.push(langFilter?.label || langCode);
    } else if (tag.startsWith('arxiv:')) {
      arxivId = tag.replace('arxiv:', '');
    } else {
      benchmarkTags.push(tag);
    }
  });
  
  return { benchmarkTags, languageTags, arxivId };
}

export default function Benchmarks() {
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAllLanguages, setShowAllLanguages] = useState(false);
  const [showAllTags, setShowAllTags] = useState(false);
  const [selectedBenchmark, setSelectedBenchmark] = useState<any>(null);
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set());
  const [taskDetails, setTaskDetails] = useState<Record<string, any>>({});
  const [loadingTasks, setLoadingTasks] = useState<Set<string>>(new Set());

  const ITEMS_PER_PAGE = 12;

  const { data, isLoading } = useQuery({
    queryKey: ['benchmarks', searchQuery, selectedLanguages, selectedTags],
    queryFn: () => {
      const languageTags = selectedLanguages.map(code => `language:${code}`);
      const allTags = [...languageTags, ...selectedTags];
      
      return apiClient.getBenchmarks({
        page: 1,
        page_size: 100,
        search: searchQuery || undefined,
        tags: allTags.length > 0 ? allTags : undefined,
      });
    },
  });

  const allBenchmarks = data?.benchmarks || [];
  const totalPages = Math.max(1, Math.ceil(allBenchmarks.length / ITEMS_PER_PAGE));
  
  const currentBenchmarks = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return allBenchmarks.slice(start, start + ITEMS_PER_PAGE);
  }, [allBenchmarks, currentPage]);

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedLanguages, selectedTags, searchQuery]);

  const toggleLanguage = (code: string) => {
    setSelectedLanguages(prev =>
      prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code]
    );
  };

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  const toggleTask = async (taskName: string) => {
    const newExpanded = new Set(expandedTasks);
    if (newExpanded.has(taskName)) {
      newExpanded.delete(taskName);
      setExpandedTasks(newExpanded);
    } else {
      newExpanded.add(taskName);
      setExpandedTasks(newExpanded);
      
      if (!taskDetails[taskName]) {
        setLoadingTasks(prev => new Set(prev).add(taskName));
        try {
          const details = await apiClient.getTaskDetails(taskName);
          setTaskDetails(prev => ({ ...prev, [taskName]: details }));
        } catch (error) {
          console.error('Failed to fetch task details:', error);
        } finally {
          setLoadingTasks(prev => {
            const newSet = new Set(prev);
            newSet.delete(taskName);
            return newSet;
          });
        }
      }
    }
  };

  const visibleLanguages = showAllLanguages ? LANGUAGE_FILTERS : LANGUAGE_FILTERS.slice(0, 8);
  const visibleTags = showAllTags ? VALID_BENCHMARK_TAGS : VALID_BENCHMARK_TAGS.slice(0, 15);

  const NestedValue = ({ value, depth = 0 }: { value: any; depth?: number }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    
    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">null</span>;
    }
    
    if (typeof value === 'object' && !Array.isArray(value)) {
      const entries = Object.entries(value);
      if (entries.length === 0) {
        return <span className="text-gray-400">{'{}'}</span>;
      }
      
      return (
        <div className="space-y-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            <span>{entries.length} {entries.length === 1 ? 'field' : 'fields'}</span>
          </button>
          {isExpanded && (
            <div className="ml-4 pl-2 border-l-2 border-gray-200 space-y-1">
              {entries.map(([key, val]) => (
                <div key={key} className="text-xs">
                  <span className="font-semibold text-gray-700">{key}:</span>{' '}
                  <NestedValue value={val} depth={depth + 1} />
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="text-gray-400">[]</span>;
      }
      
      return (
        <div className="space-y-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            <span>{value.length} {value.length === 1 ? 'item' : 'items'}</span>
          </button>
          {isExpanded && (
            <div className="ml-4 pl-2 border-l-2 border-gray-200 space-y-1">
              {value.map((item, idx) => (
                <div key={idx} className="text-xs">
                  <span className="text-gray-500">[{idx}]:</span>{' '}
                  <NestedValue value={item} depth={depth + 1} />
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }
    
    return <span className="text-gray-900 font-mono text-xs">{String(value)}</span>;
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold font-display mb-2">
            <span className="text-mint-600">Lighteval</span> Tasks Explorer
          </h1>
          <p className="text-muted-foreground">
            Browse tasks by language, tags and search the task descriptions.
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            {allBenchmarks.length} tasks
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-medium">Search</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search in module path, tags, abstract..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="text-sm pl-9"
                  />
                </div>
              </CardContent>
            </Card>

            {LANGUAGE_FILTERS.length > 0 && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium">Languages</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    {visibleLanguages.map((lang) => (
                      <div key={lang.code} className="flex items-center space-x-2">
                        <Checkbox
                          id={`lang-${lang.code}`}
                          checked={selectedLanguages.includes(lang.code)}
                          onCheckedChange={() => toggleLanguage(lang.code)}
                        />
                        <Label htmlFor={`lang-${lang.code}`} className="text-xs font-normal leading-none cursor-pointer capitalize">
                          <Badge variant="secondary" className={cn("font-normal border-transparent", lang.color)}>
                            {lang.label}
                          </Badge>
                        </Label>
                      </div>
                    ))}
                  </div>
                  {LANGUAGE_FILTERS.length > 8 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowAllLanguages(!showAllLanguages)}
                      className="w-full text-xs mt-2"
                    >
                      {showAllLanguages ? "Show less" : "Show all languages"}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-medium">Benchmark type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {visibleTags.map((tag) => (
                    <div key={tag} className="flex items-start space-x-2">
                      <Checkbox
                        id={`tag-${tag}`}
                        checked={selectedTags.includes(tag)}
                        onCheckedChange={() => toggleTag(tag)}
                        className="mt-0.5"
                      />
                      <Label htmlFor={`tag-${tag}`} className="text-sm font-normal leading-tight cursor-pointer break-words">
                        {tag}
                      </Label>
                    </div>
                  ))}
                </div>
                {VALID_BENCHMARK_TAGS.length > 15 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowAllTags(!showAllTags)}
                    className="w-full text-xs mt-2"
                  >
                    {showAllTags ? "Show less" : `Show ${VALID_BENCHMARK_TAGS.length - 15} more`}
                  </Button>
                )}
              </CardContent>
            </Card>
            
            <div className="text-xs text-muted-foreground">
              Tip: use the filters and search together. Results update live.
            </div>
          </div>

          {/* Cards */}
          <div className="lg:col-span-3">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
                <p className="mt-4 text-muted-foreground">Loading benchmarks...</p>
              </div>
            ) : allBenchmarks.length === 0 ? (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <p className="text-muted-foreground">No benchmarks found matching your filters.</p>
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-6">
                  {currentBenchmarks.map((benchmark) => {
                    const { benchmarkTags, languageTags, arxivId } = parseTags(benchmark.tags);
                    const description = benchmark.description || benchmark.dataset_name || "No description available";
                    const allTags = [...benchmarkTags, ...languageTags];
                    const visibleCardTags = allTags.slice(0, 5);
                    const tasks = benchmark.tasks || [];
                    
                    return (
                      <Card key={benchmark.id} className="hover-elevate hover-border-trace flex flex-col h-[450px]">
                        <CardHeader className="pb-2 space-y-2.5 flex-shrink-0">
                          <CardTitle className="text-lg font-bold leading-tight break-words">
                            {benchmark.dataset_name}
                          </CardTitle>
                          
                          {visibleCardTags.length > 0 && (
                            <div className="flex flex-wrap gap-1.5">
                              {visibleCardTags.map((tag, idx) => (
                                <Badge key={idx} variant="secondary" className={cn("px-2.5 py-0.5 text-xs font-normal border-0", TAG_STYLE)}>
                                  {tag}
                                </Badge>
                              ))}
                              {allTags.length > 5 && (
                                <button
                                  onClick={() => setSelectedBenchmark(benchmark)}
                                  className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-700 hover:bg-gray-200"
                                >
                                  +{allTags.length - 5} more
                                </button>
                              )}
                            </div>
                          )}
                        </CardHeader>
                        
                        <CardContent className="flex-1 flex flex-col pt-0 overflow-hidden">
                          <div className="text-sm text-muted-foreground break-words mb-1 line-clamp-3">
                            {description}
                          </div>
                          
                          {description.length > 120 && (
                            <Button
                              variant="ghost"
                              className="h-auto p-0 text-xs text-muted-foreground hover:text-foreground mb-2 w-fit"
                              onClick={() => setSelectedBenchmark(benchmark)}
                            >
                              <ChevronDown className="w-3 h-3 mr-1" />
                              Show more
                            </Button>
                          )}
                        
                          <div className="mt-auto space-y-2 flex-shrink-0">
                            {(benchmark.downloads || benchmark.estimated_input_tokens || benchmark.dataset_size) && (
                              <div className="flex items-center gap-4 text-xs text-muted-foreground pb-2">
                                {benchmark.downloads && (
                                  <div className="flex items-center gap-1" title="Downloads">
                                    <Download className="w-3 h-3" />
                                    <span>{benchmark.downloads.toLocaleString()}</span>
                                  </div>
                                )}
                                {benchmark.estimated_input_tokens && (
                                  <div className="flex items-center gap-1" title="Estimated Input Tokens">
                                    <Box className="w-3 h-3" />
                                    <span>{benchmark.estimated_input_tokens.toLocaleString()} tokens</span>
                                  </div>
                                )}
                                {benchmark.dataset_size && (
                                  <div className="flex items-center gap-1" title="Dataset Rows">
                                    <Database className="w-3 h-3" />
                                    <span>{benchmark.dataset_size.toLocaleString()} rows</span>
                                  </div>
                                )}
                              </div>
                            )}

                            <div className="pt-3 border-t">
                              <p className="text-[10px] text-muted-foreground uppercase font-semibold mb-1.5">RUN USING LIGHTEVAL:</p>
                              <div className="flex flex-wrap gap-1.5 max-h-[70px] overflow-hidden">
                                {tasks.map((task: string, idx: number) => (
                                  <div key={idx} className="bg-mint-50 rounded-md px-2 py-0.5 border border-mint-100">
                                    <code className="text-xs text-mint-700 font-mono break-all">{task}</code>
                                  </div>
                                ))}
                              </div>
                              {tasks.length > 0 && (
                                <button
                                  onClick={() => setSelectedBenchmark(benchmark)}
                                  className="text-xs text-mint-700 hover:text-mint-800 font-medium hover:underline mt-1.5"
                                >
                                  View all {tasks.length} tasks
                                </button>
                              )}
                            </div>
                          </div>
                        </CardContent>
                        
                        <CardFooter className="pt-2 pb-3 text-xs text-blue-600 gap-3 border-t bg-muted/5 flex-shrink-0">
                          <a 
                            href={benchmark.hf_repo.startsWith('http') ? benchmark.hf_repo : `https://huggingface.co/datasets/${benchmark.hf_repo}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 hover:underline font-medium"
                          >
                            source
                            <ExternalLink className="w-3 h-3" />
                          </a>
                          
                          {arxivId && (
                            <>
                              <span className="text-muted-foreground">|</span>
                              <a 
                                href={`https://arxiv.org/abs/${arxivId}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 hover:underline font-medium"
                              >
                                paper
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </>
                          )}
                        </CardFooter>
                      </Card>
                    );
                  })}
                </div>

                {totalPages > 1 && (
                  <div className="flex justify-center mt-8">
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="w-4 h-4 mr-1" />
                        Previous
                      </Button>
                      <span className="text-sm font-medium mx-2">
                        Page {currentPage} of {totalPages}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                      >
                        Next
                        <ChevronRight className="w-4 h-4 ml-1" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Modal */}
      <Dialog open={!!selectedBenchmark} onOpenChange={() => setSelectedBenchmark(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          {selectedBenchmark && (
            <>
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold break-words pr-6">
                  {selectedBenchmark.dataset_name}
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-6 mt-4">
                {(() => {
                  const { benchmarkTags, languageTags, arxivId } = parseTags(selectedBenchmark.tags);
                  const allTags = [...benchmarkTags, ...languageTags];
                  
                  return (
                    <>
                      {allTags.length > 0 && (
                        <div>
                          <h3 className="text-sm font-semibold mb-2">Tags</h3>
                          <div className="flex flex-wrap gap-1.5">
                            {allTags.map((tag, idx) => (
                              <Badge key={idx} variant="secondary" className={cn("px-2.5 py-0.5 text-xs font-normal border-0", TAG_STYLE)}>
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      <div>
                        <h3 className="text-sm font-semibold mb-2">Description</h3>
                        <p className="text-sm text-muted-foreground break-words">
                          {selectedBenchmark.description || selectedBenchmark.dataset_name || "No description available"}
                        </p>
                      </div>

                      {(selectedBenchmark.downloads || selectedBenchmark.estimated_input_tokens) && (
                        <div>
                          <h3 className="text-sm font-semibold mb-2">Metrics</h3>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            {selectedBenchmark.downloads && (
                              <div className="flex items-center gap-2">
                                <Download className="w-4 h-4" />
                                <span>{selectedBenchmark.downloads.toLocaleString()} downloads</span>
                              </div>
                            )}
                            {selectedBenchmark.estimated_input_tokens && (
                              <div className="flex items-center gap-2">
                                <Box className="w-4 h-4" />
                                <span>{selectedBenchmark.estimated_input_tokens.toLocaleString()} tokens</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {selectedBenchmark.tasks?.length > 0 && (
                        <div>
                          <h3 className="text-sm font-semibold mb-2">Run using Lighteval ({selectedBenchmark.tasks.length} tasks)</h3>
                          <div className="space-y-2">
                            {selectedBenchmark.tasks.map((task: string) => (
                              <div key={task} className="border border-gray-200 rounded-md">
                                <button
                                  onClick={() => toggleTask(task)}
                                  className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
                                >
                                  <code className="text-xs text-mint-700 font-mono break-all">{task}</code>
                                  {expandedTasks.has(task) ? (
                                    <ChevronUp className="w-4 h-4 text-gray-500 flex-shrink-0 ml-2" />
                                  ) : (
                                    <ChevronDown className="w-4 h-4 text-gray-500 flex-shrink-0 ml-2" />
                                  )}
                                </button>
                                {expandedTasks.has(task) && (
                                  <div className="px-3 pb-3 border-t border-gray-100">
                                    {loadingTasks.has(task) ? (
                                      <div className="text-xs text-gray-500 py-2">Loading task details...</div>
                                    ) : taskDetails[task] ? (
                                      <div className="mt-2 space-y-2">
                                        {Object.entries(taskDetails[task]).map(([key, value]) => (
                                          <div key={key} className="text-xs">
                                            <span className="font-semibold text-gray-700">{key}:</span>{' '}
                                            <NestedValue value={value} />
                                          </div>
                                        ))}
                                      </div>
                                    ) : (
                                      <div className="text-xs text-red-500 py-2">Failed to load task details</div>
                                    )}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-4 pt-4 border-t">
                        <a 
                          href={selectedBenchmark.hf_repo.startsWith('http') ? selectedBenchmark.hf_repo : `https://huggingface.co/datasets/${selectedBenchmark.hf_repo}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-blue-600 hover:underline font-medium"
                        >
                          View on Hugging Face
                          <ExternalLink className="w-4 h-4" />
                        </a>
                        
                        {arxivId && (
                          <>
                            <span className="text-muted-foreground">|</span>
                            <a 
                              href={`https://arxiv.org/abs/${arxivId}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-blue-600 hover:underline font-medium"
                            >
                              View Paper
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          </>
                        )}
                      </div>
                    </>
                  );
                })()}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </Layout>
  );
}
