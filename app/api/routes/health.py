from fastapi import APIRouter

from app.models.health import HealthResponse


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="platform-health",
        version="0.1.0",
    )
