from coffeebreak import Router

from .activity_registration import router as activity_registration_router

router = Router()
router.include_router(activity_registration_router, prefix="/activity-registration")

__all__ = ["router"]
