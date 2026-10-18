from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole, BloodGroup
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    OTPRequest,
    OTPVerify,
    RefreshRequest,
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_token_pair,
    decode_token,
    create_access_token,
)
from app.services.otp_service import send_otp as otp_send, verify_otp as otp_verify

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new donor or requester account."""

    # Check if phone already exists
    result = await db.execute(select(User).where(User.phone == payload.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    # Check if email already exists (if provided)
    if payload.email:
        result = await db.execute(select(User).where(User.email == payload.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    # Create user
    user = User(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole(payload.role),
        blood_group=BloodGroup(payload.blood_group) if payload.blood_group else None,
        area=payload.area,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )

    db.add(user)
    await db.flush()  # Get user.id without committing

    tokens = create_token_pair(user.id, user.role.value)
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with phone + password, returns JWT tokens."""

    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password",
        )

    tokens = create_token_pair(user.id, user.role.value)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange refresh token for a new access token."""

    token_data = decode_token(payload.refresh_token)

    if token_data is None or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = token_data["sub"]

    # Verify user still exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Return new token pair
    tokens = create_token_pair(user.id, user.role.value)
    return TokenResponse(**tokens)


@router.post("/otp/send")
async def send_otp_endpoint(payload: OTPRequest):
    """Send OTP to phone number for verification."""
    await otp_send(payload.phone)
    return {"message": "OTP sent successfully"}


@router.post("/otp/verify")
async def verify_otp_endpoint(payload: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verify phone OTP and mark user's phone as verified."""
    is_valid = await otp_verify(payload.phone, payload.code)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # Mark phone as verified
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()

    if user:
        user.is_phone_verified = True

    return {"message": "Phone verified successfully"}