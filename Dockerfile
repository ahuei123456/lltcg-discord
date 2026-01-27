# Use a specialized uv image for faster builds
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

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
