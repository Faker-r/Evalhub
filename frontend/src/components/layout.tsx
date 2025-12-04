import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Hexagon, Menu, X } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { LoginModal } from "@/components/login-modal";

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  const navItems = [
    { label: "Leaderboard", href: "/" },
    { label: "Datasets", href: "/datasets" }, // These could just be placeholders or link to home sections
    { label: "Guidelines", href: "/guidelines" },
    { label: "Compare Models", href: "/compare" },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-background font-sans">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-border bg-white/80 backdrop-blur-md">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link href="/">
            <a className="flex items-center gap-2 group">
              <div className="relative flex items-center justify-center w-8 h-8 bg-black rounded-lg group-hover:bg-mint-500 transition-colors duration-300">
                <Hexagon className="w-5 h-5 text-white group-hover:text-black transition-colors" strokeWidth={2.5} />
              </div>
              <span className="font-display font-bold text-xl tracking-tight">EvalHub</span>
            </a>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}>
                <a className={cn(
                  "text-sm font-medium transition-colors hover:text-mint-600",
                  location === item.href ? "text-black" : "text-muted-foreground"
                )}>
                  {item.label}
                </a>
              </Link>
            ))}
          </nav>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-4">
            <Button 
              variant="ghost" 
              className="font-medium"
              onClick={() => setIsLoginOpen(true)}
            >
              Log In
            </Button>
            <Button 
              className="bg-black hover:bg-zinc-800 text-white font-medium rounded-md px-6"
              onClick={() => window.location.href = '/submit'}
            >
              Get Started
            </Button>
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-border bg-white p-4 flex flex-col gap-4 animate-in slide-in-from-top-5">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}>
                <a 
                  className="text-sm font-medium py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.label}
                </a>
              </Link>
            ))}
            <div className="flex flex-col gap-2 pt-4 border-t border-border">
              <Button variant="ghost" className="justify-start" onClick={() => setIsLoginOpen(true)}>Log In</Button>
              <Button className="bg-black text-white justify-start w-full" onClick={() => { setIsMobileMenuOpen(false); window.location.href = '/submit'; }}>Get Started</Button>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-white py-12">
        <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="flex items-center justify-center w-6 h-6 bg-black rounded text-white">
                <Hexagon className="w-3 h-3" />
              </div>
              <span className="font-display font-bold text-lg">EvalHub</span>
            </div>
            <p className="text-sm text-muted-foreground">
              The modern standard for LLM evaluation and benchmarking.
            </p>
          </div>
          
          <div>
            <h4 className="font-bold mb-4 text-sm">Platform</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-black">Leaderboard</a></li>
              <li><a href="#" className="hover:text-black">Datasets</a></li>
              <li><a href="#" className="hover:text-black">API</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-4 text-sm">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-black">About</a></li>
              <li><a href="#" className="hover:text-black">Blog</a></li>
              <li><a href="#" className="hover:text-black">Careers</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-4 text-sm">Connect</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-black">Twitter</a></li>
              <li><a href="#" className="hover:text-black">GitHub</a></li>
              <li><a href="#" className="hover:text-black">Discord</a></li>
            </ul>
          </div>
        </div>
      </footer>

      <LoginModal isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} />
    </div>
  );
}
