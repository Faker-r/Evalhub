import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { Check, ChevronRight, ChevronLeft, Database, FileText, Play, Server, ChevronDown } from "lucide-react";
import { Command, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";
import { ModelSelection } from "@/components/model-selection";

interface ProviderComboboxProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  predefinedOptions?: string[];
}

function ProviderCombobox({ value, onChange, placeholder = "Select or type...", predefinedOptions = [] }: ProviderComboboxProps) {
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value);

  const handleSelect = (selectedValue: string) => {
    onChange(selectedValue);
    setInputValue(selectedValue);
    setOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange(newValue);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setOpen(false);
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className="flex items-center w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 cursor-pointer">
          <input
            className="flex-1 bg-transparent outline-none placeholder:text-muted-foreground"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
          />
          <ChevronDown className="h-4 w-4 opacity-50" />
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
        <Command>
          <CommandInput placeholder="Search or type custom..." />
          <CommandList>
            {predefinedOptions.map((option) => (
              <CommandItem
                key={option}
                onSelect={() => handleSelect(option)}
                className={value === option ? "bg-accent" : ""}
              >
                {option}
              </CommandItem>
            ))}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

const STEPS = [
  { id: 1, title: "Select Source", icon: Database },
  { id: 2, title: "Dataset Configuration", icon: FileText },
  { id: 3, title: "Model & Judge", icon: Server },
  { id: 4, title: "Submit", icon: Play },
];

type SelectionType = "dataset" | "benchmark" | null;

export default function Submit() {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [, setLocation] = useLocation();
  const [currentStep, setCurrentStep] = useState(1);
  
  // Selection type
  const [selectionType, setSelectionType] = useState<SelectionType>(null);
  
  // Dataset-specific state
  const [selectedDataset, setSelectedDataset] = useState("");
  const [selectedGuidelines, setSelectedGuidelines] = useState<string[]>([]);
  
  // Flexible evaluation state
  const [inputField, setInputField] = useState("");
  const [outputType, setOutputType] = useState<"text" | "multiple_choice" | null>(null);
  const [goldAnswerField, setGoldAnswerField] = useState("");
  const [choicesField, setChoicesField] = useState("");
  const [judgeType, setJudgeType] = useState<"llm_as_judge" | "f1_score" | "exact_match" | null>(null);
  
  // Benchmark-specific state
  const [selectedBenchmark, setSelectedBenchmark] = useState<any>(null);
  const [selectedTask, setSelectedTask] = useState("");
  const [numFewShots, setNumFewShots] = useState(0);
  const [numSamples, setNumSamples] = useState<number | undefined>(undefined);
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set());
  const [taskDetails, setTaskDetails] = useState<Record<string, any>>({});
  const [loadingTasks, setLoadingTasks] = useState<Set<string>>(new Set());
  
  // Model configuration
  const [completionModelConfig, setCompletionModelConfig] = useState({
    provider: "openai",
    model: "gpt-3.5-turbo",
    apiBase: undefined as string | undefined,
  });
  const [judgeModelConfig, setJudgeModelConfig] = useState({
    provider: "openai",
    model: "gpt-3.5-turbo",
    apiBase: undefined as string | undefined,
  });

  // Fetch datasets
  const { data: datasetsData } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => apiClient.getDatasets(),
    enabled: isAuthenticated,
  });

  // Fetch benchmarks
  const { data: benchmarksData } = useQuery({
    queryKey: ['benchmarks'],
    queryFn: () => apiClient.getBenchmarks({ page: 1, page_size: 100 }),
    enabled: isAuthenticated,
  });

  // Fetch guidelines
  const { data: guidelinesData } = useQuery({
    queryKey: ['guidelines'],
    queryFn: () => apiClient.getGuidelines(),
    enabled: isAuthenticated,
  });

  // Fetch API keys
  const { data: apiKeysData } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiClient.getApiKeys(),
    enabled: isAuthenticated,
  });

  const datasets = datasetsData?.datasets || [];
  const benchmarks = benchmarksData?.benchmarks || [];
  const guidelines = guidelinesData?.guidelines || [];
  const apiKeys = apiKeysData?.api_key_providers || [];

  // Submit flexible evaluation
  const submitFlexibleMutation = useMutation({
    mutationFn: () =>
      apiClient.createFlexibleEvaluation({
        dataset_name: selectedDataset,
        input_field: inputField,
        output_type: outputType!,
        text_config: outputType === "text" ? { gold_answer_field: goldAnswerField || undefined } : undefined,
        mc_config: outputType === "multiple_choice" ? { choices_field: choicesField, gold_answer_field: goldAnswerField } : undefined,
        judge_type: judgeType!,
        guideline_names: judgeType === "llm_as_judge" ? selectedGuidelines : undefined,
        model_completion_config: {
          model_name: completionModelConfig.model,
          model_provider: completionModelConfig.provider,
          api_base: completionModelConfig.apiBase,
        },
        judge_config: judgeType === "llm_as_judge" ? {
          model_name: judgeModelConfig.model,
          model_provider: judgeModelConfig.provider,
          api_base: judgeModelConfig.apiBase,
        } : undefined,
      }),
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Evaluation started successfully!",
      });
      setLocation("/results");
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Submit task evaluation
  const submitTaskMutation = useMutation({
    mutationFn: () =>
      apiClient.createTaskEvaluation({
        task_name: selectedTask,
        dataset_config: {
          dataset_name: selectedBenchmark.dataset_name,
          n_fewshots: numFewShots,
          n_samples: numSamples,
        },
        model_completion_config: {
          model_name: completionModelConfig.model,
          model_provider: completionModelConfig.provider,
          api_base: completionModelConfig.apiBase,
        },
      }),
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Task evaluation started successfully!",
      });
      setLocation("/results");
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleNext = () => {
    if (currentStep === 1 && !selectionType) {
      toast({
        title: "Error",
        description: "Please select a dataset or benchmark",
        variant: "destructive",
      });
      return;
    }
    if (currentStep === 2) {
      if (selectionType === "dataset") {
        if (!inputField) {
          toast({
            title: "Error",
            description: "Please enter the input field name",
            variant: "destructive",
          });
          return;
        }
        if (!outputType) {
          toast({
            title: "Error",
            description: "Please select an output type",
            variant: "destructive",
          });
          return;
        }
        if (outputType === "multiple_choice" && (!choicesField || !goldAnswerField)) {
          toast({
            title: "Error",
            description: "Please enter both choices field and gold answer field",
            variant: "destructive",
          });
          return;
        }
        if (!judgeType) {
          toast({
            title: "Error",
            description: "Please select a judge type",
            variant: "destructive",
          });
          return;
        }
        if (judgeType === "llm_as_judge" && selectedGuidelines.length === 0) {
          toast({
            title: "Error",
            description: "Please select at least one guideline",
            variant: "destructive",
          });
          return;
        }
      }
      if (selectionType === "benchmark" && !selectedTask) {
        toast({
          title: "Error",
          description: "Please select a task",
          variant: "destructive",
        });
        return;
      }
    }
    if (currentStep < STEPS.length) setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleSubmit = () => {
    if (apiKeys.length === 0) {
      toast({
        title: "Error",
        description: "Please add an API key for the model provider",
        variant: "destructive",
      });
      return;
    }
    
    if (selectionType === "dataset") {
      submitFlexibleMutation.mutate();
    } else if (selectionType === "benchmark") {
      submitTaskMutation.mutate();
    }
  };

  const toggleGuideline = (guidelineName: string) => {
    if (selectedGuidelines.includes(guidelineName)) {
      setSelectedGuidelines(selectedGuidelines.filter((g) => g !== guidelineName));
    } else {
      setSelectedGuidelines([...selectedGuidelines, guidelineName]);
    }
  };

  const handleSelectDataset = (ds: any) => {
    setSelectedDataset(ds.name);
    setSelectionType("dataset");
    setSelectedBenchmark(null);
    setSelectedTask("");
    // Reset flexible evaluation state
    setInputField("");
    setOutputType(null);
    setGoldAnswerField("");
    setChoicesField("");
    setJudgeType(null);
    setSelectedGuidelines([]);
  };

  const handleSelectBenchmark = (benchmark: any) => {
    setSelectedBenchmark(benchmark);
    setSelectionType("benchmark");
    setSelectedDataset("");
    setSelectedGuidelines([]);
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
            {isExpanded ? <ChevronLeft className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
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
            {isExpanded ? <ChevronLeft className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
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

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <Play className="w-16 h-16 text-muted-foreground mb-4" />
          <h2 className="text-2xl font-bold mb-2">Please login to submit evaluations</h2>
          <p className="text-muted-foreground">You need to be authenticated to access this page.</p>
        </div>
      </Layout>
    );
  }

  const CurrentStepIcon = STEPS[currentStep - 1].icon;

  return (
    <Layout>
      <div className="flex min-h-[calc(100vh-64px)] bg-zinc-50/30">
        {/* Sidebar Steps */}
        <aside className="w-64 border-r border-border bg-white hidden md:block">
          <div className="p-6">
            <h2 className="font-display font-bold text-lg mb-6">New Evaluation</h2>
            <div className="space-y-1">
              {STEPS.map((step) => (
                <div
                  key={step.id}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    currentStep === step.id
                      ? "bg-mint-50 text-mint-900"
                      : currentStep > step.id
                      ? "text-black"
                      : "text-muted-foreground"
                  )}
                >
                  <div
                    className={cn(
                      "w-6 h-6 rounded-full flex items-center justify-center text-xs border",
                      currentStep === step.id
                        ? "border-mint-500 bg-mint-500 text-white"
                        : currentStep > step.id
                        ? "border-black bg-black text-white"
                        : "border-zinc-200 bg-white"
                    )}
                  >
                    {currentStep > step.id ? <Check className="w-3 h-3" /> : step.id}
                  </div>
                  {step.title}
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            <Card className="min-h-[500px] flex flex-col shadow-sm border-border">
              <CardHeader className="border-b border-border bg-zinc-50/30">
                <div className="flex items-center gap-2 text-mint-600 mb-1">
                  <CurrentStepIcon className="w-5 h-5" />
                  <span className="font-bold text-xs uppercase tracking-wider">
                    Step {currentStep}
                  </span>
                </div>
                <CardTitle className="text-2xl">{STEPS[currentStep - 1].title}</CardTitle>
              </CardHeader>

              <CardContent className="flex-1 p-8">
                {currentStep === 1 && (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <Label className="text-lg font-semibold">Select a Dataset</Label>
                      {datasets.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          No datasets available. Please upload one first.
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {datasets.map((ds) => (
                            <div
                              key={ds.id}
                              onClick={() => handleSelectDataset(ds)}
                              className={cn(
                                "border p-4 rounded-lg cursor-pointer transition-all",
                                selectedDataset === ds.name
                                  ? "border-mint-500 bg-mint-50/20"
                                  : "border-border hover:border-mint-300"
                              )}
                            >
                              <div className="font-bold text-lg mb-1">{ds.name}</div>
                              <div className="text-sm text-muted-foreground">
                                {ds.category} • {ds.sample_count} samples
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t" />
                      </div>
                      <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-white px-2 text-muted-foreground">Or</span>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <Label className="text-lg font-semibold">Select a Benchmark</Label>
                      {benchmarks.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          No benchmarks available.
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                          {benchmarks.map((benchmark) => (
                            <div
                              key={benchmark.id}
                              onClick={() => handleSelectBenchmark(benchmark)}
                              className={cn(
                                "border p-4 rounded-lg cursor-pointer transition-all",
                                selectedBenchmark?.id === benchmark.id
                                  ? "border-mint-500 bg-mint-50/20"
                                  : "border-border hover:border-mint-300"
                              )}
                            >
                              <div className="font-bold text-lg mb-1">{benchmark.dataset_name}</div>
                              <div className="text-sm text-muted-foreground line-clamp-2">
                                {benchmark.description || "No description"}
                              </div>
                              {benchmark.tasks && (
                                <div className="text-xs text-muted-foreground mt-2">
                                  {benchmark.tasks.length} tasks available
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {currentStep === 2 && selectionType === "dataset" && (
                  <div className="space-y-6">
                    {/* 1. Input Field */}
                    <div className="space-y-2">
                      <Label className="text-base font-semibold">Input Field</Label>
                      <p className="text-sm text-muted-foreground">
                        The field name in your dataset that contains the input/prompt
                      </p>
                      <Input
                        value={inputField}
                        onChange={(e) => setInputField(e.target.value)}
                        placeholder="e.g., question, input, prompt"
                      />
                    </div>

                    {/* 2. Output Type - only show after input field is filled */}
                    {inputField && (
                      <div className="space-y-3">
                        <Label className="text-base font-semibold">Output Type</Label>
                        <p className="text-sm text-muted-foreground">
                          How should the model respond?
                        </p>
                        <div className="flex gap-4">
                          <div
                            onClick={() => {
                              setOutputType("text");
                              setChoicesField("");
                            }}
                            className={cn(
                              "flex-1 border p-4 rounded-lg cursor-pointer transition-all",
                              outputType === "text"
                                ? "border-mint-500 bg-mint-50/20"
                                : "border-border hover:border-mint-300"
                            )}
                          >
                            <div className="font-medium">Text</div>
                            <div className="text-sm text-muted-foreground">Free-form text response</div>
                          </div>
                          <div
                            onClick={() => setOutputType("multiple_choice")}
                            className={cn(
                              "flex-1 border p-4 rounded-lg cursor-pointer transition-all",
                              outputType === "multiple_choice"
                                ? "border-mint-500 bg-mint-50/20"
                                : "border-border hover:border-mint-300"
                            )}
                          >
                            <div className="font-medium">Multiple Choice</div>
                            <div className="text-sm text-muted-foreground">Select from options</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 2.1 Text config - gold answer field (optional) */}
                    {outputType === "text" && (
                      <div className="space-y-2">
                        <Label className="text-base font-semibold">Gold Answer Field (Optional)</Label>
                        <p className="text-sm text-muted-foreground">
                          The field name containing the expected/correct answer for comparison
                        </p>
                        <Input
                          value={goldAnswerField}
                          onChange={(e) => setGoldAnswerField(e.target.value)}
                          placeholder="e.g., answer, expected_output"
                        />
                      </div>
                    )}

                    {/* 2.2 Multiple choice config - gold answer + choices field (required) */}
                    {outputType === "multiple_choice" && (
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label className="text-base font-semibold">Choices Field</Label>
                          <p className="text-sm text-muted-foreground">
                            The field name containing the list of choices
                          </p>
                          <Input
                            value={choicesField}
                            onChange={(e) => setChoicesField(e.target.value)}
                            placeholder="e.g., choices, options"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-base font-semibold">Gold Answer Field</Label>
                          <p className="text-sm text-muted-foreground">
                            The field name containing the correct answer
                          </p>
                          <Input
                            value={goldAnswerField}
                            onChange={(e) => setGoldAnswerField(e.target.value)}
                            placeholder="e.g., answer, correct_choice"
                          />
                        </div>
                      </div>
                    )}

                    {/* 3. Judge Type - show after output type config is complete */}
                    {outputType && (outputType === "text" || (choicesField && goldAnswerField)) && (
                      <div className="space-y-3">
                        <Label className="text-base font-semibold">Judge Type</Label>
                        <p className="text-sm text-muted-foreground">
                          How should responses be evaluated?
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                          <div
                            onClick={() => setJudgeType("llm_as_judge")}
                            className={cn(
                              "border p-4 rounded-lg cursor-pointer transition-all",
                              judgeType === "llm_as_judge"
                                ? "border-mint-500 bg-mint-50/20"
                                : "border-border hover:border-mint-300"
                            )}
                          >
                            <div className="font-medium">LLM as Judge</div>
                            <div className="text-sm text-muted-foreground">Use an LLM to evaluate responses with guidelines</div>
                          </div>
                          <div
                            onClick={() => {
                              setJudgeType("exact_match");
                              setSelectedGuidelines([]);
                            }}
                            className={cn(
                              "border p-4 rounded-lg cursor-pointer transition-all",
                              judgeType === "exact_match"
                                ? "border-mint-500 bg-mint-50/20"
                                : "border-border hover:border-mint-300"
                            )}
                          >
                            <div className="font-medium">Exact Match</div>
                            <div className="text-sm text-muted-foreground">Compare output exactly to gold answer</div>
                          </div>
                          <div
                            onClick={() => {
                              setJudgeType("f1_score");
                              setSelectedGuidelines([]);
                            }}
                            className={cn(
                              "border p-4 rounded-lg cursor-pointer transition-all",
                              judgeType === "f1_score"
                                ? "border-mint-500 bg-mint-50/20"
                                : "border-border hover:border-mint-300"
                            )}
                          >
                            <div className="font-medium">F1 Score</div>
                            <div className="text-sm text-muted-foreground">Token-level F1 comparison</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 3.1 Guideline selection - only for LLM as Judge */}
                    {judgeType === "llm_as_judge" && (
                      <div className="space-y-3">
                        <Label className="text-base font-semibold">Select Guidelines</Label>
                        <p className="text-sm text-muted-foreground">
                          Choose guidelines for the LLM judge to evaluate against
                        </p>
                        {guidelines.length === 0 ? (
                          <div className="text-center py-8 text-muted-foreground border border-dashed rounded-lg">
                            No guidelines available. Please create one first.
                          </div>
                        ) : (
                          <div className="space-y-2 max-h-48 overflow-y-auto">
                            {guidelines.map((guideline) => (
                              <div
                                key={guideline.id}
                                onClick={() => toggleGuideline(guideline.name)}
                                className={cn(
                                  "border p-3 rounded-lg cursor-pointer transition-all",
                                  selectedGuidelines.includes(guideline.name)
                                    ? "border-mint-500 bg-mint-50/20"
                                    : "border-border hover:border-mint-300"
                                )}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <div className="font-medium">{guideline.name}</div>
                                    <div className="text-xs text-muted-foreground">
                                      {guideline.category} • {guideline.scoring_scale === "numeric" 
                                        ? `${guideline.scoring_scale_config.min_value}-${guideline.scoring_scale_config.max_value}` 
                                        : guideline.scoring_scale}
                                    </div>
                                  </div>
                                  {selectedGuidelines.includes(guideline.name) && (
                                    <Check className="w-4 h-4 text-mint-500" />
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 2 && selectionType === "benchmark" && (
                  <div className="space-y-4">
                    <div>
                      <Label className="text-base font-semibold">Select Task</Label>
                      <p className="text-sm text-muted-foreground mb-3">
                        Choose from {selectedBenchmark?.tasks?.length || 0} available tasks
                      </p>
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {selectedBenchmark?.tasks?.map((task: string) => (
                          <div key={task} className="border border-gray-200 rounded-md">
                            <div
                              onClick={() => setSelectedTask(task)}
                              className={cn(
                                "p-3 cursor-pointer transition-all",
                                selectedTask === task
                                  ? "bg-mint-50 border-mint-500"
                                  : "hover:bg-gray-50"
                              )}
                            >
                              <div className="flex items-center justify-between">
                                <code className="text-xs text-mint-700 font-mono break-all flex-1">
                                  {task}
                                </code>
                                <div className="flex items-center gap-2">
                                  {selectedTask === task && (
                                    <Check className="w-4 h-4 text-mint-500 flex-shrink-0" />
                                  )}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleTask(task);
                                    }}
                                    className="text-gray-500 hover:text-gray-700"
                                  >
                                    {expandedTasks.has(task) ? (
                                      <ChevronLeft className="w-4 h-4" />
                                    ) : (
                                      <ChevronRight className="w-4 h-4" />
                                    )}
                                  </button>
                                </div>
                              </div>
                            </div>
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

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                      <div className="space-y-2">
                        <Label>Number of Samples</Label>
                        <Input
                          type="number"
                          min="1"
                          value={numSamples === undefined ? "" : numSamples}
                          onChange={(e) => setNumSamples(e.target.value ? parseInt(e.target.value) : undefined)}
                          placeholder="All samples"
                        />
                        <p className="text-xs text-muted-foreground">
                          Number of samples to evaluate (leave empty for all)
                        </p>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Number of Few-Shot Examples</Label>
                        <Input
                          type="number"
                          min="0"
                          value={numFewShots}
                          onChange={(e) => setNumFewShots(parseInt(e.target.value) || 0)}
                          placeholder="e.g., 0, 5, 10"
                        />
                        <p className="text-xs text-muted-foreground">
                          Examples to include in the prompt for few-shot learning
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {currentStep === 3 && (
                  <div className={cn(
                    "grid gap-6",
                    judgeType === "llm_as_judge" ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1"
                  )}>
                    <ModelSelection
                      value={completionModelConfig}
                      onChange={setCompletionModelConfig}
                      label="Completion Model"
                    />

                    {judgeType === "llm_as_judge" && (
                      <ModelSelection
                        value={judgeModelConfig}
                        onChange={setJudgeModelConfig}
                        label="Judge Model"
                      />
                    )}
                  </div>
                )}

                {currentStep === 4 && (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="font-bold text-lg">Review Your Evaluation</h3>
                      <div className="space-y-2 p-4 bg-zinc-50 rounded-lg">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Type:</span>
                          <span className="font-medium capitalize">{selectionType}</span>
                        </div>
                        
                        {selectionType === "dataset" ? (
                          <>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Dataset:</span>
                              <span className="font-medium">{selectedDataset}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Input Field:</span>
                              <span className="font-medium font-mono text-sm">{inputField}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Output Type:</span>
                              <span className="font-medium capitalize">{outputType?.replace("_", " ")}</span>
                            </div>
                            {outputType === "text" && goldAnswerField && (
                              <div className="flex justify-between">
                                <span className="text-muted-foreground">Gold Answer Field:</span>
                                <span className="font-medium font-mono text-sm">{goldAnswerField}</span>
                              </div>
                            )}
                            {outputType === "multiple_choice" && (
                              <>
                                <div className="flex justify-between">
                                  <span className="text-muted-foreground">Choices Field:</span>
                                  <span className="font-medium font-mono text-sm">{choicesField}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-muted-foreground">Gold Answer Field:</span>
                                  <span className="font-medium font-mono text-sm">{goldAnswerField}</span>
                                </div>
                              </>
                            )}
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Judge Type:</span>
                              <span className="font-medium capitalize">{judgeType?.replace(/_/g, " ")}</span>
                            </div>
                            {judgeType === "llm_as_judge" && (
                              <>
                                <div className="flex justify-between">
                                  <span className="text-muted-foreground">Guidelines:</span>
                                  <span className="font-medium">
                                    {selectedGuidelines.length > 0 ? selectedGuidelines.join(", ") : "None"}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-muted-foreground">Judge Model:</span>
                                  <span className="font-medium">{judgeModelConfig.model}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-muted-foreground">Judge Provider:</span>
                                  <span className="font-medium">{judgeModelConfig.provider}</span>
                                </div>
                                {judgeModelConfig.apiBase && (
                                  <div className="flex justify-between">
                                    <span className="text-muted-foreground">Judge API Base:</span>
                                    <span className="font-medium text-xs">{judgeModelConfig.apiBase}</span>
                                  </div>
                                )}
                              </>
                            )}
                          </>
                        ) : (
                          <>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Benchmark:</span>
                              <span className="font-medium">{selectedBenchmark?.dataset_name}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Task:</span>
                              <span className="font-medium text-xs font-mono">{selectedTask}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Number of Samples:</span>
                              <span className="font-medium">{numSamples ?? "All"}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Few-Shot Examples:</span>
                              <span className="font-medium">{numFewShots}</span>
                            </div>
                          </>
                        )}
                        
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Completion Model:</span>
                          <span className="font-medium">{completionModelConfig.model}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Completion Provider:</span>
                          <span className="font-medium">{completionModelConfig.provider}</span>
                        </div>
                        {completionModelConfig.apiBase && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Completion API Base:</span>
                            <span className="font-medium text-xs">{completionModelConfig.apiBase}</span>
                          </div>
                        )}
                      </div>
                      {apiKeys.length === 0 && (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            Warning: No API keys configured. Please add your{" "}
                            {completionModelConfig.provider} API key in your profile settings.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>

              {/* Footer */}
              <div className="p-6 border-t border-border bg-white flex justify-between">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  disabled={currentStep === 1}
                >
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
                {currentStep < STEPS.length ? (
                  <Button onClick={handleNext}>
                    Next
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                ) : (
                  <Button
                    onClick={handleSubmit}
                    disabled={submitFlexibleMutation.isPending || submitTaskMutation.isPending}
                    className="bg-mint-500 hover:bg-mint-600"
                  >
                    {(submitFlexibleMutation.isPending || submitTaskMutation.isPending) 
                      ? "Submitting..." 
                      : "Start Evaluation"}
                    <Play className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
}
