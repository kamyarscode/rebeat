import { Button } from "@/components/ui/button";
import Icon from "./Strava_Icon.svg?react";
import { cn } from "@/lib/utils";
export const ConnectStrava = ({ className }: { className?: string }) => {
  return (
    <Button className={cn("w-full", className)}>
      <Icon className="mr-1 text-strava" />
      Connect Strava
    </Button>
  );
};
