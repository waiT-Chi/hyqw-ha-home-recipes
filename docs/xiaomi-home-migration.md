# Xiaomi Home Migration Pattern

This document describes a low-risk way to move selected devices from an older
Xiaomi/Mijia integration to a newer Xiaomi Home integration in Home Assistant.

It is a migration pattern, not a claim that every Xiaomi entity should be
switched at once.

## Why migrate slowly

Many homes accumulate Xiaomi entities from several sources:

- Xiaomi/Mijia cloud integrations;
- Xiaomi Miot custom integrations;
- newer Xiaomi Home integrations;
- BLE gateways and subdevices;
- duplicate entities exposed through multiple paths.

The risky move is to replace every entity in automations at once. A safer move
is to migrate only the entities that have stable readings and clear history.

## Migration checklist

1. Export a sanitized entity snapshot.
2. Pick one device family, such as air-quality sensors or a purifier.
3. Compare old and new entities over real history.
4. Update read-only dashboards first.
5. Update low-risk notifications next.
6. Keep the old entity as a fallback until the new path is stable.
7. Only then consider changing control automations.

## Shadow comparison

Use
[`templates/home-assistant/xiaomi-shadow-compare.yaml`](../templates/home-assistant/xiaomi-shadow-compare.yaml)
to log or notify when an old entity and a new entity drift too far apart.

This is useful for sensors such as:

- PM2.5;
- CO2;
- formaldehyde / HCHO;
- temperature;
- humidity;
- purifier mode or fan state.

## Fallback policy

Use the old entity as a fallback when:

- the new entity becomes `unavailable` more often;
- the new entity lacks an attribute used by existing automations;
- service calls work in one integration but not the other;
- historical values diverge enough to change alert behavior.

Disable old automations only after you have verified the replacement path. Do
not delete the old configuration during the first migration pass.

## What not to publish

Do not publish Xiaomi account IDs, device IDs, cloud tokens, BLE keys, or full
Home Assistant `.storage` exports. Public examples should only include generic
entity placeholders.

