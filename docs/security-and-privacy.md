# Security and Privacy

This project intentionally avoids publishing a complete working dump of a real home.

## Do not commit

- Home Assistant `.storage` files;
- cloud API tokens;
- personal account IDs or phone numbers;
- exact gateway serial numbers;
- exact home domain names;
- exact private IP topology;
- exact room layouts and household routines;
- HomeKit pairing codes, bridge ports, and advertised LAN addresses;
- captured HAR files;
- MQTT payload hex strings;
- router scripts containing live credentials;
- turnkey router scripts that can directly redirect or control a real RS-485
  gateway.

## Use placeholders

Use placeholders in public examples:

```yaml
entity_id: light.<MAIN_CIRCUIT_ENTITY>
```

```text
<DEVICE_SN>
<PROJECT_CODE>
<MQTT_TOPIC>
<CLOUD_TOKEN>
```

## Responsible disclosure / upstreaming

If you find a security-sensitive issue in the upstream adapter or vendor system, avoid publishing exploit details. Prefer responsible disclosure or a minimal, privacy-safe upstream issue.

## License intent

The license is non-commercial to discourage direct resale of these notes as a turnkey paid installation package without permission or credit.
