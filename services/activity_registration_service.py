from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.activity_registration import ActivityMetadata as ActivityMetadataModel
from ..models.activity_registration import ActivityRegistration as ActivityRegistrationModel
from ..schemas.activity_registration import SlotAvailability
from ..utils.user import get_user_id

def set_metadata_service(activity_id: int, metadata, db: Session):
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

def register_user_service(activity_id: int, user: dict, db: Session):
    user_id = get_user_id(user)

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

def deregister_user_service(activity_id: int, user: dict, db: Session):
    user_id = get_user_id(user)

    registration = db.query(ActivityRegistrationModel).filter_by(user_id=user_id, activity_id=activity_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="No registration found for this activity.")

    db.delete(registration)
    db.commit()
    return {"activity_id": activity_id, "user_id": user_id}

def get_metadata_service(activity_id: int, db: Session):
    metadata = db.query(ActivityMetadataModel).filter_by(activity_id=activity_id).first()
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found for this activity.")
    return metadata

def is_user_registered_service(activity_id: int, user_id: str, db: Session):
    registration = db.query(ActivityRegistrationModel).filter_by(activity_id=activity_id, user_id=user_id).first()
    return registration is not None

def get_available_slots_service(activity_id: int, db: Session):
    metadata = db.query(ActivityMetadataModel).filter_by(activity_id=activity_id).first()
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found for this activity.")

    if not metadata.is_restricted:
        return SlotAvailability(message="Available slots are not restricted.")

    total_registered = db.query(ActivityRegistrationModel).filter_by(activity_id=activity_id).count()
    available_slots = metadata.slots - total_registered

    return SlotAvailability(
        available_slots=max(available_slots, 0),
        total_slots=metadata.slots,
        registered=total_registered
    )