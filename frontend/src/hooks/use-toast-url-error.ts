import { useQueryState } from "nuqs";
import { useEffect } from "react";
import { toast } from "sonner";

/** Toast an error message from the URL if it exists. TODO: Why does this toast twice? */
export const useToastUrlError = () => {
  const [error, setError] = useQueryState("error");

  useEffect(() => {
    if (error) {
      toast.error(error);
      setError(null);
    }
  }, [error]);
};
