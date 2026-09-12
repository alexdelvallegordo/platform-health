from typing import Any, Literal

from pydantic import BaseModel, Field


ComponentStatus = Literal[
    "healthy",
    "degraded",
    "down",
    "unknown",
]


class ComponentHealth(BaseModel):
    id: str
    name: str
    group: str
    status: ComponentStatus

    latency_ms: float | None = None
    detail: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
