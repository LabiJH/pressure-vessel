# Pressure Vessel - Steam CDN Health Probe

This project is a best-effort tracker for the publicly available Steam CDN nodes, using Valve's own `GetServersForSteamPipe` API (https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/).

Check out the public dashboard here: <LINK TO BE ADDED>

This isn't meant to be exhaustive. Nodes can fluctuate in and out of an active state, and this probe won't catch every single one out there.

## How it works

A custom Prometheus exporter probes HTTP RTT against the discovered Steam CDN nodes and publishes the results as metrics. The Grafana dashboard then visualizes a latency ratio per region, rather than raw response time. This matters because a node that's simply farther away (Tokyo, Sydney, and so on) will naturally have a higher RTT than one nearby, and a raw threshold would flag it as degraded for no reason other than distance. The ratio compares each node against its own recent baseline instead, so only genuine slowdowns get flagged.

## Deployment and Development

If you want to deploy this yourself and develop the exporter:

1. `git clone https://github.com/LabiJH/pressure-vessel.git`
2. `cd pressure-vessel`
3. `docker compose up -d --build`
4. Navigate to `http://localhost:3000` and log in with the default Grafana credentials (`admin` / `admin`). The CDN dashboard is provisioned automatically, so it'll already be there.

### A note on exposure (PLEASE UNDERSTAND WHAT YOU ARE DOING)

By default, Grafana and Prometheus bind to all interfaces (`0.0.0.0`). Neither ships with meaningful security out of the box: Prometheus has no authentication at all, and Grafana's default login is public knowledge. If you're running this on a machine with a public IP, do at least one of the following before leaving it running:

- Set `GF_SECURITY_ADMIN_PASSWORD` via environment variable for Grafana.
- Put both services behind a firewall or reverse proxy.
- Set `BIND_ADDR` in a `.env` file (see `.env.example`) to scope the exposed ports to a private or VPN interface instead of the public internet.
