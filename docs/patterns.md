# Operational Patterns

## Pattern 1: Main circuit vs individual smart lights

### Problem

A room may have a developer-provided RS-485 circuit switch and several downstream smart lights from another ecosystem.

If Home Assistant treats all of them as equivalent lights, automations may fight the user's manual controls.

### Recommended model

- Keep the **main circuit** on during the active window so the downstream smart lights have power.
- Let the **individual smart lights** be controlled by the user's preferred physical or Bluetooth switch.
- Do not include the individual smart lights in the keep-on automation.

See [`templates/home-assistant/kitchen-main-switch.yaml`](../templates/home-assistant/kitchen-main-switch.yaml).

## Pattern 2: Power-failure recovery for devices with bad defaults

### Problem

Some built-in systems restore to an undesirable state after a power outage, such as a fresh-air system turning on automatically.

If Home Assistant runs on a desktop or mini PC with disk encryption enabled, it may not start until a user logs in. A Home Assistant automation alone may not be sufficient.

### Recommended model

Layered recovery:

1. **Device-side setting** if available: set power-restore behavior to off or memory mode.
2. **Always-on edge watchdog** if safe and appropriate: a router or small always-on device checks during a short boot window.
3. **Home Assistant fallback**: on HA start or gateway reconnect, check and correct the state.

### Safety boundary

Use a short boot/recovery window, for example 10-15 minutes, so normal manual use later in the day is not overridden.

See:

- [`templates/home-assistant/fresh-air-ha-guard.yaml`](../templates/home-assistant/fresh-air-ha-guard.yaml)
- [`templates/router-watchdog/README.md`](../templates/router-watchdog/README.md)

## Pattern 3: Verification after write

Do not treat a successful API response as proof of physical device state.

For critical operations:

1. Call the service or API.
2. Wait an appropriate short delay.
3. Read state back from a reliable source.
4. Only then report success.

Examples:

- After `light.turn_on`, read `light.<entity>` state.
- After a cloud API control call, query the device state endpoint.
- After editing Home Assistant YAML, run config check, reload, and read the automation entity state.

## Pattern 4: Keep private payloads private

Replay payloads and cloud tokens can be powerful. Treat them like credentials.

Do not publish:

- exact MQTT topic strings for a real home;
- raw captured payloads;
- complete HAR files;
- device serial numbers or account IDs.

Publish only redacted templates and explain the reasoning.
