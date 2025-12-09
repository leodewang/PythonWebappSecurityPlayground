# Project Summary

## Overview
Python Web Application Security Playground - A complete CI/CD pipeline demonstration with automated security scanning and vulnerability patching deployed to Azure.

## What's Included

### Application
- **Language**: Python 3.11
- **Framework**: Flask
- **Features**: Simple REST API with health check endpoints

### Infrastructure
- **Container Registry**: Azure Container Registry (ACR)
- **Orchestration**: Azure Kubernetes Service (AKS)
- **CI/CD**: GitHub Actions

### Security Tools
- **Scanner**: Trivy (v0.28.0)
- **Patcher**: Copacetic (Copa)
- **Reporting**: GitHub Security tab (SARIF)

## Quick Links

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Main documentation, features, and usage |
| [SETUP.md](SETUP.md) | Step-by-step Azure setup guide |
| [WORKFLOWS.md](WORKFLOWS.md) | Detailed workflow documentation |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture diagrams and data flow |

## File Structure

```
.
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage container build
├── .dockerignore                   # Docker build exclusions
├── .gitignore                      # Git exclusions
│
├── k8s/
│   ├── deployment.yaml             # K8s deployment
│   └── service.yaml                # K8s LoadBalancer service
│
├── .github/workflows/
│   ├── ci.yml                      # CI - Build & Test
│   ├── trivy-scan.yml              # Security scanning
│   ├── copacetic-patch.yml         # Vulnerability patching
│   └── azure-deploy.yml            # Deploy to Azure
│
└── docs/
    ├── README.md                   # Main documentation
    ├── SETUP.md                    # Setup guide
    ├── WORKFLOWS.md                # Workflow docs
    └── ARCHITECTURE.md             # Architecture
```

## Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| CI | Push/PR | Build and test |
| Trivy Scan | Push/PR, Daily | Vulnerability scanning |
| Copa Patch | Weekly, Manual | Automated patching |
| Azure Deploy | Push to main | Deploy to Azure |

## Required Secrets

For Azure deployment, configure these GitHub secrets:

```
AZURE_CREDENTIALS     # Service principal JSON
ACR_NAME             # Container registry name
AKS_CLUSTER_NAME     # Kubernetes cluster name
AKS_RESOURCE_GROUP   # Azure resource group
```

## Getting Started

### 1. Setup Azure Resources
```bash
# See SETUP.md for detailed instructions
az group create --name python-webapp-rg --location eastus
az acr create --name myacrname --resource-group python-webapp-rg --sku Basic
az aks create --name myaks --resource-group python-webapp-rg --attach-acr myacrname
```

### 2. Configure GitHub Secrets
Add the four required secrets in repository settings.

### 3. Deploy
Push to `main` branch or manually trigger the deployment workflow.

### 4. Access Application
```bash
kubectl get service python-webapp
# Visit http://<EXTERNAL-IP>/
```

## Testing Locally

### Run Application
```bash
pip install -r requirements.txt
python app.py
curl http://localhost:8080/health
```

### Build Container
```bash
docker build -t python-webapp .
docker run -p 8080:8080 python-webapp
```

### Scan with Trivy
```bash
trivy image python-webapp
```

## Key Features

### Security
✅ Multi-stage Docker builds
✅ Non-root container user
✅ Automated vulnerability scanning
✅ Automated OS-level patching
✅ GitHub Security integration
✅ Pinned action versions

### Reliability
✅ Health checks (liveness/readiness)
✅ Resource limits
✅ Error handling with fallbacks
✅ Rollout status verification

### Observability
✅ Workflow execution logs
✅ Security scan results
✅ Pod logs via kubectl
✅ Health endpoint monitoring

## Endpoints

- `GET /` - Application info
- `GET /health` - Health check (200 OK)

## Next Steps

1. ✅ Review [SETUP.md](SETUP.md) for Azure configuration
2. ✅ Check [WORKFLOWS.md](WORKFLOWS.md) for workflow details
3. ✅ Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. ⏭️ Configure GitHub secrets
5. ⏭️ Deploy to Azure
6. ⏭️ Monitor security scans in GitHub Security tab

## Support

- **GitHub Actions**: Repository Actions tab
- **Security Alerts**: Repository Security tab
- **Trivy Docs**: https://aquasecurity.github.io/trivy/
- **Copa Docs**: https://project-copacetic.github.io/copacetic/
- **Azure Docs**: https://docs.microsoft.com/azure/

## License

Educational and demonstration purposes.
