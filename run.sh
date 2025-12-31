#!/bin/bash
set -euo pipefail # [Safety] Exit immediately if a command exits with a non-zero status.

# ------------------------------------------------------------------
# [Description]
# This script manages the Docker environment for the Tutor Scheduler App.
# It supports building the image, running the container, and cleaning up.
# ------------------------------------------------------------------

IMAGE_NAME="tutor-scheduler-dev"

# Detect Host OS for correct path mounting
case "$(uname -s)" in
    Linux*)                 ROOT=$(pwd);;
    Darwin*)                ROOT=$(pwd);;
    CYGWIN*|MINGW*|MSYS*)   ROOT=$(pwd -W);;
    *)                      ROOT=$(pwd);;
esac

# ------------------------------------------------------------------
# Function: clean_image
# Description: Removes containers and the specific Docker image.
# ------------------------------------------------------------------
clean_image() {
    local containers
    # List all containers using the image (running or stopped)
    containers=$(docker ps -aq --filter "ancestor=$IMAGE_NAME")
    
    if [[ -n "$containers" ]]; then                                         
        echo "Found containers using '$IMAGE_NAME'. Removing..."
        docker rm -f $containers
    fi
    
    # Check if image exists before removing
    if [[ "$(docker images -q "$IMAGE_NAME" 2> /dev/null)" != "" ]]; then
        docker rmi "$IMAGE_NAME"
        echo "Removed Docker image '$IMAGE_NAME'."
    else
        echo "No existing Docker image '$IMAGE_NAME' found."
    fi
}

# ------------------------------------------------------------------
# Function: build_and_run
# Description: Builds the image (if missing) and runs the container.
# ------------------------------------------------------------------
build_and_run() {
    # Build only if missing
    if [[ "$(docker images -q "$IMAGE_NAME" 2> /dev/null)" == "" ]]; then
        echo "Image '$IMAGE_NAME' not found. Building..."
        docker build -t "$IMAGE_NAME" .
    else
        echo "Image '$IMAGE_NAME' found. Skipping build."
    fi

    # Determine command to run: use arguments if provided, else default to 'bash'
    local cmd="${*:-bash}"

    echo ""
    echo "--------------------------------------------------------"
    echo "  Environment Ready!"
    echo "  Starting container with command: $cmd"
    echo "--------------------------------------------------------"
    
    # Setup X11 Forwarding args (Best Effort)
    # Allows GUI apps to show on host screen if X Server is configured.
    X11_ARGS=""
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        X11_ARGS="-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # For Windows, assumes X server (like VcXsrv) running on host
        # access control disabled or configured for host.docker.internal
        X11_ARGS="-e DISPLAY=host.docker.internal:0.0"
    fi
    
    # Run interactive shell, mounting the current directory to /app
    # We use $cmd (unquoted) to allow arguments to be expanded correctly
    docker run --rm -it -v "$ROOT:/app" $X11_ARGS "$IMAGE_NAME" $cmd
}

# ------------------------------------------------------------------
# Main Logic: Menu
# ------------------------------------------------------------------
if [ -n "${1:-}" ]; then
    choice="$1"
    shift # Remove the first argument (choice) so $@ contains the rest
else
    echo "Tutor Scheduler - Docker Manager"
    echo "1. Run (Build if missing)"
    echo "2. Rebuild & Run"
    echo "3. Clean (Remove image) & Exit"
    read -p "Enter choice [1-3]: " choice
fi

case "$choice" in
    1) build_and_run "$@";;
    2) clean_image && build_and_run "$@";;
    3) clean_image && exit 0;;
    *) echo "Invalid choice. Exiting." && exit 1;;
esac
