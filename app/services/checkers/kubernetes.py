import asyncio
import time

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException

from app.core.config import settings
from app.models.component import ComponentHealth
from app.services.checkers.base import HealthChecker


class KubernetesChecker(HealthChecker):

    def _load_clients(
        self,
    ) -> tuple[
        client.CoreV1Api,
        client.AppsV1Api,
    ]:

        try:
            config.load_incluster_config()

        except ConfigException:
            config.load_kube_config()

        return (
            client.CoreV1Api(),
            client.AppsV1Api(),
        )

    @staticmethod
    def _workload_status(
        desired: int,
        ready: int,
    ) -> str:

        if desired <= 0:
            return "unknown"

        if ready >= desired:
            return "healthy"

        if ready == 0:
            return "down"

        return "degraded"

    def _deployment_component(
        self,
        apps_api: client.AppsV1Api,
        deployment_name: str,
        component_id: str,
        display_name: str,
    ) -> ComponentHealth:

        try:
            deployment = (
                apps_api.read_namespaced_deployment_status(
                    name=deployment_name,
                    namespace=settings.kubernetes_namespace,
                    _request_timeout=settings.kubernetes_timeout,
                )
            )

            desired = deployment.spec.replicas or 0
            ready = (
                deployment.status.ready_replicas
                or 0
            )

            status = self._workload_status(
                desired,
                ready,
            )

            detail = None

            if status != "healthy":
                detail = (
                    f"{ready}/{desired} replicas ready"
                )

            return ComponentHealth(
                id=component_id,
                name=display_name,
                group="automation-platform",
                status=status,
                detail=detail,
                metadata={
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                },
            )

        except ApiException as exc:
            return ComponentHealth(
                id=component_id,
                name=display_name,
                group="automation-platform",
                status="down",
                detail=(
                    "Kubernetes API error: "
                    f"{exc.status}"
                ),
            )

    def _statefulset_component(
        self,
        apps_api: client.AppsV1Api,
        statefulset_name: str,
        component_id: str,
        display_name: str,
    ) -> ComponentHealth:

        try:
            statefulset = (
                apps_api.read_namespaced_stateful_set_status(
                    name=statefulset_name,
                    namespace=settings.kubernetes_namespace,
                    _request_timeout=settings.kubernetes_timeout,
                )
            )

            desired = statefulset.spec.replicas or 0
            ready = (
                statefulset.status.ready_replicas
                or 0
            )

            status = self._workload_status(
                desired,
                ready,
            )

            detail = None

            if status != "healthy":
                detail = (
                    f"{ready}/{desired} replicas ready"
                )

            return ComponentHealth(
                id=component_id,
                name=display_name,
                group="automation-platform",
                status=status,
                detail=detail,
                metadata={
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                },
            )

        except ApiException as exc:
            return ComponentHealth(
                id=component_id,
                name=display_name,
                group="automation-platform",
                status="down",
                detail=(
                    "Kubernetes API error: "
                    f"{exc.status}"
                ),
            )

    def _check_sync(
        self,
    ) -> list[ComponentHealth]:

        start_time = time.perf_counter()

        core_api, apps_api = self._load_clients()

        nodes = core_api.list_node(
            _request_timeout=settings.kubernetes_timeout
        )

        latency_ms = round(
            (
                time.perf_counter()
                - start_time
            )
            * 1000,
            2,
        )

        components: list[ComponentHealth] = [
            ComponentHealth(
                id="kubernetes-api",
                name="Kubernetes API",
                group="kubernetes",
                status="healthy",
                latency_ms=latency_ms,
                metadata={
                    "nodes": len(nodes.items),
                },
            )
        ]

        for node in nodes.items:

            ready_condition = next(
                (
                    condition
                    for condition
                    in node.status.conditions
                    if condition.type == "Ready"
                ),
                None,
            )

            is_ready = (
                ready_condition is not None
                and ready_condition.status == "True"
            )

            components.append(
                ComponentHealth(
                    id=(
                        "kubernetes-node-"
                        f"{node.metadata.name}"
                    ),
                    name=node.metadata.name,
                    group="kubernetes",
                    status=(
                        "healthy"
                        if is_ready
                        else "down"
                    ),
                    detail=(
                        None
                        if is_ready
                        else "Node is not Ready"
                    ),
                    metadata={
                        "ready": is_ready,
                    },
                )
            )

        components.append(
            self._deployment_component(
                apps_api,
                deployment_name="awx-web",
                component_id="awx-web",
                display_name="AWX Web",
            )
        )

        components.append(
            self._deployment_component(
                apps_api,
                deployment_name="awx-task",
                component_id="awx-task",
                display_name="AWX Task",
            )
        )

        components.append(
            self._statefulset_component(
                apps_api,
                statefulset_name="awx-postgres-15",
                component_id="postgresql",
                display_name="PostgreSQL",
            )
        )

        return components

    async def check(
        self,
    ) -> list[ComponentHealth]:

        try:
            return await asyncio.to_thread(
                self._check_sync
            )

        except Exception as exc:
            return [
                ComponentHealth(
                    id="kubernetes-api",
                    name="Kubernetes API",
                    group="kubernetes",
                    status="down",
                    detail=str(exc),
                ),
                ComponentHealth(
                    id="awx-web",
                    name="AWX Web",
                    group="automation-platform",
                    status="unknown",
                    detail=(
                        "Kubernetes API unavailable"
                    ),
                ),
                ComponentHealth(
                    id="awx-task",
                    name="AWX Task",
                    group="automation-platform",
                    status="unknown",
                    detail=(
                        "Kubernetes API unavailable"
                    ),
                ),
                ComponentHealth(
                    id="postgresql",
                    name="PostgreSQL",
                    group="automation-platform",
                    status="unknown",
                    detail=(
                        "Kubernetes API unavailable"
                    ),
                ),
            ]
