import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  serverComponentsExternalPackages: [
    'lightningcss',
    'lightningcss-darwin-arm64',
    'lightningcss-darwin-x64',
  ],
  webpack: (config) => {
    // Ensure native modules are not bundled
    config.resolve.alias = {
      ...config.resolve.alias,
    };
    return config;
  },
};

export default nextConfig;
