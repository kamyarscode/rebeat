import { redirect } from "@tanstack/react-router";
import { AuthContext } from "@/routes/__root";

// Storage key for the auth token (must match the one in auth.tsx)
export const TOKEN_STORAGE_KEY = "rebeat_auth_token";

/**
 * Utility function to check authentication in route beforeLoad
 */
export function requireAuth(
  authContext: AuthContext | undefined,
  redirectTo = "/"
) {
  if (!authContext?.isAuthenticated) {
    throw redirect({
      to: redirectTo,
      replace: true,
    });
  }

  return authContext;
}

/**
 * Extract auth token from URL params and localStorage
 * URL token takes precedence over localStorage unless skipUrlToken is true
 */
export function extractAuthToken(skipUrlToken = false): string | null {
  // Only check localStorage if skipUrlToken is true
  if (skipUrlToken) {
    return typeof window !== "undefined"
      ? localStorage.getItem(TOKEN_STORAGE_KEY)
      : null;
  }

  // First try URL params
  const urlParams = new URLSearchParams(window.location.search);
  const urlToken = urlParams.get("token");

  // Then try localStorage if no URL token
  if (!urlToken && typeof window !== "undefined") {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  }

  return urlToken;
}
