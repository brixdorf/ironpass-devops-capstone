import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev mode the browser talks to Vite and Vite forwards /api to the backend.
// The backend listens on port 8000 (uvicorn, or docker compose).
const backend = process.env.BACKEND_URL || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": backend,
      "/backend-health": {
        target: backend,
        rewrite: () => "/health",
      },
    },
  },
});
