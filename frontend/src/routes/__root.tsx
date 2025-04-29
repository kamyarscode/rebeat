import { Outlet, createRootRoute } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { AuthProvider } from "@/lib/auth";
import { extractAuthToken } from "@/lib/auth-utils";

export interface AuthContext {
  isAuthenticated: boolean;
  token: string | null;
}

export const Route = createRootRoute({
  component: RootComponent,
  // This ensures the auth context is available to all routes
  beforeLoad: async ({ location }) => {
    // Check if there's a token in the URL for determining initial auth state
    // The actual token management (removing from URL, storing in localStorage)
    // will be handled by the AuthProvider
    const hasTokenInUrl = new URLSearchParams(location.search).has("token");

    // Get token from URL or localStorage
    const token = extractAuthToken();

    // Return the auth context for use in child routes
    return {
      authContext: {
        isAuthenticated: !!token,
        token,
      } satisfies AuthContext,
      // Also pass if we detected a token in URL, useful for child routes
      hasTokenInUrl,
    };
  },
});

function RootComponent() {
  return (
    <AuthProvider>
      <Outlet />
      <TanStackRouterDevtools />
    </AuthProvider>
  );
}
