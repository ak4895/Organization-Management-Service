# Architecture and Design Notes

## Overview
This document provides a detailed explanation of the architectural decisions, design patterns, and trade-offs in the Organization Management Service.

## Architecture Pattern: Multi-Tenant SaaS

### Chosen Approach: Collection-per-Tenant
Each organization gets its own MongoDB collection within a shared database.

```
Master Database
├── organizations (metadata collection)
├── admins (global admin collection)
├── org_company_a (tenant collection)
├── org_company_b (tenant collection)
└── org_startup_xyz (tenant collection)
```

### Alternative Approaches Considered

#### 1. Database-per-Tenant
```
MongoDB Instance
├── master_db
│   ├── organizations
│   └── admins
├── org_company_a_db
├── org_company_b_db
└── org_startup_xyz_db
```

**Pros**:
- True data isolation
- Independent backups per tenant
- Can scale individual tenants
- Compliance-friendly (e.g., GDPR)

**Cons**:
- Connection management complexity
- Higher resource overhead
- More expensive
- Difficult to query across tenants

**When to use**: Enterprise customers, regulated industries, 1000+ tenants

#### 2. Shared Collection (Discriminator Column)
```
Master Database
├── organizations
├── admins
└── shared_data (organization_id, data...)
```

**Pros**:
- Simple to implement
- Best for small scale
- Easy cross-tenant queries

**Cons**:
- No data isolation
- Risk of data leakage
- Poor scalability
- Query performance degrades

**When to use**: Proof of concept, <100 tenants

### Why Collection-per-Tenant?

✅ **Balanced approach** for most SaaS applications
- Moderate isolation without extreme complexity
- Good performance up to ~5,000 tenants
- Manageable operational overhead
- Cost-effective

## Database Design

### Master Database Schema

#### Organizations Collection
```json
{
  "_id": ObjectId("..."),
  "organization_name": "Acme Corp",
  "collection_name": "org_acme_corp",
  "admin_id": "65a1b2c3...",
  "admin_email": "admin@acme.com",
  "created_at": ISODate("2025-12-10T10:00:00Z"),
  "updated_at": ISODate("2025-12-10T11:00:00Z")
}
```

**Indexes**:
```javascript
db.organizations.createIndex({ "organization_name": 1 }, { unique: true })
db.organizations.createIndex({ "collection_name": 1 }, { unique: true })
db.organizations.createIndex({ "admin_id": 1 })
```

#### Admins Collection
```json
{
  "_id": ObjectId("..."),
  "email": "admin@acme.com",
  "hashed_password": "$2b$12$...",
  "organization_id": "65a1b2c3...",
  "created_at": ISODate("2025-12-10T10:00:00Z")
}
```

**Indexes**:
```javascript
db.admins.createIndex({ "email": 1 }, { unique: true })
db.admins.createIndex({ "organization_id": 1 })
```

### Dynamic Organization Collections

Each organization's collection is initially empty but can store:
- Users
- Settings
- Application-specific data

**Example Schema** (optional):
```json
{
  "_id": ObjectId("..."),
  "type": "user",
  "name": "John Doe",
  "email": "john@acme.com",
  "role": "member",
  "created_at": ISODate("2025-12-10T10:00:00Z")
}
```

## Authentication & Security

### JWT Token Design

**Token Payload**:
```json
{
  "admin_id": "65a1b2c3d4e5f6g7h8i9j0k2",
  "organization_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "email": "admin@acme.com",
  "exp": 1702209600
}
```

**Why JWT?**
- ✅ Stateless (no session storage needed)
- ✅ Scalable (works across multiple servers)
- ✅ Self-contained (all info in token)
- ✅ Industry standard

**Security Measures**:
1. **HTTPS Only**: Tokens should only be transmitted over HTTPS
2. **Short Expiry**: 30 minutes default (configurable)
3. **Secure Secret**: 256-bit secret key
4. **No Sensitive Data**: Don't store passwords or payment info in JWT

**Token Revocation Strategy** (Future):
```python
# Redis-based token blacklist
revoked_tokens = redis_client.get(f"revoked:{token_jti}")
if revoked_tokens:
    raise HTTPException(status_code=401, detail="Token revoked")
```

### Password Security

**Bcrypt Configuration**:
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

- **Rounds**: Default 12 (2^12 iterations)
- **Salt**: Automatically generated per password
- **Time**: ~300ms per hash (intentionally slow)

**Why not Argon2?**
- Bcrypt is proven and widely supported
- Good balance of security and performance
- Easier to integrate

For **high-security** needs, consider Argon2:
```python
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

## API Design Principles

### RESTful Conventions

```
Resource: Organization
- POST   /org/create   → Create
- GET    /org/get      → Read
- PUT    /org/update   → Update
- DELETE /org/delete   → Delete

Resource: Admin
- POST   /admin/login  → Authenticate
```

### Response Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST (create) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Invalid credentials |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Error | Server error |

### Error Response Format

```json
{
  "detail": "Organization with name 'Acme Corp' already exists"
}
```

Consistent error format helps clients handle errors gracefully.

## Service Layer Architecture

### Class-based Services (Singleton Pattern)

```python
class OrganizationService:
    def __init__(self):
        self.master_db = db_connection.get_master_db()
        # Initialize collections
    
    def create_organization(self, ...): ...
    def get_organization_by_name(self, ...): ...
    # ... more methods

# Singleton instance
organization_service = OrganizationService()
```

**Benefits**:
- ✅ Single point of initialization
- ✅ Shared database connections
- ✅ Easy to test (can mock)
- ✅ Clear separation of concerns

**Layers**:
```
Routes (API endpoints)
    ↓
Services (Business logic)
    ↓
Database (Data access)
```

## Scalability Considerations

### Current Limits

| Metric | Limit | Reason |
|--------|-------|--------|
| Organizations | ~5,000 | MongoDB collection limit |
| Concurrent Requests | ~1,000 | Synchronous I/O |
| Database Size | 500GB | Single database approach |
| Response Time | <100ms | Network + DB latency |

### Scaling Strategies

#### Horizontal Scaling (Multiple Instances)

```
                 ┌─────────────┐
                 │ Load Balancer│
                 └──────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    ┌────────┐      ┌────────┐      ┌────────┐
    │FastAPI │      │FastAPI │      │FastAPI │
    │ Node 1 │      │ Node 2 │      │ Node 3 │
    └────────┘      └────────┘      └────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
                  ┌──────────┐
                  │ MongoDB  │
                  │ (Primary)│
                  └──────────┘
```

**Setup**:
```bash
# Run multiple instances
uvicorn app.main:app --host 0.0.0.0 --port 8001 &
uvicorn app.main:app --host 0.0.0.0 --port 8002 &
uvicorn app.main:app --host 0.0.0.0 --port 8003 &

# Nginx load balancer
upstream fastapi_backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}
```

#### Vertical Scaling (Better Hardware)

- More CPU cores for concurrent requests
- More RAM for connection pooling
- Faster SSD for database I/O

**MongoDB Configuration**:
```javascript
// Increase connection pool
db.adminCommand({ setParameter: 1, maxIncomingConnections: 500 })
```

#### Database Sharding

For 10K+ organizations:

```
┌─────────────────────────────────────┐
│         MongoDB Router (mongos)      │
└───────────┬─────────────────────────┘
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
  Shard 1  Shard 2  Shard 3
  (Orgs    (Orgs    (Orgs
  1-3000)  3001-    6001-
           6000)    9000)
```

**Shard Key**: `organization_id` or `organization_name`

## Performance Optimization

### Caching Strategy (Future)

```python
import redis
cache = redis.Redis(host='localhost', port=6379)

def get_organization_cached(org_name: str):
    # Try cache first
    cached = cache.get(f"org:{org_name}")
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    org = organization_service.get_organization_by_name(org_name)
    
    # Store in cache (5 min TTL)
    cache.setex(f"org:{org_name}", 300, json.dumps(org.to_dict()))
    
    return org
```

**What to cache**:
- ✅ Organization metadata (rarely changes)
- ✅ Admin permissions (read-heavy)
- ❌ Passwords (never cache)
- ❌ JWT tokens (stateless by design)

### Database Indexing

**Critical Indexes**:
```javascript
// Organizations
db.organizations.createIndex({ "organization_name": 1 }, { unique: true })
db.organizations.createIndex({ "collection_name": 1 }, { unique: true })

// Admins
db.admins.createIndex({ "email": 1 }, { unique: true })
db.admins.createIndex({ "organization_id": 1 })
```

**Query Performance**:
```javascript
// Without index: O(n) - full collection scan
// With index: O(log n) - tree traversal
```

### Async Operations (Future)

Replace synchronous PyMongo with async Motor:

```python
from motor.motor_asyncio import AsyncIOMotorClient

class AsyncOrganizationService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MASTER_DB_NAME]
    
    async def create_organization(self, ...):
        result = await self.db.organizations.insert_one(org_data)
        return result
```

**Benefits**:
- 10x more concurrent requests
- Non-blocking I/O
- Better resource utilization

## Production Readiness Checklist

### Security
- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Add rate limiting
- [ ] Implement CORS properly
- [ ] Add request validation middleware
- [ ] Enable MongoDB authentication
- [ ] Use environment-specific configs
- [ ] Implement audit logging

### Monitoring
- [ ] Health check endpoint (/health) ✅
- [ ] Prometheus metrics
- [ ] Error tracking (Sentry)
- [ ] Log aggregation (ELK stack)
- [ ] Performance monitoring (New Relic)
- [ ] Database monitoring

### Infrastructure
- [ ] Containerize with Docker
- [ ] Docker Compose for local dev
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Automated backups
- [ ] Disaster recovery plan

### Testing
- [ ] Unit tests (pytest)
- [ ] Integration tests
- [ ] Load testing (Locust)
- [ ] Security testing (OWASP)
- [ ] API documentation tests

## Trade-offs Summary

| Decision | Pros | Cons | Alternative |
|----------|------|------|-------------|
| Collection-per-tenant | Good isolation, scalable | Collection limit | DB-per-tenant |
| Synchronous PyMongo | Simple, easier to debug | Lower throughput | Async Motor |
| JWT tokens | Stateless, scalable | Can't revoke easily | Session-based auth |
| Single database | Simple, cost-effective | Shared resources | Multiple databases |
| FastAPI | Modern, fast, async-ready | Newer framework | Django, Flask |
| MongoDB | Flexible schema, scalable | NoSQL complexity | PostgreSQL |

## Conclusion

This architecture is well-suited for:
- ✅ SaaS applications with 10-5000 tenants
- ✅ Moderate traffic (1K-10K requests/min)
- ✅ Rapid prototyping and iteration
- ✅ Cost-conscious deployments

For larger scale or stricter requirements, consider:
- 🔄 Database-per-tenant for 5000+ orgs
- 🔄 Async operations for high concurrency
- 🔄 Microservices for team scalability
- 🔄 Event-driven architecture for complex workflows

The current design provides a solid foundation that can evolve with your needs.
