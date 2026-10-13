"""
FastAPI REST API Server for Quantum Annealing Ising Sampler.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from quantum_annealing.sampler import sample_ising
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Quantum Annealing Ising Sampler API",
    description="Enterprise Distributed Component Platform (Post-Quantum Cryptography & Hardware Security)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "quantum-annealing-ising-sampler", "domain": "Post-Quantum Cryptography & Hardware Security", "standard": "NIST FIPS 203/204/205 / ISO/IEC 17825 Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


class SampleRequest(BaseModel):
    fields: List[float]
    couplings: Dict[str, float] = Field(default_factory=dict)
    num_reads: int = 32
    sweeps: int = 200
    temp_start: float = 5.0
    temp_end: float = 0.05
    seed: Optional[int] = 0


@app.post("/api/sample")
def api_sample(req: SampleRequest):
    """Classical simulated annealing; does not require quantum hardware."""
    try:
        return sample_ising(
            req.fields, req.couplings, num_reads=req.num_reads,
            sweeps=req.sweeps, temp_start=req.temp_start,
            temp_end=req.temp_end, seed=req.seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# Register routes before mounting the static site at the root.
app.mount("/", StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "web"),
                           html=True), name="static")
