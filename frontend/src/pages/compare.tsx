import Layout from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Empty, EmptyHeader, EmptyTitle, EmptyDescription, EmptyMedia } from "@/components/ui/empty";
import { ModelSelection } from "@/components/model-selection";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip as RechartsTooltip,
} from "recharts";
import { AlertCircle, Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { apiClient } from "@/lib/api";
import {
  buildComparisonRows,
  buildRadarData,
  type ComparisonRow,
  toModelProviderKey,
  getDisplayScore,
  getNumericForDiff,
} from "@/lib/comparison-adapter";
import { cn } from "@/lib/utils";

type ModelConfig = {
  provider_id?: number;
  provider_name?: string;
  provider_slug?: string;
  model_id?: number;
  model_name?: string;
  api_name?: string;
  api_base?: string;
  is_openrouter?: boolean;
  openrouter_model_id?: string;
  openrouter_model_name?: string;
  openrouter_provider_slug?: string;
};

function configToPair(config: ModelConfig): { model: string; provider: string; label: string } | null {
  if (config.is_openrouter) {
    const model = config.openrouter_model_id ?? "";
    const provider = config.openrouter_provider_slug ?? "openrouter";
    const label = (config.openrouter_model_name ?? model) || "OpenRouter model";
    return model ? { model, provider, label } : null;
  }
  const model = (config.api_name ?? config.model_name) ?? "";
  const provider = (config.provider_name ?? config.provider_slug) ?? "";
  const label = (config.model_name ?? model) || "Model";
  return model && provider ? { model, provider, label } : null;
}

const RADAR_COLORS = ["#39E29D", "#000000", "#6366f1", "#f59e0b", "#ec4899"];

export default function Compare() {
  const [pairs, setPairs] = useState<{ id: string; model: string; provider: string; label: string }[]>([]);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [addModalConfig, setAddModalConfig] = useState<ModelConfig>({ is_openrouter: false });
  const [overlappingCount, setOverlappingCount] = useState<number | null>(null);
  const [overlappingLoading, setOverlappingLoading] = useState(false);
  const [report, setReport] = useState<{
    entries: { model: string; provider: string; dataset_name: string; metric_name: string; trace_id: number; created_at: string; score?: number | Record<string, unknown> }[];
    spec_by_trace: Record<string, Record<string, unknown> | null>;
  } | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<"benchmark" | "diff" | string>("benchmark");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [selectedRow, setSelectedRow] = useState<ComparisonRow | null>(null);
  const [radarVisibility, setRadarVisibility] = useState<Record<string, boolean>>({});

  const modelProviderPairs = useMemo(
    () => pairs.map((p) => ({ model: p.model, provider: p.provider })),
    [pairs]
  );

  useEffect(() => {
    if (pairs.length < 2) {
      setOverlappingCount(null);
      return;
    }
    let cancelled = false;
    setOverlappingLoading(true);
    apiClient
      .getOverlappingDatasets(modelProviderPairs)
      .then((r) => {
        if (!cancelled) setOverlappingCount(r.count);
      })
      .catch(() => {
        if (!cancelled) setOverlappingCount(0);
      })
      .finally(() => {
        if (!cancelled) setOverlappingLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [modelProviderPairs, pairs.length]);

  const handleCompare = useCallback(() => {
    if (pairs.length < 2) return;
    setReportError(null);
    setReportLoading(true);
    apiClient
      .getSideBySideReport(modelProviderPairs)
      .then((r) => {
        const specByTrace: Record<string, Record<string, unknown> | null> = {};
        for (const [k, v] of Object.entries(r.spec_by_trace)) {
          specByTrace[String(k)] = v as Record<string, unknown> | null;
        }
        setReport({
          entries: r.entries,
          spec_by_trace: specByTrace,
        });
      })
      .catch((e) => setReportError(e?.message ?? "Failed to load report"))
      .finally(() => setReportLoading(false));
  }, [modelProviderPairs, pairs.length]);

  const addPair = useCallback(() => {
    const pair = configToPair(addModalConfig);
    if (!pair) return;
    setPairs((prev) => [
      ...prev,
      { id: crypto.randomUUID(), ...pair },
    ]);
    setAddModalOpen(false);
    setAddModalConfig({ is_openrouter: false });
  }, [addModalConfig]);

  const removePair = useCallback((id: string) => {
    setPairs((prev) => prev.filter((p) => p.id !== id));
  }, []);

  const rows = useMemo(() => {
    if (!report) return [];
    return buildComparisonRows(report.entries, report.spec_by_trace);
  }, [report]);

  const modelKeys = useMemo(
    () => pairs.map((p) => toModelProviderKey(p.model, p.provider)),
    [pairs]
  );

  const radarData = useMemo(() => {
    if (modelKeys.length === 0) return [];
    return buildRadarData(rows, modelKeys);
  }, [rows, modelKeys]);

  const sortedRows = useMemo(() => {
    const arr = [...rows];
    if (sortKey === "benchmark") {
      arr.sort((a, b) => {
        const la = `${a.dataset} (${a.metric})`;
        const lb = `${b.dataset} (${b.metric})`;
        return sortDir === "asc" ? la.localeCompare(lb) : lb.localeCompare(la);
      });
    } else if (sortKey === "diff" && modelKeys.length >= 2) {
      const [aKey, bKey] = modelKeys;
      arr.sort((a, b) => {
        const ca = a.models[aKey];
        const cb = b.models[bKey];
        const na = ca ? getNumericForDiff(ca.score) : null;
        const nb = cb ? getNumericForDiff(cb.score) : null;
        const va = ca && na != null && cb ? na - (getNumericForDiff(cb.score) ?? 0) : 0;
        const vb = cb && nb != null && ca ? nb - (getNumericForDiff(ca.score) ?? 0) : 0;
        return sortDir === "asc" ? va - vb : vb - va;
      });
    } else if (modelKeys.includes(sortKey)) {
      arr.sort((a, b) => {
        const va = getNumericForDiff(a.models[sortKey]?.score ?? 0) ?? -Infinity;
        const vb = getNumericForDiff(b.models[sortKey]?.score ?? 0) ?? -Infinity;
        return sortDir === "asc" ? va - vb : vb - va;
      });
    }
    return arr;
  }, [rows, sortKey, sortDir, modelKeys]);

  const toggleRadarSeries = useCallback((dataKey: string) => {
    setRadarVisibility((prev) => ({ ...prev, [dataKey]: !prev[dataKey] }));
  }, []);

  const hasOverlapping = overlappingCount !== null && overlappingCount > 0;
  const noOverlappingWarning = pairs.length >= 2 && overlappingCount === 0 && !overlappingLoading;

  return (
    <Layout>
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-4xl font-display font-bold mb-2">Model Comparison</h1>
          <p className="text-muted-foreground max-w-2xl">
            Compare evaluation performance across models on overlapping datasets.
          </p>
        </div>

        <div className="sticky top-16 z-40 bg-background/95 backdrop-blur border-b border-border -mx-4 px-4 py-4 mb-6">
          <div className="flex flex-wrap items-center gap-3">
            {pairs.map((p) => (
              <Badge
                key={p.id}
                variant="secondary"
                className="pl-2 pr-1 py-1.5 gap-1 font-normal"
              >
                <span className="max-w-[140px] truncate">{p.label}</span>
                <button
                  type="button"
                  onClick={() => removePair(p.id)}
                  className="rounded hover:bg-muted p-0.5"
                  aria-label="Remove"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </Badge>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAddModalOpen(true)}
              className="gap-1.5"
            >
              <Plus className="w-4 h-4" />
              Add model
            </Button>
            {pairs.length >= 2 && (
              <>
                <span className="text-sm text-muted-foreground">
                  {overlappingLoading
                    ? "…"
                    : `${overlappingCount ?? 0} overlapping dataset${(overlappingCount ?? 0) !== 1 ? "s" : ""}`}
                </span>
                <Button
                  onClick={handleCompare}
                  disabled={reportLoading || (overlappingCount ?? 0) === 0}
                  className="bg-black hover:bg-zinc-800"
                >
                  {reportLoading ? "Loading…" : "Compare"}
                </Button>
              </>
            )}
          </div>
        </div>

        {noOverlappingWarning && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              No overlapping datasets for the selected models. Add models that share at least one evaluated dataset.
            </AlertDescription>
          </Alert>
        )}

        {reportError && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{reportError}</AlertDescription>
          </Alert>
        )}

        {report && pairs.length >= 2 && (
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <div className="lg:col-span-2">
              <Card className="border-border h-full">
                <CardHeader>
                  <CardTitle>Guideline Performance</CardTitle>
                  <CardDescription>Capability-level comparison (0–100)</CardDescription>
                </CardHeader>
                <CardContent className="h-[360px]">
                  {radarData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart
                        cx="50%"
                        cy="50%"
                        outerRadius="75%"
                        data={radarData}
                        onClick={(state) => {
                          if (state?.activePayload?.[0]?.dataKey) {
                            toggleRadarSeries(state.activePayload[0].dataKey as string);
                          }
                        }}
                      >
                        <PolarGrid stroke="#e5e7eb" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: "#6b7280", fontSize: 11 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                        {modelKeys.map((key, i) => (
                          <Radar
                            key={key}
                            name={pairs.find((p) => toModelProviderKey(p.model, p.provider) === key)?.label ?? key}
                            dataKey={key}
                            stroke={RADAR_COLORS[i % RADAR_COLORS.length]}
                            strokeWidth={2}
                            fill={RADAR_COLORS[i % RADAR_COLORS.length]}
                            fillOpacity={radarVisibility[key] === false ? 0 : 0.2}
                            strokeOpacity={radarVisibility[key] === false ? 0 : 1}
                          />
                        ))}
                        <RechartsTooltip
                          formatter={(value: number) => [value.toFixed(1), ""]}
                          contentStyle={{ fontSize: 12 }}
                        />
                        <Legend
                          onClick={(e) => e.dataKey != null && toggleRadarSeries(String(e.dataKey))}
                          wrapperStyle={{ cursor: "pointer" }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
                      No capability data for overlapping datasets.
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="lg:col-span-3">
              <Card className="border-border">
                <CardHeader>
                  <CardTitle>Benchmark Comparison</CardTitle>
                  <CardDescription>Head-to-head scores; click a row for trace details.</CardDescription>
                </CardHeader>
                <CardContent>
                  {sortedRows.length === 0 ? (
                    <Empty>
                      <EmptyMedia variant="icon">
                        <AlertCircle className="size-6" />
                      </EmptyMedia>
                      <EmptyHeader>
                        <EmptyTitle>No results</EmptyTitle>
                        <EmptyDescription>
                          Adjust model selection or run evaluations on shared datasets.
                        </EmptyDescription>
                      </EmptyHeader>
                    </Empty>
                  ) : (
                    <ScrollArea className={cn(sortedRows.length > 30 && "h-[480px]")}>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead
                              className="cursor-pointer"
                              onClick={() => {
                                setSortKey("benchmark");
                                setSortDir((d) => (sortKey === "benchmark" ? (d === "asc" ? "desc" : "asc") : "asc"));
                              }}
                            >
                              Benchmark {sortKey === "benchmark" && (sortDir === "asc" ? "↑" : "↓")}
                            </TableHead>
                            {modelKeys.map((key) => (
                              <TableHead
                                key={key}
                                className="text-right cursor-pointer"
                                onClick={() => {
                                  setSortKey(key);
                                  setSortDir((d) => (sortKey === key ? (d === "asc" ? "desc" : "asc") : "asc"));
                                }}
                              >
                                {pairs.find((p) => toModelProviderKey(p.model, p.provider) === key)?.label ?? key}{" "}
                                {sortKey === key && (sortDir === "asc" ? "↑" : "↓")}
                              </TableHead>
                            ))}
                            {modelKeys.length >= 2 && (
                              <TableHead
                                className="text-right cursor-pointer"
                                onClick={() => {
                                  setSortKey("diff");
                                  setSortDir((d) => (sortKey === "diff" ? (d === "asc" ? "desc" : "asc") : "desc"));
                                }}
                              >
                                Diff {sortKey === "diff" && (sortDir === "asc" ? "↑" : "↓")}
                              </TableHead>
                            )}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {sortedRows.map((row) => {
                            const nums = modelKeys.map((k) => ({
                              key: k,
                              num: getNumericForDiff(row.models[k]?.score ?? 0),
                              cell: row.models[k],
                            }));
                            const maxNum = Math.max(...nums.map((n) => n.num ?? -Infinity));
                            const diffVal =
                              modelKeys.length >= 2 && nums[0].num != null && nums[1].num != null
                                ? nums[0].num! - nums[1].num!
                                : null;
                            return (
                              <TableRow
                                key={`${row.dataset}-${row.metric}`}
                                className="cursor-pointer"
                                onClick={() => setSelectedRow(row)}
                              >
                                <TableCell className="font-medium">
                                  {row.dataset} ({row.metric})
                                </TableCell>
                                {modelKeys.map((key) => {
                                  const cell = row.models[key];
                                  const num = getNumericForDiff(cell?.score ?? 0);
                                  const isMax = num != null && num === maxNum && maxNum > -Infinity;
                                  const display = cell ? getDisplayScore(cell.score) : null;
                                  return (
                                    <TableCell key={key} className="text-right">
                                      <Tooltip>
                                        <TooltipTrigger asChild>
                                          <span className={cn(isMax && "font-bold")}>
                                            {display?.type === "number"
                                              ? display.value
                                              : display?.type === "object"
                                                ? <Badge variant="secondary" className="font-mono text-xs">JSON</Badge>
                                                : "—"}
                                          </span>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                          {cell ? (
                                            <>trace_id: {cell.trace_id}, {new Date(cell.created_at).toLocaleString()}</>
                                          ) : (
                                            <>—</>
                                          )}
                                        </TooltipContent>
                                      </Tooltip>
                                    </TableCell>
                                  );
                                })}
                                {modelKeys.length >= 2 && (
                                  <TableCell
                                    className={cn(
                                      "text-right font-mono",
                                      diffVal == null && "bg-muted/50 text-muted-foreground",
                                      diffVal != null && diffVal > 0 && "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-200",
                                      diffVal != null && diffVal < 0 && "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200"
                                    )}
                                  >
                                    {diffVal != null
                                      ? (diffVal >= 0 ? "+" : "") + diffVal.toFixed(1) + "%"
                                      : "—"}
                                  </TableCell>
                                )}
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </ScrollArea>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {!report && pairs.length >= 2 && hasOverlapping && !reportLoading && (
          <Empty className="py-12">
            <EmptyHeader>
              <EmptyTitle>Click Compare</EmptyTitle>
              <EmptyDescription>
                Load the side-by-side report to see the radar chart and benchmark table.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        )}
      </div>

      <Dialog open={addModalOpen} onOpenChange={setAddModalOpen}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add model to compare</DialogTitle>
          </DialogHeader>
          <ModelSelection
            value={addModalConfig}
            onChange={setAddModalConfig}
            label=""
          />
          <DialogFooter>
            <Button onClick={addPair} disabled={!configToPair(addModalConfig)}>
              Add to comparison
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Sheet open={!!selectedRow} onOpenChange={(open) => !open && setSelectedRow(null)}>
        <SheetContent className="sm:max-w-lg overflow-y-auto">
          <SheetHeader>
            <SheetTitle>
              {selectedRow
                ? `${selectedRow.dataset} (${selectedRow.metric})`
                : "Trace details"}
            </SheetTitle>
          </SheetHeader>
          {selectedRow && (
            <div className="mt-4 space-y-4">
              {modelKeys.map((key) => {
                const cell = selectedRow.models[key];
                const label = pairs.find((p) => toModelProviderKey(p.model, p.provider) === key)?.label ?? key;
                return (
                  <div key={key} className="border rounded-lg p-3 space-y-2">
                    <div className="font-medium text-sm">{label}</div>
                    {cell ? (
                      <>
                        <div className="text-xs text-muted-foreground">
                          trace_id: {cell.trace_id} · {new Date(cell.created_at).toLocaleString()}
                        </div>
                        <div className="text-sm">
                          Score:{" "}
                          {typeof cell.score === "object" && cell.score !== null
                            ? JSON.stringify(cell.score)
                            : String(cell.score)}
                        </div>
                        <div className="text-xs">
                          Spec:{" "}
                          {cell.spec ? (
                            <pre className="mt-1 p-2 bg-muted rounded text-xs overflow-auto max-h-32">
                              {JSON.stringify(cell.spec, null, 2)}
                            </pre>
                          ) : (
                            "No spec event"
                          )}
                        </div>
                      </>
                    ) : (
                      <span className="text-muted-foreground text-sm">—</span>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </SheetContent>
      </Sheet>
    </Layout>
  );
}
