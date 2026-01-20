# Docker Deployment Guide

## Quick Start with Docker

### 1. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### 2. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Services

### Backend (FastAPI)
- Port: 8000
- Auto-restarts on failure
- Connected to PostgreSQL and Redis

### PostgreSQL
- Port: 5432
- Database: `ctms_db`
- User: `ctms_user`
- Password: `ctms_password`
- Data persisted in Docker volume

### Redis
- Port: 6379
- Used for caching and Celery tasks

## Environment Variables

Set environment variables in `docker-compose.yml` or create a `.env` file:

```bash
SECRET_KEY=your-super-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Production Deployment

### 1. Generate Secret Key

```bash
openssl rand -hex 32
```

### 2. Update docker-compose.yml

```yaml
environment:
  - SECRET_KEY=your-generated-secret-key
  - ALLOWED_ORIGINS=https://yourdomain.com
  - DEBUG=False
```

### 3. Use Production Database

Update the `DATABASE_URL` to use your production PostgreSQL instance.

### 4. Enable HTTPS

Use a reverse proxy like Nginx or Traefik:

```yaml
# Add to docker-compose.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
  depends_on:
    - backend
```

## Database Migrations

### Initialize Database

The database tables are created automatically on first run.

### Manual Migration (if needed)

```bash
# Access the backend container
docker-compose exec backend bash

# Run Python shell
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

## Backup and Restore

### Backup PostgreSQL

```bash
docker-compose exec db pg_dump -U ctms_user ctms_db > backup.sql
```

### Restore PostgreSQL

```bash
docker-compose exec -T db psql -U ctms_user ctms_db < backup.sql
```

## Scaling

### Run Multiple Backend Instances

```bash
docker-compose up -d --scale backend=3
```

Add a load balancer (Nginx) to distribute traffic.

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f redis
```

### Check Health

```bash
# Backend health
curl http://localhost:8000/health

# PostgreSQL
docker-compose exec db pg_isready -U ctms_user

# Redis
docker-compose exec redis redis-cli ping
```

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose build --no-cache backend
docker-compose up -d
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```

## Development with Docker

### Hot Reload

The `docker-compose.yml` mounts the `app` directory for hot reload during development.

### Run Commands in Container

```bash
# Python shell
docker-compose exec backend python

# Install new package
docker-compose exec backend pip install package-name

# Run tests
docker-compose exec backend pytest
```

## Security Best Practices

1. **Change Default Passwords**: Update PostgreSQL password in production
2. **Use Secrets**: Store sensitive data in Docker secrets or environment variables
3. **Network Isolation**: Use Docker networks to isolate services
4. **Regular Updates**: Keep Docker images updated
5. **HTTPS Only**: Use SSL/TLS in production
6. **Firewall**: Restrict access to database and Redis ports

## Production Checklist

- [ ] Generate and set secure `SECRET_KEY`
- [ ] Update database credentials
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_ORIGINS` for your domain
- [ ] Set up HTTPS/SSL
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging
- [ ] Configure firewall rules
- [ ] Test disaster recovery
- [ ] Document deployment process
