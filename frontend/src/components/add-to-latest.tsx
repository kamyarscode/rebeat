import { getLatestRun } from "@/lib/api";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Button } from "./ui/button";
import { addPlaylistToLatestRun } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
export const AddToLatest = ({ className }: { className?: string }) => {
  const { data: latestRun } = useQuery({
    queryKey: ["latestRun"],
    queryFn: getLatestRun,
  });

  const runName = latestRun?.name ? `${latestRun?.name}` : "latest run";
  const runUrl = latestRun?.url;
  const { mutate: addToLatest, isPending } = useMutation({
    mutationFn: addPlaylistToLatestRun,
    onSuccess: () => {
      toast.success(
        <span className="w-fit">
          Added a playlist to{" "}
          <a
            href={runUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            {runName}
          </a>
        </span>,
        { duration: 10000 }
      );
    },
    onError: (e) => {
      toast.error(
        <span>
          <span className="font-bold">Failed to add playlist to {runName}</span>
          <br />
          <br />
          <span className="text-xs font-mono">{e.message}</span>
        </span>
      );
    },
  });

  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <Button
        variant="secondary"
        onClick={() => addToLatest()}
        className="text-wrap h-fit p-3"
        disabled={isPending}
      >
        <span className="min-w-0">
          {isPending ? "🎵 Adding playlist to " : "🎵 Add a playlist to "}
          <span className="underline">{runName}</span>
          {isPending ? "..." : ""}
        </span>
      </Button>
    </div>
  );
};
