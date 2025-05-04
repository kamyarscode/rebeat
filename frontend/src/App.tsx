import { ConnectSpotify } from "@/components/connect-spotify";
import { ConnectStrava } from "@/components/connect-strava";
import { useAuth } from "@/lib/auth";
import { API_URL } from "./lib/constants";

import { useToastUrlError } from "./hooks/use-toast-url-error";
import { AddToLatest } from "./components/add-to-latest";
import { Devtools } from "./components/devtools";
import { Button } from "./components/ui/button";

function App() {
  const { isAuthenticated, token, user, isLoading, logout } = useAuth();
  useToastUrlError();

  const title = isAuthenticated
    ? user?.name
      ? `Welcome back, ${user.name} 👋`
      : "Welcome back 👋"
    : "Welcome to Rebeat 🎵";

  return (
    <main className="flex flex-col gap-4 container mx-auto justify-center items-center h-full px-8 max-w-md">
      <div className="flex flex-col gap-6 max-w-full">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold animate-in fade-in slide-in-from-bottom-4 duration-1000 ease-out-quart">
            {title}
          </h1>
          <p className="text-base text-muted-foreground animate-in fade-in slide-in-from-bottom-4 delay-100 fill-mode-backwards ease-out-quart duration-1000">
            Turn your runs into playlists you can revisit right from Strava.
            Connect your accounts to get started.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-2 sm:flex-row">
            <ConnectStrava
              connected={!!user?.strava_id}
              disabled={isLoading || !!user?.strava_id}
              className="animate-in fade-in slide-in-from-bottom-4 delay-200 fill-mode-backwards ease-out-quart duration-1000"
              onClick={() => {
                window.location.href = `${API_URL}/strava/login${token ? `?token=${token}` : ""}`;
              }}
            />
            <ConnectSpotify
              connected={!!user?.spotify_id}
              disabled={isLoading || !!user?.spotify_id}
              className="animate-in fade-in slide-in-from-bottom-4 delay-300 fill-mode-backwards ease-out-quart duration-1000"
              onClick={() => {
                window.location.href = `${API_URL}/spotify/login${token ? `?token=${token}` : ""}`;
              }}
            />
          </div>

          {user?.strava_id && user?.spotify_id && (
            <AddToLatest className="animate-in fade-in slide-in-from-bottom-4 delay-500 fill-mode-backwards ease-out-quart duration-1000 w-full" />
          )}
          {isAuthenticated && user && (
            <div className="animate-in fade-in slide-in-from-bottom-4 delay-700 fill-mode-backwards ease-out-quart duration-1000">
              <Button
                variant="ghost"
                className="w-fit hover:text-destructive focus-visible:text-destructive"
                onClick={() => {
                  logout();
                }}
              >
                Logout
              </Button>
            </div>
          )}
        </div>
      </div>
      {import.meta.env.DEV && <Devtools />}
    </main>
  );
}

export default App;
