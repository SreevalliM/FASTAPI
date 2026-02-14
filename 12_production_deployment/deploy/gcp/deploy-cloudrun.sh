# Google Cloud Run Deployment Script

# Set variables
PROJECT_ID="your-project-id"
SERVICE_NAME="fastapi-app"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Build and push image
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars ENV=production,LOG_LEVEL=INFO \
  --set-secrets DATABASE_URL=database-url:latest,API_KEY=api-key:latest

# Get service URL
gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format 'value(status.url)'
