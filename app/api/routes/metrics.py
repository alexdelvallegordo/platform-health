from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from app.services.aggregator import PlatformAggregator


router = APIRouter(
    tags=["Observability"]
)

aggregator = PlatformAggregator()


@router.get(
    "/metrics",
    include_in_schema=False,
)
async def metrics() -> Response:

    await aggregator.collect()

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
