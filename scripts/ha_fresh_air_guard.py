#!/usr/bin/env python3
"""Home Assistant fresh-air recovery guard.

This is a privacy-safe, HA-only fallback guard for devices that may restore to an
undesired ON state after power recovery. It does **not** contain vendor cloud
endpoints, MQTT topics, device serial numbers, or captured payloads.

Typical usage:

    export HA_URL="https://home-assistant.example.invalid"
    export HA_TOKEN="<long-lived-access-token>"
    export FRESH_AIR_ENTITY="fan.<fresh_air_entity>"
    python3 scripts/ha_fresh_air_guard.py --mode notify
    python3 scripts/ha_fresh_air_guard.py --mode turn-off --confirm-delay 20

Optional notification:

    export NOTIFY_SERVICE="notify.mobile_app_your_phone"

The script is intentionally small and auditable. Use it as a pattern, not as a
vendor-specific bypass.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HAConfig:
    url: str
    token: str

    @classmethod
    def from_env(cls) -> "HAConfig":
        url = os.environ.get("HA_URL", "").rstrip("/")
        token = os.environ.get("HA_TOKEN", "")
        if not url or not token:
            raise SystemExit("HA_URL and HA_TOKEN must be set")
        return cls(url=url, token=token)


class HomeAssistantClient:
    def __init__(self, config: HAConfig, timeout: int = 10) -> None:
        self.config = config
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.config.url + path,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.config.token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                text = resp.read().decode("utf-8")
                return json.loads(text) if text else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Home Assistant API {method} {path} failed: {exc.code} {detail}") from exc

    def get_state(self, entity_id: str) -> str:
        data = self._request("GET", f"/api/states/{entity_id}")
        return str(data.get("state", "unknown"))

    def call_service(self, domain: str, service: str, entity_id: str | None = None, data: dict[str, Any] | None = None) -> Any:
        payload = dict(data or {})
        if entity_id:
            payload["entity_id"] = entity_id
        return self._request("POST", f"/api/services/{domain}/{service}", payload)


def parse_notify_service(value: str) -> tuple[str, str]:
    if not value or "." not in value:
        raise ValueError("notify service must look like notify.mobile_app_xxx")
    return tuple(value.split(".", 1))  # type: ignore[return-value]


def notify(client: HomeAssistantClient, message: str) -> None:
    service_name = os.environ.get("NOTIFY_SERVICE", "")
    if not service_name:
        print(message)
        return
    domain, service = parse_notify_service(service_name)
    client.call_service(domain, service, data={"message": message})


def main() -> int:
    parser = argparse.ArgumentParser(description="HA-only fresh-air recovery guard")
    parser.add_argument("--entity", default=os.environ.get("FRESH_AIR_ENTITY", "fan.<fresh_air_entity>"))
    parser.add_argument("--mode", choices=["notify", "turn-off"], default="notify")
    parser.add_argument("--confirm-delay", type=int, default=20, help="seconds to wait before re-checking an ON state")
    args = parser.parse_args()

    if "<" in args.entity or ">" in args.entity:
        raise SystemExit("Set --entity or FRESH_AIR_ENTITY to a real Home Assistant entity_id")

    client = HomeAssistantClient(HAConfig.from_env())
    initial = client.get_state(args.entity)
    if initial != "on":
        print(f"OK: {args.entity} state is {initial}; no recovery action needed")
        return 0

    time.sleep(max(0, args.confirm_delay))
    confirmed = client.get_state(args.entity)
    if confirmed != "on":
        print(f"OK: {args.entity} recovered from on to {confirmed}; no action taken")
        return 0

    if args.mode == "turn-off":
        client.call_service("fan", "turn_off", args.entity)
        final_state = client.get_state(args.entity)
        if final_state != "off":
            notify(client, f"Fresh-air guard tried to turn off {args.entity}, but final state is {final_state}")
            return 2
        notify(client, f"Fresh-air guard detected {args.entity} was on after recovery and turned it off.")
    else:
        notify(client, f"Fresh-air guard detected {args.entity} is on after recovery. No action taken.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
