#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAG="${1:-microservices-stress-analyzer:latest}"
cd "$ROOT"
docker build -f Dockerfile.analyzer -t "$TAG" .
echo "Built: $TAG"
