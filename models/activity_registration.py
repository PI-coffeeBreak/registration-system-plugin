from datetime import datetime
from dependencies.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint

class ActivityMetadata(Base):
    __tablename__ = "activity_registration_metadata"

    activity_id = Column(Integer, ForeignKey("activities.id"), primary_key=True)
    is_restricted = Column(Boolean, default=False)
    slots = Column(Integer, nullable=False)

class ActivityRegistration(Base):
    __tablename__ = "activity_registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "activity_id", name="unique_user_activity"),
    )
