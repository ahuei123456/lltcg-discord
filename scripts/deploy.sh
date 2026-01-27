#!/bin/bash

# LLTCG Discord Bot - Deployment Automation Script
# This script handles pulling latest code, rebuilding the image, and replacing the container.

echo "🚀 Starting deployment..."

# 1. Pull latest changes
echo "📥 Pulling latest changes from Git..."
git pull

# 2. Build the Docker image
echo "🏗️ Building Docker image..."
docker build -t lltcg-bot .

# 3. Replace the container
echo "🔄 Replacing container..."

# Check if container exists before stopping
if [ "$(docker ps -aq -f name=lltcg-bot)" ]; then
    echo "Stopping and removing old container..."
    docker stop lltcg-bot
    docker rm lltcg-bot
fi

# Run the new container
# Note: We mount config.json, card_data.json, and the images folder
docker run -d \
  --name lltcg-bot \
  --restart always \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  -v "$(pwd)/data/card_data.json:/app/data/card_data.json:ro" \
  -v "$(pwd)/data/images:/app/data/images" \
  lltcg-bot

echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✨ Deployment complete! Bot is now running."
echo "📝 You can view logs with: docker logs -f lltcg-bot"
