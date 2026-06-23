# Solution Design

## Overview

The exporter is a single Python process that polls an ASUS router's local HTTP API on a
configurable interval and exposes the results as Prometheus metrics on `/metrics`.

## Design Decisions

### Library: asusrouter (Vaskivskyi)

The `asusrouter` library ([PyPI](https://pypi.org/project/asusrouter/)) is used for all
router communication. It handles HTTP authentication, session management, and response
parsing for a wide range of ASUS firmware versions.

Alternatives considered:

| Option | Reason rejected |
|---|---|
| Raw HTTP (reverse-engineered endpoints) | Fragile — firmware updates change endpoints |
| CipherDoc34/asus-prometheus-exporter (Go) | No WiFi client data; no published Docker image |
| Fork of RafaelMoreira1180778/asus-router-monitoring | docker-compose stack, not a standalone exporter; still uses asusrouter internally |
| SNMP | Removed from stock firmware `3.0.0.4.388+` |

### Single target per instance

Each exporter instance monitors one router. For AiMesh systems, the main router aggregates
client state for all nodes — polling only the main router is sufficient to get mesh-wide
client counts. Individual node metrics (per-node CPU, RAM) are not available through the
main router API and are not in scope.

### Async-native

`asusrouter` is an async library. The exporter uses `asyncio` throughout and fetches all
metric categories concurrently within each scrape using `asyncio.gather`.

### Connection lifecycle

A single `async with AsusRouter(...)` context is held open across all scrape intervals.
If the connection drops (router reboot, network blip), the outer `while True` loop catches
the exception, sets `asus_scrape_success=0`, and reconnects after 60 seconds.

### Defensive attribute access

Router firmware versions differ in which fields are populated. All attribute reads use
`getattr(obj, "attr", None)` and skip metric updates when data is absent. This ensures
the exporter works across firmware versions without crashing on missing fields.

### Image tagging

Images are tagged with the git SHA (`ghcr.io/<repo>:<sha>`) for reproducibility. The
`latest` tag is also pushed for convenience but deployments should always pin to the SHA.

### GitHub-hosted runner

The CI pipeline runs on `ubuntu-latest` (GitHub-hosted). The build step — `docker build`
+ `docker push to GHCR` + `git commit to infra repo` — requires no cluster access.
Using a GitHub-hosted runner avoids the risk of arbitrary PR code executing on private
self-hosted infrastructure.

### Security

- Credentials are injected at runtime via environment variables only
- Credentials never appear in logs — the exporter logs the target hostname only
- The Docker image runs as `nobody` (non-root)
- The router HTTP password is stored in a secrets manager in the deployment environment;
  it is never committed to any repository
