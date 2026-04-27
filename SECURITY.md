# Security Policy & Vulnerability Disclosure

**Last Updated:** April 2024  
**Status:** Production-Ready  
**Next Review:** July 2024

---

## 1. Reporting Security Vulnerabilities

If you discover a security vulnerability in ForgeOS, **please report it responsibly** to avoid public disclosure of the issue.

### Reporting Process

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. **Email:** security@forgeos.dev with:
   - Vulnerability description
   - Affected components/endpoints
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if available)
3. **Response Time:** We aim to respond within 48 hours
4. **Timeline:** Critical vulnerabilities will be patched within 24-48 hours; high-priority within 1 week

### Responsible Disclosure

- Allow 90 days for patches before public disclosure
- Credit the researcher in security advisory (optional)
- Coordinate public disclosure timing with ForgeOS team
- Follow coordinated vulnerability disclosure practices

---

## 2. Security Architecture

### Authentication & Authorization

#### JWT Token Handling (P1.1)
- **Signature Verification:** ✅ ENABLED
  - Uses RS256 asymmetric signing with Clerk's public keys
  - Invalid signatures are rejected with 401 Unauthorized
  - Forged tokens cannot bypass authentication

- **Token Validation:**
  ```
  ✅ Signature verification (CRITICAL)
  ✅ Expiration enforcement (active exp claim check)
  ✅ Issuer validation (matches Clerk issuer)
  ✅ Audience validation (matches application)
  ✅ No signature bypass (verify_signature=True)
  ```

- **Token Storage (Frontend):**
  - **DO NOT** store tokens in localStorage (XSS vulnerability)
  - **MUST** use httpOnly, secure cookies
  - **SameSite=Strict** prevents CSRF/token leakage

#### Tenant Isolation (P1.2)
- **Org-Based Multi-Tenancy:**
  ```
  ✅ All endpoints filter by org_id from auth context
  ✅ Users cannot query across organizations
  ✅ DELETE operations verify org ownership
  ✅ Chat sessions scoped to org
  ✅ Files scoped to org/project
  ```

- **Database Constraints:**
  ```sql
  -- Verify org_id in WHERE clauses for all queries
  SELECT * FROM projects WHERE org_id = ? AND id = ?
  DELETE FROM projects WHERE org_id = ? AND id = ?
  ```

#### Authorization Model
- **Role-Based Access Control (RBAC):**
  - `owner` - Full access to org resources
  - `member` - Read/write projects and chat
  - `viewer` - Read-only access
  
- **Role Enforcement:**
  ```python
  @require_role("owner")
  def delete_project(project_id, auth: AuthContext):
      # Only owner can delete
      pass
  ```

### CORS & CSRF Protection

#### CORS (Cross-Origin Resource Sharing)
- **Allowed Origins:** Explicitly configured (NOT wildcard)
- **Credentials:** Enabled with restricted origins
- **Methods:** Limited to GET, POST, PUT, DELETE, OPTIONS
- **Headers:** Whitelist specific headers

```python
# apps/api/main.py
CORSMiddleware(
    allow_origins=settings.CORS_ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["authorization", "content-type"],
)
```

#### CSRF Protection
- **SameSite Cookies:** All authentication cookies use `SameSite=Strict`
- **CSRF Tokens:** Validated for state-changing operations
- **No Wildcard CORS:** Prevents attackers from making cross-origin requests

**❌ VULNERABLE:** `allow_origins=["*"]` with `allow_credentials=True`  
**✅ SECURE:** Specific origin list like `["https://app.forgeos.dev", "https://dashboard.forgeos.dev"]`

### Data Encryption

#### At Rest
- Database credentials: Environment variables, never committed
- API keys: Encrypted with `cryptography` library
- OAuth tokens: Encrypted before storage
- User passwords: Hashed with bcrypt (not stored)

#### In Transit
- **HTTPS Only:** All production connections use TLS 1.3+
- **No HTTP:** HTTP redirects to HTTPS
- **HSTS:** `Strict-Transport-Security: max-age=31536000`
- **Certificate Pinning:** Optional, available for mobile apps

### Secrets Management

#### ✅ Correct Pattern
```python
# apps/api/.env (GITIGNORED)
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET_KEY=...
ENCRYPTION_KEY=...
```

#### ❌ Incorrect Pattern (NEVER DO THIS)
```python
# ❌ WRONG: Hardcoded in code
DATABASE_URL = "postgresql://..."

# ❌ WRONG: Committed to git
# .env (committed)
SECRET_KEY = "..."
```

**Secrets Management Checklist:**
- [ ] All `.env` files in `.gitignore`
- [ ] `.env.example` has template (no real values)
- [ ] Rotate credentials quarterly
- [ ] Use AWS Secrets Manager for production
- [ ] Never log secrets in error messages

---

## 3. Vulnerability Test Coverage

### Security Test Suite (P4.6)

All vulnerabilities are tested in `apps/api/tests/test_security.py`:

#### Authentication Tests ✅
```python
test_missing_token_returns_401()          # Missing auth → 401
test_expired_token_rejected()             # Expired token → 401
test_invalid_signature_rejected()         # Wrong signature → 401
test_malformed_token_rejected()           # Invalid format → 401
```

#### Authorization Tests ✅
```python
test_user_cannot_access_other_org_projects()  # Tenant isolation
test_role_member_cannot_delete_project()      # RBAC enforcement
test_cannot_modify_other_user_data()          # Access control
```

#### Input Validation Tests ✅
```python
test_script_tags_in_project_name_rejected()   # XSS prevention
test_sql_injection_in_query_params_rejected() # SQL injection prevention
test_command_injection_in_parameters()        # Command injection prevention
test_xml_upload_safe()                        # XXE prevention
```

#### CSRF & Rate Limiting Tests ✅
```python
test_post_without_csrf_might_be_blocked()     # CSRF protection
test_rate_limit_enforced_per_user()           # Rate limiting
test_different_user_not_rate_limited_by_other() # Per-user limits
```

**Run tests:**
```bash
cd apps/api
pytest tests/test_security.py -v
# Expected: All tests PASS
```

---

## 4. Known Vulnerabilities & Mitigations

### Current Status (As of April 2024)

| Issue | Severity | Status | Mitigation |
|-------|----------|--------|-----------|
| JWT signature verification | CRITICAL | ✅ FIXED (P1.1) | RS256 with Clerk keys |
| Tenant isolation bypass | CRITICAL | ✅ FIXED (P1.2) | org_id in all queries |
| Hardcoded user "aaron" | CRITICAL | ✅ FIXED (P1.2) | Dynamic user context |
| CORS wildcard + credentials | CRITICAL | ✅ FIXED (P1.3) | Explicit origin list |
| Secrets in repository | CRITICAL | ✅ FIXED (P1.4) | .env in .gitignore |
| Tokens in localStorage | HIGH | ✅ FIXED (P3.2) | httpOnly cookies |
| Missing rate limiting | HIGH | ✅ FIXED (P2.4) | slowapi + per-user limits |

### Historical Issues

**None currently outstanding.** All critical vulnerabilities from Phase 1 have been remediated and verified.

---

## 5. Security Best Practices for Developers

### Code Guidelines

#### ✅ DO

1. **Always validate input:**
   ```python
   from pydantic import BaseModel, constr
   
   class ProjectInput(BaseModel):
       name: constr(min_length=1, max_length=255)
       description: constr(max_length=2000)
   ```

2. **Always filter by org_id:**
   ```python
   @router.get("/projects")
   def list_projects(auth: AuthContext = Depends(get_current_user)):
       db_projects = session.query(Project).filter(
           Project.organization_id == auth.org_id  # ← REQUIRED
       ).all()
       return db_projects
   ```

3. **Use parameterized queries:**
   ```python
   # ✅ CORRECT - SQLAlchemy automatically parameterizes
   query = session.query(User).filter(User.email == user_email)
   
   # ❌ WRONG - SQL injection vulnerability
   query = session.execute(f"SELECT * FROM users WHERE email = '{user_email}'")
   ```

4. **Sanitize HTML output:**
   ```python
   from bleach import clean
   
   safe_html = clean(
       user_input,
       tags=['b', 'i', 'u', 'p'],
       strip=True
   )
   ```

5. **Log security events:**
   ```python
   logger.warning(
       "Unauthorized access attempt",
       extra={
           "user_id": user_id,
           "org_id": org_id,
           "resource": resource_id,
           "action": "DELETE"
       }
   )
   ```

#### ❌ DON'T

1. **Never use `verify_signature=False`:**
   ```python
   # ❌ WRONG
   payload = jwt.decode(token, options={"verify_signature": False})
   ```

2. **Never trust client input without validation:**
   ```python
   # ❌ WRONG
   delete_statement = f"DELETE FROM projects WHERE id = {project_id}"
   ```

3. **Never concatenate SQL:**
   ```python
   # ❌ WRONG
   query = session.execute(f"SELECT * FROM projects WHERE name = '{name}'")
   ```

4. **Never hardcode secrets:**
   ```python
   # ❌ WRONG
   ENCRYPTION_KEY = "super-secret-key-abc123"
   ```

5. **Never log sensitive data:**
   ```python
   # ❌ WRONG
   logger.info(f"User logged in: {email}, password: {password}")
   ```

6. **Never skip org_id validation:**
   ```python
   # ❌ WRONG - Anyone can access anyone's projects
   @router.get("/projects/{project_id}")
   def get_project(project_id: str):
       return session.query(Project).filter(Project.id == project_id).first()
   ```

### Security Testing Checklist

Before pushing code:

- [ ] **Authentication:** Token validation tests pass
- [ ] **Authorization:** Org isolation verified
- [ ] **Input Validation:** XSS/SQLi tests pass
- [ ] **CORS:** Only allowed origins configured
- [ ] **Secrets:** No credentials in code/commits
- [ ] **Logging:** No sensitive data logged
- [ ] **Dependencies:** No known CVEs (`npm audit`, `pip-audit`)

### Dependency Management

#### Keep Dependencies Updated
```bash
# Python
pip-audit  # Check for known vulnerabilities
pip install --upgrade pip setuptools

# Node.js
npm audit
npm audit fix
npm outdated
```

#### Lock Versions
```
# Always commit lock files to git
package-lock.json
poetry.lock
requirements.txt (with pinned versions)
```

---

## 6. Compliance & Standards

### Security Standards Met

- **OWASP Top 10 2021:** All mitigations implemented
  - A01: Broken Access Control ✅
  - A02: Cryptographic Failures ✅
  - A03: Injection ✅
  - A04: Insecure Design ✅
  - A05: Security Misconfiguration ✅
  - A06: Vulnerable Components ✅
  - A07: Authentication Failures ✅
  - A08: Data Integrity Failures ✅
  - A09: Logging & Monitoring ✅
  - A10: SSRF ✅

- **NIST Cybersecurity Framework:** 
  - Identify ✅ (asset inventory, threats)
  - Protect ✅ (access control, encryption)
  - Detect ✅ (monitoring, audit logs)
  - Respond ✅ (incident procedures)
  - Recover ✅ (backups, disaster recovery)

### Audit Trail (P2.3)

All security-relevant actions are logged:
```python
# Automatic audit logging via SQLAlchemy hooks
class AuditLog(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    action: str  # CREATE, READ, UPDATE, DELETE
    resource_type: str  # Project, User, etc.
    resource_id: str
    user_id: str
    org_id: str
    timestamp: datetime
    changes: dict  # Before/after for updates
```

---

## 7. Incident Response Plan

### Discovery
1. Verify vulnerability independently
2. Document steps to reproduce
3. Assess severity and impact

### Triage (within 24 hours)
- **Critical (CVSS 9-10):** Drop all features, fix immediately
- **High (CVSS 7-8):** Fix within 24-48 hours
- **Medium (CVSS 4-6):** Fix within 1 week
- **Low (CVSS 0-3):** Fix in next release

### Remediation
1. Develop fix in private branch
2. Write test that reproduces issue
3. Fix code
4. Verify test passes
5. Code review by security team
6. Deploy to production

### Communication
1. Notify affected users (if data exposed)
2. Post security advisory on GitHub
3. Update SECURITY.md with mitigation
4. Credit researcher (with permission)

---

## 8. Security Monitoring & Logging

### Log Types

```
SECURITY LOGS:
- Authentication attempts (success/failure)
- Authorization failures (403 responses)
- Admin actions (org creation, user deletion)
- Data access patterns (suspicious queries)
- API abuse (rate limit violations)
- Configuration changes (secrets rotation)
```

### Monitoring Dashboards

- **Failed Login Attempts:** Alert if >5 failures per user in 15 minutes
- **Unauthorized Access:** Alert on any 403 errors
- **Rate Limit Violations:** Track by user/IP
- **Dependency Vulnerabilities:** Weekly scan

### Log Retention

- **Development:** 7 days
- **Staging:** 30 days
- **Production:** 90 days (compliant with regulations)
- **Audit Trail:** 1 year

---

## 9. Third-Party Security Services

### Integrations

- **Clerk:** JWT & OAuth2 provider
  - SAML/SSO ready
  - Enterprise-grade security
  
- **GitHub:** Source code hosting
  - Branch protection
  - Dependabot for dependency updates
  
- **Arize AX:** Observability & tracing
  - Request/response logging
  - Performance monitoring

### Scanning Tools

- **OWASP ZAP:** Automated vulnerability scanning
- **npm audit / pip-audit:** Dependency vulnerability scanning
- **SonarQube:** Code quality & security analysis (optional)

---

## 10. Frequently Asked Questions

### Q: How do I report a vulnerability?
A: Email security@forgeos.dev with details. Do not open public GitHub issues.

### Q: Are my tokens secure?
A: Yes. Tokens are:
- Signed with RS256 (public key verification)
- Stored in httpOnly cookies (XSS protection)
- Validated on every request
- Expiration enforced

### Q: Can I use the API with a custom token?
A: No. Tokens must be issued by Clerk's authentication service. Self-generated tokens will be rejected.

### Q: How often are dependencies updated?
A: Security patches are applied immediately. Feature updates quarterly.

### Q: Is end-to-end encryption supported?
A: Not currently, but all data is encrypted in transit (TLS) and at rest (database encryption).

### Q: How do I rotate credentials?
A: Contact operations@forgeos.dev. Rotation happens quarterly for production credentials.

---

## 11. Change Log

### Version 1.0 (April 2024)
- ✅ JWT signature verification enabled (P1.1)
- ✅ Tenant isolation enforced (P1.2)
- ✅ CORS configured with explicit origins (P1.3)
- ✅ Secrets management implemented (P1.4)
- ✅ Rate limiting per user (P2.4)
- ✅ Audit logging (P2.3)
- ✅ Security test suite created (P4.6)
- ✅ Security documentation published

### Future (v1.1+)
- [ ] FIDO2/WebAuthn support
- [ ] Passwordless authentication
- [ ] Advanced threat detection
- [ ] Bug bounty program

---

## Contact

**Security Team:** security@forgeos.dev  
**Incident Response:** +1-800-FORGEOS-1  
**GitHub Security Advisory:** https://github.com/forgeos/forgeos/security/advisories

**Last Updated:** April 27, 2024  
**Next Review:** July 27, 2024
