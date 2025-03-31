from utils.api import Router
from .activity_registration import router as registration_router

router = Router()
router.include_router(registration_router, "/activity-registration")

__all__ = ["router"]
