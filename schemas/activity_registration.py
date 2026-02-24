from datetime import datetime

from pydantic import BaseModel


class ActivityRegistrationMetadataUpdate(BaseModel):
    is_restricted: bool = False
    slots: int | None = None


class ActivityRegistrationMetadataResponse(BaseModel):
    activity_id: int
    is_restricted: bool
    slots: int | None = None

    class Config:
        from_attributes = True


class ActivityRegistrationResponse(BaseModel):
    id: int
    activity_id: int
    user_id: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ActivityRegistrationSlotsResponse(BaseModel):
    activity_id: int
    slots: int | None = None
    registered: int
    available: int | None = None
    is_restricted: bool
