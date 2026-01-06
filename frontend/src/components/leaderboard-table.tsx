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
import { ArrowUpRight, TrendingUp } from "lucide-react";

const MOCK_DATA = [
  { rank: 1, model: "GPT-4o", provider: "OpenAI", score: 88.7, ci: "±1.2", category: "Proprietary" },
  { rank: 2, model: "Claude 3.5 Sonnet", provider: "Anthropic", score: 88.2, ci: "±1.4", category: "Proprietary" },
  { rank: 3, model: "Llama 3 70B", provider: "Meta", score: 82.1, ci: "±1.8", category: "Open Source" },
  { rank: 4, model: "Mixtral 8x22B", provider: "Mistral AI", score: 80.5, ci: "±2.0", category: "Open Source" },
  { rank: 5, model: "Gemini 1.5 Pro", provider: "Google", score: 79.8, ci: "±1.5", category: "Proprietary" },
  { rank: 6, model: "Qwen 2 72B", provider: "Alibaba", score: 78.9, ci: "±1.9", category: "Open Source" },
];

export function LeaderboardTable() {
  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center bg-white p-4 rounded-lg border border-border shadow-sm">
        <div className="flex items-center gap-2 text-sm font-medium mr-2">
          <TrendingUp className="w-4 h-4 text-mint-600" />
          Filters:
        </div>
        <Select defaultValue="all">
          <SelectTrigger className="w-[180px] bg-white">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="proprietary">Proprietary</SelectItem>
            <SelectItem value="opensource">Open Source</SelectItem>
          </SelectContent>
        </Select>

        <Select defaultValue="general">
          <SelectTrigger className="w-[180px] bg-white">
            <SelectValue placeholder="Dataset" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="general">General Knowledge</SelectItem>
            <SelectItem value="coding">Coding</SelectItem>
            <SelectItem value="math">Math</SelectItem>
          </SelectContent>
        </Select>

        <div className="ml-auto text-sm text-muted-foreground">
          Last updated: <span className="font-mono text-black">Today, 10:42 AM</span>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-lg border border-border bg-white shadow-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-zinc-50/50">
            <TableRow>
              <TableHead className="w-[80px] font-bold text-black">Rank</TableHead>
              <TableHead className="font-bold text-black">Model</TableHead>
              <TableHead className="font-bold text-black">Provider</TableHead>
              <TableHead className="font-bold text-black">Category</TableHead>
              <TableHead className="text-right font-bold text-black">Score</TableHead>
              <TableHead className="text-right font-bold text-black">95% CI</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {MOCK_DATA.map((row) => (
              <TableRow 
                key={row.model} 
                className="hover:bg-mint-50/30 cursor-pointer transition-colors group"
              >
                <TableCell className="font-mono font-medium text-muted-foreground group-hover:text-black">
                  #{row.rank}
                </TableCell>
                <TableCell>
                  <div className="font-bold flex items-center gap-2">
                    {row.model}
                    <ArrowUpRight className="w-3 h-3 opacity-0 group-hover:opacity-100 text-mint-600 transition-opacity" />
                  </div>
                </TableCell>
                <TableCell>{row.provider}</TableCell>
                <TableCell>
                  <Badge 
                    variant="secondary" 
                    className={row.category === "Open Source" ? "bg-mint-100 text-mint-800 border-mint-200" : ""}
                  >
                    {row.category}
                  </Badge>
                </TableCell>
                <TableCell className="text-right font-mono font-bold text-lg">
                  {row.score}
                </TableCell>
                <TableCell className="text-right font-mono text-muted-foreground text-xs">
                  {row.ci}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
