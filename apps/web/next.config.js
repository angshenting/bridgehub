/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'Bridge Platform',
  },
  images: {
    domains: ['localhost'],
  },
  // Enable strict mode for better development experience
  reactStrictMode: true,
  // Optimize for performance
  swcMinify: true,
  // Configure redirects for bridge-specific routes
  async redirects() {
    return [
      {
        source: '/tournaments',
        destination: '/events',
        permanent: true,
      },
      {
        source: '/members',
        destination: '/players',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;