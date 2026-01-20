# CTMS FastAPI Backend - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Frontend: React/Vue/Angular or Mobile App)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │   Auth     │  │   Tasks    │  │ Analytics  │         │  │
│  │  │  Routes    │  │   Routes   │  │   Routes   │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 Middleware Layer                          │  │
│  │  • CORS Middleware                                        │  │
│  │  • Authentication Middleware                              │  │
│  │  • Request Timing Middleware                              │  │
│  │  • Exception Handler                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 Business Logic Layer                      │  │
│  │  • Dependencies (Auth, RBAC, Working Hours)               │  │
│  │  • Pydantic Schemas (Validation)                          │  │
│  │  • Security Utils (JWT, Password Hashing)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Data Access Layer                       │  │
│  │  • SQLAlchemy Models                                      │  │
│  │  • Async Database Sessions                                │  │
│  │  • Query Builders                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Async I/O
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Layer                              │
│  ┌──────────────┐                    ┌──────────────┐          │
│  │   SQLite     │  (Development)     │  PostgreSQL  │  (Prod)  │
│  │   Database   │                    │   Database   │          │
│  └──────────────┘                    └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Core Components

```
app/core/
├── config.py          # Settings & Environment Variables
│   └── Settings class (Pydantic BaseSettings)
│       ├── App config (name, version, debug)
│       ├── Security config (secret key, JWT settings)
│       ├── Database config (connection URL)
│       └── CORS config (allowed origins)
│
├── database.py        # Database Configuration
│   ├── AsyncEngine (SQLAlchemy)
│   ├── AsyncSessionLocal (Session factory)
│   ├── Base (Declarative base)
│   ├── get_db() (Dependency)
│   └── init_db() (Table creation)
│
└── security.py        # Security Utilities
    ├── pwd_context (Password hashing)
    ├── verify_password()
    ├── get_password_hash()
    ├── create_access_token()
    ├── create_refresh_token()
    └── decode_token()
```

### 2. Data Models

```
app/models/
├── user.py
│   ├── User (Main user model)
│   │   ├── Fields: id, username, email, password, role, timezone
│   │   ├── Relationships: sessions, tasks, notifications
│   │   └── Methods: is_manager(), is_developer(), is_auditor()
│   ├── UserSession (Session tracking)
│   │   └── Fields: user_id, refresh_token, device_id, timestamps
│   └── EmailVerificationToken
│       └── Fields: user_id, token, created_at
│
├── task.py
│   ├── Task (Main task model)
│   │   ├── Fields: title, description, status, priority, hours, deadline
│   │   ├── Relationships: assigned_to, created_by, parent, tags
│   │   └── Methods: is_parent()
│   ├── Tag (Task categorization)
│   │   └── Fields: name
│   └── TaskHistory (Status tracking)
│       └── Fields: task_id, action, from_status, to_status, timestamp
│
├── notification.py
│   └── Notification
│       ├── Fields: user_id, task_id, message, type, read, delivered
│       └── Relationships: user, task
│
└── audit.py
    └── APIAuditLog
        └── Fields: user_id, endpoint, method, status, request, response
```

### 3. API Schemas (Pydantic)

```
app/schemas/
├── user.py
│   ├── UserBase (Base schema)
│   ├── UserCreate (Registration)
│   ├── UserLogin (Login)
│   ├── UserResponse (API response)
│   ├── Token (JWT token)
│   └── EmailVerification (Verification)
│
├── task.py
│   ├── TaskBase (Base schema)
│   ├── TaskCreate (Create task)
│   ├── TaskUpdate (Update task)
│   ├── TaskResponse (API response)
│   ├── BulkUpdateRequest (Bulk operations)
│   └── TagCreate/TagResponse (Tags)
│
├── analytics.py
│   ├── TaskAnalytics (Task metrics)
│   └── AnalyticsResponse (Full analytics)
│
└── notification.py
    └── NotificationResponse (Notification data)
```

### 4. API Routes

```
app/api/
├── dependencies.py
│   ├── get_current_user() (Auth dependency)
│   ├── get_current_verified_user() (Email verified)
│   ├── require_role() (RBAC check)
│   ├── require_working_hours_for_developers()
│   └── check_working_hours()
│
├── router.py (Main API router)
│   └── Includes all route modules
│
└── routes/
    ├── auth.py (Authentication endpoints)
    │   ├── POST /register
    │   ├── POST /verify-email
    │   ├── POST /login
    │   ├── POST /refresh
    │   ├── POST /logout
    │   ├── POST /logout-all
    │   ├── GET /users/me
    │   └── GET /users
    │
    ├── tasks.py (Task management)
    │   ├── GET /
    │   ├── GET /{id}
    │   ├── POST /
    │   ├── PATCH /{id}
    │   ├── DELETE /{id}
    │   └── POST /bulk-update
    │
    └── analytics.py (Analytics)
        └── GET /
```

## Data Flow

### Authentication Flow

```
1. Registration
   Client → POST /api/auth/register
   ↓
   Validate input (Pydantic)
   ↓
   Hash password (bcrypt)
   ↓
   Create user in DB
   ↓
   Generate verification token
   ↓
   Return token (in production: send email)

2. Email Verification
   Client → POST /api/auth/verify-email
   ↓
   Validate token
   ↓
   Mark user as verified
   ↓
   Delete token
   ↓
   Return success

3. Login
   Client → POST /api/auth/login
   ↓
   Verify credentials
   ↓
   Check email verified
   ↓
   Create JWT tokens (access + refresh)
   ↓
   Create session in DB
   ↓
   Set HTTP-only cookies
   ↓
   Return access token

4. Protected Request
   Client → GET /api/tasks (with Bearer token)
   ↓
   Extract token from header
   ↓
   Decode and validate JWT
   ↓
   Get user from DB
   ↓
   Check permissions (RBAC)
   ↓
   Execute request
   ↓
   Return response

5. Token Refresh
   Client → POST /api/auth/refresh (with cookie)
   ↓
   Extract refresh token from cookie
   ↓
   Validate refresh token
   ↓
   Check session in DB
   ↓
   Generate new tokens
   ↓
   Update session
   ↓
   Return new access token
```

### Task Creation Flow

```
Client → POST /api/tasks
↓
Authentication (get_current_user)
↓
Email Verification Check
↓
Working Hours Check (for developers)
↓
RBAC Check (auditors cannot create)
↓
Validate input (Pydantic schema)
↓
Check assigned user exists
↓
Check parent task exists (if provided)
↓
Create task in DB
↓
Add tags (if provided)
↓
Commit transaction
↓
Return task response
```

### Analytics Flow

```
Client → GET /api/analytics
↓
Authentication
↓
Get user's assigned tasks
↓
Calculate my_tasks metrics:
  - Total, completed, pending, in_progress
↓
Get team tasks (based on role):
  - Developer: same as my_tasks
  - Manager/Auditor: all tasks
↓
Calculate efficiency score:
  - Completion rate (60%)
  - Time efficiency (40%)
↓
Return analytics response
```

## Security Architecture

### Authentication Layers

```
1. Password Security
   ├── Bcrypt hashing with salt
   ├── Minimum 8 characters
   └── Stored as hash only

2. JWT Tokens
   ├── Access Token (short-lived: 20 min)
   │   ├── Stored in client memory
   │   └── Sent in Authorization header
   └── Refresh Token (long-lived: 3 days)
       ├── Stored in HTTP-only cookie
       ├── Cannot be accessed by JavaScript
       └── Secure & SameSite attributes

3. Session Management
   ├── Max 3 concurrent sessions per user
   ├── Session tracking in database
   ├── Device ID for session identification
   └── Automatic cleanup of old sessions

4. Token Blacklisting
   ├── Tokens invalidated on logout
   ├── All tokens invalidated on logout-all
   └── Session deletion from database
```

### Authorization Layers

```
1. Role-Based Access Control (RBAC)
   ├── Manager: Full access, no restrictions
   ├── Developer: Limited access, time restrictions
   └── Auditor: Read-only access

2. Time-Based Permissions
   ├── Working hours: 9 AM - 6 PM
   ├── User's timezone considered
   ├── Applies to: create, update, delete
   └── Exception: Critical priority tasks

3. Resource-Level Permissions
   ├── Developers: Only assigned tasks
   ├── Managers: All tasks
   └── Auditors: All tasks (read-only)
```

## Database Schema

### Entity Relationship Diagram

```
┌──────────────┐
│    User      │
├──────────────┤
│ id (PK)      │
│ username     │
│ email        │
│ password     │
│ role         │
│ timezone     │
│ verified     │
└──────┬───────┘
       │
       │ 1:N
       │
       ├─────────────────────────────┐
       │                             │
       ▼                             ▼
┌──────────────┐              ┌──────────────┐
│ UserSession  │              │     Task     │
├──────────────┤              ├──────────────┤
│ id (PK)      │              │ id (PK)      │
│ user_id (FK) │              │ title        │
│ refresh_token│              │ description  │
│ device_id    │              │ status       │
│ created_at   │              │ priority     │
│ last_used    │              │ estimated_h  │
└──────────────┘              │ actual_h     │
                              │ deadline     │
                              │ assigned_to  │◄─┐
                              │ created_by   │◄─┤
                              │ parent_id    │◄─┘
                              └──────┬───────┘
                                     │
                                     │ M:N
                                     │
                                     ▼
                              ┌──────────────┐
                              │     Tag      │
                              ├──────────────┤
                              │ id (PK)      │
                              │ name         │
                              └──────────────┘
```

## Deployment Architecture

### Development

```
┌─────────────────┐
│   Developer     │
│   Machine       │
├─────────────────┤
│ • Python 3.10+  │
│ • Virtual Env   │
│ • SQLite DB     │
│ • Uvicorn       │
└─────────────────┘
```

### Production (Docker)

```
┌──────────────────────────────────────────┐
│            Docker Host                    │
│                                           │
│  ┌────────────┐  ┌────────────┐         │
│  │  FastAPI   │  │ PostgreSQL │         │
│  │ Container  │  │ Container  │         │
│  │            │  │            │         │
│  │ Port: 8000 │  │ Port: 5432 │         │
│  └────────────┘  └────────────┘         │
│         │               │                │
│         └───────┬───────┘                │
│                 │                        │
│         ┌───────▼───────┐                │
│         │     Redis     │                │
│         │   Container   │                │
│         │  Port: 6379   │                │
│         └───────────────┘                │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │      Docker Network                │  │
│  │      (ctms_network)                │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
         │
         │ Port 8000
         ▼
┌──────────────────┐
│   Nginx/Traefik  │
│  (Reverse Proxy) │
│   HTTPS/SSL      │
└──────────────────┘
         │
         │ HTTPS
         ▼
┌──────────────────┐
│     Clients      │
└──────────────────┘
```

## Performance Optimizations

1. **Async I/O**: All database operations are async
2. **Connection Pooling**: SQLAlchemy manages connection pool
3. **Lazy Loading**: Relationships loaded on demand
4. **Eager Loading**: Use `selectinload()` for N+1 prevention
5. **Indexes**: Database indexes on frequently queried fields
6. **Pydantic**: Fast validation with C extensions
7. **Minimal Middleware**: Only essential middleware enabled

## Monitoring & Logging

```
Request → Middleware → Log Request
          ↓
       Process Request
          ↓
       Log Response
          ↓
       Add Timing Header (X-Process-Time)
          ↓
       Return Response
```

## Error Handling

```
Exception Raised
    ↓
Specific Handler?
    ├─ Yes → Return specific error
    └─ No → Global Exception Handler
              ↓
           Log Error
              ↓
           Return 500 Internal Server Error
```

---

**Last Updated**: 2026-01-20  
**Version**: 1.0.0
