import asyncio

import httpx

from app.services.checkers.awx import AWXChecker


def run_checker(handler):
    transport = httpx.MockTransport(handler)

    checker = AWXChecker(
        transport=transport,
    )

    return asyncio.run(
        checker.check()
    )[0]


def test_awx_healthy():

    def handler(request):
        return httpx.Response(
            status_code=200,
            json={
                "version": "24.6.1",
            },
        )

    result = run_checker(handler)

    assert result.id == "awx-api"
    assert result.status == "healthy"

    assert result.metadata["http_status"] == 200
    assert result.metadata["version"] == "24.6.1"

    assert result.latency_ms is not None


def test_awx_http_error():

    def handler(request):
        return httpx.Response(
            status_code=500,
        )

    result = run_checker(handler)

    assert result.status == "down"

    assert (
        result.detail
        == "Unexpected HTTP status: 500"
    )


def test_awx_timeout():

    def handler(request):
        raise httpx.ConnectTimeout(
            "AWX connection timed out",
            request=request,
        )

    result = run_checker(handler)

    assert result.status == "down"
    assert result.detail is not None
    assert "timed out" in result.detail
