import { Button } from "@/components/ui/button";
import Icon from "./Strava_Icon.svg?react";
import { cn } from "@/lib/utils";
export const ConnectStrava = ({
  className,
  onClick,
}: {
  className?: string;
  onClick: () => void;
}) => {
  return (
    <Button
      variant="secondary"
      className={cn("w-full", className)}
      onClick={onClick}
    >
      <Icon className="mr-1 text-strava" />
      Connect Strava
    </Button>
  );
};
