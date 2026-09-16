# Lab 20: Containerized Pipeline Execution with Docker Bind Mounts

## Objective
Build the production multi-stage Docker container and execute the data pipeline with volume mounts for persistent data outputs.

---

## Exercise

1. Build the Docker Image (requires Docker Desktop / daemon running):
```bash
docker build -t case-management-pipeline:1.0.0 .
```

2. Inspect image size and non-root user:
```bash
docker image inspect case-management-pipeline:1.0.0 --format='{{.Config.User}}'
# Should output: appuser
```

3. Run the pipeline inside the container with bind mounts:
```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/audit:/app/audit \
  case-management-pipeline:1.0.0 \
  --mode full
```

4. Verify on Host:
   Inspect `reports/reconciliation/` and `audit/` on your host machine to confirm that reports and manifests were written directly to your host disk by the container!

---

## Troubleshooting
If Docker Desktop is not running:
- Start Docker Desktop from the Windows Start menu.
- Ensure the Linux WSL2 backend is active (`wsl --status`).
- Review `docs/week2/docker-execution.md` for detailed command flags.
