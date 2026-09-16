# Docker Containerization Runbook (Week 2)

This document provides complete instructions for building, configuring, and executing the **Case Management Enterprise Data Pipeline** inside Docker containers.

---

## 1. Architecture: Containerized Pipeline Execution

```mermaid
graph TD
    Host[Host Operating System] -->|docker build| Img[Docker Image: case-management-pipeline:2.0.0]
    Img -->|docker run with Volumes| Container[Containerized Pipeline Execution]
    
    subgraph Container Execution Space
        CLI[python -m pipeline.cli --mode full]
        InputMount[/app/data/input]
        RawMount[/app/data/raw]
        CuratedMount[/app/data/curated]
        RejectedMount[/app/data/rejected]
        ReportMount[/app/reports/]
        AuditMount[/app/audit/]
        
        CLI --> InputMount
        CLI --> RawMount
        CLI --> CuratedMount
        CLI --> RejectedMount
        CLI --> ReportMount
        CLI --> AuditMount
    end
    
    Container -->|Persists Output| HostDisk[Host File System: reports, curated data, audit manifests]
```

---

## 2. Docker Build Instructions

From the root directory:

```bash
docker build -t case-management-pipeline:2.0.0 .
```

### Build Characteristics:
- **Base Image:** `python:3.11-slim` (minimal attack surface, ~150MB base).
- **Non-Root User:** Runs under `appuser` (UID 1000) adhering to enterprise container security principles.
- **Layer Caching:** Dependency manifests are copied and installed before application code to accelerate rebuilds.

---

## 3. Container Execution Commands

### A. Run Full Pipeline Batch:
```bash
# On Windows PowerShell:
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/reports:/app/reports `
  -v ${PWD}/audit:/app/audit `
  case-management-pipeline:2.0.0

# On Linux / macOS:
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/audit:/app/audit \
  case-management-pipeline:2.0.0
```

### B. Run Incremental Delta Mode:
```bash
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/reports:/app/reports `
  -v ${PWD}/audit:/app/audit `
  case-management-pipeline:2.0.0 `
  python -m pipeline.cli --mode incremental
```

### C. Run Week 1 FastAPI Backend Inside Container:
```bash
docker run --rm -d `
  -p 8000:8000 `
  --name case-mgmt-api `
  case-management-pipeline:2.0.0 `
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*Access in browser:* `http://localhost:8000/docs`

---

## 4. Environment Configuration in Docker

Pass environment configuration at runtime using `-e` flags or `--env-file`:

```bash
docker run --rm `
  -e LOG_LEVEL=DEBUG `
  -e RUN_MODE=incremental `
  -v ${PWD}/data:/app/data `
  case-management-pipeline:2.0.0
```

---

## 5. Troubleshooting Docker Daemon

If you see:
```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```
**Cause:** Docker Desktop is installed on your machine but the background daemon service is not started.  
**Resolution:**
1. Launch **Docker Desktop** from your Windows Start Menu.
2. Wait until the whale icon in the Windows taskbar shows *"Docker Desktop is running"*.
3. Rerun your docker build or execution command.
