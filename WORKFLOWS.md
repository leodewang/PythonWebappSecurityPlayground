# GitHub Actions Workflows Documentation

This document describes each GitHub Actions workflow in detail.

## Workflow Overview

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| CI - Build and Test | `ci.yml` | Push/PR to main/develop | Build and test the application |
| Trivy Security Scan | `trivy-scan.yml` | Push/PR, daily schedule | Scan for vulnerabilities |
| Copacetic Patching | `copacetic-patch.yml` | Manual, weekly schedule | Patch vulnerabilities |
| Deploy to Azure | `azure-deploy.yml` | Push to main, manual | Deploy to Azure (ACR + AKS) |

## 1. CI - Build and Test (`ci.yml`)

### Purpose
Continuous integration workflow that validates code changes work correctly.

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Steps
1. **Checkout code**: Gets the latest code
2. **Set up Python**: Installs Python 3.11
3. **Install dependencies**: Installs packages from `requirements.txt`
4. **Test application**: Verifies the app imports correctly
5. **Build Docker image**: Creates container image
6. **Test Docker container**: Runs the container and tests health endpoint

### Required Secrets
None

### Permissions
- `contents: read` - Read repository contents

---

## 2. Trivy Security Scan (`trivy-scan.yml`)

### Purpose
Automated vulnerability scanning for both filesystem and container images.

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Daily at 2 AM UTC (scheduled)

### Steps
1. **Checkout code**: Gets the latest code
2. **Build Docker image**: Creates image for scanning
3. **Scan filesystem**: Scans source code and dependencies
4. **Scan Docker image**: Scans container image for vulnerabilities
5. **Upload results**: Uploads SARIF results to GitHub Security tab
6. **Display critical/high**: Shows CRITICAL and HIGH severity issues

### Required Secrets
None

### Permissions
- `contents: read` - Read repository contents
- `security-events: write` - Upload security scan results

### Output
- SARIF files uploaded to GitHub Security tab
- Vulnerability table in workflow logs
- Security alerts visible in repository Security tab

---

## 3. Copacetic Vulnerability Patching (`copacetic-patch.yml`)

### Purpose
Demonstrates automated vulnerability patching using Copacetic (Copa).

### Triggers
- Manual workflow dispatch (Actions tab)
- Weekly on Monday at 3 AM UTC (scheduled)

### Steps
1. **Checkout code**: Gets the latest code
2. **Build Docker image**: Creates original image
3. **Scan with Trivy**: Generates vulnerability report (JSON)
4. **Install Copacetic**: Downloads and installs Copa CLI
5. **Install buildkit**: Starts buildkit daemon for image building
6. **Patch vulnerabilities**: Uses Copa to patch OS-level vulnerabilities
7. **Scan patched image**: Verifies patching results
8. **Compare vulnerabilities**: Shows before/after comparison

### Required Secrets
None

### Permissions
- `contents: read` - Read repository contents
- `packages: write` - (Optional) Push patched images to GHCR

### Notes
- Copa primarily patches OS-level vulnerabilities
- Application-level vulnerabilities require dependency updates
- Patching is not always possible for all vulnerabilities

---

## 4. Deploy to Azure (`azure-deploy.yml`)

### Purpose
Complete CI/CD pipeline that builds, scans, patches, and deploys to Azure.

### Triggers
- Push to `main` branch
- Manual workflow dispatch (Actions tab)

### Jobs

#### Job 1: build-scan-patch-push
Builds and pushes container images to Azure Container Registry.

**Steps:**
1. **Checkout code**: Gets the latest code
2. **Azure Login**: Authenticates with Azure
3. **Login to ACR**: Authenticates with Azure Container Registry
4. **Build Docker image**: Creates container image
5. **Scan with Trivy**: Generates vulnerability report
6. **Install Copacetic**: Downloads Copa CLI
7. **Install buildkit**: Starts buildkit daemon
8. **Patch vulnerabilities**: Attempts to patch vulnerabilities
9. **Push images**: Pushes both original and patched images to ACR

#### Job 2: deploy-to-aks
Deploys the application to Azure Kubernetes Service.

**Steps:**
1. **Checkout code**: Gets the latest code
2. **Azure Login**: Authenticates with Azure
3. **Get AKS credentials**: Gets kubectl credentials
4. **Deploy to AKS**: Applies Kubernetes manifests
5. **Wait for deployment**: Waits for rollout to complete
6. **Get service endpoint**: Displays LoadBalancer IP

### Required Secrets
- `AZURE_CREDENTIALS` - Service principal JSON from `az ad sp create-for-rbac --sdk-auth`
- `ACR_NAME` - Azure Container Registry name (without .azurecr.io)
- `AKS_CLUSTER_NAME` - AKS cluster name
- `AKS_RESOURCE_GROUP` - Azure resource group name

### Permissions
- `contents: read` - Read repository contents
- `id-token: write` - Azure authentication

### Environment Variables
- `IMAGE_TAG` - Set to `${{ github.sha }}` for unique image tagging

---

## Workflow Best Practices

### Security
✅ **Pinned action versions** - All actions use specific versions (not @master)
✅ **Minimal permissions** - Each workflow has only required permissions
✅ **Secret management** - Sensitive data stored in GitHub secrets
✅ **SARIF upload** - Security scan results in GitHub Security tab
✅ **Non-root containers** - Docker images run as non-root user

### Reliability
✅ **Error handling** - Copa patching has fallback behavior
✅ **Version fallbacks** - Copa installation has fallback version
✅ **Health checks** - Container testing includes health endpoint
✅ **Rollout verification** - Waits for Kubernetes deployment completion

### Efficiency
✅ **Multi-stage builds** - Optimized Docker image size
✅ **Dependency caching** - Docker layer caching
✅ **Conditional execution** - Some steps run only when needed
✅ **Parallel jobs** - Where possible, jobs run in parallel

---

## Customization

### Changing Scan Frequency
Edit the `schedule` cron expressions:
- Trivy scan: `.github/workflows/trivy-scan.yml` line 8
- Copa patch: `.github/workflows/copacetic-patch.yml` line 6

### Adding More Branches
Edit the `branches` arrays in `on.push` and `on.pull_request` sections.

### Changing Python Version
Edit `.github/workflows/ci.yml` line 18 and `Dockerfile` line 2.

### Modifying Kubernetes Resources
Edit resource requests/limits in `k8s/deployment.yaml` lines 36-40.

---

## Troubleshooting

### Workflow Fails to Start
- Check workflow YAML syntax
- Verify required secrets are configured
- Ensure branch protection rules allow workflows

### Trivy Scan Fails
- Check internet connectivity for vulnerability database
- Verify Docker image builds successfully
- Check disk space on runner

### Copa Patching Shows No Changes
- Copa only patches OS-level vulnerabilities
- Some vulnerabilities are not patchable
- Check Trivy report for patchable vs non-patchable issues

### Azure Deployment Fails
- Verify all Azure secrets are correct
- Check service principal has contributor role
- Ensure ACR is attached to AKS
- Verify resource group and cluster exist

### LoadBalancer IP Not Assigned
- Wait a few minutes for cloud provider to assign IP
- Check AKS cluster has available public IPs
- Verify service type is LoadBalancer

---

## Monitoring Workflows

### View Workflow Runs
1. Go to repository on GitHub
2. Click **Actions** tab
3. Select a workflow from the left sidebar
4. Click on a run to see details

### View Security Alerts
1. Go to repository on GitHub
2. Click **Security** tab
3. Click **Code scanning** or **Dependabot** alerts
4. Filter by tool (Trivy)

### View Deployment Status
```bash
# Get AKS credentials
az aks get-credentials --resource-group <RG> --name <CLUSTER>

# Check pods
kubectl get pods -l app=python-webapp

# Check service
kubectl get service python-webapp

# View logs
kubectl logs -l app=python-webapp --tail=50
```

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Copacetic Documentation](https://project-copacetic.github.io/copacetic/)
- [Azure Container Registry](https://docs.microsoft.com/azure/container-registry/)
- [Azure Kubernetes Service](https://docs.microsoft.com/azure/aks/)
