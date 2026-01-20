import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "timezone": "Asia/Kolkata"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "verification_token" in data


@pytest.mark.asyncio
async def test_register_duplicate_username():
    """Test registration with duplicate username"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "user1@example.com",
                "password": "SecurePass123!",
            }
        )
        
        # Second registration with same username
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "email": "user2@example.com",
                "password": "SecurePass123!",
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_unverified_user():
    """Test login with unverified email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post(
            "/api/auth/register",
            json={
                "username": "unverified",
                "email": "unverified@example.com",
                "password": "SecurePass123!",
            }
        )
        
        # Try to login without verification
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "unverified",
                "password": "SecurePass123!",
            }
        )
        assert response.status_code == 403
        assert "not verified" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_complete_auth_flow():
    """Test complete authentication flow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Register
        register_response = await client.post(
            "/api/auth/register",
            json={
                "username": "fullflow",
                "email": "fullflow@example.com",
                "password": "SecurePass123!",
            }
        )
        assert register_response.status_code == 201
        token = register_response.json()["verification_token"]
        
        # 2. Verify email
        verify_response = await client.post(
            "/api/auth/verify-email",
            json={"token": token}
        )
        assert verify_response.status_code == 200
        
        # 3. Login
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "fullflow",
                "password": "SecurePass123!",
            }
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access"]
        
        # 4. Get current user
        me_response = await client.get(
            "/api/auth/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["username"] == "fullflow"
        assert user_data["email"] == "fullflow@example.com"


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/auth/users/me")
        assert response.status_code == 403  # No credentials provided


@pytest.mark.asyncio
async def test_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/auth/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


# Run tests with: pytest tests/test_api.py -v
