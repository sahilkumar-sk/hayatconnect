from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, OTPRequest, OTPVerify

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new donor or requester account."""
    # TODO: Week 2 — hash password, create user, return tokens
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/otp/send")
async def send_otp(payload: OTPRequest, db: AsyncSession = Depends(get_db)):
    """Send OTP to phone number for verification."""
    # TODO: Week 2 — Twilio integration
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/otp/verify")
async def verify_otp(payload: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verify phone OTP."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with phone + password, returns JWT tokens."""
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Exchange refresh token for new access token."""
    raise HTTPException(status_code=501, detail="Not implemented yet")
