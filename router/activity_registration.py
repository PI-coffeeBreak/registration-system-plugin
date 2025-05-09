from fastapi import Depends, HTTPException, Path
from utils.api import Router
from dependencies.database import get_db
from dependencies.auth import get_current_user, check_role
from sqlalchemy.orm import Session
from ..schemas.activity_registration import (
    ActivityMetadata as ActivityMetadataSchema,
    ActivityMetadataUpdate,
    ActivityRegistration as ActivityRegistrationSchema,
    SlotAvailability,
    DeregistrationResponse
)
from ..services.activity_registration_service import (
    set_metadata_service,
    register_user_service,
    deregister_user_service,
    get_metadata_service,
    is_user_registered_service,
    get_available_slots_service
)

router = Router()

@router.post("/metadata/{activity_id}", response_model=ActivityMetadataSchema)
def set_metadata(
    activity_id: int = Path(...),
    metadata: ActivityMetadataUpdate = Depends(),
    db: Session = Depends(get_db),
    user_info: dict = Depends(check_role(["manage_activities", "organizer"]))
):
    return set_metadata_service(activity_id, metadata, db)

@router.post("/register/{activity_id}", response_model=ActivityRegistrationSchema)
def register_user(
    activity_id: int = Path(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user(force_auth=True))
):
    return register_user_service(activity_id, user, db)

@router.delete("/deregister/{activity_id}", response_model=DeregistrationResponse)
def deregister_user(
    activity_id: int = Path(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user(force_auth=True))
):
    return deregister_user_service(activity_id, user, db)

@router.get("/metadata/{activity_id}", response_model=ActivityMetadataSchema)
def get_metadata(
    activity_id: int = Path(...),
    db: Session = Depends(get_db)
):
    return get_metadata_service(activity_id, db)

@router.get("/register/{activity_id}/is-registered", response_model=bool)
def is_user_registered(
    activity_id: int = Path(...),
    user_id: str = None,
    db: Session = Depends(get_db),
    _user: dict = Depends(check_role(["manage_activities", "organizer"])),
):
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id query parameter")
    return is_user_registered_service(activity_id, user_id, db)

@router.get("/register/{activity_id}/available-slots", response_model=SlotAvailability)
def get_available_slots(
    activity_id: int = Path(...),
    db: Session = Depends(get_db)
):
    return get_available_slots_service(activity_id, db)