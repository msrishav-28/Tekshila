/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // appDir is now stable in Next.js 13.4+, removed to avoid warnings in newer versions if applicable, 
    // but keeping if user is on older version. Given package.json says Next 15, appDir is default.
    // However, removing it might be safer to avoid "experimental features" warnings.
    // verification showed "next": "^15.0.0", so we can remove experimental.appDir
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
      },
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      }
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL
          ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
          : 'http://localhost:8000/api/:path*', // Default to local for dev
      },
      {
        source: '/auth/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL
          ? `${process.env.NEXT_PUBLIC_API_URL}/auth/:path*`
          : 'http://localhost:8000/auth/:path*',
      },
    ]
  },
}

module.exports = nextConfig
