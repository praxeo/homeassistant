#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path("/config")
OUT_PATH = CONFIG_DIR / "entities.md"
HASS_URL = os.environ.get("HASS_URL", "http://supervisor/core").rstrip("/")
TOKEN = os.environ.get("HASS_TOKEN")

if not TOKEN:
    sys.exit("Missing HASS_TOKEN environment variable. Source /config/.hass_env first.")

req = urllib.request.Request(
    f"{HASS_URL}/api/states",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    },
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        states = json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as exc:
    sys.exit(f"API call failed ({exc.code}): {exc.reason}")
except urllib.error.URLError as exc:
    sys.exit(f"Unable to reach {HASS_URL}: {exc.reason}")

states.sort(key=lambda item: item.get("entity_id", ""))

timestamp = datetime.now().isoformat(timespec="seconds")
lines = [
    "# Home Assistant Entities\n",
    f"- Generated: {timestamp}\n",
    f"- Count: {len(states)}\n\n",
    "| entity_id | friendly_name | domain | area_id | device_id |\n",
    "|---|---|---|---|---|\n",
]

for state in states:
    entity_id = state.get("entity_id", "")
    domain = entity_id.split(".", 1)[0] if "." in entity_id else ""
    attrs = state.get("attributes") or {}
    friendly = str(attrs.get("friendly_name", "")).replace("|", "\\|").replace("\n", " ").strip()
    area_id = str(attrs.get("area_id", "") or "")
    device_id = str(attrs.get("device_id", "") or "")
    lines.append(f"| `{entity_id}` | {friendly} | {domain} | {area_id} | {device_id} |\n")

OUT_PATH.write_text("".join(lines), encoding="utf-8")
print(f"Wrote {OUT_PATH} ({len(states)} entities)")
