import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowUpRight, TrendingUp, Loader2, ArrowUpDown } from "lucide-react";
import { apiClient } from "@/lib/api";

function formatModelProvider(provider: string) {
  if (!provider) return "—";
  if (provider.toLowerCase() === "openrouter") return "OpenRouter (routing)";
  return provider;
}

export function LeaderboardTable() {
  const [selectedDataset, setSelectedDataset] = useState<string>("all");
  const [sortByMetric, setSortByMetric] = useState<string>("all");

  const { data: leaderboardData, isLoading, error } = useQuery({
    queryKey: ["leaderboard"],
    queryFn: () => apiClient.getLeaderboard(),
  });

  const datasets = leaderboardData?.datasets || [];

  const showAllDatasets = selectedDataset === "all";
  const showAllMetrics = sortByMetric === "all";

  const currentDataset = datasets.find(d => d.dataset_name === selectedDataset);
  const entries = showAllDatasets ? [] : (currentDataset?.entries || []);
  const sampleCount = currentDataset?.sample_count || 0;

  const allMetricNames = new Set<string>();
  entries.forEach(entry => {
    entry.scores.forEach(score => allMetricNames.add(score.metric_name));
  });
  const metricNames = Array.from(allMetricNames).sort();

  const allEntriesByModel = new Map<string, any>();
  if (showAllDatasets) {
    datasets.forEach(dataset => {
      dataset.entries.forEach(entry => {
        const key = `${entry.completion_model}|${entry.model_provider}`;
        if (!allEntriesByModel.has(key)) {
          allEntriesByModel.set(key, {
            completion_model: entry.completion_model,
            model_provider: entry.model_provider,
            trace_id: entry.trace_id,
            created_at: entry.created_at,
            scoresByDataset: new Map<string, Map<string, { mean: number; std: number; failed: number }>>(),
          });
        }
        const modelEntry = allEntriesByModel.get(key);
        if (!modelEntry.scoresByDataset.has(dataset.dataset_name)) {
          modelEntry.scoresByDataset.set(dataset.dataset_name, new Map());
        }
        entry.scores.forEach(score => {
          modelEntry.scoresByDataset.get(dataset.dataset_name).set(score.metric_name, {
            mean: score.mean,
            std: score.std,
            failed: score.failed,
          });
        });
      });
    });
  }

  const rankedEntries = showAllDatasets 
    ? Array.from(allEntriesByModel.values()).map((entry, index) => ({ ...entry, rank: index + 1 }))
    : [...entries]
        .sort((a, b) => {
          const aScore = a.scores.find(s => s.metric_name === sortByMetric);
          const bScore = b.scores.find(s => s.metric_name === sortByMetric);
          const aValue = aScore?.mean ?? -1;
          const bValue = bScore?.mean ?? -1;
          return bValue - aValue;
        })
        .map((entry, index) => ({
          ...entry,
          rank: index + 1,
        }));

  const formatLastUpdated = () => {
    if (showAllDatasets) {
      if (rankedEntries.length === 0) return "Never";
      const latestEntry = rankedEntries.reduce((latest, entry) => {
        const entryDate = new Date(entry.created_at);
        const latestDate = new Date(latest.created_at);
        return entryDate > latestDate ? entry : latest;
      }, rankedEntries[0]);
      const date = new Date(latestEntry.created_at);
      return date.toLocaleString();
    } else {
      if (entries.length === 0) return "Never";
      const latestEntry = entries.reduce((latest, entry) => {
        const entryDate = new Date(entry.created_at);
        const latestDate = new Date(latest.created_at);
        return entryDate > latestDate ? entry : latest;
      }, entries[0]);
      const date = new Date(latestEntry.created_at);
      return date.toLocaleString();
    }
  };

  const datasetMetricStructure: { dataset: string; metrics: string[] }[] = [];
  if (showAllDatasets && showAllMetrics) {
    datasets.forEach(dataset => {
      const metrics = new Set<string>();
      dataset.entries.forEach(entry => {
        entry.scores.forEach(score => metrics.add(score.metric_name));
      });
      if (metrics.size > 0) {
        datasetMetricStructure.push({
          dataset: dataset.dataset_name,
          metrics: Array.from(metrics).sort(),
        });
      }
    });
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-4 items-center bg-white p-4 rounded-lg border border-border shadow-sm">
        <div className="flex items-center gap-2 text-sm font-medium mr-2">
          <TrendingUp className="w-4 h-4 text-mint-600" />
          Filters:
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-muted-foreground">Dataset:</label>
          <Select value={selectedDataset} onValueChange={setSelectedDataset}>
            <SelectTrigger className="w-[180px] bg-white">
              <SelectValue placeholder="Select dataset" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Datasets</SelectItem>
              {datasets.map((dataset) => (
                <SelectItem key={dataset.dataset_name} value={dataset.dataset_name}>
                  {dataset.dataset_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-muted-foreground">Metric:</label>
          <Select value={sortByMetric} onValueChange={setSortByMetric}>
            <SelectTrigger className="w-[180px] bg-white">
              <SelectValue placeholder="Select metric" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Metrics</SelectItem>
              {metricNames.map((metric) => (
                <SelectItem key={metric} value={metric}>
                  {metric}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="ml-auto text-sm text-muted-foreground">
          Last updated: <span className="font-mono text-black">{formatLastUpdated()}</span>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-white shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="w-6 h-6 animate-spin text-mint-600" />
            <span className="ml-2 text-muted-foreground">Loading leaderboard...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">
            Error loading leaderboard: {error instanceof Error ? error.message : "Unknown error"}
          </div>
        ) : rankedEntries.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            No entries found
          </div>
        ) : (
          <>
            {!showAllDatasets && (
              <div className="p-4 bg-zinc-50/50 border-b border-border">
                <div className="text-sm text-muted-foreground">
                  Dataset: <span className="font-semibold text-black">{currentDataset?.dataset_name}</span> • 
                  Samples: <span className="font-semibold text-black">{sampleCount}</span> • 
                  Entries: <span className="font-semibold text-black">{rankedEntries.length}</span>
                </div>
              </div>
            )}
            {showAllDatasets && (
              <div className="p-4 bg-zinc-50/50 border-b border-border">
                <div className="text-sm text-muted-foreground">
                  Showing all datasets • 
                  Models: <span className="font-semibold text-black">{rankedEntries.length}</span>
                </div>
              </div>
            )}
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-zinc-50/50">
                  {showAllDatasets && showAllMetrics ? (
                    <>
                      <TableRow>
                        <TableHead className="w-[60px] font-bold text-black" rowSpan={2}>Rank</TableHead>
                        <TableHead className="font-bold text-black" rowSpan={2}>Model</TableHead>
                        <TableHead className="font-bold text-black" rowSpan={2}>Model provider</TableHead>
                        {datasetMetricStructure.map(({ dataset, metrics }) => (
                          <TableHead 
                            key={dataset} 
                            className="text-center font-bold text-black border-l border-border"
                            colSpan={metrics.length}
                          >
                            {dataset}
                          </TableHead>
                        ))}
                      </TableRow>
                      <TableRow>
                        {datasetMetricStructure.map(({ dataset, metrics }) => 
                          metrics.map(metric => (
                            <TableHead 
                              key={`${dataset}-${metric}`} 
                              className="text-right font-bold text-black text-xs"
                            >
                              <div>{metric}</div>
                              <div className="text-xs font-normal text-muted-foreground">mean ± std</div>
                            </TableHead>
                          ))
                        )}
                      </TableRow>
                    </>
                  ) : (
                    <TableRow>
                      <TableHead className="w-[60px] font-bold text-black">Rank</TableHead>
                      <TableHead className="font-bold text-black">Model</TableHead>
                      <TableHead className="font-bold text-black">Model provider</TableHead>
                      {metricNames.map(metricName => (
                        <TableHead key={metricName} className="text-right font-bold text-black">
                          <div className="flex items-center justify-end gap-1">
                            {metricName}
                            {sortByMetric === metricName && <ArrowUpDown className="w-3 h-3" />}
                          </div>
                          <div className="text-xs font-normal text-muted-foreground">mean ± std</div>
                        </TableHead>
                      ))}
                      <TableHead className="text-right font-bold text-black">Failures</TableHead>
                    </TableRow>
                  )}
                </TableHeader>
                <TableBody>
                  {showAllDatasets && showAllMetrics ? (
                    rankedEntries.map((entry) => (
                      <TableRow 
                        key={entry.trace_id} 
                        className="hover:bg-mint-50/30 cursor-pointer transition-colors group"
                      >
                        <TableCell className="font-mono font-medium text-muted-foreground group-hover:text-black">
                          #{entry.rank}
                        </TableCell>
                        <TableCell>
                          <div className="font-bold flex items-center gap-2">
                            {entry.completion_model}
                            <ArrowUpRight className="w-3 h-3 opacity-0 group-hover:opacity-100 text-mint-600 transition-opacity" />
                          </div>
                        </TableCell>
                        <TableCell>{formatModelProvider(entry.model_provider)}</TableCell>
                        {datasetMetricStructure.map(({ dataset, metrics }) => 
                          metrics.map(metric => {
                            const score = entry.scoresByDataset?.get(dataset)?.get(metric);
                            return (
                              <TableCell key={`${dataset}-${metric}`} className="text-right font-mono text-sm">
                                {score ? (
                                  <div>
                                    <div className="font-bold">{(score.mean).toFixed(1)}</div>
                                    <div className="text-xs text-muted-foreground">± {(score.std).toFixed(1)}</div>
                                  </div>
                                ) : (
                                  <span className="text-muted-foreground">—</span>
                                )}
                              </TableCell>
                            );
                          })
                        )}
                      </TableRow>
                    ))
                  ) : (
                    rankedEntries.map((entry) => {
                      const scoresByMetric = new Map(
                        entry.scores.map((s: any) => [s.metric_name, s])
                      );
                      
                      return (
                        <TableRow 
                          key={entry.trace_id} 
                          className="hover:bg-mint-50/30 cursor-pointer transition-colors group"
                        >
                          <TableCell className="font-mono font-medium text-muted-foreground group-hover:text-black">
                            #{entry.rank}
                          </TableCell>
                          <TableCell>
                            <div className="font-bold flex items-center gap-2">
                              {entry.completion_model}
                              <ArrowUpRight className="w-3 h-3 opacity-0 group-hover:opacity-100 text-mint-600 transition-opacity" />
                            </div>
                          </TableCell>
                          <TableCell>{formatModelProvider(entry.model_provider)}</TableCell>
                          {metricNames.map(metricName => {
                            const score = scoresByMetric.get(metricName);
                            const isSortedBy = sortByMetric === metricName;
                            return (
                              <TableCell key={metricName} className={`text-right font-mono text-sm ${isSortedBy ? 'bg-mint-50/50' : ''}`}>
                                {score ? (
                                  <div>
                                    <div className={isSortedBy ? "font-bold text-lg" : "font-bold"}>{((score as any).mean).toFixed(1)}</div>
                                    <div className="text-xs text-muted-foreground">± {((score as any).std).toFixed(1)}</div>
                                  </div>
                                ) : (
                                  <span className="text-muted-foreground">—</span>
                                )}
                              </TableCell>
                            );
                          })}
                          <TableCell className="text-right font-mono text-muted-foreground text-xs">
                            {entry.total_failures}
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
