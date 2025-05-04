import { Button } from "@/components/ui/button";
import Icon from "./Strava_Icon.svg?react";
import { cn } from "@/lib/utils";
export const ConnectStrava = ({
  className,
  onClick,
  ref,
  disabled,
  connected,
}: {
  className?: string;
  onClick: () => void;
  ref?: React.Ref<HTMLButtonElement>;
  disabled?: boolean;
  connected?: boolean;
}) => {
  return (
    <Button
      ref={ref}
      variant={connected ? "success" : "secondary"}
      className={cn("w-full", className)}
      onClick={onClick}
      disabled={disabled}
    >
      <Icon className="mr-1 text-strava" />
      {connected ? "Strava Connected" : "Log in with Strava"}
    </Button>
  );
};
