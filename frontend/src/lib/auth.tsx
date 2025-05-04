import { createContext, useContext, ReactNode, useEffect } from "react";
import { useQueryState } from "nuqs";
import { TOKEN_STORAGE_KEY } from "./auth-utils";
import { useNavigate } from "@tanstack/react-router";
import { API_URL } from "@/lib/constants";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useLocalStorage } from "@uidotdev/usehooks";

// User interface based on what the API returns
interface User {
  id: number;
  strava_id?: string;
  spotify_id?: string;
  created_at: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
  login: (token: string) => void;
  logout: () => void;
  isLoading: boolean;
  error: Error | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Function to fetch user data from the API
const fetchUserData = async (token: string): Promise<User> => {
  if (!token) {
    throw new Error("No token provided");
  }

  const response = await fetch(`${API_URL}/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Unauthorized");
    }
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};

/** Provider component that wraps your app and makes auth available to any child component */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [urlToken, setUrlToken] = useQueryState("token");
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [localToken, setLocalToken] = useLocalStorage<string | null>(
    TOKEN_STORAGE_KEY,
    null
  );

  // Resolve token priority: URL token takes precedence over localStorage
  const token = urlToken || localToken;
  const isAuthenticated = !!token;

  // Use TanStack Query to fetch and cache user data
  const {
    data: user,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["user", token],
    queryFn: () => (token ? fetchUserData(token) : null),
    enabled: !!token,
    retry: (failureCount, error: unknown) => {
      if (error instanceof Error && error.message === "Unauthorized") {
        return false;
      }
      return failureCount < 3;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Handle URL token: store in localStorage and remove from URL
  useEffect(() => {
    if (urlToken) {
      setLocalToken(urlToken);

      // Remove token from URL
      navigate({
        to: window.location.pathname,
        search: {},
        replace: true,
      });

      setUrlToken(null);
    }
  }, [urlToken, navigate, setUrlToken, setLocalToken]);

  // Handle unauthorized errors
  useEffect(() => {
    if (error instanceof Error && error.message === "Unauthorized" && token) {
      logout();
    }
  }, [error, token]);

  const login = (newToken: string) => {
    setLocalToken(newToken);
    queryClient.invalidateQueries({ queryKey: ["user"] });
  };

  const logout = () => {
    setLocalToken(null);
    queryClient.resetQueries({ queryKey: ["user"] });
    navigate({ to: "/", replace: true });
  };

  const value = {
    isAuthenticated,
    token,
    user: user || null,
    login,
    logout,
    isLoading,
    error: error instanceof Error ? error : null,
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
