# GitHub Actions - Automated CI/CD

This project uses **3 separate workflows** following best practices from worker-whisper:

## 1. 🔄 Continuous Deployment (cd.yml - docker-build-push.yml)
Automatically builds and pushes Docker images to **Docker Hub** and **GitHub Container Registry**.

### Triggers:
- Push to `main` or `master` branch
- New version tags (`v*.*.*`)
- Release published
- Manual workflow dispatch

### What it does:
- ✓ Builds Docker image for `linux/amd64`
- ✓ Pushes to Docker Hub as `s1710374103/flux2kleinserverless`
- ✓ Pushes to GHCR as `ghcr.io/<your-username>/flux2_serverless`
- ✓ Creates multiple tags: `latest`, `tagname`, branch name, commit SHA
- ✓ Uses GitHub Actions cache for faster builds

## 2. ✅ Continuous Integration (ci.yml)
Runs code quality checks and validates the Dockerfile.

### Triggers:
- Push to `main`, `master`, or `dev` branches
- Pull requests
- Manual workflow dispatch

### What it does:
- ✓ **Code Quality Checks:** Black, isort, flake8, pylint
- ✓ **Dockerfile Validation:** Ensures it builds successfully
- ✓ **Security Scanning:** Trivy vulnerability scanner

## 3. 📦 RunPod Package Updater (update-runpod.yml)
Automatically checks for new runpod package versions and creates PRs.

### Triggers:
- Push to `main` or `master`
- Manual workflow dispatch
- Repository dispatch events

### What it does:
- ✓ Checks PyPI for new runpod versions
- ✓ Updates `requirements.txt` if major/minor version changes
- ✓ Creates automatic pull request with changes

---

## Initial Setup

### Required Secrets

Go to **Settings** → **Secrets and variables** → **Actions** and add:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `DOCKERHUB_TOKEN` | Docker Hub access token | https://hub.docker.com/settings/security → "New Access Token" |

**Note:** `GITHUB_TOKEN` is automatically provided by GitHub Actions.

---

## Usage

### Option 1: Automatic on Push
```bash
git add .
git commit -m "Update Flux2 worker"
git push origin main
```

The workflows will automatically:
1. Run CI checks (linting, validation, security scan)
2. Build and push Docker images
3. Check for runpod package updates

### Option 2: Manual Trigger
1. Go to **Actions** tab in your repository
2. Select the workflow you want to run
3. Click **"Run workflow"**
4. Select branch and click **"Run workflow"**

---

## Docker Image Locations

After successful build, your images will be available at:

### Docker Hub (Primary)
```
docker.io/s1710374103/flux2kleinserverless:tagname
docker.io/s1710374103/flux2kleinserverless:latest
```

### GitHub Container Registry (Backup)
```
ghcr.io/<your-username>/flux2_serverless:latest
ghcr.io/<your-username>/flux2_serverless:main
```

---

## Use in RunPod

When creating a serverless endpoint, use:
```
s1710374103/flux2kleinserverless:tagname
```

Or for latest:
```
s1710374103/flux2kleinserverless:latest
```

---

## Workflow Status Badges

Add these to your README.md:

```markdown
[![CD](https://github.com/<USERNAME>/Flux2_serverless/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/<USERNAME>/Flux2_serverless/actions/workflows/docker-build-push.yml)
[![CI](https://github.com/<USERNAME>/Flux2_serverless/actions/workflows/ci.yml/badge.svg)](https://github.com/<USERNAME>/Flux2_serverless/actions/workflows/ci.yml)
```
