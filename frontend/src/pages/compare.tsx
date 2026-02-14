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
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
  Tooltip as RechartsTooltip,
} from "recharts";
import { AlertCircle, Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { apiClient } from "@/lib/api";
import {
  buildComparisonRows,
  buildGroupedBarData,
  type ComparisonRow,
  type BarChartDataPoint,
  toModelProviderKey,
  getDisplayScore,
  getDisplayStd,
  getNumericForDiff,
} from "@/lib/comparison-adapter";
import { cn } from "@/lib/utils";
import type { ModelConfig } from "@/types/model-config";

function configToPair(config: ModelConfig): { model: string; provider: string; label: string } | null {
  if (config.is_openrouter) {
    const model = config.openrouter_model_id ?? "";
    const provider = config.openrouter_provider_slug ?? "openrouter";
    const label = (config.openrouter_model_id ?? config.openrouter_model_name ?? model) || "OpenRouter model";
    return model ? { model, provider, label } : null;
  }
  const model = (config.api_name ?? config.model_name) ?? "";
  const provider = config.provider_slug ?? "";
  const label = (config.api_name ?? config.model_name ?? model) || "Model";
  return model && provider ? { model, provider, label } : null;
}

const BAR_COLORS = ["#39E29D", "#6366f1", "#f59e0b", "#ec4899", "#8b5cf6"];

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

  const rowsWithAllModels = useMemo(
    () => rows.filter((row) => modelKeys.length > 0 && modelKeys.every((k) => row.models[k])),
    [rows, modelKeys]
  );

  const barChartData = useMemo(() => {
    if (modelKeys.length === 0) return [];
    return buildGroupedBarData(rowsWithAllModels, modelKeys);
  }, [rowsWithAllModels, modelKeys]);

  const barChartDataNormalized = useMemo(() => {
    return barChartData.map((point) => {
      const values = Object.values(point.modelScores).filter((n): n is number => n != null);
      const maxVal = values.length ? Math.max(...values) : 1;
      const normalized: Record<string, number> = {};
      for (const k of modelKeys) {
        const v = point.modelScores[k];
        normalized[k] = maxVal > 0 && v != null ? (v / maxVal) * 100 : 0;
      }
      return { ...point, normalizedModelScores: normalized };
    });
  }, [barChartData, modelKeys]);

  const sortedRows = useMemo(() => {
    const arr = [...rowsWithAllModels];
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
  }, [rowsWithAllModels, sortKey, sortDir, modelKeys]);


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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {pairs.map((p) => (
              <Card key={p.id} className="border-border relative">
                <button
                  type="button"
                  onClick={() => removePair(p.id)}
                  className="absolute top-2 right-2 rounded hover:bg-muted p-1.5 z-10"
                  aria-label="Remove model"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium pr-8 truncate">
                    {p.label}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-1">
                  <div className="flex items-center gap-1">
                    <span className="font-medium">Provider:</span>
                    <span className="truncate">{p.provider}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="font-medium">Model:</span>
                    <span className="truncate">{p.model}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
            <Card className="border-dashed border-2 border-border hover:border-primary/50 transition-colors cursor-pointer" onClick={() => setAddModalOpen(true)}>
              <CardContent className="flex flex-col items-center justify-center h-full min-h-[120px] p-6">
                <div className="rounded-full bg-primary/10 p-3 mb-2">
                  <Plus className="w-5 h-5 text-primary" />
                </div>
                <span className="text-sm font-medium">Add Model</span>
              </CardContent>
            </Card>
          </div>
          {pairs.length >= 2 && (
            <div className="flex items-center gap-3 mt-4">
              <span className="text-sm text-muted-foreground">
                {overlappingLoading
                  ? "…"
                  : `${overlappingCount ?? 0} overlapping dataset${(overlappingCount ?? 0) !== 1 ? "s" : ""}`}
              </span>
              <Button
                onClick={handleCompare}
                disabled={reportLoading || (overlappingCount ?? 0) === 0}
              >
                {reportLoading ? "Loading…" : "Compare"}
              </Button>
            </div>
          )}
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
          <div className="space-y-6">
            <Card className="border-border">
              <CardHeader>
                <CardTitle>Performance Comparison</CardTitle>
                <CardDescription>Score comparison across benchmarks and metrics</CardDescription>
              </CardHeader>
              <CardContent>
                {barChartData.length > 0 ? (
                  <ResponsiveContainer
                    width="100%"
                    height={Math.max(200, barChartDataNormalized.length * 88)}
                    debounce={0}
                  >
                    <BarChart
                      data={barChartDataNormalized}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 150, bottom: 5 }}
                      barCategoryGap={28}
                      barGap={8}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={[0, 100]} hide />
                      <YAxis
                        type="category"
                        dataKey={(item: BarChartDataPoint & { normalizedModelScores?: Record<string, number> }) =>
                          `${item.benchmark} (${item.metric})`
                        }
                        width={140}
                        tick={{ fontSize: 11 }}
                      />
                      <RechartsTooltip
                        formatter={(_value: number, name: string, props: { payload?: BarChartDataPoint }) => {
                          const key = modelKeys.find((k) => {
                            const p = pairs.find((pp) => toModelProviderKey(pp.model, pp.provider) === k);
                            return p && `${p.provider} / ${p.label}` === name;
                          });
                          const raw = key != null && props.payload ? props.payload.modelScores[key] : null;
                          return [raw != null ? raw.toFixed(2) : "—", name];
                        }}
                        contentStyle={{ fontSize: 12 }}
                      />
                      <Legend />
                      {modelKeys.map((key, i) => {
                        const p = pairs.find((p) => toModelProviderKey(p.model, p.provider) === key);
                        const name = p ? `${p.provider} / ${p.label}` : key;
                        return (
                          <Bar
                            key={key}
                            name={name}
                            dataKey={(item: BarChartDataPoint & { normalizedModelScores?: Record<string, number> }) =>
                              item.normalizedModelScores?.[key] ?? 0
                            }
                            fill={BAR_COLORS[i % BAR_COLORS.length]}
                            radius={[0, 4, 4, 0]}
                            barSize={18}
                            cursor="pointer"
                            onClick={(data: unknown) => {
                              const point = (data as { payload?: { benchmark: string; metric: string } })?.payload ?? (data as { benchmark?: string; metric?: string });
                              const benchmark = point?.benchmark;
                              const metric = point?.metric;
                              if (benchmark != null && metric != null) {
                                const row = rowsWithAllModels.find((r) => r.dataset === benchmark && r.metric === metric);
                                if (row) setSelectedRow(row);
                              }
                            }}
                          />
                        );
                      })}
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[360px] text-sm text-muted-foreground">
                    No performance data for overlapping datasets.
                  </div>
                )}
              </CardContent>
            </Card>

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
                          {modelKeys.map((key) => {
                            const p = pairs.find((p) => toModelProviderKey(p.model, p.provider) === key);
                            const headerLabel = p ? `${p.provider} / ${p.label}` : key;
                            return (
                            <TableHead
                              key={key}
                              className="text-right cursor-pointer"
                              onClick={() => {
                                setSortKey(key);
                                setSortDir((d) => (sortKey === key ? (d === "asc" ? "desc" : "asc") : "asc"));
                              }}
                            >
                              {headerLabel}{" "}
                              {sortKey === key && (sortDir === "asc" ? "↑" : "↓")}
                            </TableHead>
                          );})}
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
                                const stdStr = cell ? getDisplayStd(cell.score) : null;
                                return (
                                  <TableCell key={key} className="text-right">
                                    <Tooltip>
                                      <TooltipTrigger asChild>
                                        <span className={cn(isMax && "font-bold")}>
                                          {display?.type === "number"
                                            ? stdStr
                                              ? `${display.value} ± ${stdStr}`
                                              : display.value
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
                                    ? (diffVal >= 0 ? "+" : "") + diffVal.toFixed(2)
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
                const p = pairs.find((p) => toModelProviderKey(p.model, p.provider) === key);
                const label = p ? `${p.provider} / ${p.label}` : key;
                return (
                  <div key={key} className="border rounded-lg p-3 space-y-2">
                    <div className="font-medium text-sm">{label}</div>
                    {cell ? (
                      <>
                        <div className="text-xs text-muted-foreground">
                          trace_id: {cell.trace_id} · {new Date(cell.created_at).toLocaleString()}
                        </div>
                        <div className="text-sm">
                          {(() => {
                            const display = getDisplayScore(cell.score);
                            const stdStr = getDisplayStd(cell.score);
                            if (display.type === "number") {
                              return (
                                <>
                                  <span className="text-muted-foreground">Score </span>
                                  <span className="font-medium">
                                    {display.value}
                                    {stdStr && ` ± ${stdStr}`}
                                  </span>
                                </>
                              );
                            }
                            if (
                              typeof cell.score === "object" &&
                              cell.score !== null &&
                              !Array.isArray(cell.score)
                            ) {
                              const entries = Object.entries(cell.score);
                              const primary =
                                "mean" in cell.score
                                  ? (cell.score as { mean: unknown }).mean
                                  : "value" in cell.score
                                    ? (cell.score as { value: unknown }).value
                                    : null;
                              const omitKeys = new Set(primary != null ? ["mean", "value", "std"] : []);
                              return (
                                <div className="space-y-1">
                                  {primary != null && (
                                    <div>
                                      <span className="text-muted-foreground">Score </span>
                                      <span className="font-medium">
                                        {typeof primary === "number"
                                          ? primary.toFixed(2)
                                          : String(primary)}
                                        {stdStr && ` ± ${stdStr}`}
                                      </span>
                                    </div>
                                  )}
                                  {entries.filter(([k]) => !omitKeys.has(k)).length > 0 && (
                                    <dl className="grid gap-x-2 gap-y-0.5 text-xs [&>div]:grid [&>div]:grid-cols-[auto_1fr] [&>div]:items-baseline">
                                      {entries
                                        .filter(([k]) => !omitKeys.has(k))
                                        .map(([k, v]) => (
                                          <div key={k}>
                                            <dt className="text-muted-foreground capitalize pr-2">
                                              {k.replace(/_/g, " ")}
                                            </dt>
                                            <dd className="truncate" title={String(v)}>
                                              {typeof v === "object" && v !== null
                                                ? JSON.stringify(v)
                                                : String(v)}
                                            </dd>
                                          </div>
                                        ))}
                                    </dl>
                                  )}
                                </div>
                              );
                            }
                            return (
                              <>
                                <span className="text-muted-foreground">Score </span>
                                <span className="font-medium">{String(cell.score)}</span>
                              </>
                            );
                          })()}
                        </div>
                        {cell.spec ? (
                          cell.spec.data ? (
                            <div className="text-xs space-y-1.5 pt-1 border-t">
                              <div className="font-medium text-muted-foreground mb-1">Run config</div>
                              <dl className="grid gap-x-2 gap-y-1 [&>div]:grid [&>div]:grid-cols-[minmax(0,7rem)_1fr] [&>div]:items-baseline">
                                {Object.entries(cell.spec.data).map(([k, v]) => {
                                  const label =
                                    {
                                      task_name: "Task",
                                      dataset_name: "Dataset",
                                      input_field: "Input field",
                                      output_type: "Output type",
                                      judge_type: "Judge type",
                                      completion_model: "Completion model",
                                      model_provider: "Model provider",
                                      judge_model: "Judge model",
                                      guideline_names: "Guidelines",
                                      sample_count: "Samples",
                                      n_fewshots: "Few-shots",
                                    }[k] ?? k.replace(/_/g, " ");
                                  const val =
                                    Array.isArray(v)
                                      ? (v as string[]).join(", ")
                                      : String(v ?? "—");
                                  return (
                                    <div key={k}>
                                      <dt className="text-muted-foreground truncate">{label}</dt>
                                      <dd className="truncate font-medium" title={val}>
                                        {val}
                                      </dd>
                                    </div>
                                  );
                                })}
                              </dl>
                            </div>
                          ) : (
                            <div className="text-xs text-muted-foreground pt-1">No spec data</div>
                          )
                        ) : (
                          <div className="text-xs text-muted-foreground pt-1">No spec event</div>
                        )}
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
