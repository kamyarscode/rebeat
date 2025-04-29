import {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
} from "react";
import { useQueryState } from "nuqs";
import { TOKEN_STORAGE_KEY } from "./auth-utils";
import { useNavigate } from "@tanstack/react-router";

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

/** Provider component that wraps your app and makes auth available to any child component */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [urlToken, setUrlToken] = useQueryState("token");
  const navigate = useNavigate();
  const [localToken, setLocalToken] = useState<string | null>(() => {
    // Initialize from localStorage when the component mounts
    if (typeof window !== "undefined") {
      return localStorage.getItem(TOKEN_STORAGE_KEY);
    }
    return null;
  });

  // Resolve token priority: URL token takes precedence over localStorage
  const token = urlToken || localToken;
  const isAuthenticated = !!token;

  // Handle URL token: store in localStorage and remove from URL
  useEffect(() => {
    if (urlToken) {
      // Store token in localStorage
      localStorage.setItem(TOKEN_STORAGE_KEY, urlToken);
      setLocalToken(urlToken);

      // Remove token from URL without a full page reload
      const currentPath = window.location.pathname;
      navigate({
        to: currentPath,
        search: {},
        replace: true,
      });

      // Reset the URL token state
      setUrlToken(null);
    }
  }, [urlToken, navigate, setUrlToken]);

  const login = (newToken: string) => {
    // Only update localStorage - we no longer keep tokens in URL
    localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
    setLocalToken(newToken);
  };

  const logout = () => {
    // Clear token from localStorage
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setLocalToken(null);

    // Navigate user back to home page
    navigate({ to: "/", replace: true });
  };

  const value = {
    isAuthenticated,
    token,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/** Hook to use the auth context */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
