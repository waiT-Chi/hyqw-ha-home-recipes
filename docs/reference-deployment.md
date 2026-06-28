# Reference Deployment Scope

This repository is based on a real homeowner deployment, not only a theoretical
Home Assistant install.

The upstream [`origintree/hyqw_adapter`](https://github.com/origintree/hyqw_adapter)
project is treated as the adapter layer for the property-developer RS-485
system. The referenced deployment then builds a complete Home Assistant
operations layer above it.

## Host layer

The referenced deployment runs on a Mac mini. Home Assistant and nearby
supporting services are containerized with Docker so they can be managed,
backed up, restarted, and migrated as service units rather than as one-off
manual installs.

The public docs intentionally do not publish exact compose files, host paths,
ports, LAN addresses, or secrets. The reusable point is the host pattern:

- keep Home Assistant and supporting services on an always-on local machine;
- use containers for repeatable service boundaries;
- keep persistent volumes and backups explicit;
- document which services are required for daily control versus optional
  monitoring or notification workflows.

## What was built on top of the adapter

The deployment brings several ecosystems into one Home Assistant control plane:

- property-developer RS-485 devices through the HYQW adapter;
- Home Assistant and nearby services running as Docker containers on a Mac mini;
- Mijia / Xiaomi Home / Xiaomi Miot devices;
- Midea / Toshiba and similar appliance integrations;
- optional local MQTT broker or bridge paths;
- Apple Home / Siri exposure through HomeKit Bridge;
- Home Assistant automations, dashboards, notifications, and recovery checks.

The practical work is not only "install an integration". It includes deciding
which system owns which control layer, validating state after writes, handling
integration instability, and keeping private infrastructure controls away from
voice assistants.

## Field feedback to the adapter layer

During real deployment, several adapter-layer issues became visible, including:

- hard-coded device validation values that do not work for other homes;
- `paho-mqtt` 2.x compatibility problems in newer Home Assistant environments;
- MQTT connection-loop timing that can make the connection drop too early;
- base URL and HAR parsing assumptions that may not match every deployment.

Those issues belong in the upstream adapter as generic fixes when they can be
made privacy-safe. This repo keeps the operational lessons and safe templates
around them.

## Operations work captured here

This companion repo documents the home-operations layer:

- lighting ownership between RS-485 main circuits and downstream smart lights;
- staged Xiaomi Home migration with old-entity fallback;
- Midea / appliance availability monitoring and verified reminders;
- conservative HomeKit / Siri exposure;
- power-failure recovery windows;
- local MQTT first with an automatic cloud-safe fallback for the developer
  RS-485 gateway;
- sanitization rules for publishing examples without leaking home details.

## What remains private

The reference deployment intentionally does not publish:

- real gateway serial numbers;
- real MQTT topics, credentials, or replay payloads;
- complete HAR files;
- exact room layout and daily routines;
- HomeKit pairing codes or local network broadcast details;
- appliance cloud account identifiers.

Public examples should stay at the pattern and template level.
