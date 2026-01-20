# PostgreSQL Setup Guide

This guide helps you set up PostgreSQL for the CTMS FastAPI backend.

## Why PostgreSQL?

- ✅ **Production-Ready**: Industry standard for web applications
- ✅ **Async Support**: Full async/await with asyncpg driver
- ✅ **Scalable**: Handles concurrent connections efficiently
- ✅ **Reliable**: ACID compliance and data integrity
- ✅ **Feature-Rich**: Advanced queries, indexes, and constraints

## Installation

### Ubuntu/Debian

```bash
# Update package list
sudo apt-get update

# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### macOS

```bash
# Using Homebrew
brew install postgresql@15

# Start service
brew services start postgresql@15

# Check status
brew services list
```

### Windows

1. Download installer from https://www.postgresql.org/download/windows/
2. Run installer and follow wizard
3. Remember the password you set for postgres user
4. PostgreSQL service starts automatically

## Database Setup

### Option 1: Local PostgreSQL

```bash
# Switch to postgres user (Linux/macOS)
sudo -u postgres psql

# Or connect directly (if configured)
psql -U postgres
```

Then run these SQL commands:

```sql
-- Create database
CREATE DATABASE ctms_db;

-- Create user
CREATE USER ctms_user WITH PASSWORD 'ctms_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ctms_db TO ctms_user;

-- Grant schema privileges (PostgreSQL 15+)
\c ctms_db
GRANT ALL ON SCHEMA public TO ctms_user;

-- Exit
\q
```

### Option 2: Docker PostgreSQL

**Quick Start:**
```bash
docker run -d \
  --name ctms-postgres \
  -e POSTGRES_DB=ctms_db \
  -e POSTGRES_USER=ctms_user \
  -e POSTGRES_PASSWORD=ctms_password \
  -p 5432:5432 \
  postgres:15-alpine
```

**With Persistence:**
```bash
docker run -d \
  --name ctms-postgres \
  -e POSTGRES_DB=ctms_db \
  -e POSTGRES_USER=ctms_user \
  -e POSTGRES_PASSWORD=ctms_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

**Using docker-compose:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: ctms-postgres
    environment:
      POSTGRES_DB: ctms_db
      POSTGRES_USER: ctms_user
      POSTGRES_PASSWORD: ctms_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Save as `docker-compose-db.yml` and run:
```bash
docker-compose -f docker-compose-db.yml up -d
```

## Configuration

### Update .env File

```bash
# Copy example
cp .env.example .env

# Edit .env
nano .env  # or your preferred editor
```

Update the DATABASE_URL:
```
DATABASE_URL=postgresql+asyncpg://ctms_user:ctms_password@localhost:5432/ctms_db
```

**Connection String Format:**
```
postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
```

### For Production

Use environment variables or secrets management:

```bash
# Example for production
DATABASE_URL=postgresql+asyncpg://prod_user:${DB_PASSWORD}@db.example.com:5432/ctms_prod
```

## Verify Connection

### Using psql

```bash
# Connect to database
psql -h localhost -U ctms_user -d ctms_db

# List databases
\l

# List tables (after running the app)
\dt

# Exit
\q
```

### Using Python

```python
import asyncio
import asyncpg

async def test_connection():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='ctms_user',
        password='ctms_password',
        database='ctms_db'
    )
    version = await conn.fetchval('SELECT version()')
    print(f"Connected to: {version}")
    await conn.close()

asyncio.run(test_connection())
```

### Using the FastAPI App

```bash
# Start the application
source .venv/bin/activate
python run.py

# Check logs for successful connection
# Visit health endpoint
curl http://localhost:8000/health
```

## Database Management

### Backup Database

```bash
# Backup to file
pg_dump -h localhost -U ctms_user ctms_db > backup.sql

# Backup with Docker
docker exec ctms-postgres pg_dump -U ctms_user ctms_db > backup.sql
```

### Restore Database

```bash
# Restore from file
psql -h localhost -U ctms_user ctms_db < backup.sql

# Restore with Docker
docker exec -i ctms-postgres psql -U ctms_user ctms_db < backup.sql
```

### Reset Database

```bash
# Drop and recreate
sudo -u postgres psql
DROP DATABASE ctms_db;
CREATE DATABASE ctms_db;
GRANT ALL PRIVILEGES ON DATABASE ctms_db TO ctms_user;
\q

# Then restart the FastAPI app to recreate tables
```

## Common Issues

### Issue: Connection Refused

**Solution**: Check if PostgreSQL is running
```bash
# Linux
sudo systemctl status postgresql

# macOS
brew services list

# Docker
docker ps | grep postgres
```

### Issue: Authentication Failed

**Solution**: Check credentials in .env match database user
```bash
# Reset password
sudo -u postgres psql
ALTER USER ctms_user WITH PASSWORD 'new_password';
\q

# Update .env with new password
```

### Issue: Database Does Not Exist

**Solution**: Create the database
```bash
sudo -u postgres psql
CREATE DATABASE ctms_db;
GRANT ALL PRIVILEGES ON DATABASE ctms_db TO ctms_user;
\q
```

### Issue: Permission Denied

**Solution**: Grant schema privileges (PostgreSQL 15+)
```bash
sudo -u postgres psql ctms_db
GRANT ALL ON SCHEMA public TO ctms_user;
\q
```

### Issue: Port Already in Use

**Solution**: Change port or stop conflicting service
```bash
# Check what's using port 5432
sudo lsof -i :5432

# Change PostgreSQL port
# Edit postgresql.conf and change port
# Update DATABASE_URL in .env accordingly
```

## Performance Tuning

### Connection Pooling

SQLAlchemy automatically manages connection pooling. Configure in `app/core/database.py`:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,          # Number of connections to maintain
    max_overflow=10,       # Additional connections when pool is full
    pool_pre_ping=True,    # Verify connections before using
)
```

### PostgreSQL Configuration

For production, tune PostgreSQL settings in `postgresql.conf`:

```conf
# Memory
shared_buffers = 256MB
effective_cache_size = 1GB

# Connections
max_connections = 100

# Performance
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200
```

## Monitoring

### Check Active Connections

```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'ctms_db';
```

### View Running Queries

```sql
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity 
WHERE datname = 'ctms_db';
```

### Database Size

```sql
SELECT pg_size_pretty(pg_database_size('ctms_db'));
```

## Security Best Practices

1. **Use Strong Passwords**: Generate secure passwords
   ```bash
   openssl rand -base64 32
   ```

2. **Limit Network Access**: Configure `pg_hba.conf`
   ```conf
   # Allow only localhost
   host    ctms_db    ctms_user    127.0.0.1/32    md5
   ```

3. **Use SSL**: Enable SSL connections in production
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
   ```

4. **Regular Backups**: Automate database backups
   ```bash
   # Cron job for daily backups
   0 2 * * * pg_dump -U ctms_user ctms_db > /backups/ctms_$(date +\%Y\%m\%d).sql
   ```

5. **Least Privilege**: Grant only necessary permissions
   ```sql
   REVOKE ALL ON DATABASE ctms_db FROM PUBLIC;
   GRANT CONNECT ON DATABASE ctms_db TO ctms_user;
   ```

## Resources

- **Official Docs**: https://www.postgresql.org/docs/
- **asyncpg**: https://magicstack.github.io/asyncpg/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **PostgreSQL Tutorial**: https://www.postgresqltutorial.com/

## Quick Reference

```bash
# Start PostgreSQL
sudo systemctl start postgresql        # Linux
brew services start postgresql@15      # macOS
docker start ctms-postgres             # Docker

# Connect to database
psql -h localhost -U ctms_user -d ctms_db

# Common psql commands
\l          # List databases
\c dbname   # Connect to database
\dt         # List tables
\d table    # Describe table
\q          # Quit

# Backup/Restore
pg_dump -U ctms_user ctms_db > backup.sql
psql -U ctms_user ctms_db < backup.sql
```

---

**Need Help?** Check the [troubleshooting section](#common-issues) or consult the PostgreSQL documentation.
