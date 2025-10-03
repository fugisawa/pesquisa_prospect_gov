/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.amazonaws.com',
      },
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
      },
    ],
  },
  env: {
    // Government compliance configurations
    LGPD_COMPLIANCE_MODE: process.env.NODE_ENV === 'production' ? 'strict' : 'development',
    AUDIT_LOGGING: 'enabled',
    DATA_LOCALIZATION: 'brazil-only',
  },
  // Security headers for government compliance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self';",
          },
        ],
      },
    ];
  },
  // API routes configuration
  async rewrites() {
    return [
      {
        source: '/api/gov/:path*',
        destination: '/api/integration/government/:path*',
      },
      {
        source: '/api/ai/:path*',
        destination: '/api/services/ai/:path*',
      },
    ];
  },
};

module.exports = nextConfig;