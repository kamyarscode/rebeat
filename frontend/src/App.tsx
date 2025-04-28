import { ConnectSpotify } from "@/components/connect-spotify";
import { ConnectStrava } from "@/components/connect-strava";
import { useQueryState } from "nuqs";

function App() {
  // TODO: This is just a proof of concept, remove this
  const [accessToken] = useQueryState("access_token");

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
        <div className=" flex flex-col gap-2 sm:flex-row">
          <ConnectStrava
            className="animate-in fade-in slide-in-from-bottom-4 delay-200 fill-mode-backwards ease-out-quart duration-1000"
            onClick={() => {
              window.location.href = "http://localhost:8000/strava/login";
            }}
          />
          <ConnectSpotify
            className="animate-in fade-in slide-in-from-bottom-4 delay-300 fill-mode-backwards ease-out-quart duration-1000"
            onClick={() => {
              window.location.href = "http://localhost:8000/login";
            }}
          />
        </div>
        {/* TODO: This is just a proof of concept, remove this */}
        {accessToken && (
          <span className="text-wrap break-words text-xs font-mono text-muted-foreground animate-in fade-in-0 slide-in-from-bottom duration-500 p-3 rounded-md bg-muted">
            Access token: {accessToken}
          </span>
        )}
      </div>
    </main>
  );
}

export default App;
