# syntax=docker/dockerfile:1

# Build for linux/amd64 architecture
FROM python:3.13-slim AS base

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Set working directory
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (production only)
RUN uv sync --frozen --no-dev

# Copy source code
COPY src ./src

# Expose default port
EXPOSE 9009

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD [".venv/bin/python", "-c", "import httpx; httpx.get('http://localhost:9009/.well-known/agent.json')"]

# Set entrypoint to run the server module
# Accepts --host, --port, --card-url arguments
ENTRYPOINT [".venv/bin/python", "-m", "agentbeats.server"]

# Default command (can be overridden)
CMD ["--host", "0.0.0.0", "--port", "9009"]
