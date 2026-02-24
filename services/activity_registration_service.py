from fastapi import HTTPException
from sqlalchemy.orm import Session

from coffeebreak.auth import is_anonymous
from coffeebreak.models import ActivityModel

from ..models import ActivityRegistration, ActivityRegistrationMetadata
from ..schemas import (
    ActivityRegistrationMetadataResponse,
    ActivityRegistrationResponse,
    ActivityRegistrationSlotsResponse,
)


class ActivityRegistrationService:
    def __init__(self, db: Session):
        self.db = db

    def get_metadata(self, activity_id: int) -> ActivityRegistrationMetadataResponse:
        self._ensure_activity_exists(activity_id)
        metadata = self._get_metadata_record(activity_id)
        if metadata:
            return ActivityRegistrationMetadataResponse.model_validate(metadata)
        return ActivityRegistrationMetadataResponse(
            activity_id=activity_id, is_restricted=False, slots=None
        )

    def upsert_metadata(
        self, activity_id: int, is_restricted: bool, slots: int | None
    ) -> ActivityRegistrationMetadataResponse:
        self._ensure_activity_exists(activity_id)
        self._validate_metadata(is_restricted, slots)

        metadata = self._get_metadata_record(activity_id)
        if not metadata:
            metadata = ActivityRegistrationMetadata(activity_id=activity_id)
            self.db.add(metadata)

        metadata.is_restricted = is_restricted
        metadata.slots = slots
        self.db.commit()
        self.db.refresh(metadata)

        return ActivityRegistrationMetadataResponse.model_validate(metadata)

    def register(
        self, activity_id: int, user: dict | None, force_auth: bool = True
    ) -> ActivityRegistrationResponse:
        self._ensure_activity_exists(activity_id)

        if force_auth and (not user or is_anonymous(user)):
            raise HTTPException(status_code=401, detail="Authentication required")

        user_id = self._get_user_id(user)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        existing = (
            self.db.query(ActivityRegistration)
            .filter_by(activity_id=activity_id, user_id=user_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409, detail="User already registered for this activity"
            )

        metadata = self._get_metadata_record(activity_id)
        if metadata and metadata.is_restricted:
            if metadata.slots is None:
                raise HTTPException(
                    status_code=400, detail="Restricted activities must define slots"
                )

            registered = self._count_registered(activity_id)
            if registered >= metadata.slots:
                raise HTTPException(
                    status_code=409, detail="No available slots for this activity"
                )

        registration = ActivityRegistration(activity_id=activity_id, user_id=user_id)
        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)

        return ActivityRegistrationResponse.model_validate(registration)

    def get_available_slots(
        self, activity_id: int
    ) -> ActivityRegistrationSlotsResponse:
        self._ensure_activity_exists(activity_id)

        metadata = self._get_metadata_record(activity_id)
        is_restricted = metadata.is_restricted if metadata else False
        slots = metadata.slots if metadata else None
        registered = self._count_registered(activity_id)
        available = (
            max(slots - registered, 0) if is_restricted and slots is not None else None
        )

        return ActivityRegistrationSlotsResponse(
            activity_id=activity_id,
            slots=slots,
            registered=registered,
            available=available,
            is_restricted=is_restricted,
        )

    def _ensure_activity_exists(self, activity_id: int) -> None:
        activity = (
            self.db.query(ActivityModel).filter(ActivityModel.id == activity_id).first()
        )
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

    def _get_metadata_record(
        self, activity_id: int
    ) -> ActivityRegistrationMetadata | None:
        return (
            self.db.query(ActivityRegistrationMetadata)
            .filter_by(activity_id=activity_id)
            .first()
        )

    def _count_registered(self, activity_id: int) -> int:
        return (
            self.db.query(ActivityRegistration)
            .filter_by(activity_id=activity_id)
            .count()
        )

    def _get_user_id(self, user: dict | None) -> str | None:
        if not user:
            return None
        return user.get("sub")

    def _validate_metadata(self, is_restricted: bool, slots: int | None) -> None:
        if slots is not None and slots < 0:
            raise HTTPException(
                status_code=400, detail="Slots must be greater than or equal to 0"
            )
        if is_restricted and slots is None:
            raise HTTPException(
                status_code=400, detail="Slots are required when activity is restricted"
            )
