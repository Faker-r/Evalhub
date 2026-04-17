import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

interface AuthFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  isLoading: boolean;
  isLogin: boolean;
  onToggleMode: () => void;
  disabled?: boolean;
}

export function AuthForm({ onSubmit, isLoading, isLogin, onToggleMode, disabled }: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(email, password);
  };

  const isDisabled = isLoading || disabled;

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-3">
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
            disabled={isDisabled}
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
            minLength={6}
            disabled={isDisabled}
          />
        </div>
        <Button
          type="submit"
          disabled={isDisabled}
          className="w-full bg-black hover:bg-zinc-800 text-white h-10 font-bold"
        >
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : isLogin ? "Sign In" : "Sign Up"}
        </Button>
      </form>
      <div className="text-center text-sm text-muted-foreground pt-2">
        {isLogin ? (
          <>
            Don't have an account?{" "}
            <button type="button" className="text-black font-bold hover:underline" onClick={onToggleMode} disabled={isDisabled}>
              Sign up
            </button>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <button type="button" className="text-black font-bold hover:underline" onClick={onToggleMode} disabled={isDisabled}>
              Sign in
            </button>
          </>
        )}
      </div>
    </>
  );
}
