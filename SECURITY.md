# 🔒 Security Policy

## 🛡️ Supported Versions

We release security patches for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

---

## 🚨 Reporting a Vulnerability

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report security issues privately:

1. **GitHub Security Advisories**: [Create a security advisory](https://github.com/vitorpixel-6436/partmart-boost/security/advisories/new)
2. **Email**: vitorleitye6436@gmail.com
   - Subject: `[SECURITY] PartMart Boost Vulnerability`
   - Include: Version, steps to reproduce, impact assessment

**Response time:**
- Initial response: Within 48 hours
- Fix timeline: Critical issues within 7 days, others within 30 days

---

## 🔍 Security Measures in PartMart Boost

### 1. 💾 **Database Security**

**✅ SQL Injection Prevention:**
- All database queries use **parameterized statements**
- No string concatenation for SQL queries
- Input validation before database operations

```python
# ✅ SAFE
cursor.execute(
    "SELECT * FROM profiles WHERE gpu_name = ?",
    (gpu_name,)
)

# ❌ UNSAFE (not used in our code)
cursor.execute(f"SELECT * FROM profiles WHERE gpu_name = '{gpu_name}'")
```

**✅ Path Traversal Prevention:**
- Database paths validated with `_get_safe_db_path()`
- No `..` or path separators allowed in filenames
- All data stored in safe `data/` directory

```python
# Blocks: "../../../etc/passwd", "/etc/passwd", "C:\\Windows\\System32"
```

**✅ Size Limits:**
- Database capped at 10MB
- Maximum 1000 records (auto-cleanup)
- Prevents DoS via disk exhaustion

### 2. 📝 **File System Security**

**Protected directories:**
```
data/          # User data (in .gitignore)
logs/          # Log files (in .gitignore)
config/        # Configuration (in .gitignore)
```

**.gitignore protection:**
- No sensitive files committed to Git
- No API keys, tokens, or credentials in code
- No user data or logs in repository

### 3. 🔐 **Input Validation**

**All user inputs validated:**
- String length limits (prevent buffer overflow)
- Type checking (dict, int, float expected types)
- Character whitelisting (alphanumeric only for file names)

```python
# Sanitize inputs
opt_type = str(opt_type)[:100]  # Max 100 chars
notes = str(notes)[:500]        # Max 500 chars
```

### 4. 🛠️ **Privilege Escalation Prevention**

**No admin rights required:**
- Application runs with user privileges
- No registry modifications (Windows)
- No system file access

**GPU/RAM control:**
- Uses safe libraries (`pynvml`, `psutil`)
- No direct hardware access
- No kernel-level operations

### 5. 🌐 **Network Security**

**Minimal network usage:**
- Only GitHub API for updates (HTTPS only)
- No telemetry or analytics
- No user data sent externally

**Future features (v0.4+):**
- Certificate pinning for updates
- Signed releases
- Checksum verification

### 6. 📦 **Dependency Security**

**Vetted dependencies:**
```
PyQt6>=6.8.0           # Official Qt bindings
psutil>=7.0.0          # Well-maintained, 10+ years
nvidia-ml-py>=12.560   # Official NVIDIA library
scikit-learn>=1.6.0    # Trusted ML library
```

**No suspicious packages:**
- No unmaintained libraries
- No typosquatting packages
- Regular dependency updates

**Check vulnerabilities:**
```bash
pip install safety
safety check -r requirements.txt
```

---

## 📝 Security Changelog

### v0.3.4 (2026-01-28) - SECURITY PATCH 1

**✅ Fixed:**
- Added `.gitignore` to prevent sensitive file leaks
- Removed obsolete `prototype_test.py`
- Hardened `ai_optimizer.py`:
  - Path traversal prevention
  - Input validation and sanitization
  - Database size limits enforced
  - All queries parameterized
- Added `SECURITY.md` documentation

**✅ Improvements:**
- Modular monitor architecture (easier auditing)
- Comprehensive error handling
- Logging system for security events

### v0.3.3 (2026-01-28)

**✅ Fixed:**
- Removed PowerShell commands (potential code injection)
- Graceful error handling everywhere

---

## ✅ Security Best Practices (for Contributors)

### 1. **Never Commit Secrets**
```bash
# Check before committing
git diff --cached

# Remove accidentally committed secrets
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret" \
  --prune-empty --tag-name-filter cat -- --all
```

### 2. **Use Parameterized Queries**
```python
# ✅ GOOD
cursor.execute("SELECT * FROM table WHERE id = ?", (user_id,))

# ❌ BAD
cursor.execute(f"SELECT * FROM table WHERE id = {user_id}")
```

### 3. **Validate All Inputs**
```python
def process_user_input(data: str) -> str:
    # Validate type
    if not isinstance(data, str):
        raise ValueError("Expected string")
    
    # Limit length
    data = data[:500]
    
    # Sanitize
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.')
    if not all(c in allowed_chars for c in data):
        raise ValueError("Invalid characters")
    
    return data
```

### 4. **Fail Securely**
```python
try:
    result = risky_operation()
except Exception as e:
    # Log error
    logger.error(f"Operation failed: {e}")
    # Return safe default (don't expose internals)
    return None  # or empty dict, etc.
```

### 5. **Limit Resource Usage**
```python
# Prevent DoS
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_RECORDS = 1000
MAX_STRING_LENGTH = 500
```

---

## 🔍 Security Audit Checklist

Before each release, verify:

- [ ] No hardcoded credentials or API keys
- [ ] All SQL queries use parameterized statements
- [ ] File paths validated (no path traversal)
- [ ] Input validation on all user inputs
- [ ] Resource limits enforced (file size, record count)
- [ ] Error messages don't expose sensitive info
- [ ] Dependencies up-to-date
- [ ] No `eval()`, `exec()`, or `os.system()` with user input
- [ ] Logs don't contain sensitive data
- [ ] `.gitignore` includes all sensitive files

**Run security checks:**
```bash
# Check for known vulnerabilities
pip install safety
safety check

# Static analysis
pip install bandit
bandit -r src/

# Dependency audit
pip install pip-audit
pip-audit
```

---

## 📚 Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [SQLite Security](https://www.sqlite.org/security.html)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

## ⚖️ License

Security policy is part of PartMart Boost and follows the same [MIT License](LICENSE).
