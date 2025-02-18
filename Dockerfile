FROM ubuntu:latest

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages (Chromium from Debian repo, no Snap)
RUN apt update && apt install -y \
    chromium \
    x11vnc \
    xvfb \
    fluxbox \
    websockify \
    wget && \
    rm -rf /var/lib/apt/lists/*

# Download and install noVNC
RUN mkdir -p /opt/novnc && \
    wget -qO- https://github.com/novnc/noVNC/archive/refs/tags/v1.3.0.tar.gz | tar xz --strip-components=1 -C /opt/novnc

# Copy the startup script into the container
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set up environment
ENV DISPLAY=:0

# Run the startup script
CMD ["/start.sh"]
