# Quantum Annealing Ising Sampler

> **Domain:** Post-Quantum Cryptography & Zero-Knowledge Architecture
> **Standards:** NIST FIPS 203/204/205, NIST SP 800-90B & ISO/IEC Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

Quantum Annealing Ising Sampler is a Python platform that combines a multi-agent evaluation engine with a D-Wave-style quantum annealing / transverse-field Ising model (TFIM) simulation framework. It processes task payloads through specialized workers that check protocol conformance, safety boundaries, and specification invariants, then produces a cryptographically signed consensus dossier.

The project provides two parallel agent systems:

- **`agents/`** — Enterprise supervisor with PHI outbound guard, HMAC-SHA256 audit trail, and FastAPI REST API.
- **`quantum_annealing/`** — D-Wave-style embedding, annealing schedule, and spin-glass energy agents with QUBO protocol evaluation.

---

## Key Capabilities

- **Multi-Agent Evaluation Engine**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) evaluate each task payload and produce urgency-classified alerts.
- **D-Wave-Style Quantum Annealing Agents**: QUBO embedding, annealing schedule, and spin-glass energy agents audit parameters against QUBO protocol bounds.
- **Zero-PHI Outbound Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers from leaving the system.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation and state transition.
- **FastAPI REST API**: OpenAPI endpoints for audit, chat, metrics, and audit log retrieval.
- **Prometheus Telemetry**: Operational metrics exporter for tasks, alerts, PHI blocks, and audit chain depth.
- **CLI & Batch Processing**: Command-line interface with single-task, batch CSV, chat, and server subcommands.
- **Active Learning Bayesian Calibration**: Dynamic worker reliability weight tracker with Brier calibration drift monitoring.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/quantum-annealing-ising-sampler.git
cd quantum-annealing-ising-sampler

# Install dependencies
pip install -e .

# For development (testing + API server)
pip install -e ".[dev]"
```

### Optional Dependencies

The core engine has no required dependencies. For the REST API and testing:

```bash
pip install fastapi uvicorn pydantic pytest
```

---

## Configuration

Set the audit secret key for persistent cryptographic integrity across restarts:

```bash
export AUDIT_SECRET_KEY="your-random-secret-key"
```

If not set, a random ephemeral key is generated at startup (audit trail will not persist across restarts).

---

## CLI Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### 6. Run Simulation Benchmark
```bash
python simulator.py 1000
```

---

## Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | str | Unique task / case identifier | Required |
| `target_identifier` | str | Entity or target key | Required |
| `primary_metric` | float | Primary domain measurement | Required |
| `secondary_metric` | float | Secondary kinetic/confidence score | Optional (default 0.0) |
| `status_descriptor` | str | Status code or phenotype descriptor | Optional (default "NOMINAL") |
| `is_critical_flag` | bool | Emergency escalation trigger | Optional (default False) |

---

## REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/health` | Service health check |
| GET | `/metrics` | Operational metrics |
| POST | `/api/audit` | Submit task payload for evaluation |
| POST | `/api/chat` | Query the supervisory chat |
| GET | `/api/audit/logs` | Retrieve HMAC audit trail |

---

## Testing

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## Container Deployment

```bash
docker build -t quantum-annealing-ising-sampler .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key quantum-annealing-ising-sampler
```

Or with Docker Compose:

```bash
AUDIT_SECRET_KEY=your-secret-key docker compose up
```

---

## Project Structure

```
quantum-annealing-ising-sampler/
├── agents/                  # Enterprise supervisor, workers, API, audit trail
│   ├── api.py               # FastAPI REST server
│   ├── base.py              # PHI guard, HMAC audit trail, security
│   ├── models.py            # Pydantic schemas
│   ├── supervisor.py        # Multi-agent orchestrator
│   ├── workers.py           # Specialized evaluation workers
│   ├── llm_factory.py       # LLM provider factory (mock/Ollama/Claude/OpenAI)
│   ├── metrics.py           # Prometheus telemetry exporter
│   ├── learning.py          # Bayesian calibration engine
│   └── streamer.py          # WebSocket telemetry broadcaster
├── quantum_annealing/       # D-Wave-style quantum annealing agents
│   ├── agents.py            # QUBO, annealing, spin-glass agents
│   ├── engine.py            # Core algorithmic engine
│   ├── models.py            # Data models
│   ├── cli.py               # CLI for quantum annealing module
│   └── server.py            # FastAPI server factory
├── tests/                   # Pytest test suite
├── web/index.html           # Operations console UI
├── cli.py                   # Main CLI entry point
├── simulator.py             # High-throughput simulation benchmark
├── enrichment.py            # Enrichment feature engines
├── Dockerfile               # Container build
└── docker-compose.yml       # Container orchestration
```

---

## Security

- **Zero-PHI Outbound Interceptor**: Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation.
- **Path Traversal Protection**: All CLI file I/O uses safe path resolution.
- **Input Validation**: Simulator and CLI validate all user inputs before processing.
- **No Hardcoded Secrets**: Audit key sourced from environment variable; ephemeral key generated if unset.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
