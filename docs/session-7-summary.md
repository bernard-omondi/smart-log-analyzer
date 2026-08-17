# 📘 SUMMARY – SESSION 7 (Docker & Containerization)

**Date:** 2026-08-17  
**Apprentice:** Bernard Omondi  
**Stage:** Production Readiness – Docker  
**Status:** ✅ COMPLETED

---

## 1. WHAT WE ACCOMPLISHED

| Task | Status | Proof |
|------|--------|-------|
| Installed Docker Desktop | ✅ | `docker --version` works |
| Built Docker image | ✅ | `docker build -t smart-log-analyzer .` |
| Tested CLI inside container | ✅ | `docker run smart-log-analyzer --help` |
| Ingested logs inside container | ✅ | `docker run -v $(pwd):/app/data ...` |

---

## 2. WHY DOCKER?

| Without Docker | With Docker |
|----------------|-------------|
| "It works on my machine" | "It works everywhere" |
| Manual setup for each environment | One `docker run` command |
| Dependency conflicts | Isolated environment |
| Hard to share with team | Share the image |
| Hard to deploy to cloud | Deploy the container |

---

## 3. KEY FILES CREATED

### `Dockerfile`
```dockerfile
# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install the package
RUN pip install --no-cache-dir -e ".[dev]"

# Set the default command (you can override this)
ENTRYPOINT ["python", "-m", "src.ingest"]

# Default arguments (override with --help, --verbose, etc.)
CMD ["--help"]
```

**.dockerignore**

```text

venv/
__pycache__/
*.pyc
*.log
*.db
visualizations/
.git/
.gitignore
.dockerignore
Dockerfile
*.png
*.jpg
*.md
!README.md
```

4. DOCKERFILE DEEP-DIVE

| Instruction |	What it does |
|-------------|--------------|
| FROM python:3.11-slim	| Uses a lightweight Python image |
| WORKDIR /app | Sets the working directory inside the container |
| RUN apt-get update... | Installs system dependencies (build tools) |
| COPY pyproject.toml README.md ./	| Copies project metadata |
| COPY src/ ./src/ | Copies your source code |
| COPY scripts/ ./scripts/ | Copies your helper scripts |
| RUN pip install -e ".[dev]" |	Installs your package and dependencies |
| ENTRYPOINT ["python", "-m", "src.ingest"] | Sets the default command |
| CMD ["--help"] | Default arguments (overridable) |

---

5. COMMANDS LEARNED

| Command |	What it does |
|---------|--------------|
| docker --version | Check if Docker is installed |
| docker build -t smart-log-analyzer . | Build the Docker image |
| docker run smart-log-analyzer --help | Run the container with help menu |
| docker run -v $(pwd):/app/data smart-log-analyzer /app/data/sample.log --verbose | Mount local files into container |
| docker ps	| List running containers |
| docker ps -a | List all containers (including stopped) |
| docker images | List all images |
| docker rmi smart-log-analyzer | Remove an image |
| docker system prune -f | Clean up unused resources |
| docker run --rm ... |	Remove container after it exits |

---

6. VOLUME MOUNTING EXPLAINED
bash

docker run -v $(pwd):/app/data smart-log-analyzer /app/data/sample.log --verbose


| Part | What it does |
|------|--------------|
| -v $(pwd):/app/data |	Mounts your current directory to /app/data inside the container |
| $(pwd) | Your current directory on your laptop |
| /app/data | The path inside the container |
| /app/data/sample.log | The container reads your local sample.log |

---

Why this matters: Without volume mounting, the container can't see your local files. With it, you can ingest logs from your laptop.

7. TROUBLESHOOTING

| Problem |	Solution |
|---------|----------|
| zsh: command not found: docker | Install Docker Desktop |
| Cannot connect to the Docker daemon |	Start Docker Desktop |
| The file /Applications/Docker.app does not exist | Install Docker Desktop (brew install --cask docker) |
| failed to connect to the docker API |	Wait for Docker to start, or run open /Applications/Docker.app |
| Build takes a long time |	First build is slow (downloading base image). Future builds are faster. |

---

8. NEXT STEPS

| Option | Description | Difficulty |
|--------|-------------|------------|
| **1. Deploy to Cloud** | Deploy your container to Render, Fly.io, or Railway | Medium |
| **2. Add GitHub Actions** | Auto-build and test on every push | Medium |
| **3. Add Health Check** |	Add a /health endpoint for monitoring |	Easy |
| **4. Optimize the Dockerfile** | Multi-stage builds, smaller image size |	Medium |

---

## COMMAND SEQUENCE

```bash
# Save the summary
nano docs/session-7-summary.md

# Paste the content above, save, and exit

# Add all changes
git add Dockerfile .dockerignore docs/session-7-summary.md

# Commit
git commit -m "feat: add Dockerfile for containerized deployment

docs: add session 7 summary - Docker & containerization"

# Push
git push
```

