import { Button } from "./ui/button";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
export const Devtools = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user } = useAuth();
  return (
    <div className="absolute left-2 bottom-12 z-50 flex flex-col gap-2">
      {isOpen && (
        <div className="text-wrap break-words text-xs font-mono text-muted-foreground animate-in fade-in-0 slide-in-from-bottom-1 duration-300 p-3 rounded-md bg-muted ease-out-quart">
          <p className="font-semibold mb-1">User Info:</p>
          <pre>{JSON.stringify(user, null, 2)}</pre>
        </div>
      )}
      <Button
        className="p-2 h-fit leading-none w-fit"
        variant={"outline"}
        size={"sm"}
        onClick={() => setIsOpen(!isOpen)}
      >
        🚀 Devtools
      </Button>
    </div>
  );
};
