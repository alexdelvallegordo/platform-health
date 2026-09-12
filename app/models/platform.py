from typing import Literal

from pydantic import BaseModel


class ComponentHealth(BaseModel):
    name: str
    status: Literal["healthy", "unhealthy"]
    latency_ms: float
    detail: str | None = None


class PlatformHealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    components: list[ComponentHealth]
