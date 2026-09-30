# Developer Local Setup Guide

```bash
# Clone repository
git clone <repo-url> case-management-backend
cd case-management-backend

# Initialize virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate    # Linux/macOS

# Install dependencies
pip install -e ".[dev]"

# Run full test suite to verify setup
pytest tests/
```
