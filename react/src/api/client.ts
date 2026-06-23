import axios from "axios";

const client = axios.create({
  baseURL: "/",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

// Inject CSRF token into state-changing requests
client.interceptors.request.use(async (config) => {
  if (config.method && ["post", "put", "delete", "patch"].includes(config.method)) {
    // Fetch CSRF token from session if not already cached
    if (!client.defaults.headers.common["X-CSRF-Token"]) {
      try {
        await axios.get("/api/auth/me", {
          withCredentials: true,
        });
        // Make a GET to get CSRF token set in session
        await axios.get("/api/auth/me", { withCredentials: true });
        // Use a known token from the cookie
        const token = document.cookie
          .split("; ")
          .find((row) => row.startsWith("csrf_token="))
          ?.split("=")[1];
        if (token) {
          client.defaults.headers.common["X-CSRF-Token"] = token;
        }
      } catch {
        // proceed without CSRF, server will reject if needed
      }
    }
  }
  return config;
});

export default client;
