# Small base for faster test builds
FROM python:3.10-slim

# Speed & reproducibility
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps your tests need (example)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy only what’s needed first to leverage cache
WORKDIR /app

# Install runtime deps (if your app needs them to import)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install test-only deps
COPY tests/requirements-test.txt .
RUN pip install -r tests/requirements-test.txt

# Copy the code last (invalidates fewer layers during edits)
COPY src/ ./src/
COPY tests/ ./tests/

# Default command runs tests
CMD ["pytest", "-q", "--maxfail=1", "--disable-warnings", "--cov=src", "tests"]
