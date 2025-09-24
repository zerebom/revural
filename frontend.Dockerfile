FROM node:20-bookworm-slim

ENV NEXT_TELEMETRY_DISABLED=1

ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

WORKDIR /app/frontend

# Install dependencies using pnpm (via corepack)
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack enable \
    && corepack prepare pnpm@9.12.2 --activate \
    && pnpm install --frozen-lockfile

# Copy application source and build
COPY frontend/ ./
RUN pnpm build

# Remove dev dependencies for runtime image
RUN pnpm prune --prod

ENV NODE_ENV=production
ENV PORT=8080

EXPOSE 8080

CMD ["pnpm", "start", "--hostname", "0.0.0.0"]
