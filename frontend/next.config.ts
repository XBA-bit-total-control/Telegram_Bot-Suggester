import type { NextConfig } from "next";

const backendUrl = (
  process.env.BACKEND_INTERNAL_URL ?? "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const nextConfig: NextConfig = {
  // Keep this for the current local ngrok development workflow.
  allowedDevOrigins: ["aged-dangling-chess.ngrok-free.dev"],

  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
