# 📘 SUMMARY – SESSION 8 & 9 (CI/CD + CLOUD DEPLOYMENT)

**Date:** 2026-08-18  
**Apprentice:** Bernard Omondi  
**Stage:** Production Readiness – CI/CD & Deployment  
**Status:** ✅ COMPLETED

---

## 1. WHAT ARE CI & CD?

| Acronym | Stands For | What it means |
|---------|------------|---------------|
| **CI** | **C**ontinuous **I**ntegration | Automatically **testing** your code whenever you push to GitHub |
| **CD** | **C**ontinuous **D**elivery (or Deployment) | Automatically **releasing** your code whenever tests pass |

### Continuous Integration (CI)

| What it does | Why it matters |
|--------------|----------------|
| Runs tests automatically on every `git push` | Catches bugs early |
| Checks code formatting (`black`) | Ensures consistent style |
| Lints code (`ruff`) | Finds errors before runtime |
| Type checks (`mypy`) | Prevents type-related bugs |

**Your CI tool:** GitHub Actions

### Continuous Deployment (CD)

| What it does | Why it matters |
|--------------|----------------|
| Automatically deploys your app when tests pass | No manual deployment steps |
| Builds your Docker image in the cloud | Consistent environment |
| Updates your live URL | Users always see the latest version |

**Your CD tool:** Render Auto-Deploy

### The CI/CD Pipeline (Your Flow)

git push → GitHub Actions (CI) → Tests Pass ✅ → Render (CD) → Live URL
text


---

## 2. WHAT WE ACCOMPLISHED

| Task | Status | Proof |
|------|--------|-------|
| Created GitHub Actions workflow | ✅ | `.github/workflows/ci.yml` |
| Generated new PAT with `workflow` scope | ✅ | Token with `repo` + `workflow` |
| Pushed CI/CD workflow to GitHub | ✅ | Green checkmark on Actions tab |
| Deployed to Render | ✅ | Live at `smart-log-analyzer.onrender.com` |
| Verified deployment | ✅ | Help menu visible online |

---

## 3. THE CI/CD PIPELINE (GITHUB ACTIONS)

### What We Built

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
    - run: pip install -e ".[dev]"
    - run: pytest tests/ -v
    - run: black --check src/ tests/
    - run: ruff check src/ tests/
    - run: mypy src/
```

**What It Does**

| Step | What it does |
|------|--------------|
| actions/checkout | Downloads your code from GitHub |
| setup-python | Installs Python 3.11 in the runner |
| pip install -e ".[dev]" |	Installs your package and dev dependencies |
| pytest | Runs all tests automatically |
| black --check | Verifies code formatting |
| ruff check | Lints your code for errors |
| mypy | Checks type annotations |

---

4. THE DEPLOYMENT PIPELINE (RENDER)
What We Configured

| Setting |	Value |
|---------|-------|
| Platform | Render.com |
| Environment |	Docker |
| Dockerfile Path |	./Dockerfile |
| Docker Build Context | . |
| Docker Command | python -m src.ingest --help |
| Auto-Deploy |	On commit to main |

---

**What Render Does**

| Step | What happens |
|------|--------------|
| 1 | Clones your repository from GitHub |
| 2 | Builds your Docker image |
| 3	| Runs the container |
| 4	| Assigns a public URL |
| 5	| Auto-deploys on every push |

----

5. THE PERSONAL ACCESS TOKEN (PAT) UPGRADE
Problem

```bash

remote: refusing to allow a Personal Access Token to create or update workflow `.github/workflows/ci.yml` without `workflow` scope

```

**Solution**

| Old Token	| New Token |
|-----------|-----------|
| Only repo scope |	repo + workflow scope |

---

**How to Fix** 

    1.- Generate new token with workflow scope

    2.- Update remote URL with the new token

    3.- Push successfully


6. THE FULL DEPLOYMENT ARCHITECTURE
text

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              YOUR FULL DEPLOYMENT PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  📝 You push code to GitHub                                                                 │
│         │                                                                                   │
│         ▼                                                                                   │
│  🤖 GitHub Actions runs CI pipeline                                                         │
│         ├── pytest (tests)                                                                  │
│         ├── black (formatting)                                                              │
│         ├── ruff (linting)                                                                  │
│         └── mypy (types)                                                                    │
│         │                                                                                   │
│         ▼                                                                                   │
│  ☑️ If all tests pass → Green checkmark ✅                                                  │
│         │                                                                                   │
│         ▼                                                                                   │
│  🐳 Render builds Docker image from Dockerfile                                              │
│         │                                                                                   │
│         ▼                                                                                   │
│  ☁️ Render deploys container to cloud                                                       │
│         │                                                                                   │
│         ▼                                                                                   │
│  🌍 Public URL: https://smart-log-analyzer.onrender.com                                     │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

7. KEY COMMANDS LEARNED

| Command |	What it does |
|---------|--------------|
| git credential reject | Remove cached credentials |
| git config --global --unset credential.helper | Disable credential caching |
| git remote set-url origin https://TOKEN@github.com/... | Embed token in URL (bypasses caching) |
| git push	| Push code to GitHub (triggers CI/CD) |
| docker build -t smart-log-analyzer .	| Build Docker image |
| docker run -v $(pwd):/app/data smart-log-analyzer /app/data/sample.log --verbose	| Run container with volume mount |

---

8. TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| git push rejected with workflow scope error |	Generate new token with workflow scope |
| git credential fails on macOS	| Use embedded token in URL |
| Render says "Application exited early" |	Expected for CLI tools (--help runs and exits) |
| Build takes a long time | First build is slower due to caching |

---

9. YOUR PUBLIC URL

Live at:

```text

https://smart-log-analyzer.onrender.com
```
What it shows:

```text

usage: ingest.py [-h] [-v] [-l LIMIT] [-q {top-ips,hourly-volume,error-rate}] [-n NUM_RESULTS] filepath

```
