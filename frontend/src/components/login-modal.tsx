import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LoginModal({ isOpen, onClose }: LoginModalProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password);
      }
      onClose();
    } catch (error) {
      // Error is handled by useAuth hook
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[400px] p-0 gap-0 overflow-hidden border-border">
        <div className="p-6 bg-white">
          <DialogHeader className="mb-4 text-center">
            <DialogTitle className="text-2xl font-bold font-display">
              {isLogin ? "Welcome back" : "Create account"}
            </DialogTitle>
            <DialogDescription>
              {isLogin
                ? "Log in to EvalHub to save your custom evaluations."
                : "Sign up to start evaluating LLMs."}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-3">
              <div className="space-y-1">
                <Label htmlFor="email" className="text-xs font-bold text-muted-foreground uppercase">
                  Email address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-10 border-zinc-300 focus-visible:ring-mint-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="password" className="text-xs font-bold text-muted-foreground uppercase">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="h-10 border-zinc-300 focus-visible:ring-mint-500"
                  required
                />
              </div>
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-black hover:bg-zinc-800 text-white h-10 font-bold"
              >
                {isLoading ? "Loading..." : isLogin ? "Sign In" : "Sign Up"}
              </Button>
            </div>
          </form>
        </div>
        <div className="p-4 bg-zinc-50 border-t border-border text-center text-xs text-muted-foreground">
          {isLogin ? (
            <>
              Don't have an account?{" "}
              <span
                className="text-black font-bold cursor-pointer hover:underline"
                onClick={() => setIsLogin(false)}
              >
                Sign up
              </span>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <span
                className="text-black font-bold cursor-pointer hover:underline"
                onClick={() => setIsLogin(true)}
              >
                Sign in
              </span>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
