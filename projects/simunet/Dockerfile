# Multi-stage build for netdriver-simunet
FROM ghcr.io/opensecflow/netdriver/python-poetry AS builder

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Simunet - Simulated SSH Server for Network Devices"
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
    && poetry build-project -C projects/simunet

# Final stage
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/OpenSecFlow/netdriver"
LABEL org.opencontainers.image.description="NetDriver Simunet - Simulated SSH Server for Network Devices"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Create non-root user
RUN useradd -m -u 1000 netdriver

WORKDIR /app

# Copy built wheel and install it
COPY --from=builder /build/projects/simunet/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl \
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

# Run simunet
CMD ["uvicorn", "netdriver.simunet.main:app", "--host", "0.0.0.0", "--port", "8001"]
