from fastapi import Depends, HTTPException
from utils.api import Router
from dependencies.database import get_db
from dependencies.auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import Path
from dependencies.auth import check_role
from dependencies.auth import get_current_user

from ..models.activity_registration import ActivityMetadata as ActivityMetadataModel
from ..models.activity_registration import ActivityRegistration as ActivityRegistrationModel

from ..schemas.activity_registration import (
    ActivityMetadata as ActivityMetadataSchema,
    ActivityMetadataUpdate,
    ActivityRegistration as ActivityRegistrationSchema
)

router = Router()

@router.post("/metadata/{activity_id}", response_model=ActivityMetadataSchema)
def set_metadata(
    activity_id: int = Path(...),
    metadata: ActivityMetadataUpdate = Depends(),
    db: Session = Depends(get_db),
    user_info: dict = Depends(check_role(["manage_activities", "organizer"]))
):
    db_metadata = db.query(ActivityMetadataModel).filter_by(activity_id=activity_id).first()
    
    if db_metadata:
        db_metadata.is_restricted = metadata.is_restricted
        db_metadata.slots = metadata.slots
    else:
        db_metadata = ActivityMetadataModel(activity_id=activity_id, **metadata.dict())
        db.add(db_metadata)

    db.commit()
    db.refresh(db_metadata)
    return db_metadata

@router.post("/register/{activity_id}", response_model=ActivityRegistrationSchema)
def register_user(
    activity_id: int = Path(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    user_id = user["sub"]

    existing = db.query(ActivityRegistrationModel).filter_by(user_id=user_id, activity_id=activity_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this activity.")

    metadata = db.query(ActivityMetadataModel).filter_by(activity_id=activity_id).first()
    if metadata:
        total_registered = db.query(ActivityRegistrationModel).filter_by(activity_id=activity_id).count()
        if total_registered >= metadata.slots:
            raise HTTPException(status_code=400, detail="No more slots available for this activity.")

    registration = ActivityRegistrationModel(user_id=user_id, activity_id=activity_id)
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration

@router.get("/metadata/{activity_id}", response_model=ActivityMetadataSchema)
def get_metadata(
    activity_id: int = Path(...),
    db: Session = Depends(get_db)
):
    metadata = db.query(ActivityMetadataModel).filter_by(activity_id=activity_id).first()
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found for this activity.")
    return metadata

@router.get("/register/{activity_id}/is-registered", response_model=bool)
def is_user_registered(
    activity_id: int = Path(...),
    user_id: str = None,
    db: Session = Depends(get_db),
    _user: dict = Depends(check_role(["manage_activities", "organizer"])),
):
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id query parameter")

    registration = db.query(ActivityRegistrationModel).filter_by(activity_id=activity_id, user_id=user_id).first()
    return registration is not None