# Bundles the Python echo server and client

# Start from a base ubuntu image (noble = 24.04 LTS)
FROM ubuntu:noble

WORKDIR /app

# Install Python 3
RUN apt-get update
RUN apt-get -y install curl
RUN apt-get -y install python3 python3-venv
RUN rm -rf /var/lib/apt/lists/*

# Verify Python is installed
RUN python3 --version

# Create virtual environment
RUN python3 -m venv .venv

# Copy the project manifest
COPY pyproject.toml .

# Install dependencies from pyproject.toml
RUN . .venv/bin/activate && pip install .

# Copy the application source
COPY src/ src/

# Link application source so it gets catalogued
RUN mkdir -p /opt/antithesis/catalog
RUN ln -s /app/src /opt/antithesis/catalog

# Copy entrypoint scripts
COPY antithesis/*.sh \
  .
# Make entrypoint scripts executable
RUN chmod a+x *.sh

# Command/entrypoint is set in docker-compose
CMD ["echo", "Goodbye!"]
