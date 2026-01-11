# CTMS - Conditional Task Management System

A comprehensive task management system built with Django REST Framework and React, featuring role-based access control, real-time updates, and advanced task visualization.

## 🚀 Features

- **Role-Based Access Control (RBAC)**: Manager, Developer, and Auditor roles with granular permissions
- **Time-Based Restrictions**: Developers can only create/update tasks during working hours (9 AM - 6 PM)
- **Secure Authentication**: JWT tokens with HTTP-only cookie refresh tokens
- **Advanced Dashboard**: 
  - Drag-and-drop Kanban board
  - Task dependency graph visualization
  - Real-time analytics
- **Optimistic UI**: Instant feedback with automatic rollback on errors
- **Email Verification**: Secure account activation flow
- **Session Management**: Multi-device support with session limits

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Tech Stack](#tech-stack)

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and **npm** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))
- **pip** (Python package manager, comes with Python)

---

## 🐍 Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers pytz drf-spectacular
```

**Key Packages:**
- `django` - Web framework
- `djangorestframework` - REST API framework
- `djangorestframework-simplejwt` - JWT authentication
- `django-cors-headers` - CORS support
- `pytz` - Timezone support
- `drf-spectacular` - Swagger/OpenAPI documentation

### 4. Environment Configuration

Create a `.env` file in the `backend/` directory (or copy from `.env.example`):

```bash
cp .env.example .env
```

**Required variables**:
```env
SECRET_KEY=your-secret-key-here
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_ORIGINS=http://localhost:5173
```

**Generate a secure SECRET_KEY**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 6. Start Development Server

```bash
python manage.py runserver
```

The backend API will be available at: **http://localhost:8000**

**Admin Panel**: http://localhost:8000/admin  
**Swagger UI (API Docs)**: http://localhost:8000/api/docs/  
**ReDoc (Alternative Docs)**: http://localhost:8000/api/redoc/

---

## ⚛️ Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

**Key Dependencies:**
- `react` & `react-dom` - UI library
- `react-router-dom` - Routing
- `axios` - HTTP client
- `@dnd-kit/*` - Drag-and-drop
- `reactflow` - Dependency graph
- `date-fns` - Date utilities
- `lucide-react` - Icons
- `tailwindcss` - Styling

### 3. Environment Configuration

The frontend uses Vite's proxy configuration (already set in `vite.config.ts`):

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    }
  }
}
```

No additional `.env` file needed for development.

### 4. Start Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

---

## 🏃 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

1. Open browser to **http://localhost:5173**
2. Register a new account
3. Verify email (token shown in response)
4. Login and start using the system

### Default Users

After running migrations, you can create test users via Django admin or the registration flow.

**Roles:**
- `manager` - Full access, no restrictions
- `developer` - Limited access, time-based restrictions (default)
- `auditor` - Read-only access

---

## 📁 Project Structure

```
ctms/
├── backend/                    # Django backend
│   ├── apps/                  # Django applications
│   │   ├── users/            # Authentication & user management
│   │   ├── tasks/            # Task CRUD operations
│   │   ├── analytics/        # Dashboard analytics
│   │   ├── audit/            # Audit logging
│   │   ├── notifications/    # Notification system
│   │   ├── security/         # Security features
│   │   └── common/           # Shared utilities
│   ├── config/               # Django settings
│   ├── manage.py             # Django CLI
│   └── db.sqlite3            # SQLite database
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── api/              # API service layer
│   │   ├── components/       # React components
│   │   ├── context/          # React Context (state)
│   │   ├── lib/              # Utilities (axios, etc.)
│   │   ├── pages/            # Page components
│   │   ├── types/            # TypeScript types
│   │   └── App.tsx           # Root component
│   ├── public/               # Static assets
│   └── package.json          # Dependencies
│
├── backend_documentation.md   # Backend API reference
├── frontend_documentation.md  # Frontend architecture guide
└── README.md                  # This file
```

---

## 📚 Documentation

- **[Backend Documentation](BACKEND_DOCUMENTATION.md)** - Complete API reference, RBAC, permissions, and architecture
- **[Frontend Documentation](FRONTEND_DOCUMENTATION.md)** - Component guide, state management, and development patterns
- **[Database Schema](DATABASE_SCHEMA.md)** - Entity relationship diagram and model descriptions
- **[Swagger Setup](SWAGGER_SETUP.md)** - Interactive API documentation guide

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.1
- **API**: Django REST Framework
- **Authentication**: Simple JWT (HTTP-only cookies)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **CORS**: django-cors-headers

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React Context API
- **DnD**: @dnd-kit
- **Graphs**: ReactFlow
- **Icons**: Lucide React

---

## 🔐 Security Features

- ✅ HTTP-only cookies for refresh tokens (XSS protection)
- ✅ JWT-based access tokens with short expiration
- ✅ Automatic token blacklisting on logout
- ✅ Session limit (max 3 concurrent sessions)
- ✅ RBAC with granular permissions
- ✅ Time-based access restrictions
- ✅ CORS configuration
- ✅ CSRF protection

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test  # (if tests are configured)
```

---

## 📦 Building for Production

### Backend
```bash
cd backend
# Update settings for production
# Set DEBUG=False in .env
# Configure PostgreSQL database
# Collect static files
python manage.py collectstatic --noinput
```

### Frontend
```bash
cd frontend
npm run build
# Output in dist/ directory
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

**Database locked:**
```bash
# Delete db.sqlite3 and re-run migrations
rm db.sqlite3
python manage.py migrate
```

### Frontend Issues

**Port 5173 already in use:**
```bash
# Kill process or change port in vite.config.ts
```

**Module not found:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
- Ensure backend is running on port 8000
- Check CORS_ALLOWED_ORIGINS in backend .env
- Verify Vite proxy configuration

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 👥 Authors

- **CTMS Development Team**

---

## 🙏 Acknowledgments

- Django REST Framework documentation
- React and Vite communities
- shadcn/ui for beautiful components
- All open-source contributors

---

**Last Updated**: 2026-01-11  
**Version**: 1.0.0
