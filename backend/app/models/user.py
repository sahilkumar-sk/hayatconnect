import uuid
from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    DONOR = "donor"
    REQUESTER = "requester"
    ADMIN = "admin"


class BloodGroup(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, values_callable=lambda e: [m.value for m in e]), default=UserRole.DONOR, nullable=False
    )
    blood_group: Mapped[BloodGroup | None] = mapped_column(SAEnum(BloodGroup, values_callable=lambda e: [m.value for m in e]), nullable=True)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Donor-specific
    last_donation_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_hours_start: Mapped[int | None] = mapped_column(nullable=True)  # 0-23
    preferred_hours_end: Mapped[int | None] = mapped_column(nullable=True)
    reliability_score: Mapped[float] = mapped_column(Float, default=50.0)

    # Phone verification
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    blood_requests = relationship("BloodRequest", back_populates="requester")
    donor_responses = relationship("DonorResponse", back_populates="donor")
