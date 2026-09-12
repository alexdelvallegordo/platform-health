from prometheus_client import Gauge

from app.models.platform import PlatformStatusResponse


OVERALL_VALUES = {
    "healthy": 1.0,
    "degraded": 0.5,
    "down": 0.0,
}

COMPONENT_VALUES = {
    "healthy": 1.0,
    "degraded": 0.5,
    "down": 0.0,
    "unknown": -1.0,
}


platform_overall_status = Gauge(
    "platform_health_overall_status",
    "Overall platform health. 1=healthy, 0.5=degraded, 0=down.",
)

platform_component_status = Gauge(
    "platform_health_component_status",
    "Component health. 1=healthy, 0.5=degraded, 0=down, -1=unknown.",
    ["component", "group"],
)

platform_component_latency_ms = Gauge(
    "platform_health_component_latency_ms",
    "Component health-check latency in milliseconds.",
    ["component", "group"],
)

platform_last_check_timestamp = Gauge(
    "platform_health_last_check_timestamp_seconds",
    "Unix timestamp of the latest platform health check.",
)


def record_platform_status(
    snapshot: PlatformStatusResponse,
) -> None:

    platform_overall_status.set(
        OVERALL_VALUES[snapshot.status]
    )

    platform_last_check_timestamp.set(
        snapshot.checked_at.timestamp()
    )

    for component in snapshot.components:

        labels = {
            "component": component.id,
            "group": component.group,
        }

        platform_component_status.labels(
            **labels
        ).set(
            COMPONENT_VALUES[component.status]
        )

        latency = (
            component.latency_ms
            if component.latency_ms is not None
            else float("nan")
        )

        platform_component_latency_ms.labels(
            **labels
        ).set(latency)
