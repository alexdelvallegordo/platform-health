import time

import httpx

from app.core.config import settings


AWX_HEALTH_ENDPOINT = "/api/v2/ping/"


async def check_awx_health(
    client: httpx.AsyncClient | None = None,
) -> dict:
    url = f"{settings.awx_url.rstrip('/')}{AWX_HEALTH_ENDPOINT}"

    start_time = time.perf_counter()

    owns_client = client is None

    if client is None:
        client = httpx.AsyncClient(
            timeout=settings.awx_timeout,
            trust_env=False,
        )

    try:
        response = await client.get(url)

        latency_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        if response.status_code == 200:
            return {
                "name": "awx",
                "status": "healthy",
                "latency_ms": latency_ms,
            }

        return {
            "name": "awx",
            "status": "unhealthy",
            "latency_ms": latency_ms,
            "detail": f"Unexpected HTTP status: {response.status_code}",
        }

    except httpx.RequestError as exc:
        latency_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        return {
            "name": "awx",
            "status": "unhealthy",
            "latency_ms": latency_ms,
            "detail": str(exc),
        }

    finally:
        if owns_client:
            await client.aclose()
