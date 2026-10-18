from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+92\d{10}$")  # Pakistani format
    email: str | None = None
    password: str = Field(..., min_length=8)
    blood_group: str | None = None
    role: str = "donor"  # donor | requester
    area: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+92\d{10}$")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+92\d{10}$")


class OTPVerify(BaseModel):
    phone: str = Field(..., pattern=r"^\+92\d{10}$")
    code: str = Field(..., min_length=6, max_length=6)


class RefreshRequest(BaseModel):
    refresh_token: str