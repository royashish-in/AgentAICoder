FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY coding_crew/ ./coding_crew/
COPY agents/ ./agents/
COPY core/ ./core/
COPY config/ ./config/

# Install dependencies
RUN uv sync --frozen

# Create directories
RUN mkdir -p logs cache metrics

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "coding_crew.main:app", "--host", "0.0.0.0", "--port", "8000"]