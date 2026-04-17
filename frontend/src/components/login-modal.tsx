import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { AuthForm } from "@/components/auth-form";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LoginModal({ isOpen, onClose }: LoginModalProps) {
  const [isLogin, setIsLogin] = useState(true);
  const { login, register, authOperation } = useAuth();

  const handleSubmit = async (email: string, password: string) => {
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password);
      }
      onClose();
    } catch {
      // Error handled by useAuth
    }
  };

  const isLoading = authOperation === 'login' || authOperation === 'register';

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
          <AuthForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            isLogin={isLogin}
            onToggleMode={() => setIsLogin(!isLogin)}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
