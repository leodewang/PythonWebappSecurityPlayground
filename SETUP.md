# Azure Setup Guide

This guide will help you set up the Azure resources and GitHub secrets required for the CI/CD pipeline.

## Prerequisites

- Azure CLI installed (`az --version` to check)
- An active Azure subscription
- GitHub repository with appropriate permissions

## Step 1: Login to Azure

```bash
az login
```

## Step 2: Set Variables

Replace these values with your preferred names:

```bash
# Set your preferences
RESOURCE_GROUP="python-webapp-rg"
LOCATION="eastus"
ACR_NAME="pythonwebappacr"  # Must be globally unique, lowercase alphanumeric only
AKS_NAME="python-webapp-aks"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "ACR Name: $ACR_NAME"
echo "AKS Name: $AKS_NAME"
echo "Subscription ID: $SUBSCRIPTION_ID"
```

## Step 3: Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

## Step 4: Create Azure Container Registry

```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"
```

## Step 5: Create Azure Kubernetes Service

```bash
# Create AKS cluster with 2 nodes
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys \
  --attach-acr $ACR_NAME

# Get credentials for kubectl
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --overwrite-existing

# Verify connection
kubectl get nodes
```

## Step 6: Create Service Principal for GitHub Actions

```bash
# Create service principal with contributor role
az ad sp create-for-rbac \
  --name "github-actions-python-webapp" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

**Important:** Save the entire JSON output from this command. You'll need it for the GitHub secret.

The output will look like this:
```json
{
  "clientId": "xxxx",
  "clientSecret": "xxxx",
  "subscriptionId": "xxxx",
  "tenantId": "xxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

## Step 7: Configure GitHub Secrets

Go to your GitHub repository:
1. Navigate to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add the following:

### Required Secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AZURE_CREDENTIALS` | The complete JSON output from Step 6 | Service principal credentials |
| `ACR_NAME` | Value of `$ACR_NAME` (e.g., `pythonwebappacr`) | Azure Container Registry name without `.azurecr.io` |
| `AKS_CLUSTER_NAME` | Value of `$AKS_NAME` (e.g., `python-webapp-aks`) | AKS cluster name |
| `AKS_RESOURCE_GROUP` | Value of `$RESOURCE_GROUP` (e.g., `python-webapp-rg`) | Azure resource group name |

### How to add each secret:

1. **AZURE_CREDENTIALS**
   - Name: `AZURE_CREDENTIALS`
   - Value: Paste the entire JSON output from the service principal creation

2. **ACR_NAME**
   - Name: `ACR_NAME`
   - Value: Your ACR name (e.g., `pythonwebappacr`)

3. **AKS_CLUSTER_NAME**
   - Name: `AKS_CLUSTER_NAME`
   - Value: Your AKS cluster name (e.g., `python-webapp-aks`)

4. **AKS_RESOURCE_GROUP**
   - Name: `AKS_RESOURCE_GROUP`
   - Value: Your resource group name (e.g., `python-webapp-rg`)

## Step 8: Verify Setup

### Test ACR Access
```bash
az acr login --name $ACR_NAME
docker pull hello-world
docker tag hello-world $ACR_LOGIN_SERVER/hello-world:v1
docker push $ACR_LOGIN_SERVER/hello-world:v1
```

### Test AKS Access
```bash
kubectl cluster-info
kubectl get nodes
```

## Step 9: Trigger the Workflow

Now you can trigger the GitHub Actions workflows:

1. **Push to main branch** - This will trigger the full deployment pipeline
2. **Manual trigger** - Go to Actions → Deploy to Azure → Run workflow

## Monitoring and Verification

### View Workflow Runs
- Go to your GitHub repository
- Click on **Actions** tab
- Click on a workflow run to see details

### Check Deployed Application
After successful deployment:

```bash
# Get the external IP
kubectl get service python-webapp

# Once the EXTERNAL-IP is assigned (may take a few minutes)
EXTERNAL_IP=$(kubectl get service python-webapp -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Application URL: http://$EXTERNAL_IP"

# Test the application
curl http://$EXTERNAL_IP/
curl http://$EXTERNAL_IP/health
```

### View Logs
```bash
# Get pod name
kubectl get pods

# View logs
kubectl logs -l app=python-webapp

# Stream logs
kubectl logs -f -l app=python-webapp
```

## Cleanup (Optional)

To delete all resources when you're done:

```bash
# Delete the entire resource group (includes ACR and AKS)
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Delete service principal
SP_APP_ID=$(az ad sp list --display-name "github-actions-python-webapp" --query [0].appId -o tsv)
az ad sp delete --id $SP_APP_ID
```

## Troubleshooting

### Issue: ACR name already exists
ACR names must be globally unique. Try a different name with your initials or a random number.

### Issue: AKS creation fails due to quota
Check your subscription's compute quota or choose a smaller VM size:
```bash
az vm list-usage --location $LOCATION -o table
```

### Issue: Service principal creation fails
Ensure you have sufficient permissions in your Azure AD tenant. You may need to contact your administrator.

### Issue: Workflow fails with authentication error
1. Verify the `AZURE_CREDENTIALS` secret contains the complete JSON
2. Ensure the service principal has contributor role on the resource group
3. Check that the subscription ID in the JSON matches your subscription

### Issue: Deployment can't pull from ACR
Verify ACR is attached to AKS:
```bash
az aks update \
  --name $AKS_NAME \
  --resource-group $RESOURCE_GROUP \
  --attach-acr $ACR_NAME
```

## Next Steps

- Review the [README.md](README.md) for application details
- Explore the GitHub Actions workflows in `.github/workflows/`
- Customize the Kubernetes manifests in `k8s/`
- Add monitoring and alerting
- Configure custom domain and SSL/TLS

## Cost Management

To minimize costs:
- Use Basic tier for ACR
- Use smaller VM sizes for AKS nodes (e.g., Standard_B2s)
- Scale down AKS nodes when not in use:
  ```bash
  az aks scale --name $AKS_NAME --resource-group $RESOURCE_GROUP --node-count 1
  ```
- Delete resources when not needed

## Additional Resources

- [Azure Container Registry Documentation](https://docs.microsoft.com/azure/container-registry/)
- [Azure Kubernetes Service Documentation](https://docs.microsoft.com/azure/aks/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Copacetic Documentation](https://project-copacetic.github.io/copacetic/)
