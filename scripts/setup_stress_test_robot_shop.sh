#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROBOT_SHOP_DIR="$REPO_ROOT/robot-shop"

usage() {
  cat <<'EOF'
Setup local Robot Shop (Docker) for stress testing with this repository.

This script:
- Ensures Docker is available
- Starts the Robot Shop docker-compose stack
- Prints example start.py commands for running tests and squeeze loops
EOF
}

log() { printf "\n==> %s\n" "$*"; }
die() { printf "\nERROR: %s\n" "$*" >&2; exit 1; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

RESET="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reset) RESET="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1 (use --help)" ;;
  esac
done

need_cmd docker

if [[ ! -d "$ROBOT_SHOP_DIR" ]]; then
  die "robot-shop directory not found at $ROBOT_SHOP_DIR"
fi

cd "$ROBOT_SHOP_DIR"

if [[ "$RESET" == "1" ]]; then
  log "Stopping and removing existing Robot Shop containers (if any)"
  docker compose -f docker-compose.yaml down || true
fi

log "Starting Robot Shop docker-compose stack"
docker compose -f docker-compose.yaml up -d

log "Robot Shop containers:"
docker compose -f docker-compose.yaml ps

log "Environment setup complete."
printf "\nYou can now run tests from the repo root, for example:\n\n"
printf "  cd \"%s\"\n" "$REPO_ROOT"
printf "  python3 start.py --profile low --robot-shop --no-prometheus\n"
printf "  python3 start.py --profile medium --robot-shop --no-prometheus --squeeze --until-violation\n\n"
