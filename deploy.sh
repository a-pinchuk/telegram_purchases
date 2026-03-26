#!/bin/bash
# Deploy script for DigitalOcean droplet
# Run this ON the server after cloning the repo

set -e

echo "=== Telegram Purchase Bot Deploy ==="

# 1. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# 2. Install Docker Compose plugin if not present
if ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose..."
    apt-get update && apt-get install -y docker-compose-plugin
fi

# 3. Check .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Create it: cp .env.example .env && nano .env"
    exit 1
fi

# 4. Build and run
echo "Building and starting bot..."
docker compose up -d --build

echo ""
echo "=== Done! ==="
echo "Check logs: docker compose logs -f"
echo "Stop: docker compose down"
echo "Restart: docker compose restart"
