import asyncio
from types import SimpleNamespace

from app.services.checkers.kubernetes import KubernetesChecker


def make_node(
    name: str,
    ready: str,
):
    return SimpleNamespace(
        metadata=SimpleNamespace(
            name=name,
        ),
        status=SimpleNamespace(
            conditions=[
                SimpleNamespace(
                    type="Ready",
                    status=ready,
                )
            ]
        ),
    )


def make_deployment(
    desired: int,
    ready: int,
):
    return SimpleNamespace(
        spec=SimpleNamespace(
            replicas=desired,
        ),
        status=SimpleNamespace(
            ready_replicas=ready,
        ),
    )


def make_statefulset(
    desired: int,
    ready: int,
):
    return SimpleNamespace(
        spec=SimpleNamespace(
            replicas=desired,
        ),
        status=SimpleNamespace(
            ready_replicas=ready,
        ),
    )


class FakeCoreApi:

    def list_node(
        self,
        _request_timeout=None,
    ):
        return SimpleNamespace(
            items=[
                make_node(
                    "awx-lab-control-plane",
                    "True",
                )
            ]
        )


class FakeAppsApi:

    def read_namespaced_deployment_status(
        self,
        name,
        namespace,
        _request_timeout=None,
    ):
        return make_deployment(
            desired=1,
            ready=1,
        )

    def read_namespaced_stateful_set_status(
        self,
        name,
        namespace,
        _request_timeout=None,
    ):
        return make_statefulset(
            desired=1,
            ready=1,
        )


def test_kubernetes_healthy(
    monkeypatch,
):
    checker = KubernetesChecker()

    monkeypatch.setattr(
        checker,
        "_load_clients",
        lambda: (
            FakeCoreApi(),
            FakeAppsApi(),
        ),
    )

    result = asyncio.run(
        checker.check()
    )

    statuses = {
        component.id: component.status
        for component in result
    }

    assert (
        statuses["kubernetes-api"]
        == "healthy"
    )

    assert (
        statuses[
            "kubernetes-node-awx-lab-control-plane"
        ]
        == "healthy"
    )

    assert statuses["awx-web"] == "healthy"
    assert statuses["awx-task"] == "healthy"
    assert statuses["postgresql"] == "healthy"
