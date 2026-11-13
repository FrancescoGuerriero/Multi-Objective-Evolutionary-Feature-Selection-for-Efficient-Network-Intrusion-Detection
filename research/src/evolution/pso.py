from __future__ import annotations
from .bpso import BPSOFeatureSelector

class PSOFeatureSelector(BPSOFeatureSelector):
    """Feature-selection PSO variant.

    In Phase 4 we will freeze the exact reference-paper transfer function and
    use this class for the controlled PSO-vs-BPSO comparison. For now it shares
    the validated binary swarm engine so the public API is stable.
    """
    pass
