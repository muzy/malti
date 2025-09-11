# Build stage for dashboard
FROM node:20-slim AS dashboard-builder

WORKDIR /app/dashboard

# Copy dashboard files
COPY dashboard/package*.json ./
# Clean install to ensure optional dependencies are properly installed for ARM64
RUN npm ci --include=optional && npm cache clean --force

COPY dashboard/ ./
RUN npm run build

# Main application stage
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install only binary wheels - no build dependencies needed!
# asyncpg has pre-compiled binary wheels available
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --only-binary=all -r requirements.txt \
    && rm -rf /var/cache/apt/*

# Copy built dashboard assets from builder stage
COPY --from=dashboard-builder /app/app/static ./app/static

# Copy application code
COPY app/ ./app/

# Create non-root user and set ownership in one layer
RUN useradd --create-home --shell /bin/bash malti && \
    chown -R malti:malti /app
USER malti

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]