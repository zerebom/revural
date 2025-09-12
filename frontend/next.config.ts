const parseAllowed = (val?: string) =>
  (val || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

const allowedFromEnv = parseAllowed(process.env.ALLOWED_DEV_ORIGINS);

const nextConfig = {
  // Allow accessing the dev server from LAN IPs or tunnels during development.
  // Configure via env: ALLOWED_DEV_ORIGINS="http://100.64.1.33:3000,http://localhost:3000"
  allowedDevOrigins: allowedFromEnv.length
    ? allowedFromEnv
    : ["http://localhost:3000", "http://127.0.0.1:3000"],
};

export default nextConfig;
