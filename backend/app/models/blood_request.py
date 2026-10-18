import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base
from app.models.user import BloodGroup


class UrgencyLevel(str, enum.Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class RequestStatus(str, enum.Enum):
    OPEN = "open"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    patient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    blood_group_needed: Mapped[BloodGroup] = mapped_column(
        SAEnum(BloodGroup), nullable=False
    )
    units_needed: Mapped[int] = mapped_column(Integer, default=1)
    units_fulfilled: Mapped[int] = mapped_column(Integer, default=0)
    hospital_name: Mapped[str] = mapped_column(String(200), nullable=False)
    hospital_address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    hospital_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    hospital_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    urgency: Mapped[UrgencyLevel] = mapped_column(
        SAEnum(UrgencyLevel), default=UrgencyLevel.URGENT
    )
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus), default=RequestStatus.OPEN
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    requester = relationship("User", back_populates="blood_requests")
    donor_responses = relationship("DonorResponse", back_populates="blood_request")
