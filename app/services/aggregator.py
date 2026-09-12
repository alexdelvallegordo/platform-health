import asyncio
from datetime import datetime, timezone

from app.models.component import ComponentHealth
from app.models.platform import PlatformStatusResponse
from app.observability.metrics import record_platform_status
from app.services.checkers.awx import AWXChecker
from app.services.checkers.base import HealthChecker
from app.services.checkers.kubernetes import KubernetesChecker


class PlatformAggregator:

    def __init__(
        self,
        checkers: list[HealthChecker] | None = None,
    ) -> None:

        self.checkers = checkers or [
            AWXChecker(),
            KubernetesChecker(),
        ]

    async def collect(
        self,
    ) -> PlatformStatusResponse:

        results = await asyncio.gather(
            *(
                checker.check()
                for checker in self.checkers
            )
        )

        components: list[ComponentHealth] = [
            component
            for result in results
            for component in result
        ]

        statuses = {
            component.status
            for component in components
        }

        if components and statuses == {"healthy"}:
            overall_status = "healthy"

        elif components and all(
            component.status in {"down", "unknown"}
            for component in components
        ):
            overall_status = "down"

        else:
            overall_status = "degraded"

        snapshot = PlatformStatusResponse(
            status=overall_status,
            checked_at=datetime.now(timezone.utc),
            components=components,
        )

        record_platform_status(snapshot)

        return snapshot
