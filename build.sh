#!/bin/bash
#
# Build and push Docker image to Docker Hub
# Usage: ./build.sh <dockerhub_username> [tag]
#

set -e

DOCKERHUB_USER=${1:-"your_dockerhub_username"}
TAG=${2:-"latest"}
IMAGE_NAME="flux2-klein-serverless"

echo "========================================"
echo "Building FLUX.2 Klein Serverless Worker"
echo "========================================"
echo "Image: ${DOCKERHUB_USER}/${IMAGE_NAME}:${TAG}"
echo ""

# Build the image
echo "Building Docker image..."
docker build --platform linux/amd64 -t ${DOCKERHUB_USER}/${IMAGE_NAME}:${TAG} .

echo ""
echo "Build complete!"
echo ""

# Ask to push
read -p "Push to Docker Hub? (y/n): " PUSH

if [ "$PUSH" = "y" ] || [ "$PUSH" = "Y" ]; then
    echo "Pushing to Docker Hub..."
    docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:${TAG}
    echo ""
    echo "Push complete!"
    echo ""
    echo "Your image is available at:"
    echo "  docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:${TAG}"
    echo ""
    echo "Use this URL when creating your RunPod endpoint."
else
    echo ""
    echo "Skipping push. To push later, run:"
    echo "  docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:${TAG}"
fi
