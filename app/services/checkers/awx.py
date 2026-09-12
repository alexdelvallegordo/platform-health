import time

import httpx

from app.core.config import settings
from app.models.component import ComponentHealth
from app.services.checkers.base import HealthChecker


class AWXChecker(HealthChecker):

    def __init__(
        self,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.transport = transport

    async def check(
        self,
    ) -> list[ComponentHealth]:

        url = (
            f"{settings.awx_url.rstrip('/')}"
            "/api/v2/ping/"
        )

        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=settings.awx_timeout,
                trust_env=False,
                transport=self.transport,
            ) as client:
                response = await client.get(url)

            latency_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            metadata = {
                "http_status": response.status_code,
            }

            if response.status_code == 200:

                try:
                    data = response.json()

                    if "version" in data:
                        metadata["version"] = data["version"]

                except ValueError:
                    pass

                return [
                    ComponentHealth(
                        id="awx-api",
                        name="AWX API",
                        group="automation-platform",
                        status="healthy",
                        latency_ms=latency_ms,
                        metadata=metadata,
                    )
                ]

            return [
                ComponentHealth(
                    id="awx-api",
                    name="AWX API",
                    group="automation-platform",
                    status="down",
                    latency_ms=latency_ms,
                    detail=(
                        "Unexpected HTTP status: "
                        f"{response.status_code}"
                    ),
                    metadata=metadata,
                )
            ]

        except httpx.RequestError as exc:

            latency_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            return [
                ComponentHealth(
                    id="awx-api",
                    name="AWX API",
                    group="automation-platform",
                    status="down",
                    latency_ms=latency_ms,
                    detail=str(exc),
                )
            ]
