import { withAuth } from "./auth-utils";
import { API_URL } from "./constants";

export const getLatestRun = async () => {
  const response = await fetch(`${API_URL}/latest`, withAuth());
  return response.json();
};
