#!/usr/bin/env bash
# Build → SBOM → scan → sign → SBOM-attestation. Requires: docker, syft, grype, cosign.
set -euo pipefail
IMAGE=${IMAGE:-ghcr.io/me/iris-api:0.6}

docker buildx build -t "$IMAGE" --push .

syft -o cyclonedx-json "$IMAGE" > sbom.cdx.json
grype sbom:sbom.cdx.json --fail-on high

COSIGN_EXPERIMENTAL=1 cosign sign --yes "$IMAGE"
COSIGN_EXPERIMENTAL=1 cosign attest --yes --type cyclonedx --predicate sbom.cdx.json "$IMAGE"
