from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ActivityMetadataCreate(BaseModel):
    activity_id: int
    is_restricted: bool = False
    slots: int

class ActivityMetadataUpdate(BaseModel):
    is_restricted: bool = False
    slots: int

class ActivityMetadata(ActivityMetadataCreate):
    class Config:
        from_attributes = True

class ActivityRegistrationCreate(BaseModel):
    activity_id: int

class ActivityRegistration(BaseModel):
    id: int
    user_id: str
    activity_id: int
    registered_at: datetime

    class Config:
        from_attributes = True

class SlotAvailability(BaseModel):
    available_slots: Optional[int] = None
    total_slots: Optional[int] = None
    registered: Optional[int] = None
    message: Optional[str] = None

class DeregistrationResponse(BaseModel):
    activity_id: int
    user_id: str