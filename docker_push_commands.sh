#!/bin/bash
# Commands to build and push the Docker image
# Run these on a system with full Docker support

set -e  # Exit on error

echo "========================================"
echo "Building Flux2 Klein Serverless Image"
echo "========================================"

# 1. Build the image with your specific tag
echo "Step 1: Building Docker image..."
docker build --platform linux/amd64 -t s1710374103/flux2kleinserverless:tagname .

echo ""
echo "Build complete! Verifying image..."
docker images | grep flux2kleinserverless

# 2. Login to Docker Hub (you'll be prompted for password)
echo ""
echo "Step 2: Logging in to Docker Hub..."
docker login

# 3. Push the image
echo ""
echo "Step 3: Pushing image to Docker Hub..."
docker push s1710374103/flux2kleinserverless:tagname

echo ""
echo "========================================"
echo "Image pushed successfully!"
echo "Docker Hub URL: docker.io/s1710374103/flux2kleinserverless:tagname"
echo "========================================"
