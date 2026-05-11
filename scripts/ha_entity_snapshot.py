#!/usr/bin/env python3
"""Export a sanitized Home Assistant entity snapshot.

This helps document a deployment without publishing secrets or exact household
identifiers. It keeps entity domains, coarse capabilities, and friendly names only
when they do not look sensitive.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from collections import Counter
from typing import Any

SENSITIVE_NAME = re.compile(r"(?:token|secret|password|passwd|phone|mobile|sn|serial|mac|imei|address)", re.I)


def ha_get(url: str, token: str, path: str) -> Any:
    req = urllib.request.Request(
        url.rstrip("/") + path,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sanitize_entity(entity: dict[str, Any]) -> dict[str, Any]:
    entity_id = entity.get("entity_id", "")
    domain = entity_id.split(".", 1)[0] if "." in entity_id else "unknown"
    attrs = entity.get("attributes") or {}
    safe_attrs = {}
    for key in ("device_class", "supported_features", "unit_of_measurement"):
        if key in attrs:
            safe_attrs[key] = attrs[key]
    friendly = attrs.get("friendly_name")
    if isinstance(friendly, str) and not SENSITIVE_NAME.search(friendly):
        safe_attrs["friendly_name"] = friendly
    return {
        "domain": domain,
        "entity_id_template": f"{domain}.<redacted>",
        "state_class": "available" if entity.get("state") not in ("unavailable", "unknown") else entity.get("state"),
        "attributes": safe_attrs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="export sanitized HA entity snapshot")
    parser.add_argument("--output", default="ha-entity-snapshot.sanitized.json")
    args = parser.parse_args()

    url = os.environ.get("HA_URL", "")
    token = os.environ.get("HA_TOKEN", "")
    if not url or not token:
        raise SystemExit("HA_URL and HA_TOKEN must be set")

    states = ha_get(url, token, "/api/states")
    sanitized = [sanitize_entity(item) for item in states]
    counts = Counter(item["domain"] for item in sanitized)
    payload = {
        "summary": dict(sorted(counts.items())),
        "entities": sanitized,
    }
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"Wrote sanitized snapshot to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
