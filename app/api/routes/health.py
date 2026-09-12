from fastapi import APIRouter

from app.core.config import settings
from app.models.health import HealthResponse


router = APIRouter(
    tags=["Health"]
)


@router.get(
    "/health/live",
    response_model=HealthResponse,
)
async def liveness() -> HealthResponse:

    return HealthResponse(
        status="alive",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/health/ready",
    response_model=HealthResponse,
)
async def readiness() -> HealthResponse:

    return HealthResponse(
        status="ready",
        service=settings.app_name,
        version=settings.app_version,
    )
