#!/bin/bash

# Production deployment script for KeyFixer

set -e  # Exit on any error

# Configuration
PROJECT_ID="your-gcp-project"
IMAGE_NAME="keyfixer-api"
REGION="us-central1"

echo "🚀 Starting KeyFixer production deployment..."

# Step 1: Build production image
echo "📦 Building production Docker image..."
docker build -t gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest ./cloud-server

# Step 2: Push to Google Container Registry
echo "⬆️ Pushing image to GCR..."
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest

# Step 3: Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy ${IMAGE_NAME} \
  --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars PROJECT_ID=${PROJECT_ID},REGION=${REGION}

echo "Deployment complete!"
echo "🔗 Service URL:"
gcloud run services describe ${IMAGE_NAME} --region ${REGION} --format="value(status.url)"