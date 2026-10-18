import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/", destination: "/design-system/index.html" }];
  },
};

export default nextConfig;
