import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database, FileText, Layers } from "lucide-react";

interface DatasetCardProps {
  title: string;
  category: string;
  samples: number;
  tokens: string;
  description: string;
}

export function DatasetCard({ title, category, samples, tokens, description }: DatasetCardProps) {
  return (
    <Card className="group hover:shadow-md transition-all duration-300 hover:border-mint-300 cursor-pointer border-l-4 border-l-transparent hover:border-l-mint-500">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <Badge variant="outline" className="mb-2 font-mono text-xs text-muted-foreground uppercase tracking-wider">
            {category}
          </Badge>
          <Database className="w-4 h-4 text-muted-foreground group-hover:text-mint-500 transition-colors" />
        </div>
        <CardTitle className="text-lg font-bold group-hover:text-mint-700 transition-colors">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {description}
        </p>
      </CardContent>
      <CardFooter className="pt-2 flex gap-4 text-xs font-mono text-muted-foreground border-t border-zinc-50 mt-2 bg-zinc-50/50 rounded-b-lg">
        <div className="flex items-center gap-1">
          <Layers className="w-3 h-3" />
          {samples.toLocaleString()} samples
        </div>
        <div className="flex items-center gap-1">
          <FileText className="w-3 h-3" />
          ~{tokens}
        </div>
      </CardFooter>
    </Card>
  );
}

interface GuidelineCardProps {
  title: string;
  category: string;
  description: string;
}

export function GuidelineCard({ title, category, description }: GuidelineCardProps) {
  return (
    <Card className="group hover:shadow-md transition-all duration-300 border-dashed hover:border-solid hover:border-mint-300 cursor-pointer bg-zinc-50/30 hover:bg-white">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
           <Badge className="bg-black text-white hover:bg-zinc-800 mb-2">{category}</Badge>
        </div>
        <CardTitle className="text-base font-bold">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          {description}
        </p>
      </CardContent>
    </Card>
  );
}
