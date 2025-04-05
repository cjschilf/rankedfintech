import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    domains: [
      's.gravatar.com',
      'cdn.auth0.com',
      'lh3.googleusercontent.com'  // For Google OAuth profile pictures
    ],
  },
};

export default nextConfig;
