# GitHub Actions CI/CD Workflows

This directory contains automated workflows for testing, linting, and deploying the SEIM application.

## Workflows

### 1. Test Suite (`test.yml`)
Runs on: Push and Pull Request to `main`, `master`, `develop`

**What it does:**
- Sets up PostgreSQL and Redis services
- Installs Python dependencies
- Runs database migrations
- Executes full test suite with coverage
- Uploads coverage to Codecov
- Validates test count (minimum 1000 tests)

**Environment variables required:**
- `CODECOV_TOKEN` (secret, optional)

### 2. Code Quality (`lint.yml`)
Runs on: Push and Pull Request to `main`, `master`, `develop`

**What it does:**
- Runs Ruff linter
- Runs Flake8 with complexity checks
- Performs Bandit security scanning
- Checks for dependency vulnerabilities with Safety

### 3. Deploy (`deploy.yml`)
Runs on: Push to `main`/`master`, or manual trigger

**What it does:**
- Builds and pushes Docker images
- Deploys to staging automatically
- Deploys to production with manual approval
- Runs migrations
- Performs health checks
- Rollback on failure

**Secrets required:**
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password/token

**Environments:**
- `staging` - Auto-deploy from main
- `production` - Manual approval required

### 4. Docker Compose Test (`docker-compose-test.yml`)
Runs on: Push and Pull Request to `main`, `master`, `develop`

**What it does:**
- Builds Docker images using docker-compose
- Starts all services (web, db, redis)
- Waits for services to be healthy
- Runs migrations
- Executes test suite
- Cleans up containers

## Running Workflows Locally

You can test GitHub Actions workflows locally using [act](https://github.com/nektos/act).

### Install act

**Windows (with Chocolatey):**
```powershell
choco install act-cli
```

**macOS (with Homebrew):**
```bash
brew install act
```

**Linux:**
```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Run Workflows

**List all workflows:**
```bash
act -l
```

**Run test workflow:**
```bash
act push -W .github/workflows/test.yml
```

**Run lint workflow:**
```bash
act push -W .github/workflows/lint.yml
```

**Run docker-compose test workflow:**
```bash
act push -W .github/workflows/docker-compose-test.yml
```

**Run with specific event:**
```bash
act pull_request -W .github/workflows/test.yml
```

### Using Secrets Locally

Create `.secrets` file in project root (add to `.gitignore`):
```
CODECOV_TOKEN=your-token-here
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-password
```

Run with secrets:
```bash
act -s-file .secrets push
```

## Manual Workflow Triggers

Some workflows can be triggered manually from GitHub Actions tab:

1. **Deploy workflow** - Choose environment (staging/production)

## CI/CD Best Practices

1. **All tests must pass** before merging PRs
2. **Code quality checks** should have no critical issues
3. **Coverage should be ≥ 80%** for new code
4. **Test count should be ≥ 1000** tests
5. **Security scans** should have no high-severity vulnerabilities
6. **Staging deployment** happens automatically on merge to main
7. **Production deployment** requires manual approval

## Troubleshooting

### Tests failing locally but passing in CI
- Check Python version (should be 3.12)
- Verify all dependencies are installed
- Ensure PostgreSQL and Redis are running
- Check environment variables

### Docker build failures
- Clear Docker cache: `docker system prune -a`
- Rebuild from scratch: `docker-compose build --no-cache`
- Check Dockerfile syntax

### Act not working
- Update act: `choco upgrade act-cli` (Windows)
- Use Docker Desktop or equivalent
- Check act documentation: https://github.com/nektos/act

## Continuous Improvement

### Adding New Workflows
1. Create new `.yml` file in `.github/workflows/`
2. Test locally with `act`
3. Commit and push
4. Monitor first run in GitHub Actions tab

### Updating Workflows
1. Modify existing workflow file
2. Test locally: `act -W .github/workflows/your-workflow.yml`
3. Commit changes
4. Verify in GitHub Actions

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [act Documentation](https://github.com/nektos/act)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Codecov Documentation](https://docs.codecov.com/)

