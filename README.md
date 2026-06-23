# asus-router-exporter

Prometheus exporter for ASUS routers running stock AsusWRT or Merlin firmware. Exposes
WiFi client metrics per band, WAN traffic rates, CPU and memory usage. Supports AiMesh
mesh systems. Configuration via environment variables.

## Metrics

| Metric | Description |
|---|---|
| `asus_router_info` | Router model and firmware version (label-only) |
| `asus_scrape_success` | `1` if the last scrape succeeded, `0` on failure |
| `asus_scrape_duration_seconds` | Time spent scraping the router |
| `asus_clients_total` | Total connected clients (wired + wireless) |
| `asus_clients_by_band{band}` | Wireless clients per band (`2.4 ghz` / `5 ghz` / `6 ghz`) |
| `asus_cpu_usage_percent` | CPU usage percent |
| `asus_ram_usage_percent` | RAM usage percent |
| `asus_ram_total_bytes` | Total RAM in bytes |
| `asus_ram_free_bytes` | Free RAM in bytes |
| `asus_wan_rx_rate_bytes_per_second` | WAN receive rate |
| `asus_wan_tx_rate_bytes_per_second` | WAN transmit rate |

## Quick Start

```bash
docker run -d \
  -p 9101:9101 \
  -e ROUTER_HOST=192.168.1.1 \
  -e ROUTER_USERNAME=admin \
  -e ROUTER_PASSWORD=yourpassword \
  ghcr.io/raffcorreia/asus-router-exporter:latest
```

Metrics available at `http://localhost:9101/metrics`.

## Configuration

All configuration is via environment variables.

| Variable | Required | Default | Description |
|---|---|---|---|
| `ROUTER_HOST` | yes | — | Router IP or hostname |
| `ROUTER_USERNAME` | yes | — | Admin username |
| `ROUTER_PASSWORD` | yes | — | Admin password |
| `ROUTER_PORT` | no | `80` | HTTP port (use `443` with SSL) |
| `ROUTER_USE_SSL` | no | `false` | Set `true` to use HTTPS |
| `SCRAPE_INTERVAL` | no | `30` | Seconds between scrapes |
| `PORT` | no | `9101` | Metrics server port |

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: asus_router
    static_configs:
      - targets: ["<exporter-host>:9101"]
    scrape_interval: 30s
```

## AiMesh

Point the exporter at the main router only. In an AiMesh system the main router
aggregates connected client state for all nodes, so mesh-wide client counts are
available without polling each node separately.

## Building

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t asus-router-exporter:local \
  .
```

## Documentation

- [Requirements](docs/requirements.md) — functional and non-functional requirements
- [Solution Design](docs/solution-design.md) — architecture and design decisions
- [Implementation Plan](docs/implementation/plan.md) — phased implementation roadmap

## License

MIT
