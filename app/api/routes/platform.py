from fastapi import APIRouter

from app.models.platform import (
    ComponentHealth,
    PlatformHealthResponse,
)
from app.services.awx import check_awx_health


router = APIRouter(
    prefix="/api/v1/platform",
    tags=["Platform"],
)


@router.get(
    "/health",
    response_model=PlatformHealthResponse,
)
async def platform_health() -> PlatformHealthResponse:
    awx_result = await check_awx_health()

    awx_health = ComponentHealth(**awx_result)

    overall_status = (
        "healthy"
        if awx_health.status == "healthy"
        else "unhealthy"
    )

    return PlatformHealthResponse(
        status=overall_status,
        components=[awx_health],
    )
