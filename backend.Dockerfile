FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy dependency metadata first to leverage Docker layer caching
COPY README.md pyproject.toml uv.lock ./

# Install only production dependencies defined in uv.lock
RUN uv sync --frozen --no-dev

# Copy application source and runtime assets
COPY src/ ./src/
COPY prompts/ ./prompts/

# Runtime configuration for Cloud Run compatibility
ENV PORT=8080
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "src.hibikasu_agent.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
