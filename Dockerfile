FROM debian:bullseye-slim

LABEL maintainer="OpenGrep Team"
LABEL description="OpenGrep - Security code scanning tool"

# Set environment variables
ENV OPENGREP_VERSION="1.0.1"
ENV OPENGREP_DOWNLOAD_URL="https://github.com/opengrep/opengrep/releases/download/v${OPENGREP_VERSION}/opengrep_Linux_x86_64.tar.gz"
ENV PATH="/usr/local/bin:${PATH}"
ENV OPENGREP_RULES_PATH="/app/rules"

# Install required dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    tar \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create rules directory
RUN mkdir -p /app/rules

# Copy rules file into the container
COPY semgrep-pro.json /app/rules/semgrep-pro.json

# Download and install OpenGrep
RUN curl -L ${OPENGREP_DOWNLOAD_URL} -o opengrep.tar.gz && \
    tar -xzf opengrep.tar.gz && \
    mv opengrep /usr/local/bin/ && \
    chmod +x /usr/local/bin/opengrep && \
    rm opengrep.tar.gz

# Create a directory for scanning
WORKDIR /scan

# Default command
ENTRYPOINT ["opengrep"]
CMD ["scan", "--help"]
