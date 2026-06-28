# Contribution Scope

## Upstream credit

The HYQW adapter itself is credited to:

- [`origintree/hyqw_adapter`](https://github.com/origintree/hyqw_adapter)
- Code owner: `@origintree`

This repository does not claim authorship of the original adapter.

## What belongs upstream

If you improve the adapter itself, consider contributing directly to the upstream project. Examples:

- bug fixes in entity implementations;
- Home Assistant compatibility updates;
- config-flow improvements;
- safer state synchronization logic;
- documentation for supported device types;
- generic replay-recorder improvements that do not reveal private payloads.

## What belongs in this companion repo

This repo is for deployment recipes and operational knowledge that are useful but not necessarily part of the adapter core:

- architecture notes;
- automation patterns;
- multi-ecosystem deployment notes that combine HYQW, Home Assistant, Xiaomi, Midea, and Apple Home;
- privacy-safe troubleshooting workflows;
- power-failure recovery design;
- examples of control-boundary separation;
- verification checklists.

## Why not publish everything?

A real home deployment contains information that should not be public:

- account identifiers;
- device serial numbers;
- cloud API tokens;
- exact internal IP addresses and hostnames;
- MQTT topic strings tied to a real gateway;
- captured binary payloads;
- HAR files and API responses containing private metadata.

Publishing those would put the homeowner at risk and make it easy for others to copy a deployment without understanding the safety boundary.

## Recommended attribution wording

If you reuse these notes, please credit both layers:

```text
Adapter layer based on origintree/hyqw_adapter.
Operational recipes adapted from waiT-Chi/hyqw-ha-home-recipes.
```
