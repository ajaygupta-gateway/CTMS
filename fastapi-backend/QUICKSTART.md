# CTMS FastAPI Backend - Quick Start Guide

## Quick Start (3 Steps)

### 1. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Install uv (if not already installed)
- Create a virtual environment (.venv)
- Install all dependencies using uv
- Generate a secure secret key
- Create .env file with PostgreSQL configuration

### 2. Set Up PostgreSQL Database

Make sure PostgreSQL is running and create the database:

```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database and user
sudo -u postgres psql
CREATE DATABASE ctms_db;
CREATE USER ctms_user WITH PASSWORD 'ctms_password';
GRANT ALL PRIVILEGES ON DATABASE ctms_db TO ctms_user;
\q
```

Or use Docker for PostgreSQL:
```bash
docker run -d \
  --name ctms-postgres \
  -e POSTGRES_DB=ctms_db \
  -e POSTGRES_USER=ctms_user \
  -e POSTGRES_PASSWORD=ctms_password \
  -p 5432:5432 \
  postgres:15-alpine
```

### 3. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 4. Start the Server

```bash
python run.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Testing the API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "timezone": "Asia/Kolkata"
  }'
```

Response will include a `verification_token`.

### 2. Verify Email

```bash
curl -X POST http://localhost:8000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_VERIFICATION_TOKEN"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

Response will include an `access` token.

### 4. Get Current User

```bash
curl -X GET http://localhost:8000/api/auth/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Create a Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "This is a test task",
    "status": "pending",
    "priority": "medium",
    "estimated_hours": 5.0,
    "deadline": "2026-02-01T18:00:00Z",
    "assigned_to": 1,
    "tags": []
  }'
```

### 6. Get Analytics

```bash
curl -X GET http://localhost:8000/api/analytics \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI where you can:
- See all available endpoints
- Test API calls directly from the browser
- View request/response schemas
- Authenticate and make authorized requests

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API using the interactive docs at `/docs`
3. Check out the project structure in the README
4. Configure production settings in `.env`

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, change the `PORT` in `.env`:

```
PORT=8001
```

### Database Issues

Delete the database and restart:

```bash
rm ctms.db
python run.py
```

### Import Errors

Make sure you're in the virtual environment:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Development

### Running with Auto-Reload

The server runs with auto-reload by default in development mode. Any code changes will automatically restart the server.

### Viewing Logs

Logs are printed to the console. Set `LOG_LEVEL` in `.env` to control verbosity:

```
LOG_LEVEL=DEBUG  # For detailed logs
LOG_LEVEL=INFO   # For normal logs (default)
LOG_LEVEL=ERROR  # For errors only
```

## Production Deployment

For production deployment, see the "Production Deployment" section in [README.md](README.md).

Key changes for production:
1. Set `DEBUG=False`
2. Use PostgreSQL instead of SQLite
3. Use a strong `SECRET_KEY`
4. Configure proper CORS origins
5. Use Gunicorn with Uvicorn workers
6. Set up HTTPS/SSL
