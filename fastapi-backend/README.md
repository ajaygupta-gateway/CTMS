# CTMS FastAPI Backend

A modern, high-performance backend for the Clinical Trial Management System built with FastAPI.

## Features

- ✅ **Async/Await**: Full async support with SQLAlchemy 2.0
- ✅ **JWT Authentication**: Secure token-based authentication with refresh tokens
- ✅ **Role-Based Access Control (RBAC)**: Manager, Developer, and Auditor roles
- ✅ **Time-Based Permissions**: Working hours restrictions for developers
- ✅ **Task Management**: Complete CRUD operations with bulk updates
- ✅ **Analytics**: Task metrics and efficiency scoring
- ✅ **Session Management**: Multi-device session tracking with limits
- ✅ **Email Verification**: User email verification flow
- ✅ **API Documentation**: Auto-generated OpenAPI/Swagger docs
- ✅ **Type Safety**: Full Pydantic validation and type hints
- ✅ **Database Migrations**: Alembic support (optional)

## Project Structure

```
fastapi-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Settings and configuration
│   │   ├── database.py        # Database setup and session management
│   │   └── security.py        # Authentication and password hashing
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py            # User, UserSession, EmailVerificationToken
│   │   ├── task.py            # Task, Tag, TaskHistory
│   │   ├── notification.py    # Notification
│   │   └── audit.py           # APIAuditLog
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py            # User request/response schemas
│   │   ├── task.py            # Task request/response schemas
│   │   ├── analytics.py       # Analytics schemas
│   │   └── notification.py    # Notification schemas
│   └── api/                    # API routes
│       ├── dependencies.py    # Shared dependencies (auth, permissions)
│       ├── router.py          # Main API router
│       └── routes/            # Route modules
│           ├── auth.py        # Authentication endpoints
│           ├── tasks.py       # Task management endpoints
│           └── analytics.py   # Analytics endpoints
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── run.py                     # Application runner
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ (or Docker)
- uv (will be installed automatically by setup script)

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd fastapi-backend
   ```

2. **Set up PostgreSQL**:
   
   **Option A: Local PostgreSQL**
   ```bash
   # Install PostgreSQL
   sudo apt-get install postgresql  # Ubuntu/Debian
   brew install postgresql          # macOS
   
   # Create database
   sudo -u postgres psql
   CREATE DATABASE ctms_db;
   CREATE USER ctms_user WITH PASSWORD 'ctms_password';
   GRANT ALL PRIVILEGES ON DATABASE ctms_db TO ctms_user;
   \q
   ```
   
   **Option B: Docker PostgreSQL**
   ```bash
   docker run -d \
     --name ctms-postgres \
     -e POSTGRES_DB=ctms_db \
     -e POSTGRES_USER=ctms_user \
     -e POSTGRES_PASSWORD=ctms_password \
     -p 5432:5432 \
     postgres:15-alpine
   ```

3. **Run the setup script** (installs uv and dependencies):
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

5. **Run the application**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your configuration:
   ```bash
   # Generate a secure secret key
   openssl rand -hex 32
   ```
   
   Update `SECRET_KEY` in `.env` with the generated key.

5. **Run the application**:
   ```bash
   python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/verify-email` - Verify email with token
- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout current session
- `POST /api/auth/logout-all` - Logout all sessions
- `GET /api/auth/users/me` - Get current user profile
- `GET /api/auth/users` - List users (RBAC filtered)

### Tasks (`/api/tasks`)

- `GET /api/tasks` - List tasks (RBAC filtered)
- `GET /api/tasks/{id}` - Get specific task
- `POST /api/tasks` - Create new task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/bulk-update` - Bulk update task status

### Analytics (`/api/analytics`)

- `GET /api/analytics` - Get task analytics and metrics

## Authentication Flow

1. **Register**: `POST /api/auth/register`
2. **Verify Email**: `POST /api/auth/verify-email` with token
3. **Login**: `POST /api/auth/login` (returns access token + refresh cookie)
4. **Make Requests**: Include `Authorization: Bearer <access_token>` header
5. **Refresh Token**: `POST /api/auth/refresh` (automatic via cookie)
6. **Logout**: `POST /api/auth/logout`

## Role-Based Access Control

| Role      | Task View | Task Create | Task Update | Task Delete | User View    |
|-----------|-----------|-------------|-------------|-------------|--------------|
| Manager   | All       | ✅ Anytime  | ✅ Anytime  | ✅ Anytime  | Devs + Self  |
| Developer | Assigned  | ✅ 9-18h*   | ✅ 9-18h*   | ✅ 9-18h*   | Self only    |
| Auditor   | All       | ❌          | ❌          | ❌          | All          |

*Critical priority tasks can be updated anytime by developers

## Time-Based Restrictions

- **Timezone**: User's configured timezone (default: Asia/Kolkata)
- **Working Hours**: 9:00 AM - 6:00 PM
- **Applies To**: Developers only (for create/update/delete operations)
- **Exception**: Critical priority tasks bypass time restrictions

## Database

The application uses SQLAlchemy 2.0 with async support and **PostgreSQL** as the primary database:

- **Development**: PostgreSQL (recommended)
- **Production**: PostgreSQL

### PostgreSQL Configuration

The default configuration in `.env`:
```
DATABASE_URL=postgresql+asyncpg://ctms_user:ctms_password@localhost:5432/ctms_db
```

### Alternative: SQLite (Not Recommended)

For quick testing only, you can use SQLite:
```
DATABASE_URL=sqlite+aiosqlite:///./ctms.db
```

**Note**: SQLite has limitations with async operations and concurrent connections. Use PostgreSQL for development and production.

## Development

### Installing New Packages

```bash
# Add a new dependency
uv pip install package-name

# Add to pyproject.toml
# Edit pyproject.toml and add to dependencies list
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

The project follows PEP 8 style guidelines. Use tools like `black` and `flake8`:

```bash
pip install black flake8
black app/
flake8 app/
```

### Database Migrations (Optional)

If you want to use Alembic for migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Production Deployment

### Using Gunicorn + Uvicorn Workers

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ctms-backend .
docker run -p 8000:8000 ctms-backend
```

### Environment Variables for Production

Update `.env` for production:

```bash
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<your-secure-secret-key>
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/ctms_db
ALLOWED_ORIGINS=https://yourdomain.com
```

## Security Best Practices

- ✅ HTTP-only cookies for refresh tokens (XSS protection)
- ✅ Automatic token blacklisting on logout
- ✅ Session limit (max 3 concurrent sessions)
- ✅ Secure and SameSite cookie attributes
- ✅ JWT-based access tokens with short expiration
- ✅ Password hashing with bcrypt
- ✅ CORS configuration
- ✅ Input validation with Pydantic

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Comparison with Django Backend

This FastAPI backend is a modern reimplementation of the Django backend with:

- ✅ **Better Performance**: Async/await for concurrent request handling
- ✅ **Type Safety**: Full Pydantic validation and type hints
- ✅ **Auto Documentation**: Built-in OpenAPI/Swagger docs
- ✅ **Simpler Deployment**: Single ASGI server, no separate web server needed
- ✅ **Modern Python**: Uses latest Python features and best practices
- ✅ **Same Functionality**: All features from Django backend implemented

## License

This project is part of the CTMS (Clinical Trial Management System).

## Support

For issues or questions, please contact the development team.
