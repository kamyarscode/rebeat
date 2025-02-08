import { Button } from "@/components/ui/button";
import Icon from "./Primary_Logo_Green_RGB.svg?react";
import { cn } from "@/lib/utils";

export const ConnectSpotify = ({ className }: { className?: string }) => {
  return (
    <Button className={cn("w-full", className)}>
      <Icon className="mr-1" />
      Connect Spotify
    </Button>
  );
};
