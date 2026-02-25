from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from coffeebreak import Router
from coffeebreak.auth import check_role, get_current_user
from coffeebreak.db import DB as get_db

from ..schemas import (
    ActivityRegistrationMetadataResponse,
    ActivityRegistrationMetadataUpdate,
    ActivityRegistrationResponse,
    ActivityRegistrationSlotsResponse,
)
from ..services import ActivityRegistrationService

router = Router()


def _parse_slots(slots: str | None) -> int | None:
    if slots is None:
        return None

    value = slots.strip()
    if not value or value.lower() == "nan":
        return None

    try:
        return int(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid slots value") from exc


@router.get(
    "/metadata/{activity_id}", response_model=ActivityRegistrationMetadataResponse
)
def get_activity_metadata(activity_id: int, db: Session = Depends(get_db)):
    return ActivityRegistrationService(db).get_metadata(activity_id)


@router.post(
    "/metadata/{activity_id}", response_model=ActivityRegistrationMetadataResponse
)
def upsert_activity_metadata(
    activity_id: int,
    is_restricted: bool = Query(default=False),
    slots: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"])),
):
    parsed_slots = _parse_slots(slots)
    payload = ActivityRegistrationMetadataUpdate(
        is_restricted=is_restricted,
        slots=parsed_slots,
    )
    return ActivityRegistrationService(db).upsert_metadata(
        activity_id, payload.is_restricted, payload.slots
    )


@router.post("/register/{activity_id}", response_model=ActivityRegistrationResponse)
def register_for_activity(
    activity_id: int,
    force_auth: bool = Query(default=True),
    db: Session = Depends(get_db),
    user: dict | None = Depends(get_current_user(force_auth=False)),
):
    return ActivityRegistrationService(db).register(activity_id, user, force_auth)


@router.get(
    "/register/{activity_id}/available-slots/",
    response_model=ActivityRegistrationSlotsResponse,
)
def get_available_slots(activity_id: int, db: Session = Depends(get_db)):
    return ActivityRegistrationService(db).get_available_slots(activity_id)
