import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'v3b.fal.media',
      },
      {
        protocol: 'https',
        hostname: 'fal.media',
      }
    ]
  },
  // Allow cross-origin requests from Docker containers/VMs during development
  allowedDevOrigins: [
    "172.29.96.1",
    "localhost",
    "127.0.0.1",
  ],
};

export default nextConfig;
