# Multi-stage build for netdriver-agent
FROM ghcr.io/opensecflow/netdriver/python-uv AS builder

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Agent - Network Device Automation REST API"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# uv is already installed in the base image
ENV UV_NO_PROGRESS=1
ENV UV_PYTHON=python3.12
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /build

# Copy project files
COPY . .

# Build all workspace dependency wheels
RUN uv build --directory packages/core --wheel \
    && uv build --directory packages/textfsm --wheel \
    && uv build --directory packages/agent --wheel

# Final stage
FROM ghcr.io/astral-sh/uv:python3.12-trixie

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Agent - Network Device Automation REST API"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Set uv environment variables for production
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON=python3.12

# Create non-root user
RUN useradd -m -u 1000 netdriver

WORKDIR /app

# Copy built wheel and install it using uv
COPY --from=builder /build/dist/*.whl /tmp/
RUN uv pip install --system --no-cache /tmp/*.whl \
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
CMD ["uvicorn", "netdriver_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
