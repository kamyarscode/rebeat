import { Button } from "@/components/ui/button";
import Icon from "./Primary_Logo_Green_RGB.svg?react";
import { cn } from "@/lib/utils";

export const ConnectSpotify = ({
  className,
  onClick,
}: {
  className?: string;
  onClick?: () => void;
}) => {
  return (
    <Button
      variant="secondary"
      className={cn("w-full", className)}
      onClick={onClick}
    >
      <Icon className="mr-1" />
      Connect Spotify
    </Button>
  );
};
