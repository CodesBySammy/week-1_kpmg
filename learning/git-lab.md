# Git Practical Lab: Feature Branching, Conflict Resolution & History Auditing

## Lab Objective
In this hands-on lab, you will step through the exact workflow professional backend engineers use every day. You will:
1. Initialize a repository with appropriate ignore rules
2. Create and switch to a feature branch
3. Implement and commit atomic changes using Conventional Commits
4. Create a competing branch to intentionally trigger a merge conflict
5. Resolve the merge conflict manually, inspect the diff, and commit the resolution
6. Verify and audit the commit graph using `git log`

---

## Prerequisites
- Git installed (`git --version` >= 2.30)
- Command line terminal (PowerShell or Bash)

---

## Step-by-Step Instructions

### Step 1: Create a Sandbox Directory and Initialize Git
Do not do this in your main production folder; let's create a temporary sandbox to practice safely.

```bash
# Create and navigate to sandbox
mkdir git-practice-lab
cd git-practice-lab

# Initialize new Git repository
git init -b main

# Configure your identity (if not globally configured)
git config user.name "Fresher Engineer"
git config user.email "fresher@example.com"
```

### Step 2: Establish the Initial Commit and .gitignore
Create a standard `.gitignore` and an initial project file.

```bash
# Create .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "*.db" >> .gitignore

# Create a sample service file
cat << 'EOF' > service.py
def calculate_sla_hours(priority: str) -> int:
    """Calculates resolution SLA hours based on priority."""
    if priority == "CRITICAL":
        return 4
    elif priority == "HIGH":
        return 8
    return 24
EOF

# Stage and commit
git add .gitignore service.py
git commit -m "feat(service): initialize SLA calculation service"
```

### Step 3: Create a Feature Branch
Now simulate a feature request: *"Add LOW priority SLA support"*.

```bash
# Create and switch to a new feature branch
git switch -c feat/CM-101-low-priority-sla

# Edit service.py to add LOW priority
cat << 'EOF' > service.py
def calculate_sla_hours(priority: str) -> int:
    """Calculates resolution SLA hours based on priority."""
    if priority == "CRITICAL":
        return 4
    elif priority == "HIGH":
        return 8
    elif priority == "LOW":
        return 48
    return 24
EOF

# Stage and commit on the feature branch
git add service.py
git commit -m "feat(service): add 48-hour SLA for LOW priority cases"
```

### Step 4: Create a Competing Branch on `main` to Trigger Conflict
While your feature branch was being developed, another engineer updated `main` to modify the default return value and add MEDIUM priority:

```bash
# Switch back to main
git switch main

# Modify the same file in a conflicting way
cat << 'EOF' > service.py
def calculate_sla_hours(priority: str) -> int:
    """Calculates resolution SLA hours based on priority."""
    if priority == "CRITICAL":
        return 4
    elif priority == "HIGH":
        return 8
    elif priority == "MEDIUM":
        return 16
    return 72  # Changed default SLA to 72 hours
EOF

# Commit directly on main
git add service.py
git commit -m "feat(service): add MEDIUM priority SLA and update default"
```

### Step 5: Attempt the Merge and Observe the Conflict
Now, attempt to merge your feature branch `feat/CM-101-low-priority-sla` into `main`:

```bash
git merge feat/CM-101-low-priority-sla
```

**Observed Terminal Output:**
```text
Auto-merging service.py
CONFLICT (content): Merge conflict in service.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Step 6: Inspect and Resolve the Conflict
Open `service.py` in your editor or inspect it in the terminal:
```bash
git diff
```

You will see the Git conflict markers:
```python
<<<<<<< HEAD
    elif priority == "MEDIUM":
        return 16
    return 72  # Changed default SLA to 72 hours
=======
    elif priority == "LOW":
        return 48
    return 24
>>>>>>> feat/CM-101-low-priority-sla
```

#### How to Resolve:
Reconcile both features by combining them logically:
```python
def calculate_sla_hours(priority: str) -> int:
    """Calculates resolution SLA hours based on priority."""
    if priority == "CRITICAL":
        return 4
    elif priority == "HIGH":
        return 8
    elif priority == "MEDIUM":
        return 16
    elif priority == "LOW":
        return 48
    return 72
```

### Step 7: Finalize the Merge
```bash
# Stage the resolved file
git add service.py

# Complete the merge commit
git commit -m "merge: resolve SLA priority conflicts between main and feat/CM-101"
```

### Step 8: Audit Git History and Visual Graph
Inspect the Git DAG (Directed Acyclic Graph):

```bash
git log --graph --oneline --all --decorate
```

**Expected Result:**
```text
*   2d4f8a1 (HEAD -> main) merge: resolve SLA priority conflicts between main and feat/CM-101
|\  
| * a9c1e34 (feat/CM-101-low-priority-sla) feat(service): add 48-hour SLA for LOW priority cases
* | f7b2901 feat(service): add MEDIUM priority SLA and update default
|/  
* 81e05d2 feat(service): initialize SLA calculation service
```

### Step 9: Clean Up the Branch
Once merged, feature branches should be deleted to prevent branch clutter:
```bash
git branch -d feat/CM-101-low-priority-sla
```

---

## Verification Checklist
- [x] Initial commit created on `main`
- [x] Feature branch created and committed to
- [x] Competing commit created on `main`
- [x] Conflict encountered during merge
- [x] Conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) inspected and removed
- [x] Merged commit verified with `git log --graph`
