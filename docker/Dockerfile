# docker/Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /tmp/build

# Install build dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git gcc python3-dev libpq-dev python3-hiredis && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements/ /tmp/build/requirements/
RUN pip install --user -r requirements/base.txt

FROM python:3.12-slim
WORKDIR /app

# Install runtime dependencies including PostgreSQL client for wait_for_postgres, libmagic, and hiredis
RUN apt-get update && \
    apt-get install -y libpq5 netcat-traditional postgresql-client libmagic1 python3-hiredis && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy the startup scripts
COPY scripts/ /app/scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Create necessary directories
RUN mkdir -p /app/media/exchanges /app/logs /app/staticfiles && \
    chmod -R 755 /app/media /app/logs /app/staticfiles

# The app code will be mounted as a volume in development
# For production, use:
# COPY SEIM/ /app/

# Expose port
EXPOSE 8000

# Use the temporary entrypoint script
ENTRYPOINT ["/app/scripts/entrypoint-temp.sh"]
