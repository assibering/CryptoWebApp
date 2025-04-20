# syntax=docker/dockerfile:1.4
# (this line enables modern Docker features like mount)

###########################################
# BUILDER stage
###########################################
FROM ghcr.io/astral-sh/uv:bookworm-slim as builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed

RUN uv python install 3.12

WORKDIR /app

# Install dependencies (only)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# Copy full app code
ADD . /app

# Install full project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

###########################################
# FINAL stage
###########################################
FROM debian:bookworm-slim

# Copy the Python version
COPY --from=builder --chown=python:python /python /python

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Production-specific env
ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH="/app"

# Default prod command (no reload)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
