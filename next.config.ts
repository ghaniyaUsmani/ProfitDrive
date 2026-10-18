import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [{ source: "/", destination: "/design-system/index.html", permanent: false }];
  },
};

export default nextConfig;
