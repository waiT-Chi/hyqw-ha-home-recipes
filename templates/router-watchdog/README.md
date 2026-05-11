# Router watchdog design notes

This directory intentionally does **not** include a turnkey router script.

A router-side watchdog can be useful when Home Assistant runs on a machine that may not auto-login after a power outage. The router often starts earlier than Home Assistant and can perform a narrow recovery check.

## Safe design

1. Run only during a short boot window, for example the first 10-15 minutes after router startup.
2. Check the device state first.
3. If the device is in an unsafe or undesirable restore state, send a close/off command.
4. Verify state again.
5. Exit. Do not keep overriding normal manual use.

## Possible close strategies

- MQTT replay payload, if you have safely captured and privately stored a payload for your own device.
- Cloud API fallback, if the vendor API is available and you are using your own account token.

## What not to publish

Do not publish:

- raw payload hex;
- exact MQTT topics for a real home;
- cloud tokens;
- device serial numbers;
- public instructions that allow control of someone else's gateway.

## Pseudocode

```text
if router_uptime > RESTORE_WINDOW:
    exit

state = query_device_state()
if state != ON:
    exit

if mqtt_close_payload_available:
    publish_mqtt_close_payload()
    wait
    if query_device_state() == OFF:
        exit

call_cloud_api_close()
wait
verify_state()
```

## Why this is not turnkey

A recovery script that can control fixed home infrastructure is powerful. Publishing a ready-to-use script with payload handling, cloud headers, and topic construction would make it too easy to repurpose without understanding the safety boundary. The goal here is to document the pattern, not to ship a commercial installer.
