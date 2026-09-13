#!/usr/bin/env bash

set -Eeuo pipefail


# ============================================================
# Configuration
# ============================================================

CONTROL_PLANE="awx-lab-control-plane"
KUBE_CONTEXT="kind-awx-lab"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
LOG_DIR="${RUN_DIR}/logs"

INGRESS_LOCAL_PORT="80"

mkdir -p "${RUN_DIR}" "${LOG_DIR}"


# ============================================================
# Helpers
# ============================================================

port_in_use() {
    local port="$1"

    ss -ltnH \
        | awk '{print $4}' \
        | grep -Eq ":${port}$"
}


wait_for_kubernetes_api() {
    echo
    echo "[1/6] Starting Kubernetes cluster..."

    if ! podman container exists "${CONTROL_PLANE}"; then
        echo "ERROR: Kind control-plane container '${CONTROL_PLANE}' does not exist."
        exit 1
    fi

    if [[ "$(podman inspect -f '{{.State.Running}}' "${CONTROL_PLANE}")" != "true" ]]; then
        echo "Starting Kind control plane..."
        podman start "${CONTROL_PLANE}" >/dev/null
    else
        echo "Kind control plane already running."
    fi

    kubectl config use-context "${KUBE_CONTEXT}" >/dev/null

    echo "Waiting for Kubernetes API..."

    for _ in $(seq 1 60); do
        if kubectl get nodes >/dev/null 2>&1; then
            echo "Kubernetes API is available."
            break
        fi

        sleep 2
    done

    if ! kubectl get nodes >/dev/null 2>&1; then
        echo "ERROR: Kubernetes API did not become available."
        exit 1
    fi

    echo "Waiting for Kubernetes node..."

    kubectl wait \
        --for=condition=Ready \
        node/awx-lab-control-plane \
        --timeout=120s

    echo "Kubernetes cluster is ready."
}


wait_for_awx() {
    echo
    echo "[2/6] Waiting for AWX platform..."

    if ! kubectl get deployment \
        awx-operator-controller-manager \
        -n awx \
        >/dev/null 2>&1; then

        echo "ERROR: AWX Operator deployment was not found."
        exit 1
    fi

    echo "Waiting for AWX Operator..."

    kubectl rollout status \
        deployment/awx-operator-controller-manager \
        -n awx \
        --timeout=180s

    echo "Waiting for PostgreSQL..."

    kubectl rollout status \
        statefulset/awx-postgres-15 \
        -n awx \
        --timeout=180s

    echo "Waiting for AWX Web..."

    kubectl rollout status \
        deployment/awx-web \
        -n awx \
        --timeout=180s

    echo "Waiting for AWX Task..."

    kubectl rollout status \
        deployment/awx-task \
        -n awx \
        --timeout=180s

    echo "AWX platform is ready."
}


wait_for_platform_health() {
    echo
    echo "[3/6] Waiting for Platform Health..."

    kubectl rollout status \
        deployment/platform-health \
        -n platform-health \
        --timeout=180s

    echo "Platform Health is ready."
}


wait_for_monitoring() {
    echo
    echo "[4/6] Waiting for monitoring stack..."

    kubectl rollout status \
        deployment/prometheus \
        -n monitoring \
        --timeout=180s

    kubectl rollout status \
        deployment/grafana \
        -n monitoring \
        --timeout=180s

    echo "Prometheus and Grafana are ready."
}


wait_for_ingress() {
    echo
    echo "[5/6] Waiting for Ingress..."

    if ! kubectl get deployment \
        ingress-nginx-controller \
        -n ingress-nginx \
        >/dev/null 2>&1; then

        echo "ERROR: ingress-nginx controller was not found."
        exit 1
    fi

    kubectl rollout status \
        deployment/ingress-nginx-controller \
        -n ingress-nginx \
        --timeout=180s

    echo "Ingress controller is ready."
}


start_ingress_access() {
    echo
    echo "[6/6] Exposing lab services through Ingress..."

    local name="ingress"
    local pid_file="${RUN_DIR}/${name}.pid"
    local log_file="${LOG_DIR}/${name}.log"

    if [[ -f "${pid_file}" ]]; then
        local old_pid
        old_pid="$(cat "${pid_file}")"

        if kill -0 "${old_pid}" 2>/dev/null; then
            echo "Ingress access already running (PID ${old_pid})."
            return
        fi

        rm -f "${pid_file}"
    fi

    if port_in_use "${INGRESS_LOCAL_PORT}"; then
        echo "Port ${INGRESS_LOCAL_PORT} is already in use."
        echo "Assuming Ingress access is already available."
        return
    fi

    nohup kubectl port-forward \
        -n ingress-nginx \
        svc/ingress-nginx-controller \
        "${INGRESS_LOCAL_PORT}:80" \
        --address 127.0.0.1 \
        </dev/null \
        >"${log_file}" \
        2>&1 &

    local pid=$!
    echo "${pid}" > "${pid_file}"

    for _ in $(seq 1 20); do
        if port_in_use "${INGRESS_LOCAL_PORT}"; then
            echo "Ingress listening on 127.0.0.1:${INGRESS_LOCAL_PORT} (PID ${pid})."
            return
        fi

        if ! kill -0 "${pid}" 2>/dev/null; then
            echo "ERROR: Ingress access failed to start."
            echo "Check log: ${log_file}"
            exit 1
        fi

        sleep 0.5
    done

    echo "ERROR: Ingress did not open port ${INGRESS_LOCAL_PORT}."
    echo "Check log: ${log_file}"
    exit 1
}


show_status() {
    echo
    echo "======================================"
    echo " Platform Health Lab Ready"
    echo "======================================"
    echo
    echo "AWX             : http://awx.lab.test"
    echo "Platform Health : http://platform-health.lab.test"
    echo "Prometheus      : http://prometheus.lab.test"
    echo "Grafana         : http://grafana.lab.test"
    echo

    echo "AWX:"
    kubectl get pods \
        -n awx \
        --no-headers

    echo
    echo "Platform Health:"
    kubectl get pods \
        -n platform-health \
        --no-headers

    echo
    echo "Monitoring:"
    kubectl get pods \
        -n monitoring \
        --no-headers

    echo
    echo "Ingress:"
    kubectl get pods \
        -n ingress-nginx \
        --no-headers

    echo
    echo "Ingress routes:"
    kubectl get ingress \
        -A

    echo
    echo "Lab is ready."
    echo
}


# ============================================================
# Startup
# ============================================================

echo
echo "======================================"
echo " Platform Health Lab"
echo "======================================"

wait_for_kubernetes_api
wait_for_awx
wait_for_platform_health
wait_for_monitoring
wait_for_ingress
start_ingress_access
show_status
