# Lighting Control Boundaries

This document describes how to operate mixed lighting systems where a
developer-provided RS-485 circuit, Mijia lights, and Home Assistant scenes all
exist in the same room.

The main idea is simple: do not let two control layers fight over the same
physical light.

## Common topology

```text
Wall circuit / RS-485 relay
  -> downstream smart light power
  -> Mijia / Bluetooth / Zigbee light behavior
  -> Home Assistant scene or automation
```

In this model, the RS-485 entity may represent a power circuit, not the actual
lamp behavior the user sees.

## Recommended ownership model

| Layer | Owns | Should avoid |
| --- | --- | --- |
| RS-485 / developer gateway | Main circuit availability | Fine-grained brightness or color behavior |
| Mijia / smart lights | Device-level brightness, color, and native switch behavior | Cutting power to other ecosystems |
| Home Assistant | Scenes, guardrails, status checks, and cross-ecosystem orchestration | Fighting physical switches or app-specific scenes |
| Apple Home / voice assistants | Simple daily commands with friendly names | Admin switches, duplicate entities, and unsafe circuits |

## Rules of thumb

- Treat a main circuit as power infrastructure.
- Treat a smart light as the user-facing light.
- Keep critical downstream smart lights powered during active hours.
- Do not put the same physical device into multiple automations unless one layer
  is explicitly read-only.
- Prefer room scenes over individual-device automations when several ecosystems
  must change together.
- Keep admin helpers, router switches, gateway controls, and duplicated entities
  out of voice assistants.

## Example: room scene with circuit guard

Use the template in
[`templates/home-assistant/lighting-scene-boundary.yaml`](../templates/home-assistant/lighting-scene-boundary.yaml)
when a scene needs to make sure the main circuit is on before controlling
downstream smart lights.

The template intentionally separates:

- a circuit pre-check;
- the actual user-facing scene;
- read-back verification;
- optional notification when the expected state is not reached.

## What not to publish

Avoid publishing a complete room-by-room lighting dump. It can reveal the
home's layout and habits. Public examples should use placeholders such as:

```yaml
light.<MAIN_CIRCUIT_ENTITY>
scene.<ROOM_SCENE_ENTITY>
binary_sensor.<ROOM_OCCUPANCY_ENTITY>
```

