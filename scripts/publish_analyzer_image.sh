#!/usr/bin/env bash
set -euo pipefail

# Simple Docker Hub publish flow.
# Example:
#   DOCKERHUB_USER=svastik ./scripts/publish_analyzer_image.sh

DOCKERHUB_USER="${DOCKERHUB_USER:-}"
IMAGE_NAME="${IMAGE_NAME:-microservices-stress-analyzer}"
TAG="${TAG:-latest}"
LOCAL_IMAGE="${LOCAL_IMAGE:-microservices-stress-analyzer:latest}"

if [[ -z "${DOCKERHUB_USER}" ]]; then
  echo "[publish] set DOCKERHUB_USER first (example: DOCKERHUB_USER=svastik)" >&2
  exit 1
fi

REMOTE_IMAGE="docker.io/${DOCKERHUB_USER}/${IMAGE_NAME}:${TAG}"

if [[ "${DOCKERHUB_USER}" == *"<"* || "${IMAGE_NAME}" == *"<"* ]]; then
  echo "[publish] placeholder detected in image naming vars" >&2
  exit 1
fi

echo "[publish] local image: ${LOCAL_IMAGE}"
echo "[publish] remote image: ${REMOTE_IMAGE}"

docker tag "${LOCAL_IMAGE}" "${REMOTE_IMAGE}"
docker push "${REMOTE_IMAGE}"

echo "[publish] pushed: ${REMOTE_IMAGE}"
echo "${REMOTE_IMAGE}"
