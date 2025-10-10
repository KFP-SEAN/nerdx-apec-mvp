#!/bin/bash

# Build and run Docker container for NERDX APEC Frontend

set -e

IMAGE_NAME="nerdx-apec-frontend"
CONTAINER_NAME="nerdx-frontend"
PORT=3000

echo "🐳 Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

echo "🧹 Removing existing container if it exists..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

echo "🚀 Starting container: $CONTAINER_NAME"
docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:3000 \
  -e NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000} \
  -e NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY} \
  --restart unless-stopped \
  $IMAGE_NAME

echo "✅ Container started successfully!"
echo "🌐 Frontend is running at http://localhost:$PORT"
echo ""
echo "📋 Useful commands:"
echo "   docker logs $CONTAINER_NAME      # View logs"
echo "   docker stop $CONTAINER_NAME      # Stop container"
echo "   docker restart $CONTAINER_NAME   # Restart container"
