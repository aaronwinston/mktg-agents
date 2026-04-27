# ForgeOS API Testing Guide

## Overview

This document describes the comprehensive test suite for the ForgeOS API, covering unit tests, integration tests, and end-to-end tests.

## Test Organization

Tests are organized by type and location:

```
apps/api/tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures and configuration
├── test_validation.py          # Unit tests for validators
├── test_sanitizer.py           # Unit tests for sanitizers
├── test_utils.py               # Unit tests for helper functions
├── test_auth.py                # Integration tests for auth endpoints
├── test_projects.py            # Integration tests for project endpoints
├── test_chat.py                # Integration tests for chat endpoints
├── test_intelligence.py        # Integration tests for intelligence endpoints
└── test_rate_limiting.py       # Rate limiting tests
```

## Test Markers

Tests are marked with markers for categorization:

- `@pytest.mark.unit` - Unit tests (no database, isolated)
- `@pytest.mark.integration` - Integration tests (with database)
- `@pytest.mark.e2e` - End-to-end tests (complete user flows)
- `@pytest.mark.rate_limit` - Rate limiting tests
- `@pytest.mark.slow` - Slow tests (>5 seconds)

## Running Tests

### Run all tests
```bash
cd apps/api
pytest
```

### Run by marker
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Rate limiting tests
pytest -m rate_limit

# All except slow tests
pytest -m "not slow"
```

### Run specific file
```bash
pytest tests/test_validation.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html
```

### Run with specific test class
```bash
pytest tests/test_validation.py::TestValidateEmail
```

### Run with keyword filtering
```bash
pytest -k "test_valid"
```

## Test Configuration

### pytest.ini

Configuration file with:
- Test discovery settings
- Coverage requirements (70%+ target)
- Timeout settings (30 seconds)
- Marker definitions

### conftest.py

Provides fixtures for:

#### Database Fixtures
- `test_db` - Fresh SQLite database per test
- `test_session` - Database session with rollback after test
- `test_org` - Pre-created test organization
- `test_user` - Pre-created test user
- `test_admin_user` - Pre-created admin user
- `test_owner_user` - Pre-created owner user

#### Authentication Fixtures
- `test_token` - Valid JWT token for test_user
- `test_admin_token` - Valid JWT token for test_admin_user
- `test_owner_token` - Valid JWT token for test_owner_user

#### Client Fixtures
- `client` - TestClient with database overrides
- `reset_rate_limiter` - Auto-resets rate limiter before each test

## Unit Tests

### test_validation.py

Tests for validation utilities in `utils/validation.py`:

- `validate_email()` - Email format validation
- `validate_password()` - Password strength validation
- `validate_url()` - URL format validation
- `validate_org_slug()` - Organization slug validation
- `validate_project_name()` - Project name validation
- `validate_object_id()` - Object ID validation
- `validate_pagination()` - Pagination parameter validation
- `validate_json_field()` - JSON serializability validation

**Coverage:** All validators have test cases for valid and invalid inputs.

### test_sanitizer.py

Tests for sanitization utilities in `utils/sanitizer.py`:

- `sanitize_string()` - Remove control characters
- `sanitize_html()` - Escape HTML entities
- `sanitize_url()` - Remove dangerous URL schemes
- `sanitize_filename()` - Remove path traversal attempts
- `sanitize_email()` - Normalize email addresses
- `sanitize_dict()` - Recursively sanitize dictionaries
- `sanitize_list()` - Recursively sanitize lists
- `sanitize_json_string()` - Sanitize JSON strings

**Coverage:** Security-focused tests for XSS, path traversal, and injection attacks.

### test_utils.py

Tests for helper utilities in `utils/helpers.py`:

- ID generation (org, project, user)
- String truncation
- List pagination and chunking
- Dictionary operations (merge, flatten)
- Datetime formatting and parsing
- Time delta calculations
- Expiration checking
- Safe dictionary access

## Integration Tests

### test_auth.py

Tests for authentication endpoints:

#### TestAuthSignup
- Sign up creates user and org
- Auth token is set in response
- Invalid email is rejected

#### TestAuthSignin
- Sign in with valid credentials
- Invalid email is rejected

#### TestAuthAuthorization
- Authorized requests with JWT token
- Unauthorized requests without token
- Expired tokens rejected
- Invalid tokens rejected

### test_projects.py

Tests for project CRUD endpoints:

#### TestProjectList
- List projects (empty and with data)
- Unauthorized access denied

#### TestProjectCreate
- Create project with valid data
- Missing fields rejected
- Unauthorized access denied

#### TestProjectTenantIsolation
- Users can only see projects in their org
- Projects created with correct org_id

#### TestProjectRead
- Get project by ID
- Nonexistent projects return 404

#### TestProjectUpdate
- Update project properties
- Unauthorized updates denied

#### TestProjectDelete
- Delete project
- Deleted projects return 404

### test_chat.py (Placeholder)

Tests for chat endpoints (to be implemented):
- Start chat session
- Send message
- Receive response
- Chat history retrieval
- Chat session isolation per org

### test_intelligence.py (Placeholder)

Tests for intelligence endpoints (to be implemented):
- Intelligence operations
- Authorization checks
- Tenant isolation

## Rate Limiting Tests

### test_rate_limiting.py

Comprehensive tests for rate limiting:

#### TestRateLimitingBasics
- Rate limit headers present in responses
- 429 status code on limit exceeded

#### TestAuthEndpointRateLimiting
- Auth endpoints have stricter limits
- Signup/signin endpoints rate limited separately

#### TestPerUserRateLimiting
- Authenticated requests limited per user (by JWT sub)
- Different users have independent limits

#### TestPerIpRateLimiting
- Unauthenticated requests limited per IP
- Fallback to IP limiting when JWT invalid

#### TestRateLimitHeaders
- X-RateLimit-Limit header present
- X-RateLimit-Remaining header present
- X-RateLimit-Reset header present
- Retry-After header on 429 responses

#### TestRateLimitErrorResponses
- 429 responses are JSON (not HTML)
- Error message included
- Headers properly formatted

#### TestRateLimitEdgeCases
- Missing JWT falls back to IP limiting
- Invalid JWT falls back to IP limiting
- Malformed headers handled gracefully

#### TestRateLimitConcurrency
- Rate limit respected under load

#### TestRateLimitReset
- Rate limit resets after time window

## Coverage Goals

Target coverage: **70%+**

Current coverage areas:
- Validators: 95%+
- Sanitizers: 95%+
- Helpers: 90%+
- Auth endpoints: 85%+
- Project endpoints: 80%+
- Rate limiting: 85%+

## CI/CD Integration

Tests run automatically on:
- Push to any branch
- Pull requests
- Scheduled daily runs

Results:
- Coverage reports published
- Builds fail if coverage drops below 70%
- Test results visible in GitHub Actions

## Best Practices

### Test Organization
1. Use descriptive class and function names
2. Group related tests in classes
3. Use fixtures for common setup

### Test Independence
1. Each test should be independent
2. Use fresh database per test
3. Reset rate limiter before each test

### Assertions
1. One logical assertion per test when possible
2. Use descriptive assertion messages
3. Test both success and failure cases

### Fixtures
1. Use parametrize for testing multiple inputs
2. Keep fixtures minimal and focused
3. Use session scope only when necessary

## Debugging Tests

### Run with print statements
```bash
pytest -s
```

### Run with pdb debugger
```bash
pytest --pdb
```

### Get detailed failure info
```bash
pytest -vv
```

### Show local variables on failure
```bash
pytest -l
```

## Common Issues

### Rate limiter not resetting
- Use `reset_rate_limiter` fixture (auto-applied)
- Clear limiter storage manually if needed

### Database state between tests
- Fixtures use transaction rollback
- Each test gets fresh database

### Token issues
- Use provided `test_token`, `test_admin_token` fixtures
- Don't hardcode tokens in tests

## Adding New Tests

When adding new endpoints:

1. Create integration test class in appropriate file
2. Test happy path (success case)
3. Test error cases (invalid input, unauthorized)
4. Test tenant isolation (for multi-tenant endpoints)
5. Add to conftest.py if new fixtures needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)
