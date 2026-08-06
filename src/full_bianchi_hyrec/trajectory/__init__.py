"""Primitive original-HyRec trajectory interfaces.

PR-05 keeps the original-HyRec native radiation variables and the COM--KHW
collision variables representation-local.  This package exposes typed source
rates and one-step residual contracts without constructing a fitted state
remap between them.
"""

from .primitive_rates import (
    ALPHA_TABLE_SHA256,
    R2P2S_TABLE_SHA256,
    TWO_PHOTON_TABLE_SHA256,
    OriginalHyRecPrimitiveRateTable,
    PrimitiveRateSnapshot,
    detailed_balance_residuals,
)
from .primitive_trajectory import (
    AtomicRadiationState,
    PrimitiveTrajectoryProblem,
    RadiationFeedback,
    TrajectoryStepLedger,
)
from .time_dependent_native import (
    CausalRadiationHistoryState,
    NativeRadiationTimeMeasureAudit,
    NativeRadiationTimeMeasureNotIdentifiable,
    OriginalHyRecStateBlock,
    OriginalHyRecStateLayout,
    OriginalHyRecStateRole,
    ReplacementAudit,
    ReplacementRegistry,
    ReplacementTerm,
    SourceIdentifiableOriginalHyRecDAE,
    audit_canonical_native_radiation_time_measure,
    default_pr05b1_replacement_registry,
    source_identifiable_original_hyrec_layout,
)

__all__ = [
    "ALPHA_TABLE_SHA256",
    "R2P2S_TABLE_SHA256",
    "TWO_PHOTON_TABLE_SHA256",
    "OriginalHyRecPrimitiveRateTable",
    "PrimitiveRateSnapshot",
    "detailed_balance_residuals",
    "AtomicRadiationState",
    "PrimitiveTrajectoryProblem",
    "RadiationFeedback",
    "TrajectoryStepLedger",
    "CausalRadiationHistoryState",
    "NativeRadiationTimeMeasureAudit",
    "NativeRadiationTimeMeasureNotIdentifiable",
    "OriginalHyRecStateBlock",
    "OriginalHyRecStateLayout",
    "OriginalHyRecStateRole",
    "ReplacementAudit",
    "ReplacementRegistry",
    "ReplacementTerm",
    "SourceIdentifiableOriginalHyRecDAE",
    "audit_canonical_native_radiation_time_measure",
    "default_pr05b1_replacement_registry",
    "source_identifiable_original_hyrec_layout",
]
