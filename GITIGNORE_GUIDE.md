# .gitignore Guide

This document explains what files are ignored and why across the project.

## File Structure

```
somehow-smartbridge-hackathon/
├── .gitignore                    # Root-level ignores
├── backend/.gitignore            # Backend-specific ignores
└── frontend/.gitignore           # Frontend-specific ignores
```

## What's Being Ignored

### 1. Virtual Environments
**Ignored:** `venv/`, `.venv/`, `env/`, `ENV/`

**Why:** Virtual environments contain installed packages that can be recreated from `requirements.txt`. They're large and platform-specific.

**How to recreate:**
```bash
python -m venv venv
pip install -r requirements.txt
```

---

### 2. Environment Variables
**Ignored:** `.env`, `.env.local`, `.env.production`

**Why:** Contains sensitive configuration like API keys, secrets, and local settings. Should NEVER be committed.

**What to commit instead:**
- `.env.example` (template without sensitive data)

**Example:**
```bash
# .env (ignored)
API_KEY=sk-abc123xyz789

# .env.example (committed)
API_KEY=your_api_key_here
```

---

### 3. Python Cache Files
**Ignored:** `__pycache__/`, `*.pyc`, `*.pyo`

**Why:** Generated automatically by Python. Can be recreated and contain compiled bytecode.

---

### 4. AI Model Cache (Backend)
**Ignored:** `model_cache/`, `*.bin`, `*.safetensors`, `*.pt`

**Why:** Model files are HUGE (2-3 GB). They download automatically on first run.

**Location:** `backend/model_cache/`

**Note:** First user will download the model, which is then cached locally.

---

### 5. Logs
**Ignored:** `logs/`, `*.log`

**Why:** Log files grow over time and contain runtime information, not source code.

**Location:**
- `backend/logs/app.log`
- Any `*.log` files

---

### 6. IDE/Editor Files
**Ignored:** `.vscode/`, `.idea/`, `*.swp`

**Why:** Personal editor settings shouldn't be forced on other developers.

**Exception:** You CAN commit `.vscode/settings.json` if it contains project-specific settings that benefit all developers.

---

### 7. OS-Specific Files
**Ignored:** `.DS_Store`, `Thumbs.db`, `desktop.ini`

**Why:**
- `.DS_Store` - macOS folder metadata
- `Thumbs.db` - Windows thumbnail cache
- `desktop.ini` - Windows folder config

These are OS-specific and not needed in version control.

---

### 8. Package Manager Lock Files
**Ignored:** `uv.lock`, `poetry.lock`, `Pipfile.lock`

**Why:** Can cause conflicts across different platforms/Python versions.

**Exception:** Lock files ARE important for production deployments. Consider using them in CI/CD pipelines.

**Kept:** `requirements.txt`, `pyproject.toml`

---

### 9. Database Files
**Ignored:** `*.db`, `*.sqlite`, `*.sqlite3`

**Why:** Database files contain runtime data, not source code.

**Exception:** You might want to commit a small seed database for development.

---

### 10. Testing Artifacts
**Ignored:** `.pytest_cache/`, `.coverage`, `htmlcov/`

**Why:** Generated during test runs. Can be recreated.

---

### 11. Streamlit-Specific (Frontend)
**Ignored:** `.streamlit/secrets.toml`, `.streamlit/config.toml`

**Why:** May contain secrets or personal configuration.

**Note:** Streamlit's cache is also ignored.

---

### 12. Security-Related
**Ignored:** `*.pem`, `*.key`, `*.crt`, `secrets/`, `credentials/`

**Why:** SSL certificates, private keys, and credentials should NEVER be in version control.

---

## What's NOT Ignored (Important Files)

### Always Committed:
- ✅ `requirements.txt` - Python dependencies
- ✅ `pyproject.toml` - Project configuration
- ✅ `.env.example` - Environment template
- ✅ `.gitignore` itself
- ✅ `README.md` - Documentation
- ✅ `data/sample_transactions.json` - Sample data for development
- ✅ Source code (`.py` files)

---

## Special Cases

### Backend

**Kept:**
```
backend/data/sample_transactions.json
```
This is sample data needed for development/testing.

**Ignored:**
```
backend/model_cache/
backend/logs/
backend/venv/
backend/.env
```

### Frontend

**Kept:**
```
frontend/requirements.txt
frontend/pyproject.toml
frontend/app.py
frontend/components/
frontend/pages/
```

**Ignored:**
```
frontend/.venv/
frontend/.python-version
frontend/uv.lock
frontend/.streamlit/
```

---

## Common Mistakes to Avoid

### ❌ DON'T Commit:
1. `.env` files with real credentials
2. `venv/` or `.venv/` folders
3. Large model files (`*.bin`, `*.safetensors`)
4. Database files with real user data
5. API keys or secrets
6. `__pycache__/` folders

### ✅ DO Commit:
1. `.env.example` templates
2. `requirements.txt`
3. Source code
4. Documentation
5. Sample/seed data
6. Tests

---

## Checking What's Ignored

### See what's being ignored:
```bash
git status --ignored
```

### Check if a specific file is ignored:
```bash
git check-ignore -v filename
```

### See what will be committed:
```bash
git status
```

---

## If You Accidentally Committed Something

### Remove a file from Git (but keep it locally):
```bash
git rm --cached filename
git commit -m "Remove accidentally committed file"
```

### Remove a folder from Git:
```bash
git rm -r --cached foldername/
git commit -m "Remove accidentally committed folder"
```

### Remove sensitive data from history:
```bash
# Use git filter-branch or BFG Repo-Cleaner
# This is complex - consult git documentation
```

---

## Quick Reference

| File/Folder | Backend | Frontend | Root | Reason |
|-------------|---------|----------|------|--------|
| `venv/`, `.venv/` | ✅ | ✅ | ✅ | Large, recreatable |
| `.env` | ✅ | ✅ | ✅ | Contains secrets |
| `__pycache__/` | ✅ | ✅ | ✅ | Generated cache |
| `model_cache/` | ✅ | ❌ | ✅ | Huge AI models |
| `logs/` | ✅ | ✅ | ✅ | Runtime logs |
| `.DS_Store` | ✅ | ✅ | ✅ | OS-specific |
| `*.pyc` | ✅ | ✅ | ✅ | Compiled Python |
| `requirements.txt` | ⭕ Keep | ⭕ Keep | ⭕ Keep | Dependencies |
| `.env.example` | ⭕ Keep | ⭕ Keep | ⭕ Keep | Template |

**Legend:**
- ✅ = Ignored (not committed)
- ⭕ Keep = Committed to repository
- ❌ = Not applicable

---

## Tips for Team Collaboration

1. **Always use `.env.example`**: Commit a template, never the real `.env`
2. **Update .gitignore early**: Add patterns before accidentally committing
3. **Review before committing**: Use `git status` to check what's being committed
4. **Global .gitignore**: Consider setting up a global `.gitignore` for your OS/editor files
5. **Document exceptions**: If you need to commit something usually ignored, document why

---

## Platform-Specific Notes

### Windows
- Uses backslashes in paths, but `.gitignore` uses forward slashes
- Git automatically converts line endings
- `Thumbs.db` and `desktop.ini` are ignored

### macOS
- `.DS_Store` files are ignored
- Case-insensitive filesystem by default
- Spotlight metadata folders ignored

### Linux
- Usually case-sensitive filesystem
- Fewer OS-specific files to ignore

---

## Summary

The `.gitignore` files are configured to:
- ✅ Keep your repository clean and small
- ✅ Prevent accidental commits of sensitive data
- ✅ Avoid platform-specific conflicts
- ✅ Ensure reproducible builds
- ✅ Protect secrets and credentials

**Remember:** When in doubt, DON'T commit it. You can always add it later, but removing sensitive data from Git history is difficult.
