#!/usr/bin/env bash
# generate-api.sh — genera el cliente de la API del frontend desde el OpenAPI del backend.
# Requiere openapi-typescript (instalar: npm i -D openapi-typescript).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENAPI_URL="${OPENAPI_URL:-http://localhost:8000/openapi.json}"
OUT="${ROOT}/frontend/src/app/core/openapi.ts"

echo "→ Descargando OpenAPI desde ${OPENAPI_URL}"
curl -fsSL "${OPENAPI_URL}" -o "${TMPDIR:-/tmp}/openapi.json"

echo "→ Generando cliente TypeScript"
npx openapi-typescript "${TMPDIR:-/tmp}/openapi.json" -o "${OUT}"

echo "✓ Cliente generado en ${OUT}"