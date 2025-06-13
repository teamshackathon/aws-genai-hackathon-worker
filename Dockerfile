FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.prod.txt .
RUN pip install --no-cache-dir -r requirements.prod.txt

# Copy project files
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash celery
RUN chown -R celery:celery /app
USER celery

# Default command (can be overridden in docker-compose)
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]