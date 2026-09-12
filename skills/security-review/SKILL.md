---
name: security-review
description: Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, running subprocesses, deserializing data, or handling sensitive records. Python-specific security checklist and patterns.
metadata:
  origin: ECC, rewritten for Python
---

# Security Review Skill (Python)

Checklist and patterns for Python services, pipelines, and APIs. Each area has a FAIL/PASS pair and verification steps. Examples assume FastAPI, pydantic v2, SQLAlchemy 2.x, and psycopg; the checks apply to any stack.

## When to Activate

- Implementing authentication, sessions, or authorization
- Accepting input from HTTP, CLI, files, queues, or webhooks
- Creating or changing API endpoints
- Reading secrets or credentials
- Building SQL, shell commands, or file paths from external data
- Deserializing anything (pickle, YAML, JSON from untrusted sources, model files)
- Storing or logging personal, financial, or credential data
- Calling third-party APIs with user-supplied URLs or parameters

## 1. Secrets Management

### FAIL
```python
API_KEY = "sk-proj-xxxx"                     # in source
engine = create_engine("postgresql://app:password123@db/app")
```

### PASS
```python
from pydantic_settings import BaseSettings, SecretStr

class Settings(BaseSettings):
    openai_api_key: SecretStr
    database_url: SecretStr
    model_config = {"env_file": ".env", "extra": "forbid"}

settings = Settings()                        # raises if a required var is missing
engine = create_engine(settings.database_url.get_secret_value())
```

`SecretStr` prevents the value from appearing in `repr`, logs, and tracebacks.

### Verification
- [ ] No literals matching `(key|secret|password|token)\s*=\s*["']` in source: `rg -n "(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}"`
- [ ] Secrets read via environment or a settings class; app fails fast if missing
- [ ] `.env`, `.env.*`, `*.pem`, `*.key`, credential JSON files in `.gitignore`
- [ ] Nothing in history: `gitleaks detect` or `trufflehog git file://.`
- [ ] Production secrets injected by the platform, not baked into images

## 2. Input Validation

### PASS — schemas at every boundary
```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class CreateUser(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

@app.post("/users", status_code=201)
async def create_user(body: CreateUser):    # 422 on invalid input, before your code runs
    return await repo.create(body)
```

`extra="forbid"` rejects unexpected fields; without it, mass-assignment bugs slip through.

### PASS — file uploads
```python
MAX_BYTES = 5 * 1024 * 1024
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png"}

async def validate_upload(file: UploadFile) -> bytes:
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large")
    kind = filetype.guess(data)                          # sniff magic bytes; never trust Content-Type
    if kind is None or kind.mime not in ALLOWED:
        raise HTTPException(415, "Unsupported file type")
    return data
```

Save under a generated name (`uuid4().hex + ALLOWED[kind.mime]`); never use the client filename on disk.

### Verification
- [ ] Every request body, query param, CLI arg, and queue message parsed through a schema
- [ ] `extra="forbid"` on models that map to writes
- [ ] Uploads: size cap enforced while reading, type sniffed from bytes, server-generated filename
- [ ] Allowlists, not denylists
- [ ] Validation errors return field names, never internal exception text

## 3. Injection

### SQL — FAIL
```python
cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
session.execute(text("SELECT * FROM users WHERE email = '" + email + "'"))
```

### SQL — PASS
```python
cur.execute("SELECT * FROM users WHERE email = %s", (email,))          # psycopg
session.execute(select(User).where(User.email == email))                # SQLAlchemy ORM
session.execute(text("SELECT * FROM users WHERE email = :e"), {"e": email})  # bound param
```

Dynamic identifiers (table or column names) cannot be bound; map them through an allowlist dict before use.

### Shell — FAIL / PASS
```python
subprocess.run(f"convert {filename} out.png", shell=True)               # FAIL
subprocess.run(["convert", filename, "out.png"], check=True, timeout=30)  # PASS: list args, no shell
```

### Paths — PASS
```python
BASE = Path("/srv/uploads").resolve()

def safe_path(name: str) -> Path:
    p = (BASE / name).resolve()
    if not p.is_relative_to(BASE):
        raise ValueError("path traversal")
    return p
```

### Deserialization — FAIL / PASS
```python
obj = pickle.loads(untrusted)          # FAIL: arbitrary code execution
cfg = yaml.load(text)                  # FAIL: default Loader executes tags
cfg = yaml.safe_load(text)             # PASS
model = torch.load(path, weights_only=True)   # PASS for model files; never load untrusted pickles
```

### Verification
- [ ] No f-strings, `%`, or `+` building SQL; `bandit -r . -q` and `ruff check --select S` clean
- [ ] `subprocess` calls use list arguments, `shell=False`, and a `timeout`
- [ ] Every path built from input resolved and checked against a base directory
- [ ] No `pickle.loads`, `yaml.load` without `SafeLoader`, `eval`, or `exec` on external data
- [ ] Templates (Jinja2) autoescape on; `Markup`/`|safe` only on sanitized content

## 4. Authentication and Authorization

### Password storage — PASS
```python
from argon2 import PasswordHasher
ph = PasswordHasher()                       # argon2id defaults
hashed = ph.hash(password)
ph.verify(hashed, attempt)                  # raises on mismatch
```
Never `hashlib.sha256(password)`, never MD5, never home-rolled salts.

### Tokens — PASS
```python
import jwt
token = jwt.encode({"sub": user.id, "exp": now + timedelta(minutes=15)}, settings.jwt_secret.get_secret_value(), algorithm="HS256")
claims = jwt.decode(token, settings.jwt_secret.get_secret_value(), algorithms=["HS256"])  # always pin algorithms
```
Browser clients: set the token in an `HttpOnly; Secure; SameSite=Lax` cookie, not JS-readable storage.

### Authorization — PASS
```python
def require_role(role: str):
    def dep(user: User = Depends(current_user)):
        if role not in user.roles:
            raise HTTPException(403, "Forbidden")
        return user
    return dep

@app.delete("/users/{user_id}", dependencies=[Depends(require_role("admin"))])
async def delete_user(user_id: UUID): ...

@app.get("/orders/{order_id}")
async def get_order(order_id: UUID, user: User = Depends(current_user)):
    order = await repo.get(order_id)
    if order is None or order.owner_id != user.id:
        raise HTTPException(404)             # 404, not 403: don't confirm existence
    return order
```

### Verification
- [ ] Passwords hashed with argon2 or bcrypt; compared with the library's verify, never `==`
- [ ] JWT `algorithms=[...]` pinned on decode; short expiry; refresh handled server-side
- [ ] Every protected route has an auth dependency; every object read checks ownership (no IDOR)
- [ ] Authorization checked server-side before the operation, never only in the client
- [ ] Comparison of secrets/tokens uses `hmac.compare_digest`

## 5. Output Encoding and Browser-Facing Surfaces

Only if the service renders HTML or is called from a browser.

```python
import bleach
clean = bleach.clean(user_html, tags=["b", "i", "em", "strong", "p"], attributes={}, strip=True)
```

Response headers via middleware: `Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`. CORS: explicit `allow_origins`, never `["*"]` with credentials.

### Verification
- [ ] User-provided HTML sanitized with an allowlist
- [ ] Jinja2 autoescape enabled
- [ ] CSP set; no `'unsafe-inline'` / `'unsafe-eval'` without a documented removal plan
- [ ] CORS origins explicit
- [ ] State-changing routes require a non-GET method and, for cookie auth, a CSRF token or `SameSite=Strict`

## 6. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, body: Login): ...

@app.get("/search")
@limiter.limit("10/minute")
async def search(request: Request, q: str): ...
```

For multi-process deployments back the limiter with Redis; in-memory limits reset per worker.

### Verification
- [ ] Public endpoints limited by IP; authenticated endpoints limited by user
- [ ] Stricter limits on login, password reset, search, and anything that hits external APIs
- [ ] Shared store for limits when running more than one worker

## 7. Sensitive Data Exposure

### Logging — FAIL / PASS
```python
log.info("login", email=email, password=password)         # FAIL
log.info("login", user_id=user.id)                        # PASS
log.info("payment", last4=card.last4, user_id=user.id)    # PASS
```

Add a logging filter that redacts keys named `password`, `token`, `secret`, `authorization`, `cookie`, and card fields. Wrap secrets in `SecretStr` so accidental `%r` formatting shows `**********`.

### Errors — PASS
```python
@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    log.exception("unhandled", path=request.url.path)     # full trace server-side
    return JSONResponse({"error": "internal error"}, status_code=500)
```

Run with `debug=False` in production; FastAPI/Starlette debug pages leak source and locals.

### Verification
- [ ] No credentials, tokens, or PII in logs at any level; redaction filter installed
- [ ] Client error bodies generic; tracebacks only in server logs
- [ ] `debug=False`, no `/docs` exposed publicly unless intended
- [ ] Sensitive columns encrypted at rest or tokenized where required

## 8. Outbound Requests

```python
import httpx, ipaddress
from urllib.parse import urlparse

ALLOWED_HOSTS = {"api.example.com"}

async def fetch(url: str) -> bytes:
    host = urlparse(url).hostname or ""
    if host not in ALLOWED_HOSTS:
        raise ValueError("host not allowed")            # SSRF guard for user-supplied URLs
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as c:
        r = await c.get(url)
        r.raise_for_status()
        return r.content
```

### Verification
- [ ] Every outbound call has a timeout
- [ ] User-supplied URLs checked against an allowlist; private IP ranges rejected
- [ ] API keys sent in headers, never in query strings (they end up in logs)
- [ ] TLS verification never disabled (`verify=False`)

## 9. Dependency Security

```bash
pip-audit                          # or: uv pip audit
pip list --outdated
deptry .                           # unused and undeclared dependencies
```

### Verification
- [ ] Lock file committed (`uv.lock`, `poetry.lock`, or pinned `requirements.txt` with hashes)
- [ ] `pip-audit` clean; CI fails on new advisories
- [ ] Direct dependencies version-constrained; no `>=` without an upper bound on major
- [ ] No packages installed from arbitrary git URLs or `--index-url` overrides in production

## 10. Data Pipelines and Models (if applicable)

- [ ] Model and artifact files loaded with `weights_only=True` / `safetensors`; never `pickle` from untrusted sources
- [ ] Data files parsed with size limits (`pd.read_csv(..., nrows=...)` or streaming) to avoid decompression bombs
- [ ] Scheduled jobs run with least-privilege DB roles (read-only where possible)
- [ ] Temporary files via `tempfile.NamedTemporaryFile(delete=True)` or `TemporaryDirectory`, never predictable names in `/tmp`

## Security Tests

```python
async def test_requires_auth(client):
    r = await client.get("/orders")
    assert r.status_code == 401

async def test_requires_admin(client, user_token):
    r = await client.delete("/users/123", headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 403

async def test_no_idor(client, alice_token, bobs_order_id):
    r = await client.get(f"/orders/{bobs_order_id}", headers={"Authorization": f"Bearer {alice_token}"})
    assert r.status_code == 404

async def test_rejects_extra_fields(client):
    r = await client.post("/users", json={"email": "a@b.co", "name": "a", "age": 1, "is_admin": True})
    assert r.status_code == 422

async def test_path_traversal_blocked():
    with pytest.raises(ValueError):
        safe_path("../../etc/passwd")

async def test_rate_limit(client):
    responses = [await client.post("/login", json=bad_creds) for _ in range(6)]
    assert responses[-1].status_code == 429

def test_no_secrets_in_logs(caplog, client):
    client.post("/login", json={"email": "a@b.co", "password": "hunter2"})
    assert "hunter2" not in caplog.text
```

## Pre-Deployment Checklist

- [ ] **Secrets**: none in source or history; loaded via settings; fail fast if missing
- [ ] **Input**: schemas at every boundary; `extra="forbid"`; uploads sniffed and capped
- [ ] **Injection**: parameterized SQL; list-arg subprocess; resolved paths; no pickle/`yaml.load`/`eval` on external data
- [ ] **Auth**: argon2/bcrypt; pinned JWT algorithms; ownership checks on every object read
- [ ] **Browser surface** (if any): sanitized HTML, CSP, explicit CORS, CSRF on cookie-auth writes
- [ ] **Rate limiting**: on login, reset, search, and public endpoints; shared store if multi-worker
- [ ] **Exposure**: redacting log filter; generic error bodies; `debug=False`
- [ ] **Outbound**: timeouts; URL allowlist; keys in headers; TLS verified
- [ ] **Dependencies**: lock file committed; `pip-audit` clean
- [ ] **Static analysis**: `bandit -r .` and `ruff check --select S` clean or exceptions documented inline

## Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Python Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Python_Security_Cheat_Sheet.html
- Bandit rule reference: https://bandit.readthedocs.io/en/latest/plugins/index.html
- FastAPI security docs: https://fastapi.tiangolo.com/tutorial/security/
