# Implementation Plan

## Index

| Phase | Name | Status |
|---|---|---|
| [001](#phase-001-initial-exporter) | Initial Exporter | in progress |
| [002](#phase-002-grafana-dashboard) | Grafana Dashboard | planned |
| [003](#phase-003-syslog-correlation) | Syslog Correlation Notes | planned |

---

## Phase 001: Initial Exporter

Status: in progress

### Goal

Build a working Prometheus exporter that connects to an ASUS router, collects the core
metrics, and ships a multi-arch Docker image via GitHub Actions.

### Deliverables

| File | Purpose |
|---|---|
| `exporter.py` | Main exporter — async Python using the `asusrouter` library |
| `requirements.txt` | Pinned Python dependencies |
| `Dockerfile` | Multi-arch image definition |
| `.github/workflows/build.yml` | CI: build linux/amd64 + linux/arm64, push to GHCR |

### Metrics

| Metric | Type | Description |
|---|---|---|
| `asus_router_info` | Info | Model and firmware version |
| `asus_scrape_success` | Gauge | 1 if last scrape succeeded, 0 on failure |
| `asus_scrape_duration_seconds` | Gauge | Time taken to scrape the router |
| `asus_clients_total` | Gauge | Total connected clients (wired + wireless) |
| `asus_clients_by_band{band}` | Gauge | Wireless clients per band (2.4 GHz / 5 GHz / 6 GHz) |
| `asus_cpu_usage_percent` | Gauge | Router CPU usage percent |
| `asus_ram_usage_percent` | Gauge | Router RAM usage percent |
| `asus_ram_total_bytes` | Gauge | Total RAM in bytes |
| `asus_ram_free_bytes` | Gauge | Free RAM in bytes |
| `asus_wan_rx_rate_bytes_per_second` | Gauge | WAN receive rate |
| `asus_wan_tx_rate_bytes_per_second` | Gauge | WAN transmit rate |

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ROUTER_HOST` | yes | — | Router IP or hostname |
| `ROUTER_USERNAME` | yes | — | Admin username |
| `ROUTER_PASSWORD` | yes | — | Admin password |
| `ROUTER_PORT` | no | `80` | HTTP port |
| `ROUTER_USE_SSL` | no | `false` | Use HTTPS |
| `SCRAPE_INTERVAL` | no | `30` | Scrape interval in seconds |
| `PORT` | no | `9101` | Metrics server port |

### Exit Criteria

- [ ] `exporter.py` connects to a real router and exposes metrics on `/metrics`
- [ ] `asus_scrape_success` is `1` on successful scrape
- [ ] `asus_clients_by_band` shows at least one band with connected clients
- [ ] Docker image builds for both `linux/amd64` and `linux/arm64`
- [ ] GitHub Actions pushes a SHA-tagged image to GHCR on merge to main

---

## Phase 002: Grafana Dashboard

Status: planned

### Goal

Provide a reference Grafana dashboard JSON that visualises the core router metrics.
Panels should cover: client count over time per band, WAN rx/tx rates, CPU and RAM usage.

---

## Phase 003: Syslog Correlation Notes

Status: planned

### Goal

Document how to combine this exporter's time-series metrics with router syslog data
(client connect/disconnect events, roaming events) for full observability.
