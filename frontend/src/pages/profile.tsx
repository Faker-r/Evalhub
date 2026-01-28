import Layout from "@/components/layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { User, Key, Plus, Trash2, Eye, EyeOff } from "lucide-react";
import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";

export default function Profile() {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [addKeyModalOpen, setAddKeyModalOpen] = useState(false);
  const [newKey, setNewKey] = useState({
    providerId: "",
    apiKey: "",
  });
  const [showKey, setShowKey] = useState(false);

  // Fetch providers
  const { data: providersData } = useQuery({
    queryKey: ["providers"],
    queryFn: () => apiClient.getProviders({ page: 1, page_size: 100 }),
    enabled: isAuthenticated,
  });

  const providers = providersData?.providers || [];

  useEffect(() => {
    if (!newKey.providerId && providers.length > 0) {
      setNewKey((prev) => ({ ...prev, providerId: providers[0].id.toString() }));
    }
  }, [newKey.providerId, providers]);

  // Fetch API keys
  const { data: apiKeysData, isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: () => apiClient.getApiKeys(),
    enabled: isAuthenticated,
  });

  const apiKeys = apiKeysData?.api_key_providers || [];

  // Add API key mutation
  const addKeyMutation = useMutation({
    mutationFn: (data: { providerId: string; apiKey: string }) =>
      apiClient.createApiKey(Number(data.providerId), data.apiKey),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
      setAddKeyModalOpen(false);
      setNewKey({ providerId: providers[0]?.id?.toString() || "", apiKey: "" });
      toast({
        title: "Success",
        description: "API key added successfully",
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

  // Delete API key mutation
  const deleteKeyMutation = useMutation({
    mutationFn: (providerId: number) => apiClient.deleteApiKey(providerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
      toast({
        title: "Success",
        description: "API key deleted successfully",
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

  const handleAddKey = () => {
    if (!newKey.apiKey) {
      toast({
        title: "Error",
        description: "Please enter an API key",
        variant: "destructive",
      });
      return;
    }
    addKeyMutation.mutate(newKey);
  };

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <User className="w-16 h-16 text-muted-foreground mb-4" />
          <h2 className="text-2xl font-bold mb-2">Please login to view your profile</h2>
          <p className="text-muted-foreground">You need to be authenticated to access this page.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold font-display mb-2">Profile & Settings</h1>
          <p className="text-muted-foreground">Manage your account and API keys</p>
        </div>

        {/* Account Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Your account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Email</Label>
                <p className="font-medium">{user?.email}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">User ID</Label>
                <p className="font-medium">#{user?.id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Keys */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>API Keys</CardTitle>
                <CardDescription>
                  Manage your API keys for different LLM providers
                </CardDescription>
              </div>
              <Dialog open={addKeyModalOpen} onOpenChange={setAddKeyModalOpen}>
                <DialogTrigger asChild>
                  <Button className="gap-2">
                    <Plus className="w-4 h-4" />
                    Add API Key
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add New API Key</DialogTitle>
                    <DialogDescription>
                      Add an API key for accessing LLM providers
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="provider">Provider</Label>
                      <Select
                        value={newKey.providerId}
                        onValueChange={(value) =>
                          setNewKey({ ...newKey, providerId: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {providers.map((provider) => (
                            <SelectItem key={provider.id} value={provider.id.toString()}>
                              {provider.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="apiKey">API Key</Label>
                      <div className="relative">
                        <Input
                          id="apiKey"
                          type={showKey ? "text" : "password"}
                          placeholder="sk-..."
                          value={newKey.apiKey}
                          onChange={(e) =>
                            setNewKey({ ...newKey, apiKey: e.target.value })
                          }
                          className="pr-10"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                          onClick={() => setShowKey(!showKey)}
                        >
                          {showKey ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Your API key is encrypted and stored securely
                      </p>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      onClick={() => setAddKeyModalOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleAddKey}
                      disabled={addKeyMutation.isPending}
                    >
                      {addKeyMutation.isPending ? "Adding..." : "Add Key"}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : apiKeys.length === 0 ? (
              <div className="text-center py-8">
                <Key className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground mb-4">
                  No API keys configured yet
                </p>
                <p className="text-sm text-muted-foreground">
                  Add an API key to start running evaluations
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {apiKeys.map((key) => (
                  <div
                    key={key.provider_id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-mint-50 flex items-center justify-center">
                        <Key className="w-5 h-5 text-mint-600" />
                      </div>
                      <div>
                        <p className="font-medium">{key.provider_name}</p>
                        <p className="text-sm text-muted-foreground">
                          API key configured
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">Active</Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteKeyMutation.mutate(key.provider_id)}
                        disabled={deleteKeyMutation.isPending}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Info Box */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                <strong>💡 Tip:</strong> API keys are required to run evaluations.
                Add keys for OpenAI, Anthropic, or other providers to get started.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}

