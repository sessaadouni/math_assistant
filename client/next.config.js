/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Désactiver le cache pendant le dev pour voir les changements
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
  // Logs plus verbeux
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
}

module.exports = nextConfig
