# Organization Management Service

A multi-tenant backend service built with **FastAPI** and **MongoDB** that supports creating and managing organizations in a scalable architecture. Each organization has its own dedicated MongoDB collection for data isolation, with a Master Database maintaining global metadata.

## 📋 Table of Contents

- [Features](#features)
- [Live Demo](#-live-demo)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Design Choices & Trade-offs](#design-choices--trade-offs)
- [Future Improvements](#future-improvements)

## ✨ Features

- **Multi-tenant Architecture**: Each organization gets a dedicated MongoDB collection
- **Dynamic Collection Creation**: Automatically creates collections when organizations are created
- **JWT Authentication**: Secure admin authentication with token-based authorization
- **Password Security**: Passwords are hashed using bcrypt
- **RESTful API**: Clean and well-documented REST endpoints
- **Class-based Design**: Modular, maintainable, and scalable code structure
- **Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Proper error responses with meaningful messages

## � Live Demo

**No setup required!** Test the API directly:

| Resource | URL |
|----------|-----|
| **API Base URL** | `https://organization-management-service.onrender.com` |
| **Swagger Docs** | `https://organization-management-service.onrender.com/docs` |
| **ReDoc** | `https://organization-management-service.onrender.com/redoc` |

## �🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Auth       │  │  Middleware  │  │   API Routes    │   │
│  │  (JWT/bcrypt)│  │   (CORS)     │  │  (Org/Admin)    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│                 ┌─────────────────┐                         │
│                 │  Service Layer  │                         │
│                 │ (Business Logic)│                         │
│                 └─────────────────┘                         │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │         MongoDB Database             │
         ├─────────────────────────────────────┤
         │       Master Database (Global)       │
         │  ┌────────────────────────────────┐ │
         │  │  Collections:                   │ │
         │  │  - organizations                │ │
         │  │  - admins                       │ │
         │  └────────────────────────────────┘ │
         │                                      │
         │   Dynamic Organization Collections   │
         │  ┌────────────────────────────────┐ │
         │  │  - org_company_a                │ │
         │  │  - org_company_b                │ │
         │  │  - org_startup_xyz              │ │
         │  │  - ...                          │ │
         │  └────────────────────────────────┘ │
         └─────────────────────────────────────┘
```

### Data Flow

1. **Organization Creation**:
   - Client → POST /org/create
   - Validate organization name uniqueness
   - Hash admin password
   - Create organization document in Master DB
   - Create admin document in Master DB
   - Dynamically create collection `org_<name>`
   - Return organization metadata

2. **Admin Login**:
   - Client → POST /admin/login
   - Validate credentials
   - Generate JWT token with admin_id and organization_id
   - Return token

3. **Protected Operations** (Update/Delete):
   - Client sends JWT token in Authorization header
   - Middleware validates token
   - Extract admin identity
   - Verify permissions
   - Execute operation

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: MongoDB (PyMongo 4.6.1)
- **Authentication**: JWT (python-jose), bcrypt (passlib)
- **Validation**: Pydantic 2.5.3
- **Server**: Uvicorn 0.27.0
- **Language**: Python 3.8+

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB 4.0+ (local or MongoDB Atlas)
- pip (Python package manager)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/ak4895/Organization-Management-Service.git
cd Organization-Management-Service

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### MongoDB Setup Options

#### Option 1: MongoDB Atlas (Recommended - Cloud)
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free M0 cluster
3. Get your connection string
4. Update `.env` with your connection string

#### Option 2: Local MongoDB
```bash
# macOS (with Homebrew)
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Verify installation
mongosh --eval "db.version()"
```

#### Option 3: Docker
```bash
docker run -d --name mongodb -p 27017:27017 mongo:7.0
```

## ⚙️ Configuration

### Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your values:

   | Variable | Description | Example |
   |----------|-------------|---------|
   | `MONGODB_URL` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
   | `MASTER_DB_NAME` | Master database name | `master_organization_db` |
   | `SECRET_KEY` | JWT secret (generate with `openssl rand -hex 32`) | `a1b2c3d4e5f6...` |
   | `ALGORITHM` | JWT algorithm | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes | `30` |
   | `DEBUG` | Debug mode | `True` |

### Quick Setup for Evaluators

```bash
# 1. Clone and enter directory
git clone https://github.com/ak4895/Organization-Management-Service.git
cd Organization-Management-Service

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file from template
cp .env.example .env

# 5. Edit .env with your MongoDB Atlas URL
# Get free MongoDB at: https://mongodb.com/atlas

# 6. Run the application
uvicorn app.main:app --reload

# 7. Open API docs
open http://localhost:8000/docs
```

**⚠️ Security Note**: 
- Generate a strong `SECRET_KEY` for production:
  ```bash
  openssl rand -hex 32
  ```
- Never commit `.env` file to version control

## 🚀 Running the Application

### Development Mode (with auto-reload)

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run the application
.venv/bin/python -m uvicorn app.main:app --reload
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://127.0.0.1:8000
- **Interactive Docs (Swagger)**: http://127.0.0.1:8000/docs
- **Alternative Docs (ReDoc)**: http://127.0.0.1:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify the Server is Running

```bash
# Test the root endpoint
curl http://127.0.0.1:8000/

# Or open in browser
open http://127.0.0.1:8000/docs
```

## 🌐 Deployment

### Live Deployment

| Resource | URL |
|----------|-----|
| **API Base URL** | `https://organization-management-service.onrender.com` |
| **API Documentation (Swagger)** | `https://organization-management-service.onrender.com/docs` |
| **API Documentation (ReDoc)** | `https://organization-management-service.onrender.com/redoc` |

### Deploy Your Own Instance

#### Step 1: Set Up MongoDB Atlas (Free Database)

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Sign up and create a **Free Shared Cluster (M0)**
3. Click **"Connect"** → **"Connect your application"**
4. Copy the connection string:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. In **Network Access**, add IP: `0.0.0.0/0` (allow all)

#### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Select your repository: `Organization-Management-Service`
4. Configure the service:

   | Field | Value |
   |-------|-------|
   | **Name** | `organization-management-service` |
   | **Region** | Oregon (US West) or nearest |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

5. Add **Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | Generate a secure random string |
   | `ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
   | `MONGODB_URL` | Your MongoDB Atlas connection string |
   | `MASTER_DB_NAME` | `master_organization_db` |
   | `DEBUG` | `false` |

6. Click **"Create Web Service"**

#### Deployment Files

The following files are required for Render deployment:

**Procfile**:
```
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**render.yaml** (optional - for blueprint deployment):
```yaml
services:
  - type: web
    name: organization-management-service
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: 30
      - key: MONGODB_URL
        sync: false
      - key: MASTER_DB_NAME
        value: master_organization_db
      - key: DEBUG
        value: false
```

#### Alternative Deployment Platforms

| Platform | Best For | Free Tier |
|----------|----------|-----------|
| **Render** | Simple deployment | ✅ 750 hours/month |
| **Railway** | Easiest setup | ✅ $5/month credit |
| **Fly.io** | Global edge | ✅ 3 shared VMs |
| **Vercel** | Serverless | ✅ Generous limits |

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Create Organization
**POST** `/org/create`

Creates a new organization with an admin user.

**Request Body**:
```json
{
  "organization_name": "Acme Corp",
  "email": "admin@acme.com",
  "password": "SecurePass123!"
}
```

**Response** (201 Created):
```json
{
  "organization_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "organization_name": "Acme Corp",
  "collection_name": "org_acme_corp",
  "admin_email": "admin@acme.com",
  "created_at": "2025-12-10T10:30:00.000Z",
  "updated_at": null
}
```

---

#### 2. Get Organization
**GET** `/org/get?organization_name=Acme Corp`

Retrieves organization details by name.

**Query Parameters**:
- `organization_name` (string, required)

**Response** (200 OK):
```json
{
  "organization_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "organization_name": "Acme Corp",
  "collection_name": "org_acme_corp",
  "admin_email": "admin@acme.com",
  "created_at": "2025-12-10T10:30:00.000Z",
  "updated_at": null
}
```

---

#### 3. Update Organization
**PUT** `/org/update`

Updates (renames) an organization and syncs data to a new collection.

**Request Body**:
```json
{
  "organization_name": "Acme Corporation",
  "email": "admin@acme.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "organization_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "organization_name": "Acme Corporation",
  "collection_name": "org_acme_corporation",
  "admin_email": "admin@acme.com",
  "created_at": "2025-12-10T10:30:00.000Z",
  "updated_at": "2025-12-10T11:00:00.000Z"
}
```

---

#### 4. Delete Organization
**DELETE** `/org/delete`

Deletes an organization (requires authentication).

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "organization_name": "Acme Corp"
}
```

**Response** (204 No Content)

---

#### 5. Admin Login
**POST** `/admin/login`

Authenticates an admin and returns a JWT token.

**Request Body**:
```json
{
  "email": "admin@acme.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin_id": "65a1b2c3d4e5f6g7h8i9j0k2",
  "organization_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "organization_name": "Acme Corp"
}
```

---

### Testing with cURL

#### Create Organization:
```bash
curl -X POST "http://127.0.0.1:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Test Corp",
    "email": "admin@test.com",
    "password": "SecurePass123!"
  }'
```

#### Admin Login:
```bash
curl -X POST "http://127.0.0.1:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "SecurePass123!"
  }'
```

#### Delete Organization (with token):
```bash
curl -X DELETE "http://127.0.0.1:8000/org/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "organization_name": "Test Corp"
  }'
```

## 🤔 Design Choices & Trade-offs

### Architecture Decisions

#### ✅ **What Works Well**

1. **Single Database with Dynamic Collections**
   - **Choice**: Use one MongoDB database with dynamic collections per organization
   - **Pros**:
     - Simpler connection management
     - Lower overhead (single connection pool)
     - Easier backup and maintenance
     - Cost-effective for small to medium deployments
   - **Best for**: 10-1000 organizations

2. **Class-based Service Layer**
   - **Choice**: Singleton service classes for business logic
   - **Pros**:
     - Clear separation of concerns
     - Easy to test and mock
     - Reusable and maintainable
     - Clean dependency injection

3. **JWT Authentication**
   - **Choice**: Stateless JWT tokens
   - **Pros**:
     - Scalable (no server-side session storage)
     - Works well with microservices
     - Mobile-friendly
   - **Cons**:
     - Cannot revoke tokens before expiry (solution: keep expiry short)

4. **Bcrypt Password Hashing**
   - **Choice**: Industry-standard bcrypt
   - **Pros**:
     - Slow and computationally expensive (good against brute-force)
     - Built-in salt
   - **Cons**:
     - Slower than alternatives (acceptable trade-off for security)

#### ⚠️ **Trade-offs & Limitations**

1. **Collection-based Multi-tenancy**
   - **Current**: Each org gets a collection in the same database
   - **Trade-off**: 
     - ✅ Simple and fast for moderate scale
     - ❌ All orgs share database resources
     - ❌ No true data isolation at DB level
     - ❌ MongoDB has a limit on collections (~10,000)
   
   **Better Alternative for Scale**: Database-per-tenant
   ```python
   # Future improvement: Each org gets its own database
   org_db = client[f"org_{organization_name}"]
   ```

2. **Synchronous Database Operations**
   - **Current**: PyMongo (synchronous)
   - **Trade-off**:
     - ✅ Simpler code
     - ❌ Blocks thread during I/O
   
   **Better Alternative for Performance**: Motor (async)
   ```python
   # Future: Use async MongoDB driver
   from motor.motor_asyncio import AsyncIOMotorClient
   ```

3. **In-memory Secret Key**
   - **Current**: Secret key in `.env` file
   - **Trade-off**:
     - ✅ Simple for development
     - ❌ Risk if `.env` is committed
   
   **Better Alternative for Production**: 
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

4. **No Rate Limiting**
   - **Current**: No rate limiting implemented
   - **Risk**: Vulnerable to brute-force attacks
   
   **Future Improvement**: Add rate limiting middleware
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

### Scalability Analysis

#### Current Design Supports:
- ✅ **10-1,000 organizations**: Excellent performance
- ⚠️ **1,000-10,000 organizations**: Good, but monitor collection count
- ❌ **10,000+ organizations**: Need architectural changes

#### Scaling Strategies

**For 10K+ Organizations**:
1. **Database-per-tenant**: Each org gets a dedicated database
2. **Sharding**: Distribute collections across multiple MongoDB instances
3. **Separate metadata service**: Microservice for Master DB
4. **Caching layer**: Redis for frequently accessed org metadata

**For High Traffic**:
1. **Async operations**: Switch to Motor (async MongoDB driver)
2. **Connection pooling**: Tune MongoDB connection pool size
3. **Load balancing**: Multiple FastAPI instances behind nginx/AWS ALB
4. **CDN**: For static content and API responses

**For Enterprise**:
1. **Separate databases**: Physical separation for compliance
2. **Database replication**: Read replicas for each org
3. **Kubernetes**: Container orchestration for auto-scaling
4. **Message queue**: RabbitMQ/Kafka for async operations

## 🚀 Future Improvements

### Security
- [ ] Implement refresh tokens for JWT
- [ ] Add rate limiting and brute-force protection
- [ ] Two-factor authentication (2FA)
- [ ] API key support for service-to-service auth
- [ ] Audit logging for all operations

### Features
- [ ] User management within organizations
- [ ] Role-based access control (RBAC)
- [ ] Organization settings and customization
- [ ] Billing and subscription management
- [ ] Webhook notifications

### Performance
- [ ] Switch to async MongoDB driver (Motor)
- [ ] Implement caching with Redis
- [ ] Database query optimization and indexing
- [ ] Connection pool tuning
- [ ] Horizontal scaling with load balancer

### Architecture
- [ ] Database-per-tenant for better isolation
- [ ] Event-driven architecture with message queues
- [ ] Microservices separation (auth, org management)
- [ ] GraphQL API support
- [ ] Real-time updates with WebSockets

### DevOps
- [ ] Docker containerization
- [ ] Docker Compose for local development
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Kubernetes deployment manifests
- [ ] Monitoring and alerting (Prometheus/Grafana)
- [ ] Automated testing (unit, integration, e2e)

## 🧪 Testing

### Manual Testing
Use the interactive API documentation at http://127.0.0.1:8000/docs

### Automated Testing (Future)
```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📝 Project Structure

```
Organization-Management-Service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and settings
│   ├── models.py               # Data models (Organization, Admin)
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── database.py             # Database connection management
│   ├── services.py             # Business logic layer
│   ├── auth.py                 # Authentication utilities
│   ├── dependencies.py         # FastAPI dependencies
│   └── routes/
│       ├── __init__.py
│       ├── organizations.py    # Organization endpoints
│       └── admin.py            # Admin authentication endpoints
├── .env                        # Environment variables (not in git)
├── requirements.txt            # Python dependencies
├── Procfile                    # Render deployment configuration
├── render.yaml                 # Render blueprint (optional)
├── ARCHITECTURE.md             # Detailed architecture documentation
├── DIAGRAMS.md                 # System diagrams
└── README.md                   # This file
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Backend Developer**
- GitHub: [@ak4895](https://github.com/ak4895)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- MongoDB for the flexible document database
- The Python community for amazing libraries

---

**Note**: This is an assignment project demonstrating multi-tenant architecture with FastAPI and MongoDB. For production use, implement additional security measures, testing, and monitoring.
