#!/usr/bin/env bash
# setup-toaruos.sh
#
# Builds ToaruOS, cross-compiles every example C program in this directory
# (currently: tree) and re-packages image.iso with them installed under
# /bin/copilot/.
#
# Usage:
#   ./setup-toaruos.sh                # clone sources + pull container image
#   ./setup-toaruos.sh --build        # build the ToaruOS ISO (~10 min)
#   ./setup-toaruos.sh --install      # build programs + repackage ISO
#   ./setup-toaruos.sh --run          # boot the ISO in QEMU
#
# After --install you can run the example inside ToaruOS by typing its
# name in the terminal (PATH is extended with /bin/copilot).

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
TOARU_DIR="${SCRIPT_DIR}/toaruos"
TOARU_REPO="https://github.com/klange/toaruos.git"
# The repo default branch is a 'github_notice' tombstone (upstream left GitHub);
# the archived sources live on 'master'.
TOARU_BRANCH="${TOARU_BRANCH:-master}"
# Fully qualified: podman refuses unqualified names unless
# unqualified-search-registries is set in /etc/containers/registries.conf.
BUILD_IMAGE="docker.io/toaruos/build-tools:1.99.x"

# Space-separated list of binaries that get cross-compiled and installed.
# Add a new program by dropping <name>.c next to this script and appending
# <name> here (and to GUI_PROGS in the Makefile).
PROGRAMS="tree"

# ROOTFUL=1 (default) -> sudo podman / docker-group docker. Set ROOTFUL=0
# in the environment for rootless podman with cgroupfs / userns-keep-id.
ROOTFUL="${ROOTFUL:-1}"

info() { printf '\033[1;36m[info]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[err ]\033[0m %s\n' "$*" >&2; exit 1; }

container_cmd() {
    if command -v podman &>/dev/null; then
        if [[ "$ROOTFUL" == "1" ]]; then
            echo "sudo podman"
        else
            echo "podman --cgroup-manager=cgroupfs"
        fi
    elif command -v docker &>/dev/null; then
        if docker info &>/dev/null; then
            echo docker
        else
            echo "sudo docker"
        fi
    else
        return 1
    fi
}

clone_sources() {
    if [[ -d "${TOARU_DIR}/.git" ]]; then
        info "ToaruOS sources already in ${TOARU_DIR} (skip clone)"
    else
        info "cloning ${TOARU_REPO} (branch ${TOARU_BRANCH}) -> ${TOARU_DIR}"
        git clone --depth 1 --branch "${TOARU_BRANCH}" "${TOARU_REPO}" "${TOARU_DIR}"
    fi

    # A pre-existing clone may still sit on the 'github_notice' tombstone
    # branch (no Makefile, no .gitmodules) — switch it to the real sources.
    if [[ ! -f "${TOARU_DIR}/Makefile" ]]; then
        info "no Makefile in ${TOARU_DIR} — fetching ${TOARU_BRANCH} and checking it out"
        (cd "${TOARU_DIR}" \
            && git fetch --depth 1 origin "${TOARU_BRANCH}" \
            && git checkout -B "${TOARU_BRANCH}" FETCH_HEAD)
    fi

    (cd "${TOARU_DIR}" && git submodule update --init --depth 1 kuroko bim)
}

pull_image() {
    local rt
    rt="$(container_cmd)"
    info "pulling ${BUILD_IMAGE}"
    # shellcheck disable=SC2086
    ${rt} pull "${BUILD_IMAGE}"
}

# Rootless podman maps host UID -> container root, so the upstream useradd
# trick from util/build-in-docker.sh does not work. We invoke make directly;
# files are written back under our UID.
run_in_container() {
    local workdir="$1"; shift
    local rt
    rt="$(container_cmd)"

    # --userns=keep-id is rootless-only; in rootful mode files end up
    # owned by root (or the docker user), which is fine for transient
    # builds.
    local userns=()
    [[ "$ROOTFUL" != "1" ]] && userns=(--userns=keep-id:uid=0,gid=0)

    # shellcheck disable=SC2086
    ${rt} run --rm \
        "${userns[@]}" \
        -v "${SCRIPT_DIR}:/work:Z" \
        -v "${TOARU_DIR}:/root/misaka:Z" \
        -w "${workdir}" \
        -e LANG=C.UTF-8 \
        -t "${BUILD_IMAGE}" \
        bash -c "$*"
}

build_iso() {
    info "building ToaruOS (~10 min)"
    run_in_container /root/misaka '
        set -e
        chmod o+x /root
        chmod -R o+rw /root/gcc_local/bin
        ln -sfn /root/gcc_local util/local
        make util/local/bin/kuroko
        make base/lib/libc.so
        make -j"$(nproc)"
        rm -f util/local
    '
    [[ -f "${TOARU_DIR}/image.iso" ]] \
        && info "done: ${TOARU_DIR}/image.iso" \
        || warn "image.iso did not appear in ${TOARU_DIR}"
}

compile_programs() {
    info "cross-compiling examples"
    run_in_container /work '
        set -e
        export PATH=/root/gcc_local/bin:$PATH
        export LD_LIBRARY_PATH=/root/gcc_local/lib:/root/gcc_local/x86_64-pc-linux-gnu/x86_64-pc-toaru/lib:/root/misaka/base/lib:/root/misaka/base/usr/lib
        make clean >/dev/null
        make TOARU_ROOT=/root/misaka
    '
}

install_programs() {
    [[ -f "${TOARU_DIR}/image.iso" ]] || die \
        "ToaruOS not built — run $0 --build"

    compile_programs

    info "copying programs into /bin/copilot/"
    local dst="${TOARU_DIR}/base/bin/copilot"
    mkdir -p "${dst}"
    for p in $PROGRAMS; do
        [[ -x "${SCRIPT_DIR}/${p}" ]] || die "missing compiled binary: ${p}"
        cp "${SCRIPT_DIR}/${p}" "${dst}/${p}"
        rm -f "${TOARU_DIR}/base/bin/${p}"
    done

    # Extend PATH with /bin/copilot so the programs are callable by name.
    local rc="${TOARU_DIR}/base/etc/startup.d/99_runstart.sh"
    if ! grep -q "/bin/copilot" "${rc}" 2>/dev/null; then
        info "adding /bin/copilot to PATH in ${rc#${TOARU_DIR}/}"
        sed -i 's|^export PATH=\(.*\)$|export PATH=\1:/bin/copilot|' "${rc}"
    fi

    info "rebuilding ramdisk.igz + image.iso"
    run_in_container /root/misaka '
        set -e
        chmod o+x /root
        chmod -R o+rw /root/gcc_local/bin
        ln -sfn /root/gcc_local util/local
        make
        rm -f util/local
    '
    info "done: in the ToaruOS terminal run e.g. 'tree'"
}

run_qemu() {
    local iso="${TOARU_DIR}/image.iso"
    [[ -f "$iso" ]] || die "${iso} does not exist — run $0 --build"
    command -v qemu-system-x86_64 &>/dev/null \
        || die "missing qemu-system-x86_64 (dnf install qemu-system-x86)"
    info "launching QEMU (close the window to quit)"
    qemu-system-x86_64 -enable-kvm -m 1024 -cdrom "$iso" -vga std
}

# --- main --------------------------------------------------------------------

command -v git &>/dev/null || die "missing git (dnf install git)"

case "${1:-}" in
    ""|"--default")
        container_cmd &>/dev/null || die "missing podman or docker (dnf install podman)"
        clone_sources
        pull_image
        ;;
    "--build")
        container_cmd &>/dev/null || die "missing podman or docker"
        clone_sources
        pull_image
        build_iso
        ;;
    "--install")
        container_cmd &>/dev/null || die "missing podman or docker"
        clone_sources
        pull_image
        [[ -f "${TOARU_DIR}/image.iso" ]] || build_iso
        install_programs
        ;;
    "--run")
        run_qemu
        ;;
    "-h"|"--help")
        sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
        ;;
    *) die "unknown option: $1 (try --help)" ;;
esac
