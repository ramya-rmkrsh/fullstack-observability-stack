# 🐳 Fullstack Observability Stack

A containerized full-stack CRUD application with end-to-end observability — structured log streaming, APM tracing, RUM (Real User Monitoring), operational dashboards, monitors, and SLOs via Datadog.

> Built by a Technical Support Engineer with 8+ years in production systems to demonstrate real-world Docker and observability skills across the full stack: browser → backend → database.

---

## 🧱 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      Docker Network                       │
│                                                           │
│  ┌──────────────────┐     ┌──────────────────────────┐   │
│  │    Frontend       │────▶│    Backend (Python)      │   │
│  │  HTML/JS/CSS      │     │  Flask + Gunicorn        │   │
│  │  Datadog RUM SDK  │     │  ddtrace instrumented    │   │
│  └──────────────────┘     └────────────┬─────────────┘   │
│                                        │                  │
│                             ┌──────────▼──────────┐      │
│                             │    PostgreSQL DB      │      │
│                             │    postgres:15        │      │
│                             └──────────────────────┘      │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Datadog Agent (sidecar)                 │  │
│  │   Logs · APM Traces · RUM · Infra Metrics           │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Services

| Service | Technology | Purpose |
|---|---|---|
| `frontend` | HTML / JavaScript / CSS + Nginx | CRUD UI, Datadog RUM instrumented |
| `backend` | Python / Flask / Gunicorn | REST API, ddtrace APM instrumented |
| `db` | PostgreSQL 15 | Persistent data storage |
| `datadog-agent` | Datadog Agent (sidecar) | Log collection, APM, RUM, infra metrics |

---

## 🎯 What This Project Demonstrates

- **Docker Compose** orchestration of a 4-service stack with health checks and service dependencies
- **Inter-container networking** — frontend → backend → DB with proper DNS resolution
- **APM instrumentation** — `ddtrace-run gunicorn` capturing distributed traces with flame graphs
- **Structured JSON logging** — custom `JSONFormatter` across backend and Gunicorn, log levels correctly parsed by Datadog
- **RUM (Real User Monitoring)** — Datadog Browser SDK tracking page loads, JS errors, user sessions and Core Web Vitals
- **Log + Trace correlation** — trace IDs injected into log lines, connecting logs directly to APM spans
- **RED method dashboard** — Requests, Errors, Duration per service for incident-first observability
- **Monitors** — alerting on error rate, DB connectivity, and container health
- **SLO tracking** — API availability SLO based on monitor uptime
- **Secrets management** — API keys externalized via `.env`, never hardcoded

---

## 📊 Datadog Observability Setup

### Logs
- All services emit structured JSON logs via Docker label autodiscovery
- Logs tagged by `service`, `env`, `container_name`
- Custom `JSONFormatter` on backend and Gunicorn — correct INFO/WARN/ERROR level parsing
- Nginx startup noise filtered via `exclude_at_match` log processing rules
- Frontend JS events logged to stdout and captured via nginx log collection

### APM
- Backend instrumented with `ddtrace-run` wrapping Gunicorn
- `patch_all()` auto-instruments Flask, psycopg2, and all DB queries
- Trace IDs injected into JSON log lines — click a log to jump to its APM flame graph
- Service map shows `backend → appdb (PostgreSQL)` dependency auto-detected

### RUM (Real User Monitoring)
- Datadog Browser SDK (JS) integrated into frontend
- Captures page load times, JS errors, user sessions, Core Web Vitals (LCP, FID, CLS)
- Connects frontend user actions to backend APM traces end-to-end

### Dashboard — "Fullstack Service Health"
- Service Health Table: Requests / Errors / P95 Latency per service (RED method)
- Backend vs DB Latency Breakdown — isolates application vs database response time
- Backend Request Latency Percentiles — P50, P75, P90, P95
- API endpoint hit rate timeseries
- CPU and memory consumption per container
- Live backend log stream
- Service Map widget — backend → appdb topology
- RUM widgets: JS error count, active sessions, Core Web Vitals

### Monitors
- **[Backend] High Error Rate** — alerts when error count exceeds threshold in 5 minutes
- **[DB] No Active Connections** — alerts if PostgreSQL connection count drops to 0
- **[Infra] Container Down** — alerts when any container stops unexpectedly

### SLO
- **API Availability SLO** — tracks backend service availability based on monitor uptime
- Target: 99% over 7-day rolling window

---

## 🚀 Getting Started

### Prerequisites
- Docker + Docker Compose installed
- Datadog account (free trial works) with an API key from `app.datadoghq.eu`

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/ramya-rmkrsh/fullstack-observability-stack.git
cd fullstack-observability-stack

# 2. Create your environment file
cp .env.example .env
# Add your DD_API_KEY to .env

# 3. Spin up all services
docker-compose up --build

# 4. Open the app
# Frontend: http://localhost:8080
# Backend API: http://localhost:5000
```

### Environment Variables

```bash
DD_API_KEY=your_datadog_api_key_here
DD_SITE=datadoghq.eu
```

### Verify Datadog Agent is healthy

```bash
# Full agent status
docker exec datadog-agent-007 agent status

# Confirm APM traces are flowing
docker exec datadog-agent-007 agent status | grep -A10 "Receiver (previous"
```

---

## 📁 Project Structure

```
fullstack-observability-stack/
├── backend/
│   ├── app.py                  # Flask API — ddtrace, JSONFormatter, trace ID injection
│   ├── gunicorn_config.py      # Gunicorn JSON log formatter
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html              # Datadog RUM Browser SDK integrated
│   ├── app.js                  # CRUD operations with frontend structured logging
│   └── styles.css
├── screenshots/                # Datadog dashboard, APM, RUM, monitor screenshots
├── datadog/
│   └── dashboard.json          # Exportable Datadog dashboard — import into your own account
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔍 Key Technical Decisions

**Why `ddtrace-run gunicorn` instead of running Flask directly?**
Gunicorn is the production WSGI server — running Flask's built-in server wouldn't reflect real-world usage. Wrapping with `ddtrace-run` instruments every request at the process level before it hits Flask.

**Why a custom `JSONFormatter` instead of plain text logs?**
Datadog parses structured JSON to extract log levels, trace IDs, and service tags automatically. Plain text logs arrive as raw strings with no level metadata — causing everything to show as ERROR by default.

**Why inject trace IDs into logs?**
During an incident, clicking a log line jumps directly to the APM flame graph for that exact request — no manual correlation. This is standard practice in production observability.

**Why a sidecar Datadog agent instead of host-level install?**
Keeps the entire observability stack portable and reproducible. Any engineer can clone this and have full monitoring running with just a DD API key — no host configuration required.

**Why separate Backend Latency vs DB Latency in the dashboard?**
During incidents, knowing whether slowness is in the application layer or database layer determines which team to page and what to investigate first. Separating these signals reduces mean time to diagnosis.

---

## 📸 Observability Screenshots

### Full Stack Dashboard
![Dashboard](screenshots/dashboard.png)

### Service Map (backend → appdb)
![Service Map](screenshots/service_map.png)

### APM Trace Flame Graph
![APM Traces](screenshots/apm_traces.png)

### RUM — Frontend Monitoring
![RUM](screenshots/rum.png)

### Monitors & SLO
![Monitors](screenshots/monitors.png)

---

## 📌 What I'd Add Next

- [ ] PostgreSQL slow query log collection and Datadog postgres integration metrics
- [ ] GitHub Actions CI/CD — build and validate containers on every push
- [ ] Datadog Synthetic tests — automated UI and API uptime checks on a schedule
- [ ] SLO based on error budget burn rate (count-based) once traffic volume is sufficient
- [ ] Integrate with the [Incident Triage Engine](https://github.com/ramya-rmkrsh/incident-triage) — auto-classify Datadog alert payloads by severity

---

## 🛠 Tech Stack

`Docker` · `Docker Compose` · `Python` · `Flask` · `Gunicorn` · `PostgreSQL` · `Nginx` · `HTML/JS/CSS` · `Datadog APM` · `Datadog Logs` · `Datadog RUM` · `Datadog Monitors` · `Datadog SLO` · `ddtrace`

---

## 👤 Author

**ramya-rmkrsh** — Technical Support Engineer with 8+ years in production systems.

[GitHub Profile](https://github.com/ramya-rmkrsh)
