# Quantum Annealing Ising Sampler

A small, dependency-free **classical simulated-annealing solver** for finite Ising energy models, with a standalone browser interface and Python API/CLI. The repository also retains its original threshold-based audit systems as separate legacy functionality.

## What it actually computes

For spins sᵢ ∈ {−1,+1}, the energy function is:

`E(s) = Σ hᵢsᵢ + Σ Jᵢⱼsᵢsⱼ` (one J entry per unordered pair).

The sampler performs independent Metropolis reads with a geometric temperature schedule and reports the final configurations, their energies, counts, and lowest **observed** energy. It is **not** a quantum-annealing, transverse-field Ising, D-Wave hardware, Pegasus embedding, or ground-state certification implementation. No QPU or external API is used.

## Browser app

Serve `web/` with a static HTTP server, for example `python -m http.server 8001 -d web`, and open `http://127.0.0.1:8001/`. Opening the HTML directly via `file://` can block JavaScript module imports. Enter the array of local fields, an object of zero-based pair couplings such as `{"0,1":-1.2}`, and a sampling schedule. Select **Run annealing**. Results can be exported as CSV or JSON. A fixed seed is deterministic within the browser implementation (not necessarily identical to Python's RNG).

The browser runs plain JavaScript locally; Pyodide is not required. It works on static hosts such as GitHub Pages. There is no backend or data upload in the sampler page. The separate `web/audit.html` page requires the locally running FastAPI service for its audit requests; it never fabricates an offline response.

## Install and use Python

Requires Python 3.9 or newer.

```bash
python -m pip install -e ".[dev]"
quantum-annealing-ising-sampler sample --fields '[0.25,-0.4,0.1]' --couplings '{"0,1":-1.2,"1,2":0.8}' --reads 60 --sweeps 250 --seed 42
```

The sampler can also be imported:

```python
from quantum_annealing.sampler import sample_ising, ising_energy
result = sample_ising([0, 0], {"0,1": -1}, num_reads=20, seed=7)
print(result["best_energy"], result["best_spins"])
```

Inputs are limited to 1–24 spins, 1–200 independent reads, and 1–2000 sweeps/read. Temperatures must satisfy `0 < temp_end <= temp_start`, and coupling keys must identify different spins. Scores are based on the energy convention above, and there is no optimality guarantee.

## HTTP service

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the browser app or send a JSON POST request to `/api/sample` using `fields`, `couplings`, `num_reads`, `sweeps`, `temp_start`, `temp_end`, and `seed`. The endpoint uses the same Python sampler.

Existing legacy commands `audit`, `batch`, `chat`, `verify-audit`, and `serve` remain available on the primary CLI. The older `quantum_annealing.cli` module remains available for compatibility. Legacy `agents/api.py` exposes `/api/audit`, `/api/chat`, `/api/audit/logs`, `/health`, and `/metrics`. Its audit conditions are fixed heuristic thresholds, **not** standard-compliant QUBO/quantum verification. The 'mock' chat provider is deterministic and is not an actual LLM service.

## Security and privacy

The browser sampler performs all calculations and exports locally without transmitting model inputs. The FastAPI backend receives data sent to its endpoints and keeps audit entries in process memory. A regex-based identifier filter is limited and should **not** be treated as a comprehensive de-identification or HIPAA compliance guarantee. HMAC-SHA256 audit entries are linked and reverified in memory; they are not persisted between restarts. Set `AUDIT_SECRET_KEY` to a cryptographically strong private value if using the backend. Do not place secret keys in browser code.

For Docker deployment:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Do not expose the unauthenticated audit API or logs to untrusted networks.

## Tests

```bash
python -m pytest -q
ruff check .
python -m build
node --test web/sampler.test.mjs
```

CI checks Python 3.10–3.12 and Node 22. The project uses Python's standard library for sampling, FastAPI/Pydantic/Uvicorn for the optional server and legacy audit API, and plain JavaScript for the browser.

## Project notes

- `quantum_annealing/sampler.py` — classical Ising sampler.
- `web/index.html` / `web/sampler.mjs` — standalone browser sampler.
- `agents/` — retained legacy audit logic and API.
- `quantum_annealing/agents.py` — retained legacy parameter-auditing agents.
- `enrichment.py` — generic threshold evaluators, not minor-embedding or quantum simulation.
- `tests/` — numerical, security, compatibility, and API checks.

Browser compatibility: modern browsers supporting JavaScript modules. License: [MIT](LICENSE).
