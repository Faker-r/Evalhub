import Layout from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { ExternalLink, Search, ChevronLeft, ChevronRight, ChevronDown, ChevronUp, Download, Box } from "lucide-react";
import { useState, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { cn } from "@/lib/utils";

// Valid benchmark type tags from Lighteval (backend/scripts/benchmark_utils.py)
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

// Language codes that map to language:XX tags with specific colors for filters
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

export default function Benchmarks() {
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAllLanguages, setShowAllLanguages] = useState(false);
  const [showAllTags, setShowAllTags] = useState(false);
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<number>>(new Set());
  const [expandedTagLists, setExpandedTagLists] = useState<Set<number>>(new Set());
  
  // Adjusted to 100 to meet backend limit (ge=1, le=100)
  const FETCH_PAGE_SIZE = 100;
  const ITEMS_PER_PAGE = 12;


  // Fetch benchmarks
  const { data, isLoading } = useQuery({
    queryKey: ['benchmarks', searchQuery, selectedLanguages, selectedTags], // Refetch when filters change
    queryFn: () => {
      // Convert selected languages to language:XX format and combine with selected tags
      const languageTags = selectedLanguages.map(code => `language:${code}`);
      const allTags = [...languageTags, ...selectedTags];
      
      return apiClient.getBenchmarks({
        page: 1,
        page_size: FETCH_PAGE_SIZE,
        search: searchQuery || undefined,
        tags: allTags.length > 0 ? allTags : undefined,
      });
    },
  });

  const allBenchmarks = data?.benchmarks || [];

  // Get all tags separated by type, excluding arxiv tags which are handled separately
  const getAllTagsForDisplay = (tags: string[] | null) => {
    if (!tags) return { benchmarkTags: [], languageTags: [], arxivId: null };
    
    const benchmarkTags: string[] = [];
    const languageTags: string[] = [];
    let arxivId: string | null = null;
    
    tags.forEach(tag => {
      if (tag.startsWith('language:')) {
        // Extract just the language name for display
        const langCode = tag.split(':')[1];
        const langFilter = LANGUAGE_FILTERS.find(l => l.code === langCode);
        if (langFilter) {
          languageTags.push(langFilter.label);
        } else {
            languageTags.push(langCode);
        }
      } else if (tag.startsWith('arxiv:')) {
          arxivId = tag.replace('arxiv:', '');
      } else {
        benchmarkTags.push(tag);
      }
    });
    
    return { benchmarkTags, languageTags, arxivId };
  };
  
  // Unified tag style for all tags in the card
  const TAG_STYLE = "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-transparent";

  // Client-side Pagination
  const totalItems = useMemo(() => allBenchmarks.length, [allBenchmarks]);
  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(totalItems / ITEMS_PER_PAGE)),
    [totalItems]
  );
  
  const currentBenchmarks = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return allBenchmarks.slice(start, start + ITEMS_PER_PAGE);
  }, [allBenchmarks, currentPage]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedLanguages, selectedTags, searchQuery]);

  // Generic toggle function for string arrays
  const createToggle = (setter: React.Dispatch<React.SetStateAction<string[]>>) => 
    (value: string) => {
      setter(prev =>
        prev.includes(value)
          ? prev.filter(v => v !== value)
          : [...prev, value]
      );
    };

  const toggleLanguage = createToggle(setSelectedLanguages);
  const toggleTag = createToggle(setSelectedTags);

  // Generic toggle function for Set<number>
  const createSetToggle = (setter: React.Dispatch<React.SetStateAction<Set<number>>>) =>
    (id: number) => {
      setter(prev => {
        const newSet = new Set(prev);
        if (newSet.has(id)) {
          newSet.delete(id);
        } else {
          newSet.add(id);
        }
        return newSet;
      });
    };

  const toggleDescriptionExpansion = createSetToggle(setExpandedDescriptions);
  const toggleTagListExpansion = createSetToggle(setExpandedTagLists);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
  };

  // Description is already cleaned by the backend, just use it directly
  const getDescription = (benchmark: any) => {
    return benchmark.description || benchmark.dataset_name || "No description available";
  };

  // Get visible language filters
  // Show first 8 languages always, plus any that are currently selected or available in data
  const displayedLanguageFilters = LANGUAGE_FILTERS;
  const visibleLanguages = showAllLanguages 
    ? displayedLanguageFilters 
    : displayedLanguageFilters.slice(0, 8);

  // Show all valid benchmark tags
  const displayedTags = showAllTags ? VALID_BENCHMARK_TAGS : VALID_BENCHMARK_TAGS.slice(0, 15);

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold font-display mb-2">
            <span className="text-mint-600">Lighteval</span> Tasks Explorer
          </h1>
          <p className="text-muted-foreground">
            Browse tasks by language, tags and search the task descriptions.
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            {totalItems} tasks
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Filters */}
          <div className="lg:col-span-1 space-y-6">
            {/* Search */}
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
                    onChange={(e) => handleSearch(e.target.value)}
                    className="text-sm pl-9"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Languages */}
            {displayedLanguageFilters.length > 0 && (
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
                          <Label
                            htmlFor={`lang-${lang.code}`}
                            className="text-xs font-normal leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer capitalize"
                          >
                              <Badge variant="secondary" className={cn("font-normal border-transparent", lang.color)}>
                                {lang.label}
                              </Badge>
                          </Label>
                        </div>
                      ))}
                    </div>
                     {displayedLanguageFilters.length > 8 && (
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

            {/* Benchmark Type / Tags */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-medium">Benchmark type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {displayedTags.map((tag) => (
                    <div key={tag} className="flex items-start space-x-2">
                      <Checkbox
                        id={`tag-${tag}`}
                        checked={selectedTags.includes(tag)}
                        onCheckedChange={() => toggleTag(tag)}
                        className="mt-0.5"
                      />
                      <Label
                        htmlFor={`tag-${tag}`}
                        className="text-sm font-normal leading-tight peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer break-words"
                      >
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

          {/* Main Content - Benchmark Cards */}
          <div className="lg:col-span-3">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
                <p className="mt-4 text-muted-foreground">Loading benchmarks...</p>
              </div>
            ) : allBenchmarks.length === 0 ? (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <p className="text-muted-foreground">
                    No benchmarks found matching your filters.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <>
                {/* Benchmark Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-6">
                  {currentBenchmarks.map((benchmark) => {
                    const isDescriptionExpanded = expandedDescriptions.has(benchmark.id);
                    const isTagListExpanded = expandedTagLists.has(benchmark.id);
                    const description = getDescription(benchmark);
                    const hasLongDescription = description && description.length > 150;
                    const { benchmarkTags, languageTags, arxivId } = getAllTagsForDisplay(benchmark.tags);
                    
                    return (
                      <Card key={benchmark.id} className="hover:shadow-md transition-shadow flex flex-col overflow-hidden h-full">
                        <CardHeader className="pb-3 break-words space-y-3">
                          <div className="flex items-start justify-between gap-2">
                            <CardTitle className="text-lg font-bold flex items-center gap-2 break-words overflow-hidden leading-tight">
                              <span className="break-words">{benchmark.task_name}</span>
                            </CardTitle>
                          </div>
                          
                          {/* Tags */}
                          {(() => {
                            const allDisplayTags = [...benchmarkTags, ...languageTags];
                            const hasDisplayTags = allDisplayTags.length > 0;
                            
                            if (!hasDisplayTags) return null;
                            
                            const visibleCount = 5; 
                            const showExpandedTags = isTagListExpanded;
                            const visibleBenchmarkTags = showExpandedTags ? benchmarkTags : benchmarkTags.slice(0, Math.min(visibleCount - languageTags.length, benchmarkTags.length));
                            const visibleLanguageTags = showExpandedTags ? languageTags : languageTags;
                            const hasMoreTags = benchmarkTags.length + languageTags.length > visibleCount;
                            
                            return (
                              <div className="flex flex-wrap gap-1.5 align-top">
                                {/* Benchmark type tags */}
                                {visibleBenchmarkTags.map((tag, idx) => (
                                  <Badge
                                    key={`bench-${idx}`}
                                    variant="secondary"
                                    className={cn(
                                      "px-2.5 py-0.5 text-xs font-normal border-0",
                                      TAG_STYLE
                                    )}
                                  >
                                    {tag}
                                  </Badge>
                                ))}
                                
                                {/* Language tags */}
                                {visibleLanguageTags.map((tag, idx) => (
                                  <Badge
                                    key={`lang-${idx}`}
                                    variant="secondary" 
                                    className={cn(
                                      "px-2.5 py-0.5 text-xs font-normal border-0",
                                      TAG_STYLE
                                    )}
                                  >
                                    {tag}
                                  </Badge>
                                ))}
                                
                                {hasMoreTags && !showExpandedTags && (
                                  <button
                                    onClick={() => toggleTagListExpansion(benchmark.id)}
                                    className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-normal bg-gray-100 text-gray-700 hover:bg-gray-200 cursor-pointer"
                                  >
                                    +{allDisplayTags.length - visibleCount} more
                                  </button>
                                )}
                                
                                {showExpandedTags && (
                                  <button
                                    onClick={() => toggleTagListExpansion(benchmark.id)}
                                    className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-normal bg-gray-100 text-gray-700 hover:bg-gray-200 cursor-pointer"
                                  >
                                    <ChevronUp className="w-3 h-3 mr-1" />
                                    Show less
                                  </button>
                                )}
                              </div>
                            );
                          })()}
                        </CardHeader>
                        
                        <CardContent className="flex-1 flex flex-col pt-0">
                          <div className={cn(
                            "text-sm text-muted-foreground mb-4 break-words overflow-hidden",
                            !isDescriptionExpanded && "line-clamp-4"
                          )}>
                             {description}
                          </div>
                          
                          {hasLongDescription && (
                            <div className="mb-4">
                                <Button
                                variant="ghost"
                                className="h-auto p-0 text-xs text-muted-foreground hover:text-foreground cursor-pointer"
                                onClick={() => toggleDescriptionExpansion(benchmark.id)}
                                >
                                {isDescriptionExpanded ? (
                                    <>
                                        <ChevronUp className="w-3 h-3 mr-1" />
                                        Show less
                                    </>
                                ) : (
                                    <>
                                        <ChevronDown className="w-3 h-3 mr-1" />
                                        Show more
                                    </>
                                )}
                                </Button>
                            </div>
                          )}
                        
                          <div className="mt-auto space-y-4">
                            {/* Metrics */}
                            {(benchmark.downloads !== null || benchmark.estimated_input_tokens !== null) && (
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                    {benchmark.downloads !== null && (
                                        <div className="flex items-center gap-1" title="Downloads">
                                            <Download className="w-3 h-3" />
                                            <span>{benchmark.downloads.toLocaleString()}</span>
                                        </div>
                                    )}
                                    {benchmark.estimated_input_tokens !== null && (
                                        <div className="flex items-center gap-1" title="Estimated Input Tokens">
                                            <Box className="w-3 h-3" />
                                            <span>{benchmark.estimated_input_tokens.toLocaleString()} tokens</span>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Run using Lighteval button */}
                            <div className="pt-2 border-t">
                                <p className="text-[10px] text-muted-foreground uppercase font-semibold mb-2">RUN USING LIGHTEVAL:</p>
                                <div className="bg-mint-50 rounded-md p-2 border border-mint-100 w-fit max-w-[90%]">
                                    <code className="text-xs text-mint-700 font-mono break-all block">
                                        {benchmark.task_name}
                                    </code>
                                </div>
                            </div>
                        </div>
                        </CardContent>
                        
                        <CardFooter className="pt-3 pb-4 text-xs text-blue-600 gap-3 border-t bg-muted/5">
                            <a 
                                href={benchmark.hf_repo.startsWith('http') ? benchmark.hf_repo : `https://huggingface.co/datasets/${benchmark.hf_repo}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 hover:underline font-medium"
                            >
                                source
                                <ExternalLink className="w-3 h-3 flex-shrink-0" />
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
                                        <ExternalLink className="w-3 h-3 flex-shrink-0" />
                                    </a>
                                </>
                            )}
                        </CardFooter>
                      </Card>
                    );
                  })}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex justify-center mt-8">
                      <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="cursor-pointer"
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
                            className="cursor-pointer"
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
    </Layout>
  );
}
