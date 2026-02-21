import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState, useEffect, useRef } from "react";
import { Check, ChevronRight, ChevronLeft, Database, FileText, Play, Server, ChevronDown, Eye, Search, HelpCircle, BookOpen } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Command, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient, type EvaluationModelConfig } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { useLocation, useSearch } from "wouter";
import { ModelSelection } from "@/components/model-selection";
import type { ModelConfig } from "@/types/model-config";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface ExpandableCellProps {
  value: any;
}

const ExpandableCell = ({ value }: ExpandableCellProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (value === undefined || value === null) {
    return <span className="text-muted-foreground italic">—</span>;
  }

  const isObject = typeof value === 'object';

  return (
    <div
      onClick={() => setIsExpanded(!isExpanded)}
      className={`cursor-pointer hover:bg-muted/50 rounded px-1 -mx-1 transition-colors ${
        !isExpanded ? "truncate" : ""
      }`}
      title={!isExpanded ? "Click to expand" : "Click to collapse"}
    >
      {isExpanded ? (
        isObject ? (
          <pre className="font-mono text-xs whitespace-pre-wrap overflow-x-auto p-2 bg-muted rounded border mt-1">
            {JSON.stringify(value, null, 2)}
          </pre>
        ) : (
          <div className="whitespace-pre-wrap text-sm pt-1">{String(value)}</div>
        )
      ) : isObject ? (
        <span className="font-mono text-xs">{JSON.stringify(value)}</span>
      ) : (
        <span className="text-sm">{String(value)}</span>
      )}
    </div>
  );
};
  
const STEPS = [
  { id: 1, title: "Select Source", icon: Database },
  { id: 2, title: "Dataset Configuration", icon: FileText },
  { id: 3, title: "Model & Judge", icon: Server },
  { id: 4, title: "Submit", icon: Play },
];

type SelectionType = "dataset" | "benchmark" | null;

// Field help tooltip component
interface FieldHelpProps {
  title: string;
  description: string;
  examples: string[];
  tip?: string;
}

const FieldHelp = ({ title, description, examples, tip }: FieldHelpProps) => (
  <Tooltip>
    <TooltipTrigger asChild>
      <HelpCircle className="w-4 h-4 text-muted-foreground cursor-help inline-block ml-1 align-text-bottom" />
    </TooltipTrigger>
    <TooltipContent className="max-w-sm" side="right">
      <div className="space-y-2">
        <p className="font-semibold">{title}</p>
        <p className="text-sm">{description}</p>
        <div className="text-sm">
          <p className="font-medium">Examples:</p>
          <ul className="list-disc ml-4">
            {examples.map((ex, i) => (
              <li key={i} className="font-mono text-xs">{ex}</li>
            ))}
          </ul>
        </div>
        {tip && (
          <p className="text-xs text-muted-foreground italic">{tip}</p>
        )}
      </div>
    </TooltipContent>
  </Tooltip>
);

// Help content for form fields
const FIELD_HELP = {
  inputField: {
    title: "Input Field",
    description: "The column name in your dataset that contains the text you want the model to respond to (the prompt or question).",
    examples: ["question", "prompt", "input", "query", "text"],
    tip: "Click the eye icon on a dataset to preview its fields.",
  },
  choicesField: {
    title: "Choices Field",
    description: "The column name containing the list of possible answers. This should be an array/list of options.",
    examples: ["choices", "options", "answers", "alternatives"],
    tip: "The field should contain an array like [\"A\", \"B\", \"C\", \"D\"] or [\"Yes\", \"No\"].",
  },
  goldAnswerField: {
    title: "Gold Answer Field",
    description: "The column name containing the correct/expected answer. For multiple choice, this can be the answer text or index.",
    examples: ["answer", "correct_answer", "gold", "label", "target"],
    tip: "For multiple choice: can be the answer text (e.g., 'Paris') or index (e.g., 0, 1, 2).",
  },
  goldAnswerFieldText: {
    title: "Gold Answer Field (Optional)",
    description: "The column name containing the expected/correct answer for comparison. Leave empty if your dataset doesn't have reference answers.",
    examples: ["answer", "expected_output", "reference", "gold"],
    tip: "Used by Exact Match and F1 Score judges to compare model output.",
  },
};

// Visual diagram component for ASCII art
const DiagramBlock = ({ content }: { content: string }) => (
  <pre className="font-mono text-xs bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto whitespace-pre leading-relaxed">
    {content}
  </pre>
);

// Sample JSON data display component
const SampleDataBlock = ({ json }: { json: string }) => (
  <div className="bg-muted rounded-lg p-3 font-mono text-xs overflow-x-auto">
    <pre className="whitespace-pre text-foreground">{json}</pre>
  </div>
);

// Guide content for each field with visual examples
const FIELD_GUIDES = {
  inputField: {
    title: "Input Field",
    description: "The column in your dataset containing the prompt or question for the model.",
    sample: `{
  "question": "What is the capital of France?",  ← Enter "question"
  "answer": "Paris",
  "context": "France is a country in Europe..."
}`,
    diagram: `┌─────────────────────────────────────────────────┐
│              YOUR DATASET                       │
├───────────────────┬───────────┬─────────────────┤
│  question         │  answer   │  context        │
├───────────────────┼───────────┼─────────────────┤
│  "What is 2+2?"   │  "4"      │  "Math quiz"    │
│  "Capital of US?" │  "DC"     │  "Geography"    │
└─────────▲─────────┴───────────┴─────────────────┘
          │
 Enter this column name: "question"`,
    tip: "This is the text that will be sent to the model as the prompt.",
  },
  outputTypeText: {
    title: "Text Output",
    description: "The model generates free-form text responses.",
    diagram: `┌─────────────────────────────────────────────────┐
│  PROMPT                     MODEL RESPONSE      │
├─────────────────────────────────────────────────┤
│  "Explain photosynthesis"   "Photosynthesis     │
│                        →     is the process..." │
│                                                 │
│  "Write a haiku"            "Autumn moonlight   │
│                        →     a worm digs..."    │
└─────────────────────────────────────────────────┘

Use for: Essays, summaries, explanations, creative writing`,
  },
  outputTypeMC: {
    title: "Multiple Choice",
    description: "The model selects from predefined options.",
    diagram: `┌─────────────────────────────────────────────────┐
│  PROMPT                      MODEL RESPONSE     │
├─────────────────────────────────────────────────┤
│  "What is 2+2?"                                 │
│  Choices: [A] 3  [B] 4  [C] 5    →    [B] 4    │
│                                                 │
│  "Capital of France?"                           │
│  Choices: [A] London [B] Paris   →    [B] Paris│
└─────────────────────────────────────────────────┘

Use for: Quizzes, fact-checking, classification`,
  },
  choicesField: {
    title: "Choices Field",
    description: "The column containing the list of answer options.",
    sample: `{
  "question": "What is 2+2?",
  "choices": ["3", "4", "5", "6"],  ← Enter "choices"
  "answer": "4"
}`,
    diagram: `           choices field
                 │
                 ▼
      ┌──────────────────┐
      │ ["3","4","5","6"] │  ← Must be an array/list
      └──────────────────┘
                 │
                 ▼
  Model sees:  0: 3
               1: 4  ← correct
               2: 5
               3: 6`,
    tip: "The field must contain an array like [\"A\", \"B\", \"C\"] or [\"Yes\", \"No\"]",
  },
  goldAnswerField: {
    title: "Gold Answer Field",
    description: "The column containing the correct/expected answer.",
    sample: `{
  "question": "What is 2+2?",
  "choices": ["3", "4", "5", "6"],
  "answer": "4"  ← Enter "answer" (can be text or index)
}`,
    diagram: `Gold answer can be specified two ways:

  Option A: The answer text      Option B: The index
  ─────────────────────────      ───────────────────
  "answer": "Paris"              "answer": 1
       │                              │
       ▼                              ▼
  Matches choice text            Points to choices[1]
  ["London","Paris"]             ["London","Paris"]
           ▲                              ▲
           └── "Paris"                    └── index 1 = "Paris"`,
    tip: "For text output: this is compared against the model's response",
  },
  goldAnswerFieldText: {
    title: "Gold Answer Field (Optional)",
    description: "The expected answer to compare against the model's output.",
    sample: `{
  "question": "Explain gravity briefly.",
  "reference": "Gravity is the force of attraction..."  ← Enter "reference"
}`,
    diagram: `Without gold answer:
  Model output → (no comparison, judge evaluates quality)

With gold answer:
  Model output: "Gravity pulls objects together"
  Gold answer:  "Gravity is the force of attraction"
        │
        ▼
  Exact Match: 0.0 (different text)
  F1 Score:    0.5 (some word overlap)`,
    tip: "Leave empty if you only want quality evaluation without a reference answer.",
  },
  judgeLLM: {
    title: "LLM as Judge",
    description: "Uses another LLM to evaluate response quality based on guidelines.",
    diagram: `┌─────────────────────────────────────────────────┐
│           HOW LLM AS JUDGE WORKS                │
├─────────────────────────────────────────────────┤
│                                                 │
│   Question ──► Model ──► Response               │
│                              │                  │
│                              ▼                  │
│                    ┌─────────────────┐          │
│   Guidelines ────► │  JUDGE MODEL    │          │
│                    │  (evaluates)    │          │
│                    └────────┬────────┘          │
│                             │                   │
│                             ▼                   │
│                    Score: 8/10                  │
│                    "Good but could be clearer"  │
└─────────────────────────────────────────────────┘

Best for: Subjective quality, writing style, helpfulness`,
  },
  judgeExact: {
    title: "Exact Match",
    description: "Checks if the model output exactly matches the gold answer.",
    diagram: `┌─────────────────────────────────────────────────┐
│           HOW EXACT MATCH WORKS                 │
├─────────────────────────────────────────────────┤
│                                                 │
│   Model Response: "Paris"                       │
│   Gold Answer:    "Paris"                       │
│                      │                          │
│                      ▼                          │
│              "Paris" == "Paris"                 │
│                      │                          │
│                      ▼                          │
│                  ✓ MATCH (Score: 1.0)           │
│                                                 │
│   Model Response: "paris"                       │
│   Gold Answer:    "Paris"                       │
│                      │                          │
│                      ▼                          │
│              "paris" != "Paris"                 │
│                      │                          │
│                      ▼                          │
│                  ✗ NO MATCH (Score: 0.0)        │
└─────────────────────────────────────────────────┘

Best for: Factual Q&A, multiple choice, classification`,
  },
  judgeF1: {
    title: "F1 Score",
    description: "Measures token-level overlap between response and gold answer.",
    diagram: `┌─────────────────────────────────────────────────┐
│           HOW F1 SCORE WORKS                    │
├─────────────────────────────────────────────────┤
│                                                 │
│   Model Response: "The capital is Paris"        │
│   Gold Answer:    "Paris is the capital"        │
│                          │                      │
│                          ▼                      │
│              Tokenize both strings:             │
│   Response: [The, capital, is, Paris]           │
│   Gold:     [Paris, is, the, capital]           │
│                          │                      │
│                          ▼                      │
│              Calculate token overlap:           │
│   Shared: {capital, is, Paris} = 3 tokens       │
│                          │                      │
│                          ▼                      │
│              F1 = 2 × (P × R) / (P + R)         │
│                  ≈ 0.86 (partial match!)        │
└─────────────────────────────────────────────────┘

Best for: Extractive Q&A, summaries, paraphrasing`,
  },
  // Benchmark-specific guides
  numSamples: {
    title: "Number of Samples",
    description: "How many examples from the benchmark to evaluate.",
    diagram: `┌─────────────────────────────────────────────────┐
│           BENCHMARK DATASET                      │
├─────────────────────────────────────────────────┤
│  Sample 1: "What is 2+2?"          ✓ Evaluated  │
│  Sample 2: "Capital of France?"    ✓ Evaluated  │
│  Sample 3: "Who wrote Hamlet?"     ✓ Evaluated  │
│  Sample 4: "Largest planet?"       ✗ Skipped    │
│  Sample 5: "Speed of light?"       ✗ Skipped    │
│  ... (1000 more samples)           ✗ Skipped    │
└─────────────────────────────────────────────────┘
         ▲
         │
  numSamples = 3  (only first 3 evaluated)

Leave empty to evaluate ALL samples in the benchmark.`,
    tip: "Use a smaller number (e.g., 10-50) for quick testing, then run the full benchmark.",
  },
  numFewShots: {
    title: "Few-Shot Examples",
    description: "Examples included in the prompt to help the model understand the task format.",
    diagram: `┌─────────────────────────────────────────────────┐
│           PROMPT SENT TO MODEL                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │ FEW-SHOT EXAMPLES (numFewShots = 2):    │    │
│  │                                          │    │
│  │ Example 1:                               │    │
│  │ Q: What is the capital of Spain?         │    │
│  │ A: Madrid                                │    │
│  │                                          │    │
│  │ Example 2:                               │    │
│  │ Q: What is the capital of Italy?         │    │
│  │ A: Rome                                  │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │ ACTUAL QUESTION:                        │    │
│  │ Q: What is the capital of France?       │    │
│  │ A: ???  ← Model generates this          │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
└─────────────────────────────────────────────────┘

0 = Zero-shot (no examples, just the question)
5 = Five examples shown before each question`,
    tip: "Few-shot learning often improves accuracy. Start with 0 or 5 to compare.",
  },
};

// Collapsible guide section component
interface GuideExampleProps {
  sample?: string;
  diagram?: string;
  tip?: string;
}

const GuideExample = ({ sample, diagram, tip }: GuideExampleProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger asChild>
        <button
          type="button"
          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors mt-2"
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>{isOpen ? "Hide example" : "Show example"}</span>
          <ChevronDown className={cn("w-3.5 h-3.5 transition-transform", isOpen && "rotate-180")} />
        </button>
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-3 space-y-3">
        {sample && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1.5">Example dataset row:</p>
            <SampleDataBlock json={sample} />
          </div>
        )}
        {diagram && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1.5">How it works:</p>
            <DiagramBlock content={diagram} />
          </div>
        )}
        {tip && (
          <p className="text-xs text-muted-foreground bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-md px-3 py-2">
            💡 {tip}
          </p>
        )}
      </CollapsibleContent>
    </Collapsible>
  );
};

// Helper function to convert ModelConfig to API format
function convertModelConfigToAPI(config: ModelConfig): EvaluationModelConfig {
  if (config.is_openrouter) {
    return {
      api_source: "openrouter",
      model: {
        id: config.openrouter_model_id || "",
        name: config.openrouter_model_name || config.openrouter_model_id || "",
        description: config.openrouter_model_description,
        pricing: config.openrouter_model_pricing,
        context_length: config.openrouter_model_context_length,
        canonical_slug: config.openrouter_model_canonical_slug,
        architecture: config.openrouter_model_architecture,
        top_provider: config.openrouter_model_top_provider,
        supported_parameters: config.openrouter_model_supported_parameters,
        per_request_limits: config.openrouter_model_per_request_limits,
        provider_slugs: config.openrouter_model_provider_slugs,
      },
      provider: {
        name:
          config.openrouter_provider_name ||
          config.openrouter_provider_slug ||
          "openrouter",
        slug: config.openrouter_provider_slug || "openrouter",
      },
    };
  } else {
    const provider = {
      id: config.provider_id || "",
      name: config.provider_name || "",
      slug: config.provider_slug || null,
      base_url: config.api_base || "",
    };
    return {
      api_source: "standard",
      model: {
        id: config.model_id || "",
        display_name: config.model_name || "",
        developer: config.model_developer || "",
        api_name: config.api_name || "",
        providers: config.model_providers?.length
          ? config.model_providers.map((p) => ({
              id: p.id,
              name: p.name,
              slug: p.slug || null,
              base_url: p.base_url,
            }))
          : [provider],
      },
      provider,
    };
  }
}

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

  // Search state
  const [datasetSearch, setDatasetSearch] = useState("");
  const [benchmarkSearch, setBenchmarkSearch] = useState("");

  // Preview state
  const [previewDatasetId, setPreviewDatasetId] = useState<number | null>(null);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);

  // Model configuration
  const [completionModelConfig, setCompletionModelConfig] = useState<ModelConfig>({});
  const [judgeModelConfig, setJudgeModelConfig] = useState<ModelConfig>({});
  const judgeSectionRef = useRef<HTMLDivElement | null>(null);
  const wasCompletionConfiguredRef = useRef(false);

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

  const { data: previewData, isLoading: isPreviewLoading } = useQuery({
    queryKey: ['dataset-preview', previewDatasetId],
    queryFn: () => previewDatasetId ? apiClient.getDatasetPreview(previewDatasetId) : null,
    enabled: !!previewDatasetId && previewModalOpen,
  });

  const datasets = datasetsData?.datasets || [];
  const benchmarks = benchmarksData?.benchmarks || [];
  const guidelines = guidelinesData?.guidelines || [];
  const apiKeys = apiKeysData?.api_key_providers || [];

  // Get the selected dataset's ID for inline preview in Step 2
  const selectedDatasetId = datasets.find((ds: any) => ds.name === selectedDataset)?.id;

  // Fetch preview for the selected dataset (for inline display in Step 2)
  const { data: inlinePreviewData, isLoading: isInlinePreviewLoading } = useQuery({
    queryKey: ['dataset-preview-inline', selectedDatasetId],
    queryFn: () => selectedDatasetId ? apiClient.getDatasetPreview(selectedDatasetId) : null,
    enabled: !!selectedDatasetId && currentStep === 2 && selectionType === "dataset",
  });

  // State for benchmark preview modal
  const [benchmarkPreviewOpen, setBenchmarkPreviewOpen] = useState(false);

  // Fetch preview for the selected benchmark (for modal display)
  const { data: benchmarkPreviewData, isLoading: isBenchmarkPreviewLoading } = useQuery({
    queryKey: ['benchmark-preview', selectedBenchmark?.id],
    queryFn: () => selectedBenchmark?.id ? apiClient.getBenchmarkPreview(selectedBenchmark.id) : null,
    enabled: !!selectedBenchmark?.id && benchmarkPreviewOpen,
  });

  const isOpenRouterSelectionComplete = (config: ModelConfig) =>
    Boolean(config.openrouter_provider_slug && config.openrouter_model_id);

  const isCompletionConfigured = isOpenRouterSelectionComplete(completionModelConfig);

  // Handle pre-selection from URL params (from benchmarks page)
  const searchString = useSearch();
  useEffect(() => {
    if (!benchmarks.length) return;

    const params = new URLSearchParams(searchString);
    const benchmarkId = params.get('benchmarkId');
    const taskName = params.get('task');

    if (benchmarkId && taskName) {
      const benchmark = benchmarks.find((b: any) => b.id === parseInt(benchmarkId));
      if (benchmark) {
        setSelectedBenchmark(benchmark);
        setSelectionType("benchmark");
        setSelectedTask(taskName);
        // Clear URL params after setting state
        setLocation('/submit', { replace: true });
      }
    }
  }, [benchmarks, searchString]);

  useEffect(() => {
    if (judgeType !== "llm_as_judge") {
      wasCompletionConfiguredRef.current = false;
      return;
    }

    if (!wasCompletionConfiguredRef.current && isCompletionConfigured) {
      setTimeout(() => {
        judgeSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 0);
    }
    wasCompletionConfiguredRef.current = isCompletionConfigured;
  }, [isCompletionConfigured, judgeType, judgeSectionRef, wasCompletionConfiguredRef]);

  // Filter datasets and benchmarks
  const filteredDatasets = datasets.filter((ds: any) =>
    (ds.name && ds.name.toLowerCase().includes(datasetSearch.toLowerCase())) ||
    (ds.category && ds.category.toLowerCase().includes(datasetSearch.toLowerCase()))
  );

  const filteredBenchmarks = benchmarks.filter((bm: any) =>
    (bm.dataset_name && bm.dataset_name.toLowerCase().includes(benchmarkSearch.toLowerCase())) ||
    (bm.description && bm.description.toLowerCase().includes(benchmarkSearch.toLowerCase()))
  );

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
        model_completion_config: convertModelConfigToAPI(completionModelConfig),
        judge_config: judgeType === "llm_as_judge" ? convertModelConfigToAPI(judgeModelConfig) : undefined,
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
        model_completion_config: convertModelConfigToAPI(completionModelConfig),
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

  const resetDatasetStepState = () => {
    setInputField("");
    setOutputType(null);
    setGoldAnswerField("");
    setChoicesField("");
    setJudgeType(null);
    setSelectedGuidelines([]);
  };

  const resetBenchmarkStepState = () => {
    setSelectedTask("");
    setNumFewShots(0);
    setNumSamples(undefined);
    setExpandedTasks(new Set());
    setTaskDetails({});
    setLoadingTasks(new Set());
  };

  const resetModelStepState = () => {
    setCompletionModelConfig({});
    setJudgeModelConfig({});
  };

  const resetDownstreamState = (targetStep: number) => {
    // Returning to step 1 invalidates step 2+ state.
    if (targetStep <= 1) {
      resetDatasetStepState();
      resetBenchmarkStepState();
      resetModelStepState();
      return;
    }

    // Returning to step 2 invalidates step 3+ state.
    if (targetStep <= 2) {
      resetModelStepState();
    }
  };

  const handleBack = () => {
    if (currentStep <= 1) return;
    const targetStep = currentStep - 1;
    resetDownstreamState(targetStep);
    setCurrentStep(targetStep);
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

  const handlePreviewDataset = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setPreviewDatasetId(id);
    setPreviewModalOpen(true);
  };

  const toggleGuideline = (guidelineName: string) => {
    if (selectedGuidelines.includes(guidelineName)) {
      setSelectedGuidelines(selectedGuidelines.filter((g) => g !== guidelineName));
    } else {
      setSelectedGuidelines([...selectedGuidelines, guidelineName]);
    }
  };

  const handleSelectDataset = (ds: any) => {
    resetDownstreamState(1);
    setSelectedDataset(ds.name);
    setSelectionType("dataset");
    setSelectedBenchmark(null);
  };

  const handleSelectBenchmark = (benchmark: any) => {
    resetDownstreamState(1);
    setSelectedBenchmark(benchmark);
    setSelectionType("benchmark");
    setSelectedDataset("");
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
                      <div className="flex items-center justify-between">
                        <Label className="text-lg font-semibold">Select a Dataset</Label>
                        <div className="relative w-full max-w-xs">
                          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                          <Input
                            placeholder="Search datasets..."
                            className="pl-8"
                            value={datasetSearch}
                            onChange={(e) => setDatasetSearch(e.target.value)}
                          />
                        </div>
                      </div>

                      {filteredDatasets.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          {datasets.length === 0 ? "No datasets available. Please upload one first." : "No datasets match your search."}
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                          {filteredDatasets.map((ds: any) => (
                            <div
                              key={ds.id}
                              onClick={() => handleSelectDataset(ds)}
                              className={cn(
                                "border p-4 rounded-lg cursor-pointer transition-all relative",
                                selectedDataset === ds.name
                                  ? "border-mint-500 bg-mint-50/20"
                                  : "border-border hover:border-mint-300"
                              )}
                            >
                              <div className="font-bold text-lg mb-1 pr-8">{ds.name}</div>
                              <div className="text-sm text-muted-foreground">
                                {ds.category} • {ds.sample_count} samples
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="absolute top-2 right-2 h-8 w-8 p-0"
                                onClick={(e) => handlePreviewDataset(ds.id, e)}
                              >
                                <Eye className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                              </Button>
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
                      <div className="flex items-center justify-between">
                        <Label className="text-lg font-semibold">Select a Benchmark</Label>
                        <div className="relative w-full max-w-xs">
                          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                          <Input
                            placeholder="Search benchmarks..."
                            className="pl-8"
                            value={benchmarkSearch}
                            onChange={(e) => setBenchmarkSearch(e.target.value)}
                          />
                        </div>
                      </div>

                      {filteredBenchmarks.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                          {benchmarks.length === 0 ? "No benchmarks available." : "No benchmarks match your search."}
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                          {filteredBenchmarks.map((benchmark: any) => (
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
                    {/* Dataset Preview Section */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-base font-semibold">Your Dataset: {selectedDataset}</Label>
                          <p className="text-sm text-muted-foreground">
                            Reference your data below to find the correct field names
                          </p>
                        </div>
                      </div>

                      {isInlinePreviewLoading ? (
                        <div className="flex justify-center p-6 border rounded-lg bg-muted/30">
                          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                        </div>
                      ) : inlinePreviewData?.samples && inlinePreviewData.samples.length > 0 ? (
                        <Collapsible defaultOpen>
                          <CollapsibleTrigger asChild>
                            <button
                              type="button"
                              className="flex items-center justify-between w-full p-3 border rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                            >
                              <div className="flex items-center gap-2 text-sm">
                                <Database className="w-4 h-4 text-muted-foreground" />
                                <span className="font-medium">Dataset Preview</span>
                                <span className="text-muted-foreground">
                                  ({inlinePreviewData.samples.length} samples)
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-muted-foreground">
                                  Fields: {Array.from(new Set(inlinePreviewData.samples.flatMap((s: any) => Object.keys(s)))).join(", ")}
                                </span>
                                <ChevronDown className="w-4 h-4 text-muted-foreground" />
                              </div>
                            </button>
                          </CollapsibleTrigger>
                          <CollapsibleContent>
                            <div className="mt-2 border rounded-lg overflow-hidden">
                              <div className="max-h-64 overflow-auto">
                                <Table>
                                  <TableHeader className="sticky top-0 bg-background z-10">
                                    <TableRow>
                                      <TableHead className="w-12 text-xs">#</TableHead>
                                      {Array.from(
                                        new Set(inlinePreviewData.samples.flatMap((s: any) => Object.keys(s)))
                                      ).map((key) => (
                                        <TableHead key={key as string} className="text-xs font-mono">
                                          {key as string}
                                        </TableHead>
                                      ))}
                                    </TableRow>
                                  </TableHeader>
                                  <TableBody>
                                    {inlinePreviewData.samples.slice(0, 5).map((sample: any, idx: number) => (
                                      <TableRow key={idx}>
                                        <TableCell className="text-muted-foreground text-xs">{idx + 1}</TableCell>
                                        {Array.from(
                                          new Set(inlinePreviewData.samples.flatMap((s: any) => Object.keys(s)))
                                        ).map((key) => (
                                          <TableCell key={key as string} className="max-w-xs align-top">
                                            <ExpandableCell value={sample[key as string]} />
                                          </TableCell>
                                        ))}
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </div>
                              {inlinePreviewData.samples.length > 5 && (
                                <div className="text-xs text-center text-muted-foreground py-2 border-t bg-muted/20">
                                  Showing 5 of {inlinePreviewData.samples.length} samples
                                </div>
                              )}
                            </div>
                          </CollapsibleContent>
                        </Collapsible>
                      ) : (
                        <div className="text-center py-6 text-muted-foreground border rounded-lg bg-muted/30">
                          No preview data available
                        </div>
                      )}
                    </div>

                    {/* Separator */}
                    <div className="border-t" />

                    {/* 1. Input Field */}
                    <div className="space-y-2">
                      <Label className="text-base font-semibold">
                        Input Field
                        <FieldHelp {...FIELD_HELP.inputField} />
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        The field name in your dataset that contains the input/prompt
                      </p>
                      <Input
                        value={inputField}
                        onChange={(e) => setInputField(e.target.value)}
                        placeholder="e.g., question, input, prompt"
                      />
                      <GuideExample
                        sample={FIELD_GUIDES.inputField.sample}
                        diagram={FIELD_GUIDES.inputField.diagram}
                        tip={FIELD_GUIDES.inputField.tip}
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
                              setJudgeType(null);
                              setSelectedGuidelines([]);
                              setJudgeModelConfig({});
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
                            {outputType === "text" && (
                              <GuideExample diagram={FIELD_GUIDES.outputTypeText.diagram} />
                            )}
                          </div>
                          <div
                            onClick={() => {
                              setOutputType("multiple_choice");
                              setJudgeType(null);
                              setSelectedGuidelines([]);
                              setJudgeModelConfig({});
                            }}
                            className={cn(
                              "flex-1 border p-4 rounded-lg cursor-pointer transition-all",
                              outputType === "multiple_choice"
                                ? "border-mint-500 bg-mint-50/20"
                                : "border-border hover:border-mint-300"
                            )}
                          >
                            <div className="font-medium">Multiple Choice</div>
                            <div className="text-sm text-muted-foreground">Select from options</div>
                            {outputType === "multiple_choice" && (
                              <GuideExample diagram={FIELD_GUIDES.outputTypeMC.diagram} />
                            )}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 2.1 Text config - gold answer field (optional) */}
                    {outputType === "text" && (
                      <div className="space-y-2">
                        <Label className="text-base font-semibold">
                          Gold Answer Field (Optional)
                          <FieldHelp {...FIELD_HELP.goldAnswerFieldText} />
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          The field name containing the expected/correct answer for comparison
                        </p>
                        <Input
                          value={goldAnswerField}
                          onChange={(e) => setGoldAnswerField(e.target.value)}
                          placeholder="e.g., answer, expected_output"
                        />
                        <GuideExample
                          sample={FIELD_GUIDES.goldAnswerFieldText.sample}
                          diagram={FIELD_GUIDES.goldAnswerFieldText.diagram}
                          tip={FIELD_GUIDES.goldAnswerFieldText.tip}
                        />
                      </div>
                    )}

                    {/* 2.2 Multiple choice config - gold answer + choices field (required) */}
                    {outputType === "multiple_choice" && (
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label className="text-base font-semibold">
                            Choices Field
                            <FieldHelp {...FIELD_HELP.choicesField} />
                          </Label>
                          <p className="text-sm text-muted-foreground">
                            The field name containing the list of choices
                          </p>
                          <Input
                            value={choicesField}
                            onChange={(e) => setChoicesField(e.target.value)}
                            placeholder="e.g., choices, options"
                          />
                          <GuideExample
                            sample={FIELD_GUIDES.choicesField.sample}
                            diagram={FIELD_GUIDES.choicesField.diagram}
                            tip={FIELD_GUIDES.choicesField.tip}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-base font-semibold">
                            Gold Answer Field
                            <FieldHelp {...FIELD_HELP.goldAnswerField} />
                          </Label>
                          <p className="text-sm text-muted-foreground">
                            The field name containing the correct answer
                          </p>
                          <Input
                            value={goldAnswerField}
                            onChange={(e) => setGoldAnswerField(e.target.value)}
                            placeholder="e.g., answer, correct_choice"
                          />
                          <GuideExample
                            sample={FIELD_GUIDES.goldAnswerField.sample}
                            diagram={FIELD_GUIDES.goldAnswerField.diagram}
                            tip={FIELD_GUIDES.goldAnswerField.tip}
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
                            {judgeType === "llm_as_judge" && (
                              <GuideExample diagram={FIELD_GUIDES.judgeLLM.diagram} />
                            )}
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
                            {judgeType === "exact_match" && (
                              <GuideExample diagram={FIELD_GUIDES.judgeExact.diagram} />
                            )}
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
                            {judgeType === "f1_score" && (
                              <GuideExample diagram={FIELD_GUIDES.judgeF1.diagram} />
                            )}
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
                  <div className="space-y-6">
                    {/* Benchmark Info Section */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-base font-semibold">Benchmark: {selectedBenchmark?.dataset_name}</Label>
                          <p className="text-sm text-muted-foreground">
                            {selectedBenchmark?.description || "Configure your benchmark evaluation"}
                          </p>
                        </div>
                      </div>

                      {/* Benchmark source info - clickable to preview */}
                      <button
                        type="button"
                        onClick={() => setBenchmarkPreviewOpen(true)}
                        className="w-full p-3 border rounded-lg bg-muted/30 text-left transition-colors hover:bg-muted/50 hover:border-mint-300 cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-sm">
                            <Database className="w-4 h-4 text-muted-foreground" />
                            <span className="font-medium">Source Dataset</span>
                          </div>
                          <div className="flex items-center gap-1 text-xs text-mint-600">
                            <Eye className="w-3.5 h-3.5" />
                            <span>Preview</span>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          This benchmark uses the <code className="font-mono bg-muted px-1 rounded">{selectedBenchmark?.hf_repo || selectedBenchmark?.dataset_name}</code> dataset
                          from HuggingFace with {selectedBenchmark?.tasks?.length || 0} predefined tasks.
                        </p>
                      </button>
                    </div>

                    {/* Separator */}
                    <div className="border-t" />

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

                    {/* Separator */}
                    <div className="border-t" />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label className="text-base font-semibold">
                          Number of Samples
                          <FieldHelp
                            title="Number of Samples"
                            description="How many examples from the benchmark to evaluate"
                            examples={["10 (quick test)", "100 (moderate)", "empty (all samples)"]}
                            tip="Leave empty to evaluate all samples in the benchmark"
                          />
                        </Label>
                        <Input
                          type="number"
                          min="1"
                          value={numSamples === undefined ? "" : numSamples}
                          onChange={(e) => setNumSamples(e.target.value ? parseInt(e.target.value) : undefined)}
                          placeholder="All samples"
                        />
                        <GuideExample
                          diagram={FIELD_GUIDES.numSamples.diagram}
                          tip={FIELD_GUIDES.numSamples.tip}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label className="text-base font-semibold">
                          Number of Few-Shot Examples
                          <FieldHelp
                            title="Few-Shot Examples"
                            description="Examples included in each prompt to help the model understand the task"
                            examples={["0 (zero-shot)", "3 (few-shot)", "5 (recommended)"]}
                            tip="More examples often improve accuracy but increase cost"
                          />
                        </Label>
                        <Input
                          type="number"
                          min="0"
                          value={numFewShots}
                          onChange={(e) => setNumFewShots(parseInt(e.target.value) || 0)}
                          placeholder="e.g., 0, 5, 10"
                        />
                        <GuideExample
                          diagram={FIELD_GUIDES.numFewShots.diagram}
                          tip={FIELD_GUIDES.numFewShots.tip}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {currentStep === 3 && (
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                        Step 3.1
                      </p>
                      <ModelSelection
                        value={completionModelConfig}
                        onChange={setCompletionModelConfig}
                        label="Completion Model"
                      />
                    </div>

                    {judgeType === "llm_as_judge" && (
                      <div ref={judgeSectionRef} className="space-y-2">
                        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                          Step 3.2
                        </p>
                        {isCompletionConfigured ? (
                          <ModelSelection
                            value={judgeModelConfig}
                            onChange={setJudgeModelConfig}
                            label="Judge Model"
                          />
                        ) : (
                          <div className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
                            Configure the completion model first, then select the judge model.
                          </div>
                        )}
                      </div>
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
                                  <span className="font-medium">
                                    {judgeModelConfig.is_openrouter
                                      ? (judgeModelConfig.openrouter_model_name || judgeModelConfig.openrouter_model_id)
                                      : judgeModelConfig.model_name}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-muted-foreground">Judge Provider:</span>
                                  <span className="font-medium">
                                    {judgeModelConfig.is_openrouter
                                      ? (judgeModelConfig.openrouter_provider_name || judgeModelConfig.openrouter_provider_slug || 'OpenRouter')
                                      : judgeModelConfig.provider_name}
                                  </span>
                                </div>
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
                          <span className="font-medium">
                            {completionModelConfig.is_openrouter
                              ? (completionModelConfig.openrouter_model_name || completionModelConfig.openrouter_model_id)
                              : completionModelConfig.model_name}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Completion Provider:</span>
                          <span className="font-medium">
                            {completionModelConfig.is_openrouter
                              ? (completionModelConfig.openrouter_provider_name || completionModelConfig.openrouter_provider_slug || 'OpenRouter')
                              : completionModelConfig.provider_name}
                          </span>
                        </div>
                      </div>
                      {apiKeys.length === 0 && (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            Warning: No API keys configured. Please add your{" "}
                            {completionModelConfig.is_openrouter
                              ? (completionModelConfig.openrouter_provider_name || completionModelConfig.openrouter_provider_slug || 'OpenRouter')
                              : completionModelConfig.provider_name} API key in your profile settings.
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

      {/* Preview Dialog */}
      <Dialog open={previewModalOpen} onOpenChange={setPreviewModalOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Dataset Content</DialogTitle>
            <DialogDescription>
              Showing all samples from the selected dataset.
              {previewData?.samples && previewData.samples.length > 0 && (
                <span className="block mt-2">
                  <span className="font-medium">Available fields: </span>
                  <span className="font-mono text-xs">
                    {Array.from(
                      new Set(previewData.samples.flatMap((s: any) => Object.keys(s)))
                    ).join(", ")}
                  </span>
                </span>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto min-h-0 py-4">
            {isPreviewLoading ? (
               <div className="flex justify-center p-8">
                 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
               </div>
            ) : previewData?.samples && previewData.samples.length > 0 ? (
              <div className="overflow-x-auto">
                {(() => {
                  // Get all unique keys from all samples
                  const allKeys = Array.from(
                    new Set(
                      previewData.samples.flatMap((sample: any) => Object.keys(sample))
                    )
                  );

                  return (
                    <div className="border rounded-md">
                      <Table>
                        <TableHeader className="sticky top-0 bg-background z-10">
                          <TableRow>
                            <TableHead className="w-12">#</TableHead>
                            {allKeys.map((key) => (
                              <TableHead key={key}>{key}</TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {previewData.samples.map((sample: any, idx: number) => (
                            <TableRow key={idx}>
                              <TableCell className="text-muted-foreground">{idx + 1}</TableCell>
                              {allKeys.map((key) => (
                                <TableCell key={key} className="max-w-md align-top">
                                  <ExpandableCell value={sample[key]} />
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  );
                })()}
              </div>
            ) : (
                <div className="text-center text-muted-foreground p-4">
                    No preview available
                </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Benchmark Preview Dialog */}
      <Dialog open={benchmarkPreviewOpen} onOpenChange={setBenchmarkPreviewOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Benchmark Data Preview</DialogTitle>
            <DialogDescription>
              Showing sample data from <code className="font-mono bg-muted px-1 rounded">{benchmarkPreviewData?.hf_repo || selectedBenchmark?.hf_repo}</code> on HuggingFace.
              {benchmarkPreviewData?.samples && benchmarkPreviewData.samples.length > 0 && (
                <span className="block mt-2">
                  <span className="font-medium">Available fields: </span>
                  <span className="font-mono text-xs">
                    {Array.from(
                      new Set(benchmarkPreviewData.samples.flatMap((s: any) => Object.keys(s)))
                    ).join(", ")}
                  </span>
                </span>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto min-h-0 py-4">
            {isBenchmarkPreviewLoading ? (
               <div className="flex flex-col items-center justify-center p-8 gap-3">
                 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                 <p className="text-sm text-muted-foreground">Loading from HuggingFace...</p>
               </div>
            ) : benchmarkPreviewData?.samples && benchmarkPreviewData.samples.length > 0 ? (
              <div className="overflow-x-auto">
                {(() => {
                  // Get all unique keys from all samples
                  const allKeys = Array.from(
                    new Set(
                      benchmarkPreviewData.samples.flatMap((sample: any) => Object.keys(sample))
                    )
                  );

                  return (
                    <div className="border rounded-md">
                      <Table>
                        <TableHeader className="sticky top-0 bg-background z-10">
                          <TableRow>
                            <TableHead className="w-12">#</TableHead>
                            {allKeys.map((key) => (
                              <TableHead key={key}>{key}</TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {benchmarkPreviewData.samples.map((sample: any, idx: number) => (
                            <TableRow key={idx}>
                              <TableCell className="text-muted-foreground">{idx + 1}</TableCell>
                              {allKeys.map((key) => (
                                <TableCell key={key} className="max-w-md align-top">
                                  <ExpandableCell value={sample[key]} />
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  );
                })()}
              </div>
            ) : (
                <div className="text-center text-muted-foreground p-4">
                    <p>No preview available</p>
                    <p className="text-xs mt-2">The benchmark data could not be loaded from HuggingFace.</p>
                </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </Layout>
  );
}
