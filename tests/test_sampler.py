"""Known-energy, reproducibility, boundary and CLI integration checks."""
import json
import pytest
from quantum_annealing.sampler import ising_energy, sample_ising


def test_exact_energies():
    assert ising_energy([1, -1], [0.5, -1], {"0,1": -2}) == 3.5
    assert ising_energy([-1, -1], [0, 0], {"1,0": -2}) == -2
    assert ising_energy([1], [2], {}) == 2


def test_ground_state_single_spin():
    result = sample_ising([1], num_reads=8, sweeps=100, temp_start=2,
                          temp_end=0.001, seed=42)
    assert result["best_spins"] == [-1]
    assert result["best_energy"] == -1
    assert sum(s["count"] for s in result["samples"]) == 8
    assert sum(s["fraction"] for s in result["samples"]) == pytest.approx(1.0)


def test_seed_and_energy_consistency():
    args = ([0.1, -0.7, 0.2], {"0,1": -1, "1,2": 0.5})
    result = sample_ising(*args, num_reads=40, sweeps=70, seed=1234)
    assert result == sample_ising(*args, num_reads=40, sweeps=70, seed=1234)
    assert len(result["samples"]) <= 40
    assert all(s["energy"] == pytest.approx(
        ising_energy(s["spins"], *args)) for s in result["samples"])
    assert result["samples"] == sorted(result["samples"], key=lambda s:
                                      (s["energy"], -s["count"], s["spins"]))


@pytest.mark.parametrize("fields,couplings", [
    ([], {}), ([0] * 25, {}), ([float("nan")], {}),
    ([0, 0], {"0,0": 1}), ([0, 0], {"0,2": 1}),
    ([0, 0], {"0,1": 1, "1,0": 1}), ([0, 0], {"a,b": 2}),
    ([0, 0], {"0,1": float("inf")}),
])
def test_invalid_models(fields, couplings):
    with pytest.raises(ValueError):
        sample_ising(fields, couplings)


@pytest.mark.parametrize("kwargs", [
    {"num_reads": 0}, {"sweeps": -1}, {"num_reads": 201},
    {"temp_start": 0}, {"temp_end": -1}, {"temp_start": 1, "temp_end": 2},
    {"seed": -1}, {"seed": 2 ** 32},
])
def test_invalid_schedule(kwargs):
    with pytest.raises(ValueError):
        sample_ising([0], **kwargs)


def test_cli_sample(capsys):
    from cli import main
    assert main(["sample", "--fields", "[1]", "--reads", "4", "--seed", "3"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["num_reads"] == 4
    assert output["best_energy"] == -1
    assert main(["sample", "--fields", "[NaN]"]) == 2
