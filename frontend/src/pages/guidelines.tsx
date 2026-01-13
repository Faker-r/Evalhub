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
import { Scale, Plus, BookOpen, X, Eye } from "lucide-react";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { TagInput } from "@/components/ui/tag-input";

export default function Guidelines() {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newCategoryInput, setNewCategoryInput] = useState("");
  const [viewGuidelineId, setViewGuidelineId] = useState<string | number | null>(null);
  const [createData, setCreateData] = useState({
    name: "",
    prompt: "",
    category: "",
    categories: [] as string[],
    scoring_scale: "numeric" as "boolean" | "custom_category" | "numeric" | "percentage",
    scoring_scale_config: { min_value: 0, max_value: 10 } as any,
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
      setCreateData({ 
        name: "", 
        prompt: "", 
        category: "",
        categories: [], 
        scoring_scale: "numeric", 
        scoring_scale_config: { min_value: 0, max_value: 10 } 
      });
      setNewCategoryInput("");
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
    const categoryString = createData.categories.length > 0 ? createData.categories.join(", ") : createData.category;

    if (!createData.name || !createData.prompt || !categoryString) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }
    

    if (createData.scoring_scale === "custom_category" && (!createData.scoring_scale_config.categories || createData.scoring_scale_config.categories.length === 0)) {
      toast({
        title: "Error",
        description: "Custom category scale requires at least one category",
        variant: "destructive",
      });
      return;
    }

    if (createData.scoring_scale === "numeric" && (createData.scoring_scale_config.min_value >= createData.scoring_scale_config.max_value)) {
      toast({
        title: "Error",
        description: "Max value must be greater than min value",
        variant: "destructive",
      });
      return;
    }
    
    createMutation.mutate({
      ...createData,
      category: categoryString
    });
  };

  const handleScoringScaleChange = (value: string) => {
    const scale = value as "boolean" | "custom_category" | "numeric" | "percentage";
    let config: any = {};
    
    if (scale === "boolean") {
      config = {};
    } else if (scale === "custom_category") {
      config = { categories: [] };
    } else if (scale === "numeric") {
      config = { min_value: 0, max_value: 10 };
    } else if (scale === "percentage") {
      config = {};
    }
    
    setCreateData({ ...createData, scoring_scale: scale, scoring_scale_config: config });
    setNewCategoryInput("");
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
                    <Label htmlFor="category">Guideline Category</Label>
                    <TagInput 
                      value={createData.categories}
                      onChange={(tags) => setCreateData({ ...createData, categories: tags })}
                      placeholder="Add categories (press Enter to add)"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="prompt">Evaluation Prompt</Label>
                    <Textarea
                      id="prompt"
                      placeholder="You are an impartial evaluator. Compare the model's output to the reference or ground truth. Judge whether the output is factually correct and complete. Ignore style and wording."
                      value={createData.prompt}
                      onChange={(e) =>
                        setCreateData({ ...createData, prompt: e.target.value })
                      }
                      rows={6}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="scoring_scale">Scoring Scale</Label>
                    <Select value={createData.scoring_scale} onValueChange={handleScoringScaleChange}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="boolean">Boolean (True/False)</SelectItem>
                        <SelectItem value="numeric">Numeric (Min-Max)</SelectItem>
                        <SelectItem value="percentage">Percentage (0-100%)</SelectItem>
                        <SelectItem value="custom_category">Custom Categories</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {createData.scoring_scale === "numeric" && (
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="min_value">Min Value</Label>
                        <Input
                          id="min_value"
                          type="number"
                          value={createData.scoring_scale_config.min_value}
                          onChange={(e) =>
                            setCreateData({
                              ...createData,
                              scoring_scale_config: {
                                ...createData.scoring_scale_config,
                                min_value: parseInt(e.target.value) || 0,
                              },
                            })
                          }
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="max_value">Max Value</Label>
                        <Input
                          id="max_value"
                          type="number"
                          value={createData.scoring_scale_config.max_value}
                          onChange={(e) =>
                            setCreateData({
                              ...createData,
                              scoring_scale_config: {
                                ...createData.scoring_scale_config,
                                max_value: parseInt(e.target.value) || 10,
                              },
                            })
                          }
                        />
                      </div>
                    </div>
                  )}
                  {createData.scoring_scale === "custom_category" && (
                    <div className="space-y-3">
                      <Label htmlFor="category-input">Scoring Categories</Label>
                      <div className="flex gap-2">
                        <div className="flex-1">
                          <Input
                            id="category-input"
                            placeholder="Enter category name"
                            value={newCategoryInput}
                            onChange={(e) => {
                              const upperValue = e.target.value.toUpperCase();
                              if (upperValue.length <= 150) {
                                setNewCategoryInput(upperValue);
                              }
                            }}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                e.preventDefault();
                                const trimmed = newCategoryInput.trim().toUpperCase();
                                if (trimmed) {
                                  if (trimmed.length > 150) {
                                    toast({
                                      title: "Category too long",
                                      description: "Category must be 150 characters or less",
                                      variant: "destructive",
                                    });
                                    return;
                                  }
                                  const currentCategories = createData.scoring_scale_config.categories || [];
                                  if (!currentCategories.includes(trimmed)) {
                                    setCreateData({
                                      ...createData,
                                      scoring_scale_config: {
                                        categories: [...currentCategories, trimmed],
                                      },
                                    });
                                    setNewCategoryInput("");
                                  } else {
                                    toast({
                                      title: "Duplicate category",
                                      description: "This category already exists",
                                      variant: "destructive",
                                    });
                                  }
                                }
                              }
                            }}
                            maxLength={150}
                            className="uppercase"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            {newCategoryInput.length}/150 characters
                          </p>
                        </div>
                        <Button
                          type="button"
                          onClick={() => {
                            const trimmed = newCategoryInput.trim().toUpperCase();
                            if (trimmed) {
                              if (trimmed.length > 150) {
                                toast({
                                  title: "Category too long",
                                  description: "Category must be 150 characters or less",
                                  variant: "destructive",
                                });
                                return;
                              }
                              const currentCategories = createData.scoring_scale_config.categories || [];
                              if (!currentCategories.includes(trimmed)) {
                                setCreateData({
                                  ...createData,
                                  scoring_scale_config: {
                                    categories: [...currentCategories, trimmed],
                                  },
                                });
                                setNewCategoryInput("");
                              } else {
                                toast({
                                  title: "Duplicate category",
                                  description: "This category already exists",
                                  variant: "destructive",
                                });
                              }
                            }
                          }}
                          disabled={!newCategoryInput.trim()}
                        >
                          Add
                        </Button>
                      </div>
                      {createData.scoring_scale_config.categories && createData.scoring_scale_config.categories.length > 0 && (
                        <div className="border rounded-md p-3 bg-muted/30 min-h-[60px]">
                          <div className="flex flex-wrap gap-2">
                            {createData.scoring_scale_config.categories.map((cat: string, index: number) => (
                              <Badge 
                                key={index} 
                                variant="secondary" 
                                className="pr-7 py-1.5 text-sm font-medium relative group"
                              >
                                {cat}
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  className="h-4 w-4 absolute right-0.5 top-1/2 -translate-y-1/2 p-0 hover:bg-destructive/20 rounded-full"
                                  onClick={() => {
                                    const currentCategories = createData.scoring_scale_config.categories || [];
                                    setCreateData({
                                      ...createData,
                                      scoring_scale_config: {
                                        categories: currentCategories.filter((_: string, i: number) => i !== index),
                                      },
                                    });
                                  }}
                                >
                                  <X className="h-3 w-3 text-muted-foreground group-hover:text-destructive" />
                                </Button>
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {(!createData.scoring_scale_config.categories || createData.scoring_scale_config.categories.length === 0) && (
                        <div className="border border-dashed rounded-md p-4 bg-muted/20 text-center text-sm text-muted-foreground">
                          No categories added yet. Add categories above.
                        </div>
                      )}
                    </div>
                  )}
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
                  <p className="text-sm text-muted-foreground">Numeric Scales</p>
                  <p className="text-3xl font-bold">
                    {guidelines.filter(g => g.scoring_scale === "numeric").length}
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
                    <TableHead>Scoring Scale</TableHead>
                    <TableHead>Scale Config</TableHead>
                    <TableHead>Prompt Preview</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredGuidelines.map((guideline) => (
                    <TableRow key={guideline.id}>
                      <TableCell className="font-medium">{guideline.name}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{guideline.category}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {guideline.scoring_scale === "boolean" && "Boolean"}
                          {guideline.scoring_scale === "numeric" && "Numeric"}
                          {guideline.scoring_scale === "percentage" && "Percentage"}
                          {guideline.scoring_scale === "custom_category" && "Custom"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">
                        {guideline.scoring_scale === "numeric" && 
                          `${guideline.scoring_scale_config.min_value}-${guideline.scoring_scale_config.max_value}`}
                        {guideline.scoring_scale === "custom_category" && 
                          guideline.scoring_scale_config.categories?.slice(0, 2).join(", ") + 
                          (guideline.scoring_scale_config.categories?.length > 2 ? "..." : "")}
                        {(guideline.scoring_scale === "boolean" || guideline.scoring_scale === "percentage") && "-"}
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm max-w-md truncate">
                        {guideline.prompt}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setViewGuidelineId(guideline.id)}
                          className="gap-2"
                        >
                          <Eye className="h-4 w-4" />
                          View more
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* View Guideline Details Dialog */}
        {viewGuidelineId && (() => {
          const guideline = guidelines.find(g => String(g.id) === String(viewGuidelineId));
          if (!guideline) return null;
          
          return (
            <Dialog open={!!viewGuidelineId} onOpenChange={(open) => !open && setViewGuidelineId(null)}>
              <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-2xl">{guideline.name}</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Basic Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <Label className="text-sm font-semibold text-muted-foreground">Guideline Category</Label>
                        <div className="mt-1">
                          <Badge variant="secondary">{guideline.category}</Badge>
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm font-semibold text-muted-foreground">Scoring Scale</Label>
                        <div className="mt-1">
                          <Badge variant="outline">
                            {guideline.scoring_scale === "boolean" && "Boolean"}
                            {guideline.scoring_scale === "numeric" && "Numeric"}
                            {guideline.scoring_scale === "percentage" && "Percentage"}
                            {guideline.scoring_scale === "custom_category" && "Custom Categories"}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Evaluation Prompt</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm whitespace-pre-wrap">{guideline.prompt}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Scoring Scale Configuration</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {guideline.scoring_scale === "numeric" && (
                        <div className="space-y-2">
                          <div className="flex gap-4">
                            <div>
                              <Label className="text-sm font-semibold text-muted-foreground">Min Value</Label>
                              <p className="text-lg font-semibold mt-1">{guideline.scoring_scale_config.min_value}</p>
                            </div>
                            <div>
                              <Label className="text-sm font-semibold text-muted-foreground">Max Value</Label>
                              <p className="text-lg font-semibold mt-1">{guideline.scoring_scale_config.max_value}</p>
                            </div>
                          </div>
                        </div>
                      )}
                      {guideline.scoring_scale === "custom_category" && (
                        <div className="space-y-2">
                          <Label className="text-sm font-semibold text-muted-foreground">Scoring Categories</Label>
                          <div className="flex flex-wrap gap-2 mt-2">
                            {guideline.scoring_scale_config.categories?.map((cat: string, index: number) => (
                              <Badge key={index} variant="secondary" className="text-sm py-1.5">
                                {cat}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {(guideline.scoring_scale === "boolean" || guideline.scoring_scale === "percentage") && (
                        <p className="text-sm text-muted-foreground">No additional configuration required</p>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </DialogContent>
            </Dialog>
          );
        })()}
      </div>
    </Layout>
  );
}
