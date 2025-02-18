#!/bin/bash

# Start virtual display
Xvfb :0 -screen 0 1920x1080x24 &

# Start window manager
fluxbox &

# Start VNC server (no password)
x11vnc -display :0 -forever -rfbport 5900 -nopw &

# Start noVNC to expose it on port 6080
/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &

# Start Chromium in the foreground (keeps the container running)
exec chromium --no-sandbox --disable-gpu --start-maximized
