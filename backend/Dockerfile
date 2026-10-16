FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Enable bytecode compilation and add virtualenv to PATH
ENV UV_COMPILE_BYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev || uv sync --no-install-project --no-dev

# Copy application source
COPY . .

# Install the application
RUN uv sync --no-dev

# Expose port
EXPOSE 8000

# Start uvicorn server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
