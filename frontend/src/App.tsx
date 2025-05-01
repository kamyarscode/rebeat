import { ConnectSpotify } from "@/components/connect-spotify";
import { ConnectStrava } from "@/components/connect-strava";
import { useAuth } from "@/lib/auth";
import { API_URL } from "./lib/constants";

import { Button } from "./components/ui/button";
import { useToastUrlError } from "./hooks/use-toast-url-error";

function App() {
  const { isAuthenticated, token, user, isLoading } = useAuth();
  useToastUrlError();

  return (
    <main className="flex flex-col gap-4 container mx-auto justify-center items-center h-full px-8">
      <div className="flex flex-col gap-6 max-w-sm">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold animate-in fade-in slide-in-from-bottom-4 duration-1000 ease-out-quart">
            Welcome to Rebeat
          </h1>
          <p className="text-base text-muted-foreground animate-in fade-in slide-in-from-bottom-4 delay-100 fill-mode-backwards ease-out-quart duration-1000">
            Turn your runs into playlists you can revisit right from Strava.
            Connect your accounts to get started.
          </p>
        </div>

        {isLoading ? (
          <div className="animate-pulse p-4 bg-muted rounded">
            Loading account information...
          </div>
        ) : isAuthenticated ? (
          <div className="flex flex-col gap-4">
            <div className="p-4 bg-card rounded-lg shadow">
              <h2 className="font-semibold mb-2">Your Accounts</h2>
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span>Strava</span>
                  {user?.strava_id ? (
                    <span className="text-green-500 text-sm">Connected</span>
                  ) : (
                    <ConnectStrava
                      className="h-8 px-2 py-1 text-sm"
                      onClick={() => {
                        window.location.href = `${API_URL}/strava/login${token ? `?token=${token}` : ""}`;
                      }}
                    />
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <span>Spotify</span>
                  {user?.spotify_id ? (
                    <span className="text-green-500 text-sm">Connected</span>
                  ) : (
                    <ConnectSpotify
                      className="h-8 px-2 py-1 text-sm"
                      onClick={() => {
                        window.location.href = `${API_URL}/spotify/login${token ? `?token=${token}` : ""}`;
                      }}
                    />
                  )}
                </div>
              </div>
            </div>

            {user?.strava_id && user?.spotify_id && (
              <Button>Add a playlist to my latest run</Button>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-2 sm:flex-row">
            <ConnectStrava
              className="animate-in fade-in slide-in-from-bottom-4 delay-200 fill-mode-backwards ease-out-quart duration-1000"
              onClick={() => {
                window.location.href = `${API_URL}/strava/login`;
              }}
            />
            <ConnectSpotify
              className="animate-in fade-in slide-in-from-bottom-4 delay-300 fill-mode-backwards ease-out-quart duration-1000"
              onClick={() => {
                window.location.href = `${API_URL}/spotify/login${token ? `?token=${token}` : ""}`;
              }}
            />
          </div>
        )}

        {/* Show user details in dev environment */}
        {import.meta.env.DEV && user && (
          <div className="text-wrap break-words text-xs font-mono text-muted-foreground animate-in fade-in-0 slide-in-from-bottom duration-500 p-3 rounded-md bg-muted">
            <p className="font-semibold mb-1">User Info:</p>
            <pre>{JSON.stringify(user, null, 2)}</pre>
          </div>
        )}
      </div>
    </main>
  );
}

export default App;
