import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { RefreshCw, Clock, CheckCircle, XCircle, Loader2, Eye, Info } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useState } from "react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export default function Results() {
  const { isAuthenticated } = useAuth();

  // Fetch traces/evaluations
  const { data: tracesData, isLoading, refetch } = useQuery({
    queryKey: ["traces"],
    queryFn: () => apiClient.getTraces(),
    enabled: isAuthenticated,
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  });

  const traces = tracesData?.traces || [];

  const [selectedTrace, setSelectedTrace] = useState<any>(null);

  const { data: traceDetails, isLoading: isLoadingDetails } = useQuery({
    queryKey: ["traceDetails", selectedTrace?.id],
    queryFn: () => apiClient.getTraceDetails(selectedTrace.id),
    enabled: !!selectedTrace?.id,
  });

  const { data: traceSamplesData, isLoading: isLoadingSamples } = useQuery({
    queryKey: ["traceSamples", selectedTrace?.id],
    queryFn: () => apiClient.getTraceSamples(selectedTrace.id),
    enabled: !!selectedTrace && selectedTrace.status === "completed",
  });

  const traceSamples = traceSamplesData?.samples || [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <Badge className="bg-green-50 text-green-700 border-green-200">
            <CheckCircle className="w-3 h-3 mr-1" />
            Completed
          </Badge>
        );
      case "running":
        return (
          <Badge className="bg-blue-50 text-blue-700 border-blue-200">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Running
          </Badge>
        );
      case "failed":
        return (
          <Badge className="bg-red-50 text-red-700 border-red-200">
            <XCircle className="w-3 h-3 mr-1" />
            Failed
          </Badge>
        );
      default:
        return (
          <Badge className="bg-gray-50 text-gray-700 border-gray-200">
            <Clock className="w-3 h-3 mr-1" />
            Pending
          </Badge>
        );
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const renderScores = (scores: any, metricDocs: any) => {
    if (!scores) return null;

    const scoreEntries = Object.entries(scores);
    const hasCategoricalScores = scoreEntries.some(([, scoreData]: [string, any]) => 'distribution' in scoreData);

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Guideline</TableHead>
            <TableHead>Score</TableHead>
            {hasCategoricalScores && <TableHead>Distribution</TableHead>}
            <TableHead className="text-right">Failed</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {scoreEntries.map(([guidelineName, scoreData]: [string, any]) => {
            const isNumeric = 'mean' in scoreData;
            const isCategorical = 'distribution' in scoreData;
            const hasMetricDoc = metricDocs && metricDocs[guidelineName];

            return (
              <TableRow key={guidelineName}>
                <TableCell className="font-medium">
                  <div className="flex items-center gap-2">
                    <span>{guidelineName}</span>
                    {hasMetricDoc && (
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info className="w-4 h-4 text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-md">
                            <div className="space-y-2 text-sm">
                              {metricDocs[guidelineName].map((desc: any, idx: number) => (
                                <div key={idx} className="space-y-1">
                                  <p><span className="font-semibold">Measure:</span> {desc.measure}</p>
                                  <p><span className="font-semibold">Sample:</span> {desc.sample_level}</p>
                                  <p><span className="font-semibold">Corpus:</span> {desc.corpus_level}</p>
                                </div>
                              ))}
                            </div>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  {isNumeric && (
                    <span className="font-mono">
                      {scoreData.mean.toFixed(2)} ± {scoreData.std.toFixed(2)}
                    </span>
                  )}
                  {isCategorical && (
                    <span className="font-medium">{scoreData.mode || 'N/A'}</span>
                  )}
                </TableCell>
                {hasCategoricalScores && (
                  <TableCell>
                    {isCategorical && (
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(scoreData.distribution).map(([category, count]: [string, any]) => (
                          <Badge key={category} variant="outline" className="text-xs">
                            {category}: {count}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {isNumeric && <span className="text-muted-foreground">-</span>}
                  </TableCell>
                )}
                <TableCell className="text-right">
                  {scoreData.failed > 0 ? (
                    <span className="text-red-600 font-medium">{scoreData.failed}</span>
                  ) : (
                    <span className="text-muted-foreground">0</span>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    );
  };

  const renderGuidelines = (names: string[]) => {
    const maxChars = 28;
    const visible: string[] = [];
    let usedChars = 0;

    for (const name of names) {
      const nextChars = visible.length === 0 ? name.length : usedChars + 2 + name.length;
      if (nextChars > maxChars) {
        break;
      }
      visible.push(name);
      usedChars = nextChars;
    }

    if (names.length === 1) {
      const name = names[0];
      const displayName =
        name.length > maxChars ? `${name.slice(0, maxChars)}....` : name;

      return (
        <div className="flex max-w-[240px]">
          <Badge variant="secondary" className="text-xs max-w-[240px] truncate">
            {displayName}
          </Badge>
        </div>
      );
    }

    const didTruncate = visible.some((name) => name.length > maxChars);
    const displayNames = visible.map((name) =>
      name.length > maxChars ? `${name.slice(0, maxChars)}....` : name
    );
    const hasMore = visible.length < names.length || didTruncate;

    return (
      <div className="flex flex-wrap gap-1 max-w-[240px]">
        {displayNames.map((name) => (
          <Badge key={name} variant="secondary" className="text-xs">
            {name}
          </Badge>
        ))}
        {hasMore && (
          <Badge variant="secondary" className="text-xs">
            ....
          </Badge>
        )}
      </div>
    );
  };

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <CheckCircle className="w-16 h-16 text-muted-foreground mb-4" />
          <h2 className="text-2xl font-bold mb-2">Please login to view results</h2>
          <p className="text-muted-foreground">You need to be authenticated to access this page.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-4xl font-display font-bold mb-2">Evaluation Results</h1>
            <p className="text-muted-foreground">View your evaluation history and results</p>
          </div>
          <Button
            variant="outline"
            className="gap-2"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Evaluations</p>
                  <p className="text-3xl font-bold">{traces.length}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Completed</p>
                  <p className="text-3xl font-bold text-green-600">
                    {traces.filter((t) => t.status === "completed").length}
                  </p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Running</p>
                  <p className="text-3xl font-bold text-blue-600">
                    {traces.filter((t) => t.status === "running").length}
                  </p>
                </div>
                <Loader2 className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Failed</p>
                  <p className="text-3xl font-bold text-red-600">
                    {traces.filter((t) => t.status === "failed").length}
                  </p>
                </div>
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results Table */}
        <Card>
          <CardHeader>
            <CardTitle>Evaluation History</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                Loading evaluations...
              </div>
            ) : traces.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground mb-4">No evaluations yet</p>
                <p className="text-sm text-muted-foreground">
                  Submit your first evaluation to see results here
                </p>
                <Button
                  className="mt-4"
                  onClick={() => (window.location.href = "/submit")}
                >
                  Create Evaluation
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Dataset</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Guidelines</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {traces.map((trace) => (
                    <TableRow key={trace.id}>
                      <TableCell className="font-mono text-sm">#{trace.id}</TableCell>
                      <TableCell className="font-medium">{trace.dataset_name}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div className="font-medium">{trace.completion_model}</div>
                          <div className="text-muted-foreground text-xs">
                            {trace.model_provider}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="max-w-[240px]">
                        {renderGuidelines(trace.guideline_names)}
                      </TableCell>
                      <TableCell>{getStatusBadge(trace.status)}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(trace.created_at)}
                      </TableCell>
                      <TableCell>
                        {trace.status === "completed" && trace.summary && (
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="gap-2"
                                onClick={() => setSelectedTrace(trace)}
                              >
                                <Eye className="w-4 h-4" />
                                View Scores
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-4xl h-[80vh] flex flex-col p-6 overflow-hidden">
                              <DialogHeader className="pb-4">
                                <DialogTitle>Evaluation Details #{selectedTrace?.id}</DialogTitle>
                              </DialogHeader>
                              
                              {selectedTrace && (
                                <div className="flex-1 overflow-y-auto pr-2 space-y-6">
                                  {/* Evaluation Info */}
                                  <Card>
                                    <CardHeader>
                                      <CardTitle className="text-lg">Evaluation Information</CardTitle>
                                    </CardHeader>
                                    <CardContent className="grid grid-cols-2 gap-4">
                                      {isLoadingDetails ? (
                                        <div className="col-span-2 flex justify-center p-4">
                                          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                                        </div>
                                      ) : traceDetails ? (
                                        <>
                                          <div>
                                            <span className="text-sm text-muted-foreground">Dataset:</span>
                                            <p className="font-medium">{traceDetails.spec.dataset_name ?? traceDetails.spec.task_name ?? selectedTrace.dataset_name}</p>
                                          </div>
                                          <div className="flex gap-4">
                                            <div>
                                              <span className="text-sm text-muted-foreground">Model:</span>
                                              <p className="font-medium">{traceDetails.spec.completion_model ?? selectedTrace.completion_model}</p>
                                            </div>
                                            <div>
                                              <span className="text-sm text-muted-foreground">Provider:</span>
                                              <p className="font-medium">{traceDetails.spec.model_provider ?? selectedTrace.model_provider}</p>
                                            </div>
                                          </div>
                                          {traceDetails.spec.judge_model ? (
                                            <div className="flex gap-4">
                                              <div>
                                                <span className="text-sm text-muted-foreground">Judge Model:</span>
                                                <p className="font-medium">{traceDetails.spec.judge_model}</p>
                                              </div>
                                              <div>
                                                <span className="text-sm text-muted-foreground">Judge Provider:</span>
                                                <p className="font-medium">{traceDetails.judge_model_provider}</p>
                                              </div>
                                            </div>
                                          ) : null}
                                          {traceDetails.spec.sample_count != null ? (
                                            <div>
                                              <span className="text-sm text-muted-foreground">Number of samples:</span>
                                              <p className="font-medium">{traceDetails.spec.sample_count}</p>
                                            </div>
                                          ) : null}
                                          {traceDetails.spec.n_fewshots != null ? (
                                            <div>
                                              <span className="text-sm text-muted-foreground">Few shot examples:</span>
                                              <p className="font-medium">{traceDetails.spec.n_fewshots}</p>
                                            </div>
                                          ) : null}
                                          <div>
                                            <span className="text-sm text-muted-foreground">Status:</span>
                                            <p className="font-medium">{getStatusBadge(traceDetails.status)}</p>
                                          </div>
                                          <div>
                                            <span className="text-sm text-muted-foreground">Created:</span>
                                            <p className="font-medium">{formatDate(traceDetails.created_at)}</p>
                                          </div>
                                        </>
                                      ) : (
                                        <>
                                          <div>
                                            <span className="text-sm text-muted-foreground">Dataset:</span>
                                            <p className="font-medium">{selectedTrace.dataset_name}</p>
                                          </div>
                                          <div className="flex gap-4">
                                            <div>
                                              <span className="text-sm text-muted-foreground">Model:</span>
                                              <p className="font-medium">{selectedTrace.completion_model}</p>
                                            </div>
                                            <div>
                                              <span className="text-sm text-muted-foreground">Provider:</span>
                                              <p className="font-medium">{selectedTrace.model_provider}</p>
                                            </div>
                                          </div>
                                          {selectedTrace.judge_model ? (
                                            <div className="flex gap-4">
                                              <div>
                                                <span className="text-sm text-muted-foreground">Judge Model:</span>
                                                <p className="font-medium">{selectedTrace.judge_model}</p>
                                              </div>
                                              <div>
                                                <span className="text-sm text-muted-foreground">Judge Provider:</span>
                                                <p className="font-medium">{selectedTrace.judge_model_provider ?? ""}</p>
                                              </div>
                                            </div>
                                          ) : null}
                                          {selectedTrace.summary?.n_samples != null ? (
                                            <div>
                                              <span className="text-sm text-muted-foreground">Number of samples:</span>
                                              <p className="font-medium">{selectedTrace.summary.n_samples}</p>
                                            </div>
                                          ) : null}
                                          {selectedTrace.summary?.n_fewshots != null ? (
                                            <div>
                                              <span className="text-sm text-muted-foreground">Few shot examples:</span>
                                              <p className="font-medium">{selectedTrace.summary.n_fewshots}</p>
                                            </div>
                                          ) : null}
                                          <div>
                                            <span className="text-sm text-muted-foreground">Status:</span>
                                            <p className="font-medium">{getStatusBadge(selectedTrace.status)}</p>
                                          </div>
                                          <div>
                                            <span className="text-sm text-muted-foreground">Created:</span>
                                            <p className="font-medium">{formatDate(selectedTrace.created_at)}</p>
                                          </div>
                                        </>
                                      )}
                                    </CardContent>
                                  </Card>

                                  {/* Scores */}
                                  <div>
                                    <h3 className="text-lg font-semibold mb-4">Evaluation Scores</h3>
                                    <div className="border rounded-lg">
                                      {renderScores(selectedTrace.summary?.scores, selectedTrace.summary?.metric_docs)}
                                    </div>
                                  </div>

                                  {/* Samples Section */}
                                  <div className="pt-6 border-t">
                                     <h3 className="text-lg font-semibold mb-4">Samples Preview</h3>
                                     {isLoadingSamples ? (
                                        <div className="flex justify-center p-8">
                                          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                                        </div>
                                      ) : traceSamples.length > 0 ? (
                                        <div className="space-y-6">
                                          {traceSamples.map((sample: any, idx: number) => (
                                            <Card key={idx}>
                                              <CardHeader className="pb-3">
                                                <CardTitle className="text-base font-medium">Sample {idx + 1}</CardTitle>
                                              </CardHeader>
                                              <CardContent className="space-y-4">
                                                <div>
                                                  <h4 className="text-sm font-semibold text-muted-foreground mb-1">Input</h4>
                                                  <div className="bg-muted p-3 rounded-md text-sm whitespace-pre-wrap font-mono max-h-40 overflow-y-auto">
                                                    {sample.input}
                                                  </div>
                                                </div>
                                                
                                                <div>
                                                  <h4 className="text-sm font-semibold text-muted-foreground mb-1">Model Output</h4>
                                                  <div className="bg-blue-50 border border-blue-100 p-3 rounded-md text-sm whitespace-pre-wrap font-mono text-blue-900 max-h-40 overflow-y-auto">
                                                    {sample.prediction}
                                                  </div>
                                                </div>

                                                {sample.gold && (
                                                  <div>
                                                    <h4 className="text-sm font-semibold text-muted-foreground mb-1">Reference Answer</h4>
                                                    <div className="bg-green-50 border border-green-100 p-3 rounded-md text-sm whitespace-pre-wrap font-mono text-green-900 max-h-40 overflow-y-auto">
                                                      {Array.isArray(sample.gold) ? sample.gold.join(", ") : sample.gold}
                                                    </div>
                                                  </div>
                                                )}

                                                {Object.keys(sample.metric_scores).length > 0 && (
                                                  <div>
                                                    <h4 className="text-sm font-semibold text-muted-foreground mb-2">Detailed Scores</h4>
                                                    <div className="flex flex-wrap gap-2">
                                                      {Object.entries(sample.metric_scores).map(([key, value]) => (
                                                        <Badge key={key} variant="outline" className="font-mono">
                                                          {key}: {typeof value === 'number' ? value.toFixed(3) : String(value)}
                                                        </Badge>
                                                      ))}
                                                    </div>
                                                  </div>
                                                )}
                                              </CardContent>
                                            </Card>
                                          ))}
                                        </div>
                                      ) : (
                                        <div className="text-center py-8 text-muted-foreground bg-muted/20 rounded-lg">
                                          <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                          <p>No samples available for preview.</p>
                                        </div>
                                      )}
                                  </div>
                                </div>
                              )}
                            </DialogContent>
                          </Dialog>
                        )}
                        {trace.status === "running" && (
                          <span className="text-sm text-muted-foreground">
                            In progress...
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Info Box */}
        {traces.some((t) => t.status === "running") && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              <strong>🔄 Auto-refreshing:</strong> This page automatically refreshes
              every 5 seconds to show the latest evaluation status.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
