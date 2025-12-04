import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Github, Mail } from "lucide-react";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LoginModal({ isOpen, onClose }: LoginModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[400px] p-0 gap-0 overflow-hidden border-border">
        <div className="p-6 bg-white">
          <DialogHeader className="mb-4 text-center">
            <DialogTitle className="text-2xl font-bold font-display">Welcome back</DialogTitle>
            <DialogDescription>
              Log in to EvalHub to save your custom evaluations.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <Button variant="outline" className="w-full gap-2 h-10 hover:bg-zinc-50 text-black font-medium border-zinc-300">
              <Github className="w-4 h-4" />
              Continue with GitHub
            </Button>
            <Button variant="outline" className="w-full gap-2 h-10 hover:bg-zinc-50 text-black font-medium border-zinc-300">
               <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </Button>

            <div className="flex items-center gap-4">
              <Separator className="flex-1" />
              <span className="text-xs text-muted-foreground uppercase font-bold">Or</span>
              <Separator className="flex-1" />
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <Label htmlFor="email" className="text-xs font-bold text-muted-foreground uppercase">Email address</Label>
                <Input id="email" placeholder="name@company.com" className="h-10 border-zinc-300 focus-visible:ring-mint-500" />
              </div>
              <Button className="w-full bg-black hover:bg-zinc-800 text-white h-10 font-bold">
                Sign In with Email
              </Button>
            </div>
          </div>
        </div>
        <div className="p-4 bg-zinc-50 border-t border-border text-center text-xs text-muted-foreground">
          Don't have an account? <span className="text-black font-bold cursor-pointer hover:underline">Sign up</span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
