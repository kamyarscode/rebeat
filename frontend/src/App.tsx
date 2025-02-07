import "./App.css";
import { Button } from "./components/ui/button";

function App() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Welcome to Rebeat</h1>
      <Button>Connect to Spotify</Button>
      <Button>Connect to Strava</Button>
    </div>
  );
}

export default App;
