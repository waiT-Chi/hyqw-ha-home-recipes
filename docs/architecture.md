# Architecture Notes

This document describes the architecture pattern, not a copy-paste deployment.

## Context

Many residential projects ship with a property-developer smart-home system based on an RS-485 gateway. It may control lights, HVAC, floor heating, curtains, fresh air systems, and other fixed infrastructure. These systems often expose a mobile app and a cloud backend but do not integrate cleanly with Home Assistant, Apple Home, Xiaomi/Mijia, or other ecosystems.

The referenced deployment uses the upstream [`origintree/hyqw_adapter`](https://github.com/origintree/hyqw_adapter) integration as the adapter layer, then adds a full home-operations layer around it. See [`reference-deployment.md`](reference-deployment.md) for the scope of that real deployment.

## High-level architecture

```text
Mac mini Docker host
  ↓
Home Assistant container + supporting service containers
  ↓
HYQW adapter + Mijia + Midea + HomeKit bridge integrations
  ↑
Developer / HYQW gateway -> local/cloud MQTT path -> adapter
  ↑
Property RS-485 devices

Home Assistant automations, dashboards, and user-facing controls
```

In a more complete home, Home Assistant may also integrate:

- a Mac mini host running Home Assistant and nearby services in Docker;
- Mijia / Xiaomi devices;
- Midea / Toshiba / appliance LAN integrations;
- MQTT broker or bridge;
- monitoring stack such as InfluxDB + Grafana;
- notification channels such as mobile push or chat bots;
- optional Apple Home / Siri exposure for a curated set of daily-use devices.

## Upstream network topology pattern

The upstream topology emphasizes a local network interception pattern:

```text
Developer RS-485 gateway
  -> local DNS/hosts redirect
  -> local MQTT broker
  -> MQTT bridge to vendor MQTT
  -> HYQW adapter / Home Assistant entities
```

That pattern keeps the original app and wall panel usable while allowing Home
Assistant to observe and control devices locally. This repo does not publish the
exact network rules or credentials; see
[`upstream-topology-notes.zh-CN.md`](upstream-topology-notes.zh-CN.md) for a
sanitized Chinese explanation.

## Important boundaries

### Adapter layer

The upstream adapter owns the protocol-specific work:

- device list import;
- entity creation;
- state query;
- device control abstraction;
- platform support for lights, climate, covers, fans, etc.

### Operations layer

This companion repo focuses on the home-operations layer:

- how to combine the HYQW adapter with Xiaomi, Midea, Apple Home, and other ecosystems;
- how to structure automations so different control systems do not fight each other;
- how to verify state changes rather than trusting service-call success;
- how to design power-failure recovery without depending on a desktop machine being logged in;
- how to expose only daily-use devices to voice assistants while keeping admin controls private;
- how to document and audit assumptions safely.

## Design principles

1. **Manual control wins**
   Automations should not make wall switches or household habits feel broken.

2. **Control the right abstraction**
   A main circuit switch is not the same thing as the individual smart lights downstream of it.

3. **Verify physical state**
   Some integrations update Home Assistant optimistically after an API call. Confirm with a state query or device feedback when the distinction matters.

4. **Avoid publishing secrets**
   Never publish serial numbers, cloud tokens, raw MQTT payloads, full HAR files, or exact private topic strings.

5. **Make failure modes explicit**
   Power loss, cloud outage, local network failure, and Home Assistant downtime are separate cases.
