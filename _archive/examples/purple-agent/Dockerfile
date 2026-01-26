# syntax=docker/dockerfile:1

# Base image
# Note: Specify platform at build time with: docker build --platform linux/amd64 ...
FROM python:3.13-slim AS base

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY src ./src

# Expose default port
EXPOSE 9010

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

# Set entrypoint to run the server module
# Accepts --host, --port, --card-url arguments
ENTRYPOINT ["uv", "run", "--", "python", "-m", "purpleagent.server"]

# Default command (can be overridden)
CMD ["--host", "0.0.0.0", "--port", "9010"]
