/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // PWA support will be added via next-pwa in a later week
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
