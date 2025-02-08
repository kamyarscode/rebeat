import { ConnectSpotify } from "@/components/connect-spotify";
import { ConnectStrava } from "@/components/connect-strava";

function App() {
  return (
    <main className="flex flex-col gap-4 container mx-auto justify-center items-center h-full px-8">
      <div className="flex flex-col gap-6 max-w-sm">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold animate-in fade-in-0 slide-in-from-bottom duration-300">
            Welcome to Rebeat
          </h1>
          <p className="text-sm text-muted-foreground animate-in fade-in-0 slide-in-from-bottom duration-500">
            Rebeat will add a playlist of the music you listened to on your runs
            to your strava activities.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <ConnectStrava className="animate-in fade-in slide-in-from-bottom duration-700" />
          <ConnectSpotify className="animate-in fade-in-0 slide-in-from-bottom duration-700" />
        </div>
      </div>
    </main>
  );
}

export default App;
