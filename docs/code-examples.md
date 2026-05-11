# Code Examples

This repository includes a small amount of privacy-safe code. The goal is to make
the repo useful without publishing vendor-private payloads or a turnkey commercial
integration package.

## `scripts/ha_fresh_air_guard.py`

A Home Assistant REST API guard for devices that may restore to `on` after power
recovery. It can run in two modes:

- `notify`: only report that the entity is still on;
- `turn-off`: confirm the state, call `fan.turn_off`, then read back the final state.

Required environment variables:

```bash
export HA_URL="https://home-assistant.example.invalid"
export HA_TOKEN="<long-lived-access-token>"
export FRESH_AIR_ENTITY="fan.<fresh_air_entity>"
```

Optional notification service:

```bash
export NOTIFY_SERVICE="notify.mobile_app_<device>"
```

Example:

```bash
python3 scripts/ha_fresh_air_guard.py --mode notify
python3 scripts/ha_fresh_air_guard.py --mode turn-off --confirm-delay 20
```

## `scripts/ha_entity_snapshot.py`

Exports a sanitized Home Assistant entity snapshot for documentation. It keeps
entity domains and coarse capabilities, while replacing exact entity IDs with
`<redacted>` templates.

```bash
python3 scripts/ha_entity_snapshot.py --output ha-entity-snapshot.sanitized.json
```

Do not commit the unsanitized Home Assistant state registry or `.storage` files.

## `scripts/sanitize_check.py`

A pre-publication leak scanner for this repo:

```bash
python3 scripts/sanitize_check.py .
```

It checks for common mistakes such as:

- tokens and authorization headers;
- private IP addresses;
- phone numbers;
- captured `payload_hex` assignments;
- long hex payloads;
- likely device serial numbers.

If a line is a harmless documentation-only mention, use a precise comment:

```text
# sanitize-check: ignore
```

Avoid broad allowlists.

## systemd example

`examples/systemd/` contains a timer/service pair showing how to run the HA guard
shortly after host boot. The example expects secrets to live in an external
`EnvironmentFile`, which is intentionally not committed.
