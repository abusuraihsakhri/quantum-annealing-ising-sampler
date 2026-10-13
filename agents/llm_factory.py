"""Explicit deterministic mock inference provider for the legacy audit interface."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Quantum Annealing Ising Sampler"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} deterministic mock]: No model inference was performed. "
            f"Query received: '{prompt[:60]}...'."
        )


class LLMFactory:
    """Return the implemented mock; never silently impersonate a remote provider."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Quantum Annealing Ising Sampler"):
        prov = str(provider).lower()
        if prov in ("mock", "deterministic", "test"):
            return MockLLM(system_name)
        raise ValueError(
            f"LLM provider {provider!r} is not implemented. Select 'mock'."
        )
