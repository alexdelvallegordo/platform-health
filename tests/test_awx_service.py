import asyncio

import httpx

from app.services.awx import check_awx_health


def run_check(handler):
    transport = httpx.MockTransport(handler)

    async def run():
        async with httpx.AsyncClient(
            transport=transport,
        ) as client:
            return await check_awx_health(client)

    return asyncio.run(run())


def test_awx_healthy():
    def handler(request):
        return httpx.Response(
            status_code=200,
            json={"version": "24.6.1"},
        )

    result = run_check(handler)

    assert result["name"] == "awx"
    assert result["status"] == "healthy"
    assert result["latency_ms"] >= 0
    assert "detail" not in result


def test_awx_http_error():
    def handler(request):
        return httpx.Response(
            status_code=500,
        )

    result = run_check(handler)

    assert result["name"] == "awx"
    assert result["status"] == "unhealthy"
    assert result["latency_ms"] >= 0
    assert result["detail"] == "Unexpected HTTP status: 500"


def test_awx_timeout():
    def handler(request):
        raise httpx.ConnectTimeout(
            "AWX connection timed out",
            request=request,
        )

    result = run_check(handler)

    assert result["name"] == "awx"
    assert result["status"] == "unhealthy"
    assert result["latency_ms"] >= 0
    assert "timed out" in result["detail"]
