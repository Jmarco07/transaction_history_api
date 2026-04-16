#!/usr/bin/env bash
set -euo pipefail

LAYER_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_ZIP="PythonRequirements.zip"

echo "🚀 Building Lambda layer for Python 3.11 in AWS SAM container..."

# Clean up old build
rm -rf "${LAYER_DIR}/python" "${OUTPUT_ZIP}"

docker run --rm --platform linux/amd64 \
  -v "${LAYER_DIR}":/var/task \
  -w /var/task \
  public.ecr.aws/sam/build-python3.11:latest \
  /bin/bash -c "\
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt -t python/ \
  "

# Zip it up
zip -r "${OUTPUT_ZIP}" python > /dev/null

echo "✅ Layer built: ${OUTPUT_ZIP}"
