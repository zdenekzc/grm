#!/usr/bin/env bash
# setup-kube.sh
#
# End-to-end demo: bring up a single-node Kubernetes cluster with `kind`,
# deploy MySQL + Apache/PHP Pods, load the PHP app image locally, and
# port-forward the web Service so you can reach the master/detail pages
# at http://localhost:8080.
#
# Usage:
#   ./setup-kube.sh --check       # verify kind, kubectl, docker/podman
#   ./setup-kube.sh --create      # create cluster (~30 s)
#   ./setup-kube.sh --build       # build qt2026-web:local and load into cluster
#   ./setup-kube.sh --apply       # kubectl apply mysql + web manifests
#   ./setup-kube.sh --open        # port-forward and print the URL
#   ./setup-kube.sh --status      # show pods / services
#   ./setup-kube.sh --destroy     # delete the cluster
#   ./setup-kube.sh --all         # check + create + build + apply + open
#   ./setup-kube.sh --fix-network # sudo iptables workaround for moby-engine 29
#                                 # (docker0 is special-cased, custom bridges
#                                 # drop return traffic — run once per boot)
#
# Install prerequisites (Fedora):
#   dnf install podman kubernetes-client
#   # kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
CLUSTER_NAME="qt2026"
WEB_IMAGE="qt2026-web:local"

# Images the cluster needs that are NOT built locally. Pulled on the host
# and pushed into the kind node by --build so the pods don't have to reach
# docker.io from inside the cluster. Keep in sync with k8s/*.yaml.
DEP_IMAGES=(
    mysql:8
)

# ROOTFUL=1 (default) -> rootful docker (user in docker group) or
# `sudo podman`. Drops the rootless workarounds: cgroup delegation
# check, containers.conf override, the iptables fix-network. Set
# ROOTFUL=0 in the environment if you really want rootless on cgroup v2.
ROOTFUL="${ROOTFUL:-1}"

info() { printf '\033[1;36m[info]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[err ]\033[0m %s\n' "$*" >&2; exit 1; }

# --- tool detection ----------------------------------------------------------

choose_builder() {
    if [[ "$ROOTFUL" == "1" ]]; then
        # Rootful path: docker daemon (with user in docker group) or
        # `sudo podman`. No KIND_EXPERIMENTAL_PROVIDER tricks, no
        # containers.conf override.
        if command -v docker &>/dev/null && docker info &>/dev/null; then
            BUILDER=docker
            unset KIND_EXPERIMENTAL_PROVIDER
        elif command -v podman &>/dev/null; then
            BUILDER="sudo podman"
            export KIND_EXPERIMENTAL_PROVIDER=podman
        elif command -v docker &>/dev/null; then
            die "docker client installed but daemon not reachable — start it (sudo systemctl start docker)"
        else
            die "missing docker or podman"
        fi
    else
        # Rootless path: best-effort with cgroupfs + containers.conf.
        if command -v docker &>/dev/null && docker info &>/dev/null; then
            BUILDER=docker
            unset KIND_EXPERIMENTAL_PROVIDER
        elif command -v podman &>/dev/null; then
            BUILDER=podman
            export KIND_EXPERIMENTAL_PROVIDER=podman
            export CONTAINERS_CONF="${SCRIPT_DIR}/containers.conf"
        elif command -v docker &>/dev/null; then
            die "docker client installed but daemon not reachable"
        else
            die "missing docker or podman"
        fi
    fi
}

check_tools() {
    command -v kind    &>/dev/null || die "missing kind — https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    command -v kubectl &>/dev/null || die "missing kubectl — dnf install kubernetes-client"
    choose_builder
    info "using: kind + kubectl + ${BUILDER} (ROOTFUL=$ROOTFUL)"
    # cgroup delegation only matters for rootless podman.
    if [[ "${BUILDER}" == "podman" && "$ROOTFUL" != "1" ]]; then
        info "(kind will use KIND_EXPERIMENTAL_PROVIDER=podman)"
        check_cgroup_delegation
    fi
}

# rootless podman on cgroup v2 needs cpu+cpuset+io+memory+pids delegated to
# user@.service, otherwise systemd inside the kindest/node container never
# reaches multi-user.target and `kind create cluster` times out. Print a
# sudo-required remediation hint when the set is incomplete.
check_cgroup_delegation() {
    local cg="/sys/fs/cgroup/user.slice/user-$(id -u).slice/cgroup.controllers"
    if [[ ! -r "${cg}" ]]; then
        warn "cgroup v2 not detected at ${cg} — kind may still work on v1, continuing"
        return 0
    fi
    local have; have="$(< "${cg}")"
    info "cgroup v2 delegated controllers: ${have}"
    local want=(cpu cpuset io memory pids)
    local missing=()
    for c in "${want[@]}"; do
        grep -qw "${c}" <<<"${have}" || missing+=("${c}")
    done
    if (( ${#missing[@]} == 0 )); then
        info "cgroup delegation OK (cpu cpuset io memory pids all present)"
        return 0
    fi
    warn "missing delegated controllers: ${missing[*]}"
    warn "kind will fail with 'could not find a log line that matches Reached target Multi-User System'"

    # If the drop-in is already there, the sudo block was run but the
    # running user@.service predates the drop-in — daemon-reload alone
    # doesn't restart an already-running instance. Tell the user exactly
    # that so they don't re-run sudo in a loop.
    if [[ -r /etc/systemd/system/user@.service.d/delegate.conf ]]; then
        warn "delegate.conf is already installed — you just need to log out and log"
        warn "back in (or reboot) so user@$(id -u).service picks up the drop-in."
        warn "verify afterwards with:   cat ${cg}"
        return 0
    fi

    warn "one-time fix (requires sudo; afterwards log out and log back in):"
    # Printed plain (no [warn] prefix) so the block pastes cleanly into a shell.
    cat <<'EOF'

sudo mkdir -p /etc/systemd/system/user@.service.d
sudo tee /etc/systemd/system/user@.service.d/delegate.conf > /dev/null <<CONF
[Service]
Delegate=cpu cpuset io memory pids
CONF
sudo systemctl daemon-reload
sudo loginctl enable-linger $USER

EOF
    warn "then LOG OUT and LOG BACK IN (or reboot) — daemon-reload alone will"
    warn "not restart your already-running user@<uid>.service instance."
}

# --- actions -----------------------------------------------------------------

create_cluster() {
    check_tools
    if kind get clusters 2>/dev/null | grep -qx "${CLUSTER_NAME}"; then
        info "cluster ${CLUSTER_NAME} already exists (skip create)"
    else
        info "creating kind cluster ${CLUSTER_NAME} (~30 s)"
        kind create cluster --name "${CLUSTER_NAME}"
    fi
    # `kind create cluster` only merges the kubeconfig when it can write the
    # file — in a stripped-down shell (e.g. spawned via `sg docker`) the
    # merge sometimes leaves ~/.kube/config empty with no current-context.
    # Force-export so kubectl always points at us.
    kind export kubeconfig --name "${CLUSTER_NAME}"
    kubectl cluster-info --context "kind-${CLUSTER_NAME}"
}

build_web() {
    check_tools
    info "building ${WEB_IMAGE} with ${BUILDER}"
    "${BUILDER}" build -t "${WEB_IMAGE}" -f "${SCRIPT_DIR}/Containerfile.web" "${SCRIPT_DIR}"
    load_image_into_kind "${WEB_IMAGE}"

    # Pull the dependency images on the host and load them into kind too.
    # The node's containerd would pull them itself on first Pod start, but
    # restrictive networks (university firewalls, captive portals) often
    # block the TCP hand-shake from inside the kind bridge even though DNS
    # resolves — pulling via the host dockerd is dramatically more reliable.
    for img in "${DEP_IMAGES[@]}"; do
        info "pre-pulling ${img} on host"
        "${BUILDER}" pull "${img}"
        load_image_into_kind "${img}"
    done
}

load_image_into_kind() {
    local image="$1"
    info "loading ${image} into cluster"
    # `kind load docker-image` re-tags via ctr, which trips on OCI multi-arch
    # manifests produced by Docker 29 + containerd snapshotter. Going via
    # `docker save --platform linux/amd64` + `kind load image-archive` is
    # the reliable path — it flattens the manifest to a single platform.
    local tmp
    tmp="$(mktemp --suffix=.tar)"
    if [[ "${BUILDER}" == "docker" ]]; then
        docker save --platform linux/amd64 "${image}" -o "${tmp}"
    else
        podman save "${image}" -o "${tmp}"
    fi
    kind load image-archive "${tmp}" --name "${CLUSTER_NAME}"
    rm -f "${tmp}"
}

apply_manifests() {
    check_tools
    info "applying mysql-init ConfigMap (from k8s/schema.sql)"
    kubectl create configmap mysql-init \
        --from-file="${SCRIPT_DIR}/k8s/schema.sql" \
        --dry-run=client -o yaml | kubectl apply -f -

    info "applying mysql.yaml"
    kubectl apply -f "${SCRIPT_DIR}/k8s/mysql.yaml"

    info "applying web.yaml"
    kubectl apply -f "${SCRIPT_DIR}/k8s/web.yaml"

    info "waiting for pods to become Ready (up to 3 min)..."
    kubectl wait --for=condition=ready pod -l app=mysql --timeout=180s
    kubectl wait --for=condition=ready pod -l app=web   --timeout=60s
    info "ready — run: $0 --open"
}

open_app() {
    check_tools
    info "port-forward svc/web 8080 -> localhost:8080 (Ctrl+C to stop)"
    info "open your browser:  http://localhost:8080/"
    kubectl port-forward svc/web 8080:80
}

show_status() {
    check_tools
    kubectl get pods,svc -o wide
}

fix_network() {
    check_tools
    [[ "${BUILDER}" == "docker" ]] \
        || { info "skip — only relevant for docker backend"; return 0; }

    # Find the bridge that carries the kind network.
    local net_id bridge
    net_id="$(docker network inspect kind --format '{{.Id}}' 2>/dev/null)" \
        || die "docker network 'kind' missing — run --create first"
    bridge="br-${net_id:0:12}"

    if ! ip link show "${bridge}" &>/dev/null; then
        die "expected bridge ${bridge} not present — kind cluster broken?"
    fi

    info "checking FORWARD rule for return traffic to ${bridge}"
    if sudo iptables -C DOCKER-USER -o "${bridge}" \
            -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null; then
        info "rule already present — nothing to do"
        return 0
    fi

    info "inserting rule (requires sudo, once per boot):"
    info "  iptables -I DOCKER-USER -o ${bridge} \\"
    info "    -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT"
    sudo iptables -I DOCKER-USER -o "${bridge}" \
        -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT \
        || die "iptables insert failed"
    info "done — pods should now reach external registries"
}

destroy_cluster() {
    check_tools
    if kind get clusters 2>/dev/null | grep -qx "${CLUSTER_NAME}"; then
        info "deleting cluster ${CLUSTER_NAME}"
        kind delete cluster --name "${CLUSTER_NAME}"
    else
        info "cluster ${CLUSTER_NAME} does not exist (nothing to destroy)"
    fi
}

do_all() {
    check_tools
    create_cluster
    build_web
    apply_manifests
    open_app
}

# --- main --------------------------------------------------------------------

case "${1:-}" in
    --check)    check_tools      ;;
    --create)   create_cluster   ;;
    --build)    build_web        ;;
    --apply)    apply_manifests  ;;
    --open)     open_app         ;;
    --status)      show_status      ;;
    --destroy)     destroy_cluster  ;;
    --fix-network) fix_network      ;;
    --all)         do_all           ;;
    -h|--help|"") sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//' ;;
    *)          die "unknown option: $1 (try --help)" ;;
esac
