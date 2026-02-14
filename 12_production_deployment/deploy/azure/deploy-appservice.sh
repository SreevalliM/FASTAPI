# Azure App Service configuration
# This file contains commands to deploy to Azure App Service

# Login to Azure
az login

# Create resource group
az group create --name fastapi-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name fastapi-plan \
  --resource-group fastapi-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group fastapi-rg \
  --plan fastapi-plan \
  --name fastapi-app-unique \
  --runtime "PYTHON:3.11"

# Configure startup command
az webapp config set \
  --resource-group fastapi-rg \
  --name fastapi-app-unique \
  --startup-file "startup.txt"

# Set environment variables
az webapp config appsettings set \
  --resource-group fastapi-rg \
  --name fastapi-app-unique \
  --settings \
    ENV=production \
    LOG_LEVEL=INFO \
    DATABASE_URL="your-database-url"

# Deploy code
az webapp up \
  --resource-group fastapi-rg \
  --name fastapi-app-unique \
  --runtime "PYTHON:3.11"

# View logs
az webapp log tail \
  --resource-group fastapi-rg \
  --name fastapi-app-unique
