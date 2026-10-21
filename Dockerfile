# Pin the patched uv release used to install locked dependencies
FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies without the project itself
# This layer is cached as long as pyproject.toml/uv.lock don't change
RUN uv sync --frozen --no-install-project --no-dev

# Final stage
FROM python:3.12-slim-bookworm

# Require the Debian trust-store fix for the eMudhra CA compromise.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419~deb12u2' \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy the source code and data
COPY src ./src
COPY data ./data

# Ensure image cache directory exists
RUN mkdir -p data/images

# Add .venv/bin to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot
CMD ["python", "-m", "src.main"]
