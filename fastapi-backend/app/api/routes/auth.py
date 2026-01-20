from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User, UserSession, EmailVerificationToken
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RegisterResponse,
    EmailVerificationRequest,
    EmailVerificationResponse,
)
from app.api.dependencies import get_current_user, get_current_verified_user
from app.core.config import get_settings
import uuid
from datetime import datetime

settings = get_settings()
router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        timezone=user_data.timezone,
        email_verified=False,
    )
    db.add(user)
    await db.flush()
    
    # Create email verification token
    verification_token = str(uuid.uuid4())
    email_token = EmailVerificationToken(
        user_id=user.id,
        token=verification_token,
    )
    db.add(email_token)
    await db.commit()
    
    # In production, send email here
    # For development, return token in response
    return RegisterResponse(
        message="User registered. Verify email to activate account.",
        verification_token=verification_token
    )


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(data: EmailVerificationRequest, db: AsyncSession = Depends(get_db)):
    """Verify user email"""
    
    # Find verification token
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == data.token)
    )
    token_obj = result.scalar_one_or_none()
    
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == token_obj.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify email
    user.email_verified = True
    user.is_active = True
    
    # Delete verification token
    await db.delete(token_obj)
    await db.commit()
    
    return EmailVerificationResponse(message="Email verified successfully")


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token"""
    
    # Find user
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Generate device ID
    device_id = str(uuid.uuid4())
    
    # Check session limit
    result = await db.execute(
        select(UserSession)
        .where(UserSession.user_id == user.id)
        .order_by(UserSession.last_used)
    )
    sessions = result.scalars().all()
    
    # Delete oldest session if limit exceeded
    if len(sessions) >= settings.MAX_SESSIONS_PER_USER:
        oldest_session = sessions[0]
        await db.delete(oldest_session)
    
    # Create new session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        device_id=device_id,
    )
    db.add(session)
    await db.commit()
    
    # Set cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    response.set_cookie(
        key="device_id",
        value=device_id,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    return Token(access=access_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token from cookie"""
    
    refresh_token = request.cookies.get("refresh_token")
    device_id = request.cookies.get("device_id")
    
    if not refresh_token or not device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    # Decode token
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Find session
    result = await db.execute(
        select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.refresh_token == refresh_token,
            UserSession.device_id == device_id,
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Update session
    session.refresh_token = new_refresh_token
    session.last_used = datetime.utcnow()
    await db.commit()
    
    # Update cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    return Token(access=new_access_token)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout current session"""
    
    refresh_token = request.cookies.get("refresh_token")
    device_id = request.cookies.get("device_id")
    
    if refresh_token and device_id:
        # Delete session
        await db.execute(
            delete(UserSession).where(
                UserSession.user_id == current_user.id,
                UserSession.refresh_token == refresh_token,
                UserSession.device_id == device_id,
            )
        )
        await db.commit()
    
    # Clear cookies
    response.delete_cookie("refresh_token")
    response.delete_cookie("device_id")
    
    return {"detail": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout from all sessions"""
    
    # Delete all sessions
    await db.execute(
        delete(UserSession).where(UserSession.user_id == current_user.id)
    )
    await db.commit()
    
    # Clear cookies
    response.delete_cookie("refresh_token")
    response.delete_cookie("device_id")
    
    return {"detail": "Logged out from all devices"}


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_verified_user)):
    """Get current user profile"""
    return current_user


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """List users based on role permissions"""
    
    if current_user.is_auditor():
        # Auditors can see all users
        result = await db.execute(select(User))
        users = result.scalars().all()
    elif current_user.is_manager():
        # Managers can see all developers + self
        result = await db.execute(
            select(User).where(
                (User.role == "developer") | (User.id == current_user.id)
            )
        )
        users = result.scalars().all()
    else:
        # Developers can only see themselves
        users = [current_user]
    
    return users
