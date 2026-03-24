FROM python:3.11-slim

# Metadata
LABEL org.opencontainers.image.title="claude-engineer-toolkit"
LABEL org.opencontainers.image.description="Claude-powered CLI tools for backend engineers"
LABEL org.opencontainers.image.source="https://github.com/thitami/claude-engineer-toolkit"

# Don't write .pyc files, don't buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# git is needed for cet pr
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (layer cache — rebuilds only when deps change)
COPY pyproject.toml setup.py ./
COPY cet/__init__.py ./cet/
RUN pip install --no-cache-dir -e .

# Copy the rest of the source
COPY . .

# Re-install in case pyproject changed
RUN pip install --no-cache-dir -e .

# /code is where users mount their project
WORKDIR /code

ENTRYPOINT ["cet"]
CMD ["--help"]
