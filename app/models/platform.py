from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.component import ComponentHealth


PlatformStatus = Literal[
    "healthy",
    "degraded",
    "down",
]


class PlatformStatusResponse(BaseModel):
    status: PlatformStatus
    checked_at: datetime
    components: list[ComponentHealth]
