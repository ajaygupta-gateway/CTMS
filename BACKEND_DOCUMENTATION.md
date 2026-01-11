# CTMS Backend Documentation

## Overview
Complete API reference and architecture documentation for the Clinical Trial Management System (CTMS) backend.

**Base URL**: `http://localhost:8000/api` (development)  
**Authentication**: JWT Bearer tokens with HTTP-only cookie refresh tokens  
**Framework**: Django 5.1 + Django REST Framework  
**Database**: SQLite (development) / PostgreSQL (production)  
**API Version**: 1.0

---

## Table of Contents
1. [Project Structure](#1-project-structure)
2. [Authentication & Users](#2-authentication--users)
3. [Tasks](#3-tasks)
4. [Analytics](#4-analytics)
5. [Permissions & RBAC](#5-permissions--rbac)
6. [Data Models](#6-data-models)

---

## 1. Project Structure

### 1.1. Directory Overview

```
backend/
├── manage.py                  # Django management script
├── db.sqlite3                 # SQLite database (development)
├── .env                       # Environment variables
├── config/                    # Project configuration
│   ├── __init__.py
│   ├── asgi.py               # ASGI configuration
│   ├── wsgi.py               # WSGI configuration
│   ├── urls.py               # Root URL configuration
│   └── settings/             # Settings modules
│       ├── __init__.py
│       ├── base.py           # Base settings
│       ├── development.py    # Development settings
│       └── production.py     # Production settings
└── apps/                     # Django applications
    ├── users/                # User management & authentication
    ├── tasks/                # Task management
    ├── analytics/            # Analytics & reporting
    ├── audit/                # Audit logging
    ├── notifications/        # Notification system
    ├── security/             # Security features
    └── common/               # Shared utilities
```

### 1.2. Apps Overview

#### users/ - User Management & Authentication
**Purpose**: Handle user registration, authentication, sessions, and RBAC

**Key Files**:
- `models.py`: User, UserSession, EmailVerificationToken
- `views.py`: Register, Login, Refresh, Logout, VerifyEmail
- `serializers.py`: User serialization and validation
- `permissions.py`: UserAccessPermission, AuditorReadOnly
- `urls.py`: Authentication endpoints routing
- `admin.py`: Django admin configuration
- `signals.py`: Email verification token creation

**Endpoints**:
- `/auth/register/` - User registration
- `/auth/verify-email/` - Email verification
- `/auth/login/` - User login
- `/auth/refresh/` - Token refresh
- `/auth/logout/` - Logout current session
- `/auth/logout-all/` - Logout all sessions
- `/auth/users/` - List users (RBAC-filtered)
- `/auth/users/me/` - Current user profile

---

#### tasks/ - Task Management
**Purpose**: CRUD operations for tasks with RBAC and time-based permissions

**Key Files**:
- `models.py`: Task, Tag, TaskComment
- `views.py`: TaskViewSet (CRUD operations)
- `views_bulk.py`: Bulk operations
- `serializers.py`: Task serialization
- `serializers_bulk.py`: Bulk operation serializers
- `permissions.py`: TaskAccessPermission, TaskCreatePermission
- `services.py`: Business logic
- `services_bulk.py`: Bulk operation logic
- `signals.py`: Task-related signals
- `admin.py`: Django admin with custom filters
- `admin_filters.py`: Custom admin filters
- `urls.py`: Task endpoints routing

**Endpoints**:
- `/tasks/` - List/Create tasks
- `/tasks/{id}/` - Retrieve/Update/Delete task
- `/tasks/bulk-update/` - Bulk status update
- `/tasks/analytics/` - Dashboard analytics

---

#### analytics/ - Analytics & Reporting
**Purpose**: Compute metrics and generate reports

**Key Files**:
- `services.py`: Analytics calculation logic
- `views.py`: Analytics endpoints
- `urls.py`: Analytics routing

**Features**:
- Task completion metrics
- Team performance analytics
- Efficiency score calculation
- User-specific vs team-wide stats

---

#### audit/ - Audit Logging
**Purpose**: Track all system changes for compliance

**Key Files**:
- `models.py`: AuditLog
- `middleware.py`: Automatic audit logging
- `utils.py`: Audit helper functions
- `views.py`: Audit log retrieval

**Features**:
- Automatic logging of all model changes
- User action tracking
- IP address and timestamp recording
- Queryable audit trail

---

#### notifications/ - Notification System
**Purpose**: Send notifications to users (email, in-app, etc.)

**Key Files**:
- `models.py`: Notification
- `views.py`: Notification endpoints
- `admin.py`: Notification management

**Features**:
- Email notifications
- In-app notifications
- Notification preferences
- Read/unread status

---

#### security/ - Security Features
**Purpose**: IP-based security, rate limiting, and security utilities

**Key Files**:
- `middleware/ip_security.py`: IP whitelist/blacklist
- `middleware/smart_rate_limit.py`: Adaptive rate limiting
- `utils.py`: Security helper functions
- `debug_views.py`: Security debugging endpoints
- `urls.py`: Security endpoints

**Features**:
- IP-based access control
- Smart rate limiting (adaptive thresholds)
- Security event logging
- Debug endpoints for testing

---

#### common/ - Shared Utilities
**Purpose**: Middleware and utilities used across apps

**Key Files**:
- `middleware/jwt_autorefresh.py`: Automatic JWT refresh
- `middleware/priority_escalation.py`: Auto-escalate task priority
- `middleware/__init__.py`: Middleware exports

**Features**:
- JWT auto-refresh middleware
- Priority escalation for overdue tasks
- Shared utility functions

---

### 1.3. Key Configuration Files

#### config/settings/base.py
**Purpose**: Base Django settings shared across environments

**Key Configurations**:
- Installed apps
- Middleware stack
- Database configuration
- REST Framework settings
- JWT settings (Simple JWT)
- CORS configuration
- Static files configuration

#### config/urls.py
**Purpose**: Root URL routing

**URL Patterns**:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/security/', include('apps.security.urls')),
]
```

---

### 1.4. Database Models

**User Models** (`apps/users/models.py`):
- `User`: Custom user model with roles and timezone
- `UserSession`: Track active user sessions
- `EmailVerificationToken`: Email verification tokens

**Task Models** (`apps/tasks/models.py`):
- `Task`: Main task model with all fields
- `Tag`: Task categorization
- `TaskComment`: Comments on tasks

**Audit Models** (`apps/audit/models.py`):
- `AuditLog`: System-wide audit trail

**Notification Models** (`apps/notifications/models.py`):
- `Notification`: User notifications

---

### 1.5. Middleware Stack

**Order** (from `settings/base.py`):
1. `SecurityMiddleware` - Django security
2. `SessionMiddleware` - Session management
3. `CommonMiddleware` - Common Django features
4. `CsrfViewMiddleware` - CSRF protection
5. `AuthenticationMiddleware` - User authentication
6. `MessageMiddleware` - Flash messages
7. `ClickjackingMiddleware` - Clickjacking protection
8. `AuditMiddleware` - Audit logging (custom)
9. `IPSecurityMiddleware` - IP filtering (custom)
10. `SmartRateLimitMiddleware` - Rate limiting (custom)
11. `PriorityEscalationMiddleware` - Task escalation (custom)

---

## 2. Authentication & Users

### 1.1. Register
**Endpoint**: `POST /auth/register/`  
**Description**: Register a new user account (default role: developer)  
**Permissions**: Public (AllowAny)

**Request Body**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "timezone": "Asia/Kolkata"  // Optional, default: Asia/Kolkata
}
```

**Response**: `201 Created`
```json
{
  "message": "User registered. Verify email to activate account.",
  "verification_token": "abc123..."
}
```

**Notes**:
- Account is inactive until email verification
- Verification token is sent in response (in production, sent via email)

---

### 1.2. Verify Email
**Endpoint**: `POST /auth/verify-email/`  
**Description**: Activate account using verification token  
**Permissions**: Public (AllowAny)

**Request Body**:
```json
{
  "token": "abc123..."
}
```

**Response**: `200 OK`
```json
{
  "message": "Email verified successfully"
}
```

---

### 1.3. Login
**Endpoint**: `POST /auth/login/`  
**Description**: Authenticate user and obtain access token  
**Permissions**: Public (AllowAny)

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response**: `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Cookies Set**:
- `refresh_token` (HTTP-only, Secure, SameSite=Lax)
- `device_id` (HTTP-only, Secure, SameSite=Lax)

**Notes**:
- Refresh token stored in HTTP-only cookie (not accessible to JavaScript)
- Maximum 3 concurrent sessions per user
- Oldest session deleted if limit exceeded

---

### 1.4. Refresh Token
**Endpoint**: `POST /auth/refresh/`  
**Description**: Obtain new access token using refresh token from cookie  
**Permissions**: Public (AllowAny)

**Request Body**: `{}` (empty, refresh token sent via cookie)

**Response**: `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Cookies Updated**:
- `refresh_token` (new token, old one blacklisted)

**Error Responses**:
- `401 Unauthorized`: Invalid or missing refresh token

---

### 1.5. Logout
**Endpoint**: `POST /auth/logout/`  
**Description**: Logout from current session  
**Permissions**: Authenticated

**Request Body**: `{}`

**Response**: `200 OK`
```json
{
  "detail": "Logged out successfully"
}
```

**Cookies Cleared**:
- `refresh_token`
- `device_id`

**Notes**:
- Blacklists current refresh token
- Deletes current session from database

---

### 1.6. Logout All Devices
**Endpoint**: `POST /auth/logout-all/`  
**Description**: Logout from all sessions/devices  
**Permissions**: Authenticated

**Request Body**: `{}`

**Response**: `200 OK`
```json
{
  "detail": "Logged out from all devices"
}
```

**Notes**:
- Blacklists all refresh tokens for the user
- Deletes all sessions from database

---

### 1.7. Get Current User
**Endpoint**: `GET /auth/users/me/`  
**Description**: Get authenticated user's profile  
**Permissions**: Authenticated

**Response**: `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "developer",
  "timezone": "Asia/Kolkata",
  "email_verified": true
}
```

---

### 1.8. List Users
**Endpoint**: `GET /auth/users/`  
**Description**: List users based on role permissions  
**Permissions**: Authenticated

**Visibility Rules**:
- **Auditor**: All users
- **Manager**: All developers + self
- **Developer**: Self only

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "developer",
    "timezone": "Asia/Kolkata",
    "email_verified": true
  }
]
```

---

## 2. Tasks

### 2.1. List Tasks
**Endpoint**: `GET /tasks/`  
**Description**: List tasks based on role permissions  
**Permissions**: Authenticated

**Visibility Rules**:
- **Auditor**: All tasks (read-only)
- **Manager**: All tasks
- **Developer**: Only tasks assigned to them

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "title": "Fix login bug",
    "description": "Login fails for...",
    "status": "in_progress",
    "priority": "high",
    "estimated_hours": 4.5,
    "actual_hours": 2.0,
    "deadline": "2024-01-15T18:00:00Z",
    "priority_escalated": false,
    "assigned_to": 2,
    "assigned_to_user": "john_doe",
    "created_by": 1,
    "created_by_user": "manager_user",
    "parent_task": null,
    "tags": [1, 2],
    "created_at": "2024-01-10T09:00:00Z",
    "updated_at": "2024-01-10T14:30:00Z"
  }
]
```

---

### 2.2. Get Single Task
**Endpoint**: `GET /tasks/{id}/`  
**Description**: Retrieve a specific task  
**Permissions**: Authenticated (must have access to task)

**Response**: `200 OK` (same structure as list)

---

### 2.3. Create Task
**Endpoint**: `POST /tasks/`  
**Description**: Create a new task  
**Permissions**: Authenticated (with time restrictions for developers)

**Time Restrictions**:
- **Developers**: Can only create tasks between 9:00 AM - 6:00 PM (user's timezone)
- **Managers**: No time restrictions
- **Auditors**: Cannot create tasks

**Request Body**:
```json
{
  "title": "Implement feature X",
  "description": "Detailed description...",
  "status": "pending",
  "priority": "medium",
  "estimated_hours": 8.0,
  "actual_hours": null,
  "deadline": "2024-01-20T18:00:00Z",
  "priority_escalated": false,
  "assigned_to": 2,
  "parent_task": null,
  "tags": [1, 3]
}
```

**Response**: `201 Created` (full task object)

**Notes**:
- `created_by` automatically set to current user
- Developers can only assign tasks to themselves
- Managers can assign to any user

---

### 2.4. Update Task
**Endpoint**: `PATCH /tasks/{id}/`  
**Description**: Update specific fields of a task  
**Permissions**: Authenticated (with role and time restrictions)

**Update Restrictions**:
- **Auditors**: Cannot update (read-only)
- **Managers**: Can update any task anytime
- **Developers**: 
  - Can update tasks between 9:00 AM - 6:00 PM (user's timezone)
  - **Exception**: Critical priority tasks can be updated anytime

**Request Body** (partial update):
```json
{
  "status": "completed",
  "actual_hours": 7.5
}
```

**Response**: `200 OK` (full task object)

---

### 2.5. Delete Task
**Endpoint**: `DELETE /tasks/{id}/`  
**Description**: Delete a task  
**Permissions**: Same as update

**Response**: `204 No Content`

---

### 2.6. Bulk Update Status
**Endpoint**: `POST /tasks/bulk-update/`  
**Description**: Update status for multiple tasks atomically  
**Permissions**: Authenticated (same restrictions as update)

**Request Body**:
```json
{
  "task_ids": [10, 11, 12],
  "status": "completed"
}
```

**Response**: `200 OK`
```json
{
  "updated_count": 3
}
```

**Notes**:
- Atomic transaction (all or nothing)
- Same time restrictions apply as single update

---

## 3. Analytics

### 3.1. Task Analytics
**Endpoint**: `GET /tasks/analytics/`  
**Description**: Get dashboard analytics and metrics  
**Permissions**: Authenticated

**Response**: `200 OK`
```json
{
  "my_tasks": {
    "total": 10,
    "completed": 5,
    "pending": 3,
    "in_progress": 2
  },
  "team_tasks": {
    "total": 50,
    "completed": 30
  },
  "efficiency_score": 85.5
}
```

**Notes**:
- `my_tasks`: Tasks assigned to current user
- `team_tasks`: All tasks (for managers/auditors) or team tasks (for developers)
- `efficiency_score`: Calculated based on completion rate and time estimates

---

## 4. Permissions & RBAC

### 4.1. Role-Based Access Control

| Role      | Task View | Task Create | Task Update | Task Delete | User View |
|-----------|-----------|-------------|-------------|-------------|-----------|
| Manager   | All       | ✅ Anytime  | ✅ Anytime  | ✅ Anytime  | Devs + Self |
| Developer | Assigned  | ✅ 9-18h*   | ✅ 9-18h*   | ✅ 9-18h*   | Self only |
| Auditor   | All       | ❌          | ❌          | ❌          | All       |

*Critical priority tasks can be updated anytime by developers

### 4.2. Time-Based Restrictions
- **Timezone**: User's configured timezone (default: Asia/Kolkata)
- **Working Hours**: 9:00 AM - 6:00 PM
- **Applies To**: Developers only (for create/update/delete operations)
- **Exception**: Critical priority tasks bypass time restrictions

---

## 5. Data Models

### 5.1. User
```typescript
{
  id: number;
  username: string;
  email: string;
  role: "manager" | "developer" | "auditor";
  timezone: string;  // e.g., "Asia/Kolkata"
  email_verified: boolean;
}
```

### 5.2. Task
```typescript
{
  id: number;
  title: string;
  description: string;
  status: "pending" | "in_progress" | "blocked" | "completed";
  priority: "low" | "medium" | "high" | "critical";
  estimated_hours: number;
  actual_hours: number | null;
  deadline: string;  // ISO 8601 datetime
  priority_escalated: boolean;
  assigned_to: number;  // User ID
  assigned_to_user: string;  // Username (read-only)
  created_by: number;  // User ID
  created_by_user: string;  // Username (read-only)
  parent_task: number | null;  // Parent task ID
  tags: number[];  // Tag IDs
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
}
```

### 5.3. Enums

**User Roles**:
- `manager`: Full access, no restrictions
- `developer`: Limited access, time-based restrictions (default role)
- `auditor`: Read-only access to all resources

**Task Status**:
- `pending`: Not started
- `in_progress`: Currently being worked on
- `blocked`: Blocked by dependencies or issues
- `completed`: Finished

**Task Priority**:
- `low`: Low priority
- `medium`: Medium priority
- `high`: High priority
- `critical`: Critical (bypasses time restrictions for developers)

---

## 6. Error Responses

### Common Error Codes

**400 Bad Request**:
```json
{
  "field_name": ["Error message"]
}
```

**401 Unauthorized**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden**:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found**:
```json
{
  "detail": "Not found."
}
```

---

## 7. Authentication Flow

### Standard Flow
1. **Register** → `POST /auth/register/`
2. **Verify Email** → `POST /auth/verify-email/`
3. **Login** → `POST /auth/login/` (receive access token + refresh cookie)
4. **Make Requests** → Include `Authorization: Bearer {access_token}` header
5. **Token Expires** → Frontend automatically calls `POST /auth/refresh/` (using cookie)
6. **Logout** → `POST /auth/logout/`

### Security Features
- ✅ HTTP-only cookies for refresh tokens (XSS protection)
- ✅ Automatic token blacklisting on logout
- ✅ Session limit (max 3 concurrent sessions)
- ✅ Secure and SameSite cookie attributes
- ✅ JWT-based access tokens with short expiration

---

## 8. Rate Limiting & Best Practices

### Best Practices
1. **Always include timezone** in user registration
2. **Use PATCH** for partial updates (not PUT)
3. **Handle 401 errors** by refreshing token automatically
4. **Respect time restrictions** in UI (disable buttons outside working hours)
5. **Use bulk operations** when updating multiple tasks
6. **Cache user profile** to reduce API calls

### Recommended Headers
```
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
```

---

**Last Updated**: 2026-01-11  
**Maintained By**: CTMS Development Team
