# Security Policy

**Version:** 0.3.5d+patch5

## Supported Versions

| Version | Supported |
|---------|----------|
| 0.4.x | ✅ Yes |
| 0.3.5d+ | ✅ Yes |
| < 0.3.5 | ❌ No |

## Quick Security Guide

### Safe Usage

✅ **Do:**
- Download from official GitHub releases
- Verify checksums (when provided)
- Run with normal user permissions
- Keep Python and dependencies updated
- Report security issues privately

❌ **Don't:**
- Run as administrator/root (not needed)
- Install from unofficial sources
- Modify system files
- Share logs with sensitive data

### Privacy

**What we collect:** Nothing
- No telemetry
- No analytics
- No crash reports sent
- All data stays local

**What we access:**
- System performance metrics (CPU, GPU, RAM)
- Process information (only for monitoring)
- Temperature sensors (read-only)
- Power state (read-only)

### Permissions Required

**Windows:**
- Read system metrics
- Create files in installation directory
- Network: None

**Linux:**
- Read `/sys` filesystem
- Read `/proc` filesystem
- No special capabilities needed

## Reporting a Vulnerability

### Private Disclosure

Please report security vulnerabilities privately:

1. **GitHub Security Advisories:**
   - Go to: https://github.com/vitorpixel-6436/partmart-boost/security/advisories
   - Click "Report a vulnerability"

2. **Direct Contact:**
   - Create a private issue
   - Mark as "Security"
   - We'll respond within 48 hours

### What to Include

- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial Assessment:** Within 7 days
- **Fix Released:** Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next release

## Security Features

### Input Validation

- All user input validated
- Type checking enforced
- Range checking on numeric values
- Path traversal protection

### Memory Safety

- Bounds checking on arrays
- No buffer overflows
- Proper resource cleanup
- No unsafe memory operations

### Thread Safety

- Lock-based synchronization
- Atomic operations where needed
- No data races
- Deadlock prevention

### Error Handling

- Graceful error recovery
- No sensitive data in errors
- Proper exception handling
- Safe failure modes

## Security Best Practices

### Installation

```bash
# Verify you're downloading from official repo
git clone https://github.com/vitorpixel-6436/partmart-boost.git

# Check remote
git remote -v

# Install in virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Running

```bash
# Run as normal user (not root/admin)
python src/main.py

# Or use CLI
python src/main_cli.py
```

### Updates

```bash
# Pull latest changes
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Check version
cat VERSION
```

## Known Security Considerations

### Low Risk

1. **System Metrics Access:**
   - Read-only access to system info
   - Standard OS APIs used
   - No sensitive data exposed

2. **Configuration Files:**
   - Stored in user directory
   - No credentials stored
   - Plain text (no encryption needed)

### No Risk

- No network communication
- No code execution from external sources
- No privilege escalation
- No system modification

## Dependencies

### Core Dependencies

- **NumPy:** Widely audited, mature library
- **PyQt6:** Established GUI framework

### Security Updates

We monitor dependencies for vulnerabilities:
- Regular updates
- Security advisories tracked
- Quick patching when needed

### Dependency Verification

```bash
# Check for known vulnerabilities
pip install safety
safety check

# Or use pip-audit
pip install pip-audit
pip-audit
```

## Compliance

### Data Protection

- **GDPR:** N/A (no data collection)
- **CCPA:** N/A (no data collection)
- **SOC 2:** Not applicable

### Open Source

- **License:** MIT
- **Source:** Fully open
- **Audit:** Community reviewed

## Security Checklist

Before each release:

- [ ] All dependencies updated
- [ ] Security audit completed
- [ ] Input validation reviewed
- [ ] Memory safety checked
- [ ] Thread safety verified
- [ ] Error handling tested
- [ ] Documentation updated

## Contact

- **Security Issues:** Use GitHub Security Advisories
- **General Questions:** Open a public issue
- **Other:** See README.md

## Acknowledgments

We thank security researchers who help keep PartMart Boost secure.

### Hall of Fame

(None yet - be the first!)

---

**Stay Safe!**

Remember:
- Keep software updated
- Don't run as admin
- Report issues privately
- Trust but verify
