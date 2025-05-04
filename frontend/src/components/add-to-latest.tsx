import { getLatestRun } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Button } from "./ui/button";

export const AddToLatest = () => {
  const { data: latestRun } = useQuery({
    queryKey: ["latestRun"],
    queryFn: getLatestRun,
  });
  return (
    <div className="flex flex-col gap-2">
      <Button variant="outline">
        🎵 Add a playlist to{" "}
        {latestRun?.name ? `"${latestRun?.name}"` : "my latest run"}
      </Button>
    </div>
  );
};
