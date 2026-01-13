import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";
import { Check, ChevronRight, ChevronLeft, Database, FileText, Play, Server } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";

const STEPS = [
  { id: 1, title: "Select Dataset", icon: Database },
  { id: 2, title: "Guidelines", icon: FileText },
  { id: 3, title: "Model & Judge", icon: Server },
  { id: 4, title: "Submit", icon: Play },
];

export default function Submit() {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [, setLocation] = useLocation();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [selectedGuidelines, setSelectedGuidelines] = useState<string[]>([]);
  const [completionModel, setCompletionModel] = useState("gpt-3.5-turbo");
  const [judgeModel, setJudgeModel] = useState("gpt-3.5-turbo");
  const [modelProvider, setModelProvider] = useState("openai");
  const [judgeProvider, setJudgeProvider] = useState("openai");

  // Fetch datasets
  const { data: datasetsData } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => apiClient.getDatasets(),
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
  const guidelines = guidelinesData?.guidelines || [];
  const apiKeys = apiKeysData?.api_key_providers || [];

  // Submit evaluation
  const submitMutation = useMutation({
    mutationFn: () =>
      apiClient.createEvaluation({
        dataset_name: selectedDataset,
        guideline_names: selectedGuidelines,
        completion_model: completionModel,
        model_provider: modelProvider,
        judge_model: judgeModel,
        judge_model_provider: judgeProvider,
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

  const handleNext = () => {
    if (currentStep === 1 && !selectedDataset) {
      toast({
        title: "Error",
        description: "Please select a dataset",
        variant: "destructive",
      });
      return;
    }
    if (currentStep === 2 && selectedGuidelines.length === 0) {
      toast({
        title: "Error",
        description: "Please select at least one guideline",
        variant: "destructive",
      });
      return;
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
    submitMutation.mutate();
  };

  const toggleGuideline = (guidelineName: string) => {
    if (selectedGuidelines.includes(guidelineName)) {
      setSelectedGuidelines(selectedGuidelines.filter((g) => g !== guidelineName));
    } else {
      setSelectedGuidelines([...selectedGuidelines, guidelineName]);
    }
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
                  <div className="space-y-4">
                    <Label>Select a dataset</Label>
                    {datasets.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        No datasets available. Please upload one first.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {datasets.map((ds) => (
                          <div
                            key={ds.id}
                            onClick={() => setSelectedDataset(ds.name)}
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
                )}

                {currentStep === 2 && (
                  <div className="space-y-4">
                    <Label>Select guidelines (at least one)</Label>
                    {guidelines.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        No guidelines available. Please create one first.
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {guidelines.map((guideline) => (
                          <div
                            key={guideline.id}
                            onClick={() => toggleGuideline(guideline.name)}
                            className={cn(
                              "border p-4 rounded-lg cursor-pointer transition-all",
                              selectedGuidelines.includes(guideline.name)
                                ? "border-mint-500 bg-mint-50/20"
                                : "border-border hover:border-mint-300"
                            )}
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="font-bold">{guideline.name}</div>
                                <div className="text-sm text-muted-foreground">
                                  {guideline.category} • {guideline.scoring_scale === "numeric" 
                                    ? `${guideline.scoring_scale_config.min_value}-${guideline.scoring_scale_config.max_value}` 
                                    : guideline.scoring_scale}
                                </div>
                              </div>
                              {selectedGuidelines.includes(guideline.name) && (
                                <Check className="w-5 h-5 text-mint-500" />
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 3 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Judge Section - Left */}
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Judge Provider</Label>
                        <Select value={judgeProvider} onValueChange={setJudgeProvider}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="openai">OpenAI</SelectItem>
                            <SelectItem value="anthropic">Anthropic</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Judge Model</Label>
                        <Input
                          value={judgeModel}
                          onChange={(e) => setJudgeModel(e.target.value)}
                          placeholder="e.g., gpt-4"
                        />
                      </div>
                    </div>

                    {/* Completion Model Section - Right */}
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Model Provider</Label>
                        <Select value={modelProvider} onValueChange={setModelProvider}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="openai">OpenAI</SelectItem>
                            <SelectItem value="anthropic">Anthropic</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Completion Model</Label>
                        <Input
                          value={completionModel}
                          onChange={(e) => setCompletionModel(e.target.value)}
                          placeholder="e.g., gpt-3.5-turbo"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {currentStep === 4 && (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="font-bold text-lg">Review Your Evaluation</h3>
                      <div className="space-y-2 p-4 bg-zinc-50 rounded-lg">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Dataset:</span>
                          <span className="font-medium">{selectedDataset}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Guidelines:</span>
                          <span className="font-medium">
                            {selectedGuidelines.join(", ")}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Completion Model:</span>
                          <span className="font-medium">{completionModel}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Judge Model:</span>
                          <span className="font-medium">{judgeModel}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Judge Provider:</span>
                          <span className="font-medium">{judgeProvider}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Completion Provider:</span>
                          <span className="font-medium">{modelProvider}</span>
                        </div>
                      </div>
                      {apiKeys.length === 0 && (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            ⚠️ No API keys configured. Please add your{" "}
                            {modelProvider} API key in your profile settings.
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
                    disabled={submitMutation.isPending}
                    className="bg-mint-500 hover:bg-mint-600"
                  >
                    {submitMutation.isPending ? "Submitting..." : "Start Evaluation"}
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
