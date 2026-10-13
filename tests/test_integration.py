"""HTTP, audit-integrity, and CSV behavior regression tests."""
import csv
import json

from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail
from cli import main


def test_hmac_recomputed_and_snapshots_isolated():
    trail = AuditTrail(secret_key="test-fixture-key")
    first = trail.log("actor", "worker", "EVENT", {"task_id": "T1"})
    trail.log("actor", "worker", "EVENT", {"task_id": "T2"})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "external mutation"
    assert trail.verify_integrity()
    first["actor"] = "forged actor"
    assert not trail.verify_integrity()


def test_api_sampler_and_static_frontend():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    home = client.get("/")
    assert home.status_code == 200
    assert "Ising energy sampler" in home.text
    response = client.post("/api/sample", json={
        "fields": [1], "num_reads": 8, "sweeps": 80,
        "temp_start": 2, "temp_end": 0.001, "seed": 2
    })
    assert response.status_code == 200
    result = response.json()
    assert result["best_energy"] == -1
    assert sum(s["count"] for s in result["samples"]) == 8
    assert client.post("/api/sample", json={
        "fields": [1, 2], "couplings": {"0,0": 1}
    }).status_code == 422


def test_batch_false_boolean(tmp_path):
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    input_file.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "T1,TARGET-01,1,1,False,NOMINAL\n"
        "T2,TARGET-02,1,1,True,NOMINAL\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(input_file), "-o", str(output_file)]) == 0
    with output_file.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"


def test_cli_reports_invalid_schedule(capsys):
    assert main(["sample", "--fields", "[0]", "--reads", "0"]) == 2
    assert "Invalid Ising" in capsys.readouterr().err
