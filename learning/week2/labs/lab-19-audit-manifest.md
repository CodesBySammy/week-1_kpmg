# Lab 19: Inspecting Audit Manifests & The Execution Ledger

## Objective
Inspect the forensic run manifest JSON and query the append-only JSONL execution ledger.

---

## Exercise

1. Inspect generated manifests:
```python
import json
from pathlib import Path

# Find latest manifest
manifest_files = sorted(Path("audit").glob("manifest_*.json"))
if manifest_files:
    latest = manifest_files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    print(f"=== Manifest: {latest.name} ===")
    print("Run ID:", manifest["run_id"])
    print("Execution Duration:", manifest["duration_seconds"], "seconds")
    print("Reconciliation Status:", manifest["status"])
    print("Counts Breakdown:", manifest["counts"])

# Read Execution Ledger
ledger_file = Path("audit/execution_ledger.jsonl")
if ledger_file.exists():
    print("\n=== Execution Ledger (Historic Runs) ===")
    with open(ledger_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            print(f"[{entry['timestamp']}] Run: {entry['run_id']} | Status: {entry['status']} | Curated: {entry['curated_records']}")
```

---

## Verification
- Notice how every pipeline invocation is cryptographically and historically accountable.
