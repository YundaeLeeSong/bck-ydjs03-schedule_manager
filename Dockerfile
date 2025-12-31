# Use Official Python 3.11 Slim image
FROM python:3.11-slim

# Install basic utilities and system libraries required for PySide6 (Qt)
# dos2unix: ensures scripts run correctly regardless of host OS line endings
# binutils: required by PyInstaller
# libgl1.../libxcb...: required for Qt GUI support on Linux
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    dos2unix \
    binutils \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies explicitly to leverage Docker layer caching
RUN pip install --no-cache-dir \
    PySide6 \
    requests \
    python-dotenv \
    ics \
    pipreqs \
    pyinstaller

# Copy project files
COPY . .

# Fix line endings and permissions for scripts
RUN dos2unix runner.py run.sh || true \
 && chmod +x runner.py run.sh

# Default command: interactive shell
CMD ["bash"]