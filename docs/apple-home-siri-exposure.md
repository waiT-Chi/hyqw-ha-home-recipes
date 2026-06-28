# Apple Home and Siri Exposure

This document describes a conservative Home Assistant to Apple Home exposure
strategy for mixed smart-home deployments.

The safest setup is not to expose every Home Assistant entity. Expose the
devices that make sense for daily voice and Apple Home control, and keep
infrastructure controls private.

## Good candidates

- user-facing room lights;
- curtains and covers with clear open/close semantics;
- air purifiers and fans that are safe to control by voice;
- read-only temperature, humidity, and air-quality sensors;
- a small number of scenes with friendly names.

## Poor candidates

- gateway admin switches;
- router or Wi-Fi toggles;
- main power circuits that can accidentally cut power to downstream devices;
- duplicate entities representing the same physical device;
- alarm, lock, and camera controls unless you have reviewed the security model;
- debug helpers, scripts, and one-off maintenance switches.

## Naming model

Use names that are natural in the room where the device appears:

```text
Living Room Main Light
Bedroom Curtains
Kitchen Air Purifier
```

Avoid exposing integration-specific names such as:

```text
HYQW RS485 Switch 03
Xiaomi Miot Light Entity 2
Midea Cloud AC Toggle
```

## Exposure checklist

1. Build a candidate list from daily-use entities only.
2. Remove duplicates and admin helpers.
3. Rename entities for voice use.
4. Pair the bridge and verify each room in Apple Home.
5. Add one batch at a time rather than exposing the whole HA instance.

## Home Assistant example

The following is a shape, not a complete configuration:

```yaml
homekit:
  - name: Home Assistant Bridge
    filter:
      include_entities:
        - light.<ROOM_LIGHT_ENTITY>
        - cover.<ROOM_CURTAIN_ENTITY>
        - fan.<AIR_PURIFIER_ENTITY>
        - sensor.<AIR_QUALITY_ENTITY>
    entity_config:
      light.<ROOM_LIGHT_ENTITY>:
        name: Living Room Main Light
```

Keep pairing codes, advertised addresses, bridge ports, and network-specific
values out of public examples.

