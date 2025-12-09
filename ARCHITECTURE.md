# CI/CD Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                                │
│                   Python Flask Web Application                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌───────────────┐  ┌──────────────┐  ┌────────────────┐
        │   CI Build    │  │ Trivy Scan   │  │  Copa Patch    │
        │   & Test      │  │   Daily      │  │    Weekly      │
        └───────────────┘  └──────────────┘  └────────────────┘
                │               │                      │
                │               ▼                      │
                │      ┌──────────────┐               │
                │      │   GitHub     │               │
                │      │  Security    │               │
                │      │     Tab      │               │
                │      └──────────────┘               │
                │                                      │
                └──────────────┬───────────────────────┘
                               ▼
                    ┌──────────────────┐
                    │  Push to Main    │
                    └──────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
        ┌───────────────────┐   ┌────────────────┐
        │  Build & Scan     │   │     Patch      │
        │   with Trivy      │───│   with Copa    │
        └───────────────────┘   └────────────────┘
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌──────────────────┐
                    │   Azure ACR      │
                    │  (Push Images)   │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Azure AKS      │
                    │    (Deploy)      │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  LoadBalancer    │
                    │   Public IP      │
                    └──────────────────┘
```

## Workflow Flow

### Development Flow
1. **Code Push/PR** → Triggers CI and Trivy scans
2. **CI Workflow** → Builds and tests the application
3. **Trivy Scan** → Scans for vulnerabilities
4. **Security Tab** → Results uploaded for review

### Security Flow
1. **Daily Scan** → Automated Trivy security scanning
2. **Weekly Patch** → Copacetic patches vulnerabilities
3. **Security Alerts** → Visible in GitHub Security tab

### Deployment Flow (Main Branch)
1. **Build Image** → Create Docker container
2. **Scan Image** → Trivy vulnerability assessment
3. **Patch Image** → Copa attempts to patch vulnerabilities
4. **Push to ACR** → Upload images to Azure Container Registry
5. **Deploy to AKS** → Apply Kubernetes manifests
6. **Expose Service** → LoadBalancer assigns public IP

## Key Components

### GitHub Actions Workflows
- **CI** (`ci.yml`) - Continuous Integration
- **Trivy** (`trivy-scan.yml`) - Security Scanning
- **Copa** (`copacetic-patch.yml`) - Vulnerability Patching
- **Deploy** (`azure-deploy.yml`) - Azure Deployment

### Azure Resources
- **ACR** - Azure Container Registry (image storage)
- **AKS** - Azure Kubernetes Service (orchestration)
- **LoadBalancer** - Exposes application to internet

### Security Tools
- **Trivy** - Vulnerability scanner
- **Copa** - Automated vulnerability patcher
- **SARIF** - Security scan result format

## Data Flow

```
Code → Build → Scan → Patch → Push → Deploy → Serve
```

### Image Tagging Strategy
- `{sha}` - Specific commit SHA for traceability
- `{sha}-patched` - Patched version of the image
- `latest` - Points to most recent deployment (patched if available)

## Security Layers

1. **Code Level**
   - Python dependency scanning
   - Static code analysis

2. **Container Level**
   - Base image vulnerabilities
   - OS package vulnerabilities
   - Multi-stage build optimization

3. **Runtime Level**
   - Non-root user execution
   - Resource limits
   - Health checks

4. **Network Level**
   - LoadBalancer service type
   - Port exposure configuration

## Monitoring Points

- **GitHub Actions** → Workflow execution logs
- **GitHub Security** → Vulnerability alerts
- **Azure Portal** → Resource health
- **Kubernetes** → Pod logs and events
- **Application** → Health endpoint `/health`
