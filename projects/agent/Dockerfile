# Multi-stage build for netdriver-agent
FROM ghcr.io/opensecflow/netdriver/python-poetry AS builder

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Agent - Network Device Automation REST API"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Poetry is already installed with plugins in the base image
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VIRTUALENVS_CREATE=true

WORKDIR /build

# Copy project files
COPY . .

# Install dependencies and build
RUN poetry install --only main --no-interaction --no-ansi \
    && poetry build-project -C projects/agent

# Final stage
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Agent - Network Device Automation REST API"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Create non-root user
RUN useradd -m -u 1000 netdriver

WORKDIR /app

# Copy built wheel and install it
COPY --from=builder /build/projects/agent/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl \
    && rm -rf /tmp/*.whl

# Copy configuration files
COPY config/agent /app/config/agent

# Create logs directory
RUN mkdir -p /app/logs && chown -R netdriver:netdriver /app

USER netdriver

# Expose API port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FATSTAPI_ENV=production
ENV NETDRIVER_CONFIG_PATH=/app/config/agent/agent.yml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run agent
CMD ["uvicorn", "netdriver.agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
