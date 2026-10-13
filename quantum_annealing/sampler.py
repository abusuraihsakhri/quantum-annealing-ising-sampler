"""Dependency-free classical simulated annealing for finite Ising spin models.

This is a stochastic classical heuristic, not a quantum-annealing or TFIM simulator.
E(s) = sum_i h_i*s_i + sum_(i<j) J_ij*s_i*s_j, with s_i in {-1, +1}.
"""
import math
import random
from collections import Counter


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return value


def _model(fields, couplings):
    if not isinstance(fields, (list, tuple)) or not 1 <= len(fields) <= 24:
        raise ValueError("fields must be a list of 1 to 24 numbers")
    h = [_number(v, f"fields[{i}]") for i, v in enumerate(fields)]
    if not isinstance(couplings, dict):
        raise ValueError("couplings must be an object mapping 'i,j' to J_ij")
    edges = {}
    for key, value in couplings.items():
        if not isinstance(key, str) or len(key.split(",")) != 2:
            raise ValueError("coupling keys must have the form 'i,j'")
        parts = key.split(",")
        if any(not p.isdigit() for p in parts):
            raise ValueError("coupling indices must be nonnegative integers")
        i, j = map(int, parts)
        if i >= len(h) or j >= len(h) or i == j:
            raise ValueError("coupling indices must refer to distinct existing spins")
        edge = (min(i, j), max(i, j))
        if edge in edges:
            raise ValueError(f"duplicate coupling for spins {edge}")
        edges[edge] = _number(value, f"couplings[{key}]")
    return h, edges


def ising_energy(spins, fields, couplings):
    """Evaluate Ising energy. Coupling keys are 'i,j' (0-based)."""
    h, edges = _model(fields, couplings)
    if len(spins) != len(h) or any(type(s) is not int or s not in (-1, 1) for s in spins):
        raise ValueError("spins must contain exactly one -1 or +1 per field")
    return sum(a * s for a, s in zip(h, spins)) + sum(
        jval * spins[i] * spins[j] for (i, j), jval in edges.items()
    )


def sample_ising(fields, couplings=None, *, num_reads=32, sweeps=200,
                 temp_start=5.0, temp_end=0.05, seed=None):
    """Run independent Metropolis simulated-annealing reads.

    Records final samples (not intermediate states), ordered by ascending energy.
    Fixed seeds are reproducible within the Python implementation.
    """
    h, edges = _model(fields, {} if couplings is None else couplings)
    if type(num_reads) is not int or not 1 <= num_reads <= 200:
        raise ValueError("num_reads must be an integer from 1 to 200")
    if type(sweeps) is not int or not 1 <= sweeps <= 2000:
        raise ValueError("sweeps must be an integer from 1 to 2000")
    start = _number(temp_start, "temp_start")
    end = _number(temp_end, "temp_end")
    if not 0 < end <= start:
        raise ValueError("temperatures must satisfy 0 < temp_end <= temp_start")
    if seed is not None and (type(seed) is not int or not 0 <= seed <= 4294967295):
        raise ValueError("seed must be a 32-bit unsigned integer or None")

    rng = random.Random(seed)
    n = len(h)
    neighbors = [[] for _ in range(n)]
    for (i, j), value in edges.items():
        neighbors[i].append((j, value))
        neighbors[j].append((i, value))

    counts = Counter()
    for _ in range(num_reads):
        spins = [rng.choice((-1, 1)) for _ in range(n)]
        for step in range(sweeps):
            temperature = start * (end / start) ** (step / (sweeps - 1)) if sweeps > 1 else end
            for i in rng.sample(range(n), n):
                delta = -2 * spins[i] * (
                    h[i] + sum(weight * spins[j] for j, weight in neighbors[i])
                )
                if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                    spins[i] = -spins[i]
        counts[tuple(spins)] += 1

    samples = [
        {
            "spins": list(spins),
            "energy": sum(a * s for a, s in zip(h, spins)) +
                      sum(value * spins[i] * spins[j] for (i, j), value in edges.items()),
            "count": count,
            "fraction": count / num_reads,
        }
        for spins, count in counts.items()
    ]
    samples.sort(key=lambda s: (s["energy"], -s["count"], s["spins"]))
    return {
        "method": "classical_simulated_annealing",
        "model": "Ising",
        "energy_definition": "E(s) = sum(h_i*s_i) + sum(J_ij*s_i*s_j)",
        "num_reads": num_reads,
        "sweeps": sweeps,
        "best_energy": samples[0]["energy"],
        "best_spins": samples[0]["spins"],
        "samples": samples,
    }
