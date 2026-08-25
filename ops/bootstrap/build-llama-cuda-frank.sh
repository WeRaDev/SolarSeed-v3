#!/usr/bin/env bash
# Build llama.cpp server image matching Frank's driver 550 (CUDA 12.4) + GTX 1050 Ti (sm_61).
# Do NOT use rolling ghcr.io/ggml-org/llama.cpp:server-cuda (CUDA >=12.8 breaks this host).
set -euo pipefail

SRC_DIR="${SRC_DIR:-/data-bulk/build/llama.cpp}"
IMAGE_TAG="${IMAGE_TAG:-local/llama.cpp:server-cuda-12.4.1-sm61}"
CUDA_VERSION="${CUDA_VERSION:-12.4.1}"
UBUNTU_VERSION="${UBUNTU_VERSION:-22.04}"
CUDA_DOCKER_ARCH="${CUDA_DOCKER_ARCH:-61}"
GCC_VERSION="${GCC_VERSION:-11}"
LOG="${LOG:-/tmp/llama-cuda-build.log}"

if [[ ! -d "$SRC_DIR/.git" ]]; then
  mkdir -p "$(dirname "$SRC_DIR")"
  git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$SRC_DIR"
fi

cd "$SRC_DIR"
echo "Building $IMAGE_TAG from $(git rev-parse --short HEAD) in $SRC_DIR"
echo "Log: $LOG"

docker build \
  -t "$IMAGE_TAG" \
  --target server \
  -f .devops/cuda.Dockerfile \
  --build-arg "CUDA_VERSION=${CUDA_VERSION}" \
  --build-arg "UBUNTU_VERSION=${UBUNTU_VERSION}" \
  --build-arg "CUDA_DOCKER_ARCH=${CUDA_DOCKER_ARCH}" \
  --build-arg "GCC_VERSION=${GCC_VERSION}" \
  . | tee "$LOG"

docker image inspect "$IMAGE_TAG" >/dev/null
echo "OK: $IMAGE_TAG"
