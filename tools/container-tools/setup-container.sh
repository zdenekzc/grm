#!/usr/bin/env bash
# setup-container.sh
#
# Example wrapper showing how to build and run the 10-edit editor inside
# a rootless podman/docker container (Ubuntu or AlmaLinux).
#
# Workflow:
#   ./setup-container.sh --build           # build the container image
#   ./setup-container.sh --clone           # git clone repo into ./clone/qt-2026
#                                          # (visible on the host, inside container)
#   ./setup-container.sh --make            # run `make` in ./clone/qt-2026/10-edit
#   ./setup-container.sh --view            # run view.py inside (GUI via X11)
#   ./setup-container.sh --shell           # interactive bash in the container
#
# Override the base image with --image alma (default = ubuntu):
#   ./setup-container.sh --image alma --build
#
# The host repo (this checkout) is bind-mounted at /host:ro for --clone
# so git can read the pack files; the workspace ./clone/ is bind-mounted
# at /work so everything the container writes there shows up on the host.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
HOST_REPO="$(cd -- "${SCRIPT_DIR}/../../.." &>/dev/null && pwd)"
WORKSPACE="${SCRIPT_DIR}/clone"

IMAGE_VARIANT="ubuntu"    # ubuntu | alma
IMAGE_NAME=""             # filled in after args parsed

# Container privilege mode. With ROOTFUL=1 (default) the script invokes
# `sudo podman` or plain `docker` (assuming the user is in the docker
# group) — this is the simplest path on WSL and any system where sudo
# is available. Set ROOTFUL=0 in the environment to fall back to rootless
# podman with cgroupfs / userns-keep-id workarounds.
ROOTFUL="${ROOTFUL:-1}"

info() { printf '\033[1;36m[info]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[err ]\033[0m %s\n' "$*" >&2; exit 1; }

container_cmd() {
    if command -v podman &>/dev/null; then
        if [[ "$ROOTFUL" == "1" ]]; then
            echo "sudo podman"
        else
            # cgroupfs avoids the rootless systemd-cgroup sd-bus dance.
            echo "podman --cgroup-manager=cgroupfs"
        fi
    elif command -v docker &>/dev/null; then
        # Docker daemon is rootful by default; if the user is in the
        # docker group, sudo is unnecessary.
        if docker info &>/dev/null; then
            echo docker
        else
            echo "sudo docker"
        fi
    else
        return 1
    fi
}

# --- argument parsing --------------------------------------------------------

COMMAND=""
while (( $# )); do
    case "$1" in
        --image)      IMAGE_VARIANT="${2:-}"; shift 2 ;;
        --build)      COMMAND="build";        shift ;;
        --clone)      COMMAND="clone";        shift ;;
        --make)       COMMAND="make";         shift ;;
        --view)       COMMAND="view";         shift ;;
        --shell)      COMMAND="shell";        shift ;;
        -h|--help)    sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)            die "unknown option: $1 (try --help)" ;;
    esac
done

case "${IMAGE_VARIANT}" in
    ubuntu) IMAGE_NAME="qt2026-ubuntu:local";  CFILE="Containerfile.ubuntu" ;;
    alma)   IMAGE_NAME="qt2026-alma:local";    CFILE="Containerfile.alma"   ;;
    *)      die "unknown --image: ${IMAGE_VARIANT} (use ubuntu or alma)" ;;
esac

[[ -n "${COMMAND}" ]] || die "no action — try --build, --clone, --make, --view, --shell (--help)"

RT="$(container_cmd)" || die "missing podman or docker (dnf install podman)"

# --- helpers -----------------------------------------------------------------

image_exists() {
    # shellcheck disable=SC2086
    ${RT} image inspect "${IMAGE_NAME}" &>/dev/null
}

ensure_image() {
    if ! image_exists; then
        die "image ${IMAGE_NAME} not built — run: $0 --image ${IMAGE_VARIANT} --build"
    fi
}

ensure_clone() {
    [[ -d "${WORKSPACE}/qt-2026/.git" ]] \
        || die "workspace missing — run: $0 --image ${IMAGE_VARIANT} --clone"
}

# X11 forwarding args. One-time `xhost +SI:localuser:$USER` lets the
# in-container root (which the rootless user namespace maps back to the
# host user) talk to the host X server. On Wayland hosts, XWayland makes
# /tmp/.X11-unix available transparently.
x11_args() {
    local xauth="${XAUTHORITY:-$HOME/.Xauthority}"
    local args=(
        -e "DISPLAY=${DISPLAY:-:0}"
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw
    )
    if [[ -f "${xauth}" ]]; then
        args+=(-v "${xauth}:/root/.Xauthority:ro" -e "XAUTHORITY=/root/.Xauthority")
    fi
    command -v xhost &>/dev/null \
        && xhost +SI:localuser:"${USER}" &>/dev/null || true
    printf '%s\n' "${args[@]}"
}

# Run a command in a fresh container. Bind-mounts:
#   /host   read-only view of the original host repo (git clone source)
#   /work   writable workspace (./clone on host), current working dir
run_in_container() {
    local interactive="$1"; shift
    local mode="$1"; shift   # "gui" -> forward X11; anything else -> plain
    local cmd="$*"

    local x11=()
    if [[ "${mode}" == "gui" ]]; then
        mapfile -t x11 < <(x11_args)
    fi

    mkdir -p "${WORKSPACE}"

    local it="-t"
    [[ "${interactive}" == "yes" ]] && it="-it"

    # --userns=keep-id maps the in-container root onto the host user;
    # only meaningful in rootless mode. Skip in rootful mode so files
    # written into /work end up owned by root (or the docker user).
    local userns=()
    [[ "$ROOTFUL" != "1" ]] && userns=(--userns=keep-id:uid=0,gid=0)

    # shellcheck disable=SC2086
    ${RT} run --rm ${it} \
        "${userns[@]}" \
        -v "${HOST_REPO}:/host:ro" \
        -v "${WORKSPACE}:/work:Z" \
        -w /work \
        "${x11[@]}" \
        "${IMAGE_NAME}" \
        bash -lc "${cmd}"
}

# --- actions -----------------------------------------------------------------

build() {
    info "building ${IMAGE_NAME} from ${CFILE}"
    # shellcheck disable=SC2086
    ${RT} build -t "${IMAGE_NAME}" -f "${SCRIPT_DIR}/${CFILE}" "${SCRIPT_DIR}"
    info "done: ${IMAGE_NAME}"
}

do_clone() {
    ensure_image
    if [[ -d "${WORKSPACE}/qt-2026/.git" ]]; then
        info "workspace already contains a clone (${WORKSPACE}/qt-2026) — skip"
        return 0
    fi
    info "cloning /host -> ${WORKSPACE}/qt-2026 (inside container)"
    run_in_container no plain 'git clone /host /work/qt-2026'
    info "clone ready: ${WORKSPACE}/qt-2026"
}

do_make() {
    ensure_image
    ensure_clone
    info "running make in 10-edit/"
    run_in_container no plain 'cd /work/qt-2026/10-edit && make'
}

do_view() {
    ensure_image
    ensure_clone
    info "launching view.py (GUI via X11 forward)"
    run_in_container no gui 'cd /work/qt-2026/10-edit && python3 view.py'
}

do_shell() {
    ensure_image
    info "interactive shell (GUI-capable); workspace = /work"
    run_in_container yes gui 'cd /work && bash'
}

# --- main --------------------------------------------------------------------

case "${COMMAND}" in
    build)  build    ;;
    clone)  do_clone ;;
    make)   do_make  ;;
    view)   do_view  ;;
    shell)  do_shell ;;
esac
