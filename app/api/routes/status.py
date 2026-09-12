from fastapi import APIRouter

from app.models.platform import PlatformStatusResponse
from app.services.aggregator import PlatformAggregator


router = APIRouter(
    prefix="/api/v1",
    tags=["Platform"],
)


aggregator = PlatformAggregator()


@router.get(
    "/status",
    response_model=PlatformStatusResponse,
)
async def platform_status() -> PlatformStatusResponse:

    return await aggregator.collect()
