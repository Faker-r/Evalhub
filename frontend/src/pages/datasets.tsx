import Layout from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Database, Upload, FileText, Calendar, Layers } from "lucide-react";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";

export default function Datasets() {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadData, setUploadData] = useState({
    name: "",
    category: "",
    file: null as File | null,
  });

  // Fetch datasets
  const { data: datasetsData, isLoading } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => apiClient.getDatasets(),
    enabled: isAuthenticated,
  });

  const datasets = datasetsData?.datasets || [];

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (data: { name: string; category: string; file: File }) =>
      apiClient.createDataset(data.name, data.category, data.file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      setUploadModalOpen(false);
      setUploadData({ name: "", category: "", file: null });
      toast({
        title: "Success",
        description: "Dataset uploaded successfully",
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

  const handleUpload = () => {
    if (!uploadData.name || !uploadData.category || !uploadData.file) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }
    uploadMutation.mutate(uploadData);
  };

  // Filter datasets
  const filteredDatasets = datasets.filter((dataset) => {
    const matchesSearch = dataset.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "all" || dataset.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  // Get unique categories
  const categories = Array.from(new Set(datasets.map((d) => d.category)));

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <Database className="w-16 h-16 text-muted-foreground mb-4" />
          <h2 className="text-2xl font-bold mb-2">Please login to view datasets</h2>
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
              <h1 className="text-4xl font-bold font-display mb-2">Datasets</h1>
              <p className="text-muted-foreground">
                Browse and upload evaluation datasets in JSONL format
              </p>
            </div>
            <Dialog open={uploadModalOpen} onOpenChange={setUploadModalOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Upload className="w-4 h-4" />
                  Upload Dataset
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Upload New Dataset</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Dataset Name</Label>
                    <Input
                      id="name"
                      placeholder="My Dataset"
                      value={uploadData.name}
                      onChange={(e) =>
                        setUploadData({ ...uploadData, name: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <Input
                      id="category"
                      placeholder="e.g., qa, coding, math"
                      value={uploadData.category}
                      onChange={(e) =>
                        setUploadData({ ...uploadData, category: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="file">JSONL File</Label>
                    <Input
                      id="file"
                      type="file"
                      accept=".jsonl,.json"
                      onChange={(e) =>
                        setUploadData({
                          ...uploadData,
                          file: e.target.files?.[0] || null,
                        })
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Each line should be a JSON object with an "input" field
                    </p>
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setUploadModalOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleUpload}
                    disabled={uploadMutation.isPending}
                  >
                    {uploadMutation.isPending ? "Uploading..." : "Upload"}
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
                  <p className="text-sm text-muted-foreground">Total Datasets</p>
                  <p className="text-3xl font-bold">{datasets.length}</p>
                </div>
                <Database className="w-8 h-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Samples</p>
                  <p className="text-3xl font-bold">
                    {datasets.reduce((sum, d) => sum + d.sample_count, 0)}
                  </p>
                </div>
                <Layers className="w-8 h-8 text-muted-foreground" />
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
                <FileText className="w-8 h-8 text-muted-foreground" />
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
                  placeholder="Search datasets..."
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

        {/* Datasets Table */}
        <Card>
          <CardHeader>
            <CardTitle>Your Datasets</CardTitle>
            <CardDescription>Manage your evaluation datasets</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : filteredDatasets.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                {datasets.length === 0
                  ? "No datasets yet. Upload your first dataset!"
                  : "No datasets match your filters."}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Samples</TableHead>
                    <TableHead>ID</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDatasets.map((dataset) => (
                    <TableRow key={dataset.id}>
                      <TableCell className="font-medium">{dataset.name}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{dataset.category}</Badge>
                      </TableCell>
                      <TableCell>{dataset.sample_count}</TableCell>
                      <TableCell className="text-muted-foreground">
                        #{dataset.id}
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
