#!/usr/bin/env python3
"""Prometheus exporter for ASUS routers via the asusrouter library."""

import asyncio
import logging
import os
import time

from prometheus_client import Gauge, Info, start_http_server
from asusrouter import AsusRouter
from asusrouter.modules.data import AsusData

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

ROUTER_HOST     = os.environ["ROUTER_HOST"]
ROUTER_USERNAME = os.environ["ROUTER_USERNAME"]
ROUTER_PASSWORD = os.environ["ROUTER_PASSWORD"]
ROUTER_PORT     = int(os.environ.get("ROUTER_PORT", "80"))
ROUTER_USE_SSL  = os.environ.get("ROUTER_USE_SSL", "false").lower() == "true"
SCRAPE_INTERVAL = int(os.environ.get("SCRAPE_INTERVAL", "30"))
METRICS_PORT    = int(os.environ.get("PORT", "9101"))

# ── Metrics ───────────────────────────────────────────────────────────────────

router_info       = Info("asus_router", "Router model and firmware")
scrape_success    = Gauge("asus_scrape_success", "1 if the last scrape succeeded")
scrape_duration   = Gauge("asus_scrape_duration_seconds", "Time spent scraping the router")

clients_total     = Gauge("asus_clients_total", "Total connected clients (wired + wireless)")
clients_by_band   = Gauge("asus_clients_by_band", "Connected wireless clients per band", ["band"])

cpu_usage         = Gauge("asus_cpu_usage_percent", "CPU usage percent")

ram_usage         = Gauge("asus_ram_usage_percent", "RAM usage percent")
ram_total_bytes   = Gauge("asus_ram_total_bytes", "Total RAM in bytes")
ram_free_bytes    = Gauge("asus_ram_free_bytes", "Free RAM in bytes")

wan_rx_rate_bytes = Gauge("asus_wan_rx_rate_bytes_per_second", "WAN receive rate bytes/sec")
wan_tx_rate_bytes = Gauge("asus_wan_tx_rate_bytes_per_second", "WAN transmit rate bytes/sec")

# ── Scrape helpers ────────────────────────────────────────────────────────────

async def _scrape_clients(router: AsusRouter) -> None:
    data = await router.async_get_data(AsusData.CLIENTS)
    if not data:
        return
    band_counts: dict[str, int] = {}
    total = 0
    for client in data.values():
        total += 1
        conn = getattr(client, "connection", None)
        if conn is not None:
            # connection.type is a ConnectionType enum; .value is e.g. "2ghz", "5ghz", "wired"
            ctype = getattr(conn, "type", None)
            if ctype is not None:
                label = str(getattr(ctype, "value", ctype))
                band_counts[label] = band_counts.get(label, 0) + 1
    clients_total.set(total)
    for band, count in band_counts.items():
        clients_by_band.labels(band=band).set(count)


async def _scrape_cpu(router: AsusRouter) -> None:
    data = await router.async_get_data(AsusData.CPU)
    if not data or "total" not in data:
        return
    stats = data["total"]
    total = stats.get("total", 0)
    used  = stats.get("used", 0)
    if total:
        cpu_usage.set(used / total * 100)


async def _scrape_ram(router: AsusRouter) -> None:
    # RAM values are in KB
    data = await router.async_get_data(AsusData.RAM)
    if not data:
        return
    if (usage := data.get("usage")) is not None:
        ram_usage.set(float(usage))
    if (total := data.get("total")) is not None:
        ram_total_bytes.set(float(total) * 1024)
    if (free := data.get("free")) is not None:
        ram_free_bytes.set(float(free) * 1024)


async def _scrape_wan(router: AsusRouter) -> None:
    # WAN endpoint returns connection status only — no rate data available.
    # WAN throughput can be derived from Cisco switch SNMP uplink port stats.
    pass


async def scrape(router: AsusRouter) -> None:
    start = time.monotonic()
    try:
        await asyncio.gather(
            _scrape_clients(router),
            _scrape_cpu(router),
            _scrape_ram(router),
            _scrape_wan(router),
        )
        scrape_success.set(1)
    except Exception as exc:
        log.warning("Scrape error: %s", exc)
        scrape_success.set(0)
    finally:
        scrape_duration.set(time.monotonic() - start)


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    log.info(
        "asus-router-exporter starting — target=%s port=%d interval=%ds",
        ROUTER_HOST, METRICS_PORT, SCRAPE_INTERVAL,
    )
    start_http_server(METRICS_PORT)

    while True:
        router = AsusRouter(
            hostname=ROUTER_HOST,
            username=ROUTER_USERNAME,
            password=ROUTER_PASSWORD,
            port=ROUTER_PORT,
            use_ssl=ROUTER_USE_SSL,
        )
        try:
            await router.async_connect()
            try:
                fw = await router.async_get_data(AsusData.FIRMWARE)
                if fw and isinstance(fw, dict):
                    router_info.info({"firmware": str(fw.get("current", "unknown"))})
            except Exception:
                pass

            log.info("Connected to router at %s", ROUTER_HOST)
            while True:
                await scrape(router)
                await asyncio.sleep(SCRAPE_INTERVAL)

        except Exception as exc:
            log.error("Connection failed: %s — retrying in 60s", exc)
            scrape_success.set(0)
        finally:
            try:
                await router.async_disconnect()
            except Exception:
                pass
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
