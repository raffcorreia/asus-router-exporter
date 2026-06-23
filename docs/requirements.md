# Requirements

## Functional

- Export Prometheus metrics from ASUS routers running stock AsusWRT or Merlin firmware
- Expose connected client count broken down by WiFi band (2.4 GHz, 5 GHz, 6 GHz)
- Expose total connected client count (wired + wireless)
- Expose WAN receive and transmit rates
- Expose CPU usage percent
- Expose RAM total, free, and usage percent
- Expose router model and firmware version as an info metric
- Expose a scrape health metric (`asus_scrape_success`) so alerting can detect connectivity loss
- Support AiMesh systems — data is collected from the main router which aggregates mesh-wide client state

## Non-Functional

- All configuration via environment variables — no config files, no hard-coded values
- Credentials must never appear in logs or metric output
- Reconnect automatically if the router becomes unreachable (reboot, network blip)
- Scrape interval configurable — default 30 seconds
- Metrics port configurable — default 9101
- Multi-architecture Docker image: `linux/amd64` and `linux/arm64`
- Python 3.12+

## Constraints

- No SNMP — stock AsusWRT firmware `3.0.0.4.388+` removed the SNMP tab
- No firmware modification — works with stock firmware as shipped
- No router-side configuration beyond enabling the admin HTTP/HTTPS interface
- Uses the `asusrouter` library for router communication — no raw HTTP session management
