# High-Level System Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │  Web App │  │  Mobile  │  │   CLI    │  │   Third-party     │  │
│  │          │  │   App    │  │   Tool   │  │   Services        │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬────────────┘  │
└───────┼─────────────┼─────────────┼────────────────┼───────────────┘
        │             │             │                │
        └─────────────┴─────────────┴────────────────┘
                              │
                         HTTP/HTTPS
                              │
        ┌─────────────────────▼────────────────────────┐
        │         API GATEWAY / LOAD BALANCER          │
        │          (nginx / AWS ALB / Kong)            │
        └─────────────────────┬────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
┌───────────────▼──────────────┐ ┌──────────▼────────────────┐
│   FastAPI Instance 1         │ │  FastAPI Instance N       │
│  ┌───────────────────────┐   │ │ ┌───────────────────────┐ │
│  │   CORS Middleware     │   │ │ │   CORS Middleware     │ │
│  └───────────┬───────────┘   │ │ └───────────┬───────────┘ │
│  ┌───────────▼───────────┐   │ │ ┌───────────▼───────────┐ │
│  │  Auth Middleware      │   │ │ │  Auth Middleware      │ │
│  │  (JWT Validation)     │   │ │ │  (JWT Validation)     │ │
│  └───────────┬───────────┘   │ │ └───────────┬───────────┘ │
│  ┌───────────▼───────────┐   │ │ ┌───────────▼───────────┐ │
│  │   API Routes          │   │ │ │   API Routes          │ │
│  │  • /org/*             │   │ │ │  • /org/*             │ │
│  │  • /admin/*           │   │ │ │  • /admin/*           │ │
│  │  • /health            │   │ │ │  • /health            │ │
│  └───────────┬───────────┘   │ │ └───────────┬───────────┘ │
│  ┌───────────▼───────────┐   │ │ ┌───────────▼───────────┐ │
│  │   Service Layer       │   │ │ │   Service Layer       │ │
│  │  • OrganizationSvc    │   │ │ │  • OrganizationSvc    │ │
│  │  • AuthService        │   │ │ │  • AuthService        │ │
│  └───────────┬───────────┘   │ │ └───────────┬───────────┘ │
└──────────────┼───────────────┘ └─────────────┼─────────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
                   ┌───────────▼──────────────┐
                   │   DATABASE LAYER         │
                   │   MongoDB Connection     │
                   │   Manager (Singleton)    │
                   └───────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼──────────┐   ┌───────▼──────────┐   ┌──────▼──────────┐
│  Master Database │   │  Cache Layer     │   │  File Storage   │
│   (MongoDB)      │   │  (Optional)      │   │  (Optional)     │
│                  │   │   ┌──────────┐   │   │  ┌──────────┐   │
│ ┌──────────────┐ │   │   │  Redis   │   │   │  │  S3/GCS  │   │
│ │organizations │ │   │   │          │   │   │  │          │   │
│ │              │ │   │   │ • Org    │   │   │  │ • Uploads│   │
│ │ - org_name   │ │   │   │   metadata│   │   │  │ • Assets │   │
│ │ - collection │ │   │   │ • Sessions│   │   │  └──────────┘   │
│ │ - admin_id   │ │   │   │ • Tokens │   │   │                 │
│ │ - created_at │ │   │   └──────────┘   │   └─────────────────┘
│ └──────────────┘ │   └──────────────────┘
│                  │
│ ┌──────────────┐ │
│ │    admins    │ │
│ │              │ │
│ │ - email      │ │
│ │ - password   │ │
│ │ - org_id     │ │
│ └──────────────┘ │
│                  │
│ Dynamic Tenant   │
│ Collections:     │
│ ┌──────────────┐ │
│ │org_techcorp  │ │
│ │   (empty)    │ │
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │org_startup   │ │
│ │   (empty)    │ │
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │org_enterprise│ │
│ │   (empty)    │ │
│ └──────────────┘ │
└──────────────────┘
```

## Request Flow Diagram

### 1. Create Organization Flow

```
┌─────────┐                                                    ┌─────────┐
│ Client  │                                                    │ MongoDB │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │ POST /org/create                                             │
     │ {organization_name, email, password}                         │
     ├──────────────────────────────────────►                      │
     │                                       │                      │
     │                          Validate Input (Pydantic)           │
     │                                       │                      │
     │                          Check if org exists                 │
     │                                       ├─────────────────────►│
     │                                       │  find(org_name)      │
     │                                       │◄─────────────────────┤
     │                                       │  null                │
     │                                       │                      │
     │                          Hash Password (bcrypt)              │
     │                                       │                      │
     │                          Create Org Document                 │
     │                                       ├─────────────────────►│
     │                                       │ insert_one(org_data) │
     │                                       │◄─────────────────────┤
     │                                       │ {org_id}             │
     │                                       │                      │
     │                          Create Admin Document               │
     │                                       ├─────────────────────►│
     │                                       │insert_one(admin_data)│
     │                                       │◄─────────────────────┤
     │                                       │ {admin_id}           │
     │                                       │                      │
     │                          Create Collection                   │
     │                                       ├─────────────────────►│
     │                                       │create_collection()   │
     │                                       │◄─────────────────────┤
     │                                       │ success              │
     │◄──────────────────────────────────────┤                      │
     │ 201 Created                           │                      │
     │ {org_id, org_name, collection_name}   │                      │
     │                                                              │
```

### 2. Admin Login Flow

```
┌─────────┐                                                    ┌─────────┐
│ Client  │                                                    │ MongoDB │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │ POST /admin/login                                            │
     │ {email, password}                                            │
     ├──────────────────────────────────────►                      │
     │                                       │                      │
     │                          Find Admin by Email                 │
     │                                       ├─────────────────────►│
     │                                       │ find_one({email})    │
     │                                       │◄─────────────────────┤
     │                                       │ {admin_doc}          │
     │                                       │                      │
     │                          Verify Password                     │
     │                          (bcrypt.verify)                     │
     │                                       │                      │
     │                          Get Organization                    │
     │                                       ├─────────────────────►│
     │                                       │find_one({org_id})    │
     │                                       │◄─────────────────────┤
     │                                       │ {org_doc}            │
     │                                       │                      │
     │                          Generate JWT Token                  │
     │                          {admin_id, org_id, email, exp}      │
     │                                       │                      │
     │◄──────────────────────────────────────┤                      │
     │ 200 OK                                │                      │
     │ {access_token, admin_id, org_id}      │                      │
     │                                                              │
```

### 3. Delete Organization Flow (Authenticated)

```
┌─────────┐                                                    ┌─────────┐
│ Client  │                                                    │ MongoDB │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │ DELETE /org/delete                                           │
     │ Authorization: Bearer <token>                                │
     │ {organization_name}                                          │
     ├──────────────────────────────────────►                      │
     │                                       │                      │
     │                          Validate JWT Token                  │
     │                          Extract {admin_id, org_id}          │
     │                                       │                      │
     │                          Find Organization                   │
     │                                       ├─────────────────────►│
     │                                       │find_one({org_name})  │
     │                                       │◄─────────────────────┤
     │                                       │ {org_doc}            │
     │                                       │                      │
     │                          Verify Ownership                    │
     │                          (org.admin_id == token.admin_id)    │
     │                                       │                      │
     │                          Drop Collection                     │
     │                                       ├─────────────────────►│
     │                                       │drop_collection()     │
     │                                       │◄─────────────────────┤
     │                                       │ success              │
     │                                       │                      │
     │                          Delete Admin                        │
     │                                       ├─────────────────────►│
     │                                       │ delete_one(admin_id) │
     │                                       │◄─────────────────────┤
     │                                       │ success              │
     │                                       │                      │
     │                          Delete Organization                 │
     │                                       ├─────────────────────►│
     │                                       │ delete_one(org_id)   │
     │                                       │◄─────────────────────┤
     │                                       │ success              │
     │◄──────────────────────────────────────┤                      │
     │ 204 No Content                        │                      │
     │                                                              │
```

## Component Interaction Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                        │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    Routes Layer                         │    │
│  │  ┌──────────────┐           ┌──────────────┐          │    │
│  │  │ organizations│           │    admin     │          │    │
│  │  │    .py       │           │    .py       │          │    │
│  │  │              │           │              │          │    │
│  │  │ - create     │           │ - login      │          │    │
│  │  │ - get        │           │              │          │    │
│  │  │ - update     │           │              │          │    │
│  │  │ - delete     │           │              │          │    │
│  │  └──────┬───────┘           └──────┬───────┘          │    │
│  └─────────┼────────────────────────────┼─────────────────┘    │
│            │                          │                        │
│            │ depends on               │ depends on             │
│            ▼                          ▼                        │
│  ┌─────────────────────┐    ┌────────────────────┐           │
│  │  dependencies.py    │    │    schemas.py      │           │
│  │                     │    │                    │           │
│  │ - get_current_admin │    │ - Request models   │           │
│  │   (JWT validation)  │    │ - Response models  │           │
│  └─────────┬───────────┘    │ - Token data       │           │
│            │                └────────────────────┘           │
│            │ uses                                             │
│            ▼                                                  │
│  ┌─────────────────────┐                                      │
│  │     auth.py         │                                      │
│  │  (AuthService)      │                                      │
│  │                     │                                      │
│  │ - verify_password   │                                      │
│  │ - hash_password     │                                      │
│  │ - create_token      │                                      │
│  │ - decode_token      │                                      │
│  └─────────────────────┘                                      │
│            ▲                                                  │
│            │                                                  │
│  ┌─────────┴───────────┐                                      │
│  │    services.py      │                                      │
│  │ (OrganizationSvc)   │                                      │
│  │                     │                                      │
│  │ - create_org        │                                      │
│  │ - get_org           │                                      │
│  │ - update_org        │                                      │
│  │ - delete_org        │                                      │
│  │ - authenticate_admin│                                      │
│  └─────────┬───────────┘                                      │
│            │ uses                                             │
│            ▼                                                  │
│  ┌─────────────────────┐         ┌────────────────┐          │
│  │    database.py      │         │   models.py    │          │
│  │ (DatabaseConnection)│         │                │          │
│  │                     │         │ - Organization │          │
│  │ - get_master_db     │         │ - Admin        │          │
│  │ - get_collection    │         │                │          │
│  │ - create_collection │         └────────────────┘          │
│  │ - drop_collection   │                                      │
│  └─────────┬───────────┘                                      │
│            │                                                  │
│            │ uses                                             │
│            ▼                                                  │
│  ┌─────────────────────┐                                      │
│  │     config.py       │                                      │
│  │   (Settings)        │                                      │
│  │                     │                                      │
│  │ - MONGODB_URL       │                                      │
│  │ - SECRET_KEY        │                                      │
│  │ - JWT settings      │                                      │
│  └─────────────────────┘                                      │
│                                                               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
                ┌────────────────┐
                │    MongoDB     │
                │                │
                │ - Master DB    │
                │ - Tenant DBs   │
                └────────────────┘
```

## Data Model Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Master Database Schema                    │
│                  (master_organization_db)                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐       ┌──────────────────────────────┐
│   organizations Collection    │       │      admins Collection        │
├──────────────────────────────┤       ├──────────────────────────────┤
│ _id: ObjectId               │       │ _id: ObjectId               │
│ organization_name: string    │◄──┐   │ email: string (unique)       │
│ collection_name: string      │   │   │ hashed_password: string      │
│ admin_id: ObjectId          ├───┘───┤ organization_id: ObjectId    │
│ admin_email: string          │       │ created_at: datetime         │
│ created_at: datetime         │       └──────────────────────────────┘
│ updated_at: datetime         │
└──────────────────────────────┘
         │
         │ creates
         ▼
┌──────────────────────────────┐
│  Dynamic Tenant Collections  │
│                              │
│  org_techcorp                │
│  ├─ (initially empty)        │
│  └─ Can store:               │
│     - Users                  │
│     - Settings               │
│     - App data               │
│                              │
│  org_startup_inc             │
│  ├─ (initially empty)        │
│  └─ Isolated from other      │
│     organizations            │
│                              │
│  org_enterprise_co           │
│  └─ (initially empty)        │
└──────────────────────────────┘

Relationships:
• organizations.admin_id → admins._id (1:1)
• admins.organization_id → organizations._id (1:1)
• organizations.collection_name → dynamic collection (1:1)
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Production Setup                       │
└────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   Internet   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Load Balancer│
                    │ (AWS ALB/    │
                    │  nginx)      │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼────┐      ┌─────▼────┐
   │FastAPI  │       │ FastAPI  │      │ FastAPI  │
   │Instance │       │ Instance │      │ Instance │
   │   #1    │       │    #2    │      │    #3    │
   └────┬────┘       └─────┬────┘      └─────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼───────┐
                    │   MongoDB    │
                    │   Cluster    │
                    │              │
                    │  Primary     │
                    │  Secondary 1 │
                    │  Secondary 2 │
                    └──────────────┘
```

## Security Flow

```
Authentication Flow:
┌─────────┐                                              ┌─────────┐
│ Client  │                                              │ Server  │
└────┬────┘                                              └────┬────┘
     │                                                        │
     │ 1. POST /admin/login {email, password}                │
     ├──────────────────────────────────────────────────────►│
     │                                                        │
     │                           2. Verify with bcrypt       │
     │                              (hashed in DB)           │
     │                                                        │
     │ 3. JWT Token (signed with SECRET_KEY)                 │
     │    {admin_id, org_id, email, exp}                     │
     │◄───────────────────────────────────────────────────────┤
     │                                                        │
     │ 4. Store token (localStorage/cookie)                  │
     │                                                        │
     │ 5. DELETE /org/delete                                 │
     │    Authorization: Bearer <token>                      │
     ├──────────────────────────────────────────────────────►│
     │                                                        │
     │                           6. Verify JWT signature     │
     │                           7. Check expiration         │
     │                           8. Extract admin_id         │
     │                           9. Verify ownership         │
     │                                                        │
     │ 10. Success / Forbidden                               │
     │◄───────────────────────────────────────────────────────┤
     │                                                        │
```

---

**Legend:**
- `─►` : Data flow direction
- `◄─` : Response flow
- `┌─┐` : Component boundary
- `├─┤` : Connection point
