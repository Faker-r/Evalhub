import Layout from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Scale, Plus, BookOpen } from "lucide-react";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";

export default function Guidelines() {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [createData, setCreateData] = useState({
    name: "",
    prompt: "",
    category: "",
    max_score: 10,
  });

  // Fetch guidelines
  const { data: guidelinesData, isLoading } = useQuery({
    queryKey: ['guidelines'],
    queryFn: () => apiClient.getGuidelines(),
    enabled: isAuthenticated,
  });

  const guidelines = guidelinesData?.guidelines || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: typeof createData) => apiClient.createGuideline(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guidelines'] });
      setCreateModalOpen(false);
      setCreateData({ name: "", prompt: "", category: "", max_score: 10 });
      toast({
        title: "Success",
        description: "Guideline created successfully",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleCreate = () => {
    if (!createData.name || !createData.prompt || !createData.category) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }
    
    if (!createData.prompt.includes('{completion}')) {
      toast({
        title: "Error",
        description: "Prompt must contain exactly one {completion} placeholder",
        variant: "destructive",
      });
      return;
    }
    
    createMutation.mutate(createData);
  };

  // Filter guidelines
  const filteredGuidelines = guidelines.filter((guideline) => {
    const matchesSearch = guideline.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "all" || guideline.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  // Get unique categories
  const categories = Array.from(new Set(guidelines.map((g) => g.category)));

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <Scale className="w-16 h-16 text-muted-foreground mb-4" />
          <h2 className="text-2xl font-bold mb-2">Please login to view guidelines</h2>
          <p className="text-muted-foreground">You need to be authenticated to access this page.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold font-display mb-2">Guidelines</h1>
              <p className="text-muted-foreground">
                Create and manage evaluation criteria for LLM outputs
              </p>
            </div>
            <Dialog open={createModalOpen} onOpenChange={setCreateModalOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Plus className="w-4 h-4" />
                  Create Guideline
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create New Guideline</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Guideline Name</Label>
                    <Input
                      id="name"
                      placeholder="e.g., Accuracy"
                      value={createData.name}
                      onChange={(e) =>
                        setCreateData({ ...createData, name: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <Input
                      id="category"
                      placeholder="e.g., accuracy, helpfulness, safety"
                      value={createData.category}
                      onChange={(e) =>
                        setCreateData({ ...createData, category: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="prompt">Evaluation Prompt</Label>
                    <Textarea
                      id="prompt"
                      placeholder="Rate the accuracy of {completion} on a scale of 1-10..."
                      value={createData.prompt}
                      onChange={(e) =>
                        setCreateData({ ...createData, prompt: e.target.value })
                      }
                      rows={6}
                    />
                    <p className="text-xs text-muted-foreground">
                      Must include exactly one <code className="bg-muted px-1 py-0.5 rounded">{'{completion}'}</code> placeholder
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="max_score">Max Score</Label>
                    <Input
                      id="max_score"
                      type="number"
                      min="1"
                      max="100"
                      value={createData.max_score}
                      onChange={(e) =>
                        setCreateData({
                          ...createData,
                          max_score: parseInt(e.target.value) || 10,
                        })
                      }
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setCreateModalOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreate}
                    disabled={createMutation.isPending}
                  >
                    {createMutation.isPending ? "Creating..." : "Create"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Guidelines</p>
                  <p className="text-3xl font-bold">{guidelines.length}</p>
                </div>
                <Scale className="w-8 h-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Categories</p>
                  <p className="text-3xl font-bold">{categories.length}</p>
                </div>
                <BookOpen className="w-8 h-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Max Score</p>
                  <p className="text-3xl font-bold">
                    {guidelines.length > 0
                      ? Math.round(
                          guidelines.reduce((sum, g) => sum + g.max_score, 0) /
                            guidelines.length
                        )
                      : 0}
                  </p>
                </div>
                <Plus className="w-8 h-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search guidelines..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Guidelines Table */}
        <Card>
          <CardHeader>
            <CardTitle>Your Guidelines</CardTitle>
            <CardDescription>Manage your evaluation guidelines</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : filteredGuidelines.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                {guidelines.length === 0
                  ? "No guidelines yet. Create your first guideline!"
                  : "No guidelines match your filters."}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Max Score</TableHead>
                    <TableHead>Prompt Preview</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredGuidelines.map((guideline) => (
                    <TableRow key={guideline.id}>
                      <TableCell className="font-medium">{guideline.name}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{guideline.category}</Badge>
                      </TableCell>
                      <TableCell>{guideline.max_score}</TableCell>
                      <TableCell className="text-muted-foreground text-sm max-w-md truncate">
                        {guideline.prompt}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
