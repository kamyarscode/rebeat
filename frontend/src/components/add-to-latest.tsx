import { getLatestRun } from "@/lib/api";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "./ui/button";
import { addPlaylistToLatestRun } from "@/lib/api";
import { toast } from "sonner";

export const AddToLatest = () => {
  const { data: latestRun } = useQuery({
    queryKey: ["latestRun"],
    queryFn: getLatestRun,
  });

  const { mutate: addToLatest, isPending } = useMutation({
    mutationFn: addPlaylistToLatestRun,
    onSuccess: () => {
      toast.success("Playlist added to latest run");
    },
    onError: () => {
      toast.error("Failed to add playlist to latest run");
    },
  });

  return (
    <div className="flex flex-col gap-2">
      <Button
        variant="outline"
        onClick={() => addToLatest()}
        disabled={isPending}
      >
        {isPending ? "🎵 Adding playlist to" : "🎵 Add a playlist to"}
        {latestRun?.name ? `"${latestRun?.name}"` : "my latest run"}
        {isPending ? "..." : ""}
      </Button>
    </div>
  );
};
