import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { Check, ChevronRight, Database, FileText, Gavel, Key, Play, Server, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: 1, title: "Select Dataset", icon: Database },
  { id: 2, title: "Guidelines", icon: FileText },
  { id: 3, title: "Models", icon: Server },
  { id: 4, title: "Judge Model", icon: Gavel },
  { id: 5, title: "API Keys", icon: Key },
  { id: 6, title: "Review", icon: Play },
];

export default function Submit() {
  const [currentStep, setCurrentStep] = useState(1);

  const handleNext = () => {
    if (currentStep < STEPS.length) setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

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
                    currentStep === step.id ? "bg-mint-50 text-mint-900" : 
                    currentStep > step.id ? "text-black" : "text-muted-foreground"
                  )}
                >
                  <div className={cn(
                    "w-6 h-6 rounded-full flex items-center justify-center text-xs border",
                    currentStep === step.id ? "border-mint-500 bg-mint-500 text-white" :
                    currentStep > step.id ? "border-black bg-black text-white" :
                    "border-zinc-200 bg-white"
                  )}>
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
            <div className="mb-8 flex justify-between items-center md:hidden">
              <span className="font-bold">Step {currentStep} of {STEPS.length}</span>
              <span className="text-muted-foreground">{STEPS[currentStep-1].title}</span>
            </div>

            <Card className="min-h-[500px] flex flex-col shadow-sm border-border">
              <CardHeader className="border-b border-border bg-zinc-50/30">
                <div className="flex items-center gap-2 text-mint-600 mb-1">
                   {CurrentStepIcon && <CurrentStepIcon className="w-5 h-5" />}
                   <span className="font-bold text-xs uppercase tracking-wider">Step {currentStep}</span>
                </div>
                <CardTitle className="text-2xl">{STEPS[currentStep-1].title}</CardTitle>
              </CardHeader>
              
              <CardContent className="flex-1 p-8">
                {/* Step Content Mockup */}
                {currentStep === 1 && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {["MMLU-Pro", "HumanEval+", "GSM8K", "TruthfulQA"].map((ds) => (
                        <div key={ds} className="border border-border p-4 rounded-lg hover:border-mint-500 hover:bg-mint-50/10 cursor-pointer transition-all">
                          <div className="font-bold text-lg mb-1">{ds}</div>
                          <div className="text-sm text-muted-foreground">Standard benchmark dataset</div>
                        </div>
                      ))}
                    </div>
                    <div className="pt-4 border-t border-border">
                      <Label>Or upload custom dataset (JSONL)</Label>
                      <div className="mt-2 border-2 border-dashed border-zinc-200 rounded-lg p-8 text-center hover:bg-zinc-50 transition-colors cursor-pointer">
                        <span className="text-muted-foreground text-sm">Drag & drop file here or click to browse</span>
                      </div>
                    </div>
                  </div>
                )}
                
                {currentStep === 3 && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {[
                        { name: "LLaMA 3 70B", provider: "Baseten.com" },
                        { name: "LLaMA 3 70B", provider: "Together.ai" },
                        { name: "Mixtral 8x22B", provider: "Baseten.com" },
                        { name: "Mistral Large", provider: "Mistral AI" },
                        { name: "GPT-4o", provider: "OpenAI" },
                        { name: "Claude 3.5 Sonnet", provider: "Anthropic" },
                        { name: "Qwen 2 72B", provider: "Together.ai" },
                        { name: "DeepSeek Coder V2", provider: "DeepSeek" },
                      ].map((model, i) => (
                        <div key={i} className="border border-border p-4 rounded-lg hover:border-mint-500 hover:bg-mint-50/10 cursor-pointer transition-all flex items-center justify-between group">
                          <div>
                            <div className="font-bold text-lg mb-1 group-hover:text-mint-900">{model.name}</div>
                            <div className="text-sm text-muted-foreground flex items-center gap-1">
                              <span className="w-2 h-2 rounded-full bg-green-500"></span>
                              {model.provider}
                            </div>
                          </div>
                          <div className="w-5 h-5 rounded-full border border-zinc-300 group-hover:border-mint-500 group-hover:bg-mint-500 transition-colors"></div>
                        </div>
                      ))}
                    </div>
                    <div className="pt-4 border-t border-border text-center">
                      <Button variant="outline" className="gap-2 border-dashed">
                        <Plus className="w-4 h-4" /> Add Custom Model Endpoint
                      </Button>
                    </div>
                  </div>
                )}

                {currentStep === 5 && (
                  <div className="space-y-6 max-w-md">
                    <div className="space-y-2">
                       <Label>OpenAI API Key</Label>
                       <Input type="password" placeholder="sk-..." />
                    </div>
                    <div className="space-y-2">
                       <Label>Anthropic API Key</Label>
                       <Input type="password" placeholder="sk-ant-..." />
                    </div>
                    <p className="text-xs text-muted-foreground bg-yellow-50 p-3 rounded text-yellow-800 border border-yellow-100">
                      Keys are never stored on our servers. They are used only for this session in your browser.
                    </p>
                  </div>
                )}

                {/* Fallback for other steps */}
                {![1, 3, 5].includes(currentStep) && (
                   <div className="flex flex-col items-center justify-center h-full text-muted-foreground space-y-4">
                      <div className="w-16 h-16 rounded-full bg-zinc-100 flex items-center justify-center">
                        <LayersIcon step={currentStep} />
                      </div>
                      <p>Configuration options for {STEPS[currentStep-1].title} will appear here.</p>
                   </div>
                )}

              </CardContent>

              <div className="p-6 border-t border-border flex justify-between bg-zinc-50/30">
                <Button 
                  variant="ghost" 
                  onClick={handleBack} 
                  disabled={currentStep === 1}
                >
                  Back
                </Button>
                <Button 
                  className="bg-black hover:bg-zinc-800 text-white gap-2" 
                  onClick={handleNext}
                >
                  {currentStep === STEPS.length ? "Submit Evaluation" : "Next Step"}
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
}

function LayersIcon({ step }: { step: number }) {
  if (step === 2) return <FileText className="w-8 h-8" />;
  if (step === 3) return <Server className="w-8 h-8" />;
  if (step === 4) return <Gavel className="w-8 h-8" />;
  if (step === 6) return <Play className="w-8 h-8" />;
  return <Database className="w-8 h-8" />;
}
