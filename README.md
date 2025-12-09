# Python Webapp Security Playground

A comprehensive container security playground demonstrating the holistic process of secure application deployment using GitHub Actions for CI/CD, Azure Container Registry for storage, and Azure Kubernetes Service (AKS) for orchestration.

## Features

- **Simple Python Flask Web Application**: Minimal web service with health check endpoints
- **Container Security**: Multi-stage Docker build with non-root user
- **Vulnerability Scanning**: Automated Trivy security scans
- **Vulnerability Patching**: Copacetic (Copa) for automated patching
- **CI/CD Pipeline**: GitHub Actions workflows for build, test, scan, and deploy
- **Azure Integration**: Deployment to Azure Container Registry and AKS

## Application Structure

```
.
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Multi-stage container build
├── k8s/                        # Kubernetes manifests
│   ├── deployment.yaml         # Deployment configuration
│   └── service.yaml           # Service configuration
└── .github/workflows/          # GitHub Actions workflows
    ├── ci.yml                 # Build and test workflow
    ├── trivy-scan.yml         # Security scanning
    ├── copacetic-patch.yml    # Vulnerability patching
    └── azure-deploy.yml       # Azure deployment
```

## Prerequisites

### Azure Resources

Before running the deployment workflow, you need to create the following Azure resources:

1. **Azure Container Registry (ACR)**
   ```bash
   az group create --name myResourceGroup --location eastus
   az acr create --resource-group myResourceGroup --name myacrname --sku Basic
   ```

2. **Azure Kubernetes Service (AKS)**
   ```bash
   az aks create \
     --resource-group myResourceGroup \
     --name myAKSCluster \
     --node-count 2 \
     --enable-managed-identity \
     --attach-acr myacrname
   ```

3. **Service Principal for GitHub Actions**
   ```bash
   az ad sp create-for-rbac \
     --name "github-actions-sp" \
     --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/myResourceGroup \
     --sdk-auth
   ```

### GitHub Secrets

Configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

- `AZURE_CREDENTIALS`: JSON output from the service principal creation
- `ACR_NAME`: Your Azure Container Registry name (without .azurecr.io)
- `AKS_CLUSTER_NAME`: Your AKS cluster name
- `AKS_RESOURCE_GROUP`: Your Azure resource group name

## Workflows

### 1. CI - Build and Test (`ci.yml`)

Triggers on push/PR to main or develop branches:
- Installs Python dependencies
- Runs basic application tests
- Builds Docker image
- Tests the containerized application

### 2. Trivy Security Scan (`trivy-scan.yml`)

Triggers on push/PR and daily schedule:
- Scans filesystem for vulnerabilities
- Scans Docker image for vulnerabilities
- Uploads results to GitHub Security tab
- Reports CRITICAL and HIGH severity issues

### 3. Copacetic Patching (`copacetic-patch.yml`)

Triggers manually or weekly:
- Scans image with Trivy
- Uses Copa to automatically patch OS-level vulnerabilities
- Compares vulnerability counts before/after patching
- Demonstrates automated remediation

### 4. Azure Deployment (`azure-deploy.yml`)

Triggers on push to main or manually:
- Builds Docker image
- Scans with Trivy
- Patches vulnerabilities with Copa
- Pushes to Azure Container Registry
- Deploys to Azure Kubernetes Service
- Reports deployment status and endpoint

## Local Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:8080
```

### Building Docker Image

```bash
# Build the image
docker build -t python-webapp .

# Run the container
docker run -p 8080:8080 python-webapp

# Test the health endpoint
curl http://localhost:8080/health
```

### Security Scanning Locally

```bash
# Install Trivy
# macOS
brew install aquasecurity/trivy/trivy

# Linux
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update && sudo apt-get install trivy

# Scan the image
trivy image python-webapp
```

## API Endpoints

- `GET /` - Welcome message with application info
- `GET /health` - Health check endpoint (returns 200 OK)

## Security Best Practices

This project demonstrates several security best practices:

1. **Multi-stage Docker builds** - Reduces final image size and attack surface
2. **Non-root user** - Container runs as unprivileged user (UID 1000)
3. **Automated vulnerability scanning** - Continuous Trivy scans
4. **Automated patching** - Copacetic patches OS vulnerabilities
5. **SARIF integration** - Security scan results in GitHub Security tab
6. **Resource limits** - Kubernetes pod resource constraints
7. **Health checks** - Liveness and readiness probes

## Troubleshooting

### Workflow fails with Azure authentication error

Ensure your `AZURE_CREDENTIALS` secret contains valid service principal credentials with proper permissions.

### Copa patching doesn't reduce vulnerabilities

Copa primarily patches OS-level vulnerabilities. Application-level vulnerabilities require updating dependencies in `requirements.txt`.

### AKS deployment can't pull from ACR

Verify that your AKS cluster is attached to ACR:
```bash
az aks update --name myAKSCluster --resource-group myResourceGroup --attach-acr myacrname
```

## Contributing

This is a security playground for learning and experimentation. Feel free to:
- Add more security scanning tools
- Implement additional patching strategies
- Enhance the application with more features
- Improve Kubernetes configurations

## License

This project is for educational purposes.
