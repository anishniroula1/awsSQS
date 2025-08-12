FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# App/runtime deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Test-only deps
COPY tests/requirements-test.txt .
RUN pip install -r tests/requirements-test.txt

# Your code + tests
COPY aks/ ./aks/
COPY tests/ ./tests/

# Run tests
CMD ["pytest", "-q", "--maxfail=1", "--disable-warnings", "--cov=aks", "tests"]
