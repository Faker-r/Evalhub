import { useState, useEffect } from "react";
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
import { Badge } from "@/components/ui/badge";
import { ArrowUpRight, TrendingUp, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api";

// Helper function to determine if a provider is typically open source
const isOpenSourceProvider = (provider: string): boolean => {
  const openSourceProviders = ["meta", "mistral", "alibaba", "huggingface", "ollama"];
  return openSourceProviders.some(os => provider.toLowerCase().includes(os));
};

export function LeaderboardTable() {
  const [selectedDataset, setSelectedDataset] = useState<string>("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  // Fetch datasets to populate the selector
  const { data: datasetsData } = useQuery({
    queryKey: ["datasets"],
    queryFn: () => apiClient.getDatasets(),
  });

  const datasets = datasetsData?.datasets || [];

  // Set default dataset when datasets are loaded
  useEffect(() => {
    if (datasets.length > 0 && selectedDataset === "") {
      setSelectedDataset(datasets[0].name);
    }
  }, [datasets, selectedDataset]);

  // Fetch leaderboard data
  const { data: leaderboardData, isLoading, error } = useQuery({
    queryKey: ["leaderboard", selectedDataset],
    queryFn: () => apiClient.getLeaderboard(selectedDataset),
    enabled: selectedDataset !== "",
  });

  const entries = leaderboardData?.entries || [];
  const sampleCount = leaderboardData?.sample_count || 0;

  // Sort entries by normalized_avg_score (descending) and add rank
  const rankedEntries = entries
    .sort((a, b) => b.normalized_avg_score - a.normalized_avg_score)
    .map((entry, index) => ({
      ...entry,
      rank: index + 1,
    }));

  // Filter by category if needed
  const filteredEntries = rankedEntries.filter((entry) => {
    if (categoryFilter === "all") return true;
    const isOpenSource = isOpenSourceProvider(entry.model_provider);
    if (categoryFilter === "opensource") return isOpenSource;
    if (categoryFilter === "proprietary") return !isOpenSource;
    return true;
  });

  // Format date for last updated
  const formatLastUpdated = () => {
    if (entries.length === 0) return "Never";
    const latestEntry = entries.reduce((latest, entry) => {
      const entryDate = new Date(entry.created_at);
      const latestDate = new Date(latest.created_at);
      return entryDate > latestDate ? entry : latest;
    }, entries[0]);
    const date = new Date(latestEntry.created_at);
    return date.toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center bg-white p-4 rounded-lg border border-border shadow-sm">
        <div className="flex items-center gap-2 text-sm font-medium mr-2">
          <TrendingUp className="w-4 h-4 text-mint-600" />
          Filters:
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[180px] bg-white">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="proprietary">Proprietary</SelectItem>
            <SelectItem value="opensource">Open Source</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedDataset} onValueChange={setSelectedDataset}>
          <SelectTrigger className="w-[180px] bg-white">
            <SelectValue placeholder="Dataset" />
          </SelectTrigger>
          <SelectContent>
            {datasets.map((dataset) => (
              <SelectItem key={dataset.id} value={dataset.name}>
                {dataset.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="ml-auto text-sm text-muted-foreground">
          Last updated: <span className="font-mono text-black">{formatLastUpdated()}</span>
        </div>
      </div>

      {/* Table */}
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
        ) : filteredEntries.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            {selectedDataset === "" 
              ? "Please select a dataset" 
              : "No entries found for this dataset"}
          </div>
        ) : (
          <>
            <div className="p-4 bg-zinc-50/50 border-b border-border">
              <div className="text-sm text-muted-foreground">
                Dataset: <span className="font-semibold text-black">{leaderboardData?.dataset_name}</span> • 
                Samples: <span className="font-semibold text-black">{sampleCount}</span> • 
                Entries: <span className="font-semibold text-black">{filteredEntries.length}</span>
              </div>
            </div>
            <Table>
              <TableHeader className="bg-zinc-50/50">
                <TableRow>
                  <TableHead className="w-[80px] font-bold text-black">Rank</TableHead>
                  <TableHead className="font-bold text-black">Model</TableHead>
                  <TableHead className="font-bold text-black">Provider</TableHead>
                  <TableHead className="font-bold text-black">Category</TableHead>
                  <TableHead className="text-right font-bold text-black">Score</TableHead>
                  <TableHead className="text-right font-bold text-black">Failures</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEntries.map((entry) => {
                  const isOpenSource = isOpenSourceProvider(entry.model_provider);
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
                      <TableCell>{entry.model_provider}</TableCell>
                      <TableCell>
                        <Badge 
                          variant="secondary" 
                          className={isOpenSource ? "bg-mint-100 text-mint-800 border-mint-200" : ""}
                        >
                          {isOpenSource ? "Open Source" : "Proprietary"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-mono font-bold text-lg">
                        {(entry.normalized_avg_score * 100).toFixed(1)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-muted-foreground text-xs">
                        {entry.total_failures}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </>
        )}
      </div>
    </div>
  );
}
