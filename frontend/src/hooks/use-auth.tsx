import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/lib/supabase';
import { AUTH_ROUTES, OAUTH_PROVIDERS } from '@/lib/auth-constants';

interface User {
  id: number;
  email: string;
}

type AuthOperation = 'idle' | 'login' | 'register' | 'google';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  authOperation: AuthOperation;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  signInWithGoogle: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authOperation, setAuthOperation] = useState<AuthOperation>('idle');
  const { toast } = useToast();
  const toastRef = useRef(toast);
  toastRef.current = toast;

  // Check existing Supabase session on mount + listen for changes
  useEffect(() => {
    let mounted = true;

    const initializeAuth = async () => {
      // Check for existing token first (email/password flow)
      const token = apiClient.getToken();
      if (token) {
        try {
          const currentUser = await apiClient.getCurrentUser();
          if (mounted) setUser(currentUser);
        } catch {
          apiClient.logout();
        }
      }

      // Check for existing Supabase session (OAuth flow)
      const { data: { session } } = await supabase.auth.getSession();
      if (session && !apiClient.getToken()) {
        apiClient.setToken(session.access_token);
        try {
          const currentUser = await apiClient.getCurrentUser();
          if (mounted) setUser(currentUser);
        } catch {
          apiClient.logout();
        }
      }

      if (mounted) setIsLoading(false);
    };

    initializeAuth();

    // Listen for auth state changes (OAuth callbacks)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (!mounted) return;

        // Only handle SIGNED_IN from OAuth flow
        if (event === 'SIGNED_IN' && session) {
          apiClient.setToken(session.access_token);
          try {
            const currentUser = await apiClient.getCurrentUser();
            if (mounted) {
              setUser(currentUser);
              setAuthOperation('idle');
              toastRef.current({
                title: 'Success',
                description: 'Signed in successfully',
              });
            }
          } catch (error) {
            console.error('Failed to get user after OAuth:', error);
            apiClient.logout();
            if (mounted) setAuthOperation('idle');
          }
        }
      }
    );

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []); // Empty deps - runs once on mount

  const login = async (email: string, password: string) => {
    if (authOperation !== 'idle') return;
    setAuthOperation('login');
    try {
      await apiClient.login(email, password);
      const currentUser = await apiClient.getCurrentUser();
      setUser(currentUser);
      toast({
        title: 'Success',
        description: 'Logged in successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Login failed',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setAuthOperation('idle');
    }
  };

  const register = async (email: string, password: string) => {
    if (authOperation !== 'idle') return;
    setAuthOperation('register');
    try {
      await apiClient.register(email, password);
      // Auto-login after registration
      await login(email, password);
      toast({
        title: 'Success',
        description: 'Account created successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Registration failed',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setAuthOperation('idle');
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
    toast({
      title: 'Logged out',
      description: 'You have been logged out successfully',
    });
  };

  const signInWithGoogle = useCallback(async () => {
    if (authOperation !== 'idle') return;
    setAuthOperation('google');
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: OAUTH_PROVIDERS.GOOGLE,
        options: {
          redirectTo: `${window.location.origin}${AUTH_ROUTES.AUTH_PAGE}`,
        },
      });
      if (error) throw error;
      // Note: redirect happens here, authOperation will be reset on return
    } catch (error) {
      setAuthOperation('idle');
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Google sign-in failed',
        variant: 'destructive',
      });
      throw error;
    }
  }, [authOperation, toast]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        authOperation,
        login,
        register,
        logout,
        signInWithGoogle,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

