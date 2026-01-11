# Swagger/OpenAPI Setup Guide

## Installation

Install drf-spectacular package:

```bash
pip install drf-spectacular
```

## Configuration

The following has been configured in your Django project:

### 1. INSTALLED_APPS (config/settings/base.py)
```python
INSTALLED_APPS = [
    # ...
    "drf_spectacular",  # Added for Swagger
]
```

### 2. REST_FRAMEWORK Settings
```python
REST_FRAMEWORK = {
    # ...
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```

### 3. SPECTACULAR_SETTINGS
```python
SPECTACULAR_SETTINGS = {
    "TITLE": "CTMS API",
    "DESCRIPTION": "Conditional Task Management System - Complete API Documentation",
    "VERSION": "1.0.0",
    "SECURITY": [{"Bearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}],
}
```

### 4. URLs (config/urls.py)
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # ...
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
```

## Usage

### 1. Install the package
```bash
cd backend
pip install drf-spectacular
```

### 2. Run migrations (if needed)
```bash
python manage.py migrate
```

### 3. Start the server
```bash
python manage.py runserver
```

### 4. Access Swagger UI

Open your browser to:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema (JSON)**: http://localhost:8000/api/schema/

## Using Swagger UI

### Authentication
1. Click the **"Authorize"** button (top right)
2. Enter your JWT token in the format: `Bearer <your_access_token>`
3. Click **"Authorize"** then **"Close"**
4. All subsequent requests will include the token

### Getting a Token
1. Use the `/api/auth/login/` endpoint in Swagger
2. Click **"Try it out"**
3. Enter credentials:
   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```
4. Click **"Execute"**
5. Copy the `access` token from the response
6. Use it in the Authorize dialog

### Testing Endpoints
1. Navigate to any endpoint
2. Click **"Try it out"**
3. Fill in required parameters
4. Click **"Execute"**
5. View the response

## Features

✅ **Interactive API Testing**: Test all endpoints directly from the browser
✅ **Authentication Support**: JWT Bearer token authentication
✅ **Auto-Generated**: Documentation generated from your Django views
✅ **Request/Response Examples**: See example payloads for all endpoints
✅ **Schema Validation**: Validates requests against OpenAPI schema
✅ **Multiple Formats**: Swagger UI and ReDoc interfaces

## Customization

### Adding Descriptions to Views

```python
from drf_spectacular.utils import extend_schema

class MyViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="Create a new task",
        description="Creates a new task with the provided data",
        tags=["Tasks"],
    )
    def create(self, request):
        # ...
```

### Adding Examples

```python
from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    examples=[
        OpenApiExample(
            "Valid Example",
            value={"username": "john_doe", "password": "SecurePass123!"},
            request_only=True,
        )
    ]
)
def login(request):
    # ...
```

## Troubleshooting

**Issue**: Swagger UI not loading
- Ensure `drf-spectacular` is installed
- Check `INSTALLED_APPS` includes `"drf_spectacular"`
- Verify URLs are configured correctly

**Issue**: Endpoints not showing
- Ensure views inherit from DRF viewsets/views
- Check `DEFAULT_SCHEMA_CLASS` is set in `REST_FRAMEWORK`

**Issue**: Authentication not working
- Use format: `Bearer <token>` (with space)
- Ensure token is valid and not expired
- Check token is from `/api/auth/login/` endpoint
