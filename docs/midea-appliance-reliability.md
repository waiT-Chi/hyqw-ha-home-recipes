# Midea Appliance Reliability Pattern

This document covers reliability patterns for Midea, Toshiba, and similar
appliance integrations in Home Assistant.

The goal is not to present cloud-connected appliances as perfectly reliable.
The goal is to make their failure modes visible and avoid building fragile
automations around optimistic state.

## Common failure modes

- The appliance entity becomes `unavailable` while the appliance is physically
  online.
- Completion state appears late or not at all.
- A cloud integration reports a stale state.
- A local/LAN integration works for one model but not another.
- A service call succeeds but the appliance state does not actually change.

## Reliability model

| Use case | Recommended approach |
| --- | --- |
| Status display | Accept occasional stale or unavailable states, but make them visible. |
| Completion reminder | Require a stable transition and read-back before notifying. |
| Critical control | Avoid unattended control unless verified on the exact model. |
| Troubleshooting | Track availability separately from appliance state. |

## Availability watch

Use
[`templates/home-assistant/midea-availability-watch.yaml`](../templates/home-assistant/midea-availability-watch.yaml)
to notify when an appliance integration stays unavailable for a meaningful
period.

The template is intentionally generic. It can apply to a washer, dryer, AC, or
other appliance entity.

## Completion reminder

For washer/dryer style devices, prefer a conservative reminder:

1. Detect a transition from running to finished/idle.
2. Wait briefly.
3. Read the state again.
4. Notify only if the finished/idle state is still true.

This avoids reminders caused by short cloud reconnects or transient state
updates.

## What not to publish

Do not publish appliance serial numbers, cloud account IDs, real integration
diagnostic dumps, or debug logs that include request headers. Keep examples at
the entity-placeholder level.

