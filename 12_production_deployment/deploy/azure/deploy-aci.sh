# Azure Container Instances Deployment
# Deploy using Azure CLI

# variables
location="eastus"
resource_group="fastapi-rg"
container_name="fastapi-container"
image="yourregistry.azurecr.io/fastapi:latest"
dns_name_label="fastapi-app"

# Create resource group
az group create --name $resource_group --location $location

# Create container instance
az container create \
  --resource-group $resource_group \
  --name $container_name \
  --image $image \
  --cpu 2 \
  --memory 4 \
  --registry-login-server yourregistry.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label $dns_name_label \
  --ports 8000 \
  --environment-variables \
    ENV=production \
    LOG_LEVEL=INFO \
  --secure-environment-variables \
    DATABASE_URL=$DATABASE_URL \
    API_KEY=$API_KEY

# Get container URL
echo "Container URL: http://${dns_name_label}.${location}.azurecontainer.io:8000"
