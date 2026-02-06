# Multi-stage build for netdriver-simunet
FROM ghcr.io/opensecflow/netdriver/python-uv AS builder

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Simunet - Simulated SSH Server for Network Devices"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# uv is already installed in the base image
ENV UV_NO_PROGRESS=1
ENV UV_PYTHON=python3.12
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /build

# Copy project files
COPY . .

# Build the wheel using uv
RUN uv build --directory packages/simunet --wheel

# Final stage
FROM ghcr.io/astral-sh/uv:python3.12-trixie

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Simunet - Simulated SSH Server for Network Devices"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Set uv environment variables for production
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON=python3.12

# Create non-root user
RUN useradd -m -u 1000 netdriver

WORKDIR /app

# Copy built wheel and install it using uv
COPY --from=builder /build/packages/simunet/dist/*.whl /tmp/
RUN uv pip install --system --no-cache /tmp/*.whl \
    && rm -rf /tmp/*.whl

# Copy configuration files
COPY config/simunet /app/config/simunet

# Create logs directory
RUN mkdir -p /app/logs && chown -R netdriver:netdriver /app

USER netdriver

# Note: This container is designed to run with --network host
# SSH ports (default range: 2201-2220) are bound directly to the host

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FATSTAPI_ENV=production
ENV NETDRIVER_CONFIG_PATH=/app/config/simunet/simunet.yml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Run simunet
CMD ["uvicorn", "netdriver_simunet.main:app", "--host", "0.0.0.0", "--port", "8001"]
