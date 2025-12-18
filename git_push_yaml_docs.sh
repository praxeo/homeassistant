#!/usr/bin/env bash
set -euo pipefail

cd /config

ENV_FILE="/config/.hass_env"
if [[ -f "$ENV_FILE" ]]; then
  # Export variables defined in the env file (HASS_URL, HASS_TOKEN, etc.)
  set -a
  # shellcheck source=/config/.hass_env
  source "$ENV_FILE"
  set +a
else
  echo "Warning: $ENV_FILE not found. export_entities.py may fail without HASS credentials." >&2
fi

if [[ -x ./export_entities.py ]]; then
  ./export_entities.py
else
  python3 ./export_entities.py
fi

git add -A

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

timestamp="$(date '+%Y-%m-%d %H:%M:%S%z')"
git commit -m "Auto update: ${timestamp}"
git push origin main
