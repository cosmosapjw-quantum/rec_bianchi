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

from .causal_history import (
    AcceptedRadiationHistory,
    CharacteristicHistoryGrid,
    CharacteristicInterpolationStencil,
    CharacteristicQuery,
    CharacteristicStencilSwitch,
    FutureHistoryEndpointError,
    HistoryAppendCandidate,
    HistoryStepLedger,
    OriginalHyRecIncoming,
    build_original_hyrec_queries,
    construct_original_hyrec_incoming,
    original_hyrec_incoming_jvp,
)
from .causal_history_step import (
    CausalHistoryAcceptedStepProblem,
    CausalHistoryAcceptedStepResult,
    CausalHistoryStepJVP,
    CharacteristicConservationLedger,
)


from .history_ownership import (
    AcceptedStepTransaction,
    AcceptedStepTransactionStatus,
    ScalarHistoryFeedbackOwner,
    ScalarHistoryOwnershipRegistry,
    ScalarHistoryOwnerSwapProblem,
    ScalarHistoryParityAudit,
)


from .adaptive_macro import (
    AcceptedMacrostepLedger,
    AdaptiveBackwardEulerTrial,
    AdaptiveControllerTolerances,
    AdaptiveEvent,
    AdaptiveEventKind,
    AdaptiveMicrostepAttempt,
    AdaptiveTrajectoryContext,
    CanonicalMacroInterval,
    TrajectoryRestartState,
    advance_canonical_macro_interval,
    source_conditioned_backward_euler_trial,
)


from .full_coupled_adaptive import (
    CollisionStiffnessAudit,
    CoupledCollisionTransportProblem,
    CoupledCollisionTransportStepResult,
    CoupledResidualMetrics,
    FullCouplingIdentifiabilityAudit,
    ThermodynamicGridConsistencyAudit,
    audit_collision_stiffness,
    audit_full_coupling_identifiability,
    audit_thermodynamic_grid_consistency,
)






from .hyrec_source_adapter import (
    IsotropicEinsteinLineSource,
    OriginalHyRecVirtualSpikeSource,
)

from .characteristic_angular import (
    BianchiCharacteristicFaceSolver,
    BianchiCharacteristicFaceResult,
    CharacteristicAngularSolver,
    CharacteristicFaceResult,
    IsotropicTransferCoefficients,
    constant_coefficient_transfer,
    constant_coefficient_transfer_jvp,
)

from .hyrec_spike_transfer import (
    OriginalHyRecSpikeTransfer,
    SpikeTransferResult,
)

from .direct_thermodynamic import (
    DirectThermodynamicNetworkFamily,
    DirectThermodynamicNode,
    WithheldThermodynamicAudit,
)

from .explicit_full_coupling import (
    ExplicitThermodynamicNetworkFamily,
    FrequencyFaceReconstruction,
    NativeAngularClosure,
    ThermodynamicNetworkMember,
    isotropic_native_lift,
    maximum_entropy_native_lift,
    reconstruct_frequency_faces,
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
    "IsotropicEinsteinLineSource",
    "OriginalHyRecVirtualSpikeSource",
    "BianchiCharacteristicFaceSolver",
    "BianchiCharacteristicFaceResult",
    "CharacteristicAngularSolver",
    "CharacteristicFaceResult",
    "IsotropicTransferCoefficients",
    "constant_coefficient_transfer",
    "constant_coefficient_transfer_jvp",
    "OriginalHyRecSpikeTransfer",
    "SpikeTransferResult",
    "DirectThermodynamicNetworkFamily",
    "DirectThermodynamicNode",
    "WithheldThermodynamicAudit",
    "ExplicitThermodynamicNetworkFamily",
    "FrequencyFaceReconstruction",
    "NativeAngularClosure",
    "ThermodynamicNetworkMember",
    "isotropic_native_lift",
    "maximum_entropy_native_lift",
    "reconstruct_frequency_faces",
    "CollisionStiffnessAudit",
    "CoupledCollisionTransportProblem",
    "CoupledCollisionTransportStepResult",
    "CoupledResidualMetrics",
    "FullCouplingIdentifiabilityAudit",
    "ThermodynamicGridConsistencyAudit",
    "audit_collision_stiffness",
    "audit_full_coupling_identifiability",
    "audit_thermodynamic_grid_consistency",
    "AcceptedMacrostepLedger",
    "AdaptiveBackwardEulerTrial",
    "AdaptiveControllerTolerances",
    "AdaptiveEvent",
    "AdaptiveEventKind",
    "AdaptiveMicrostepAttempt",
    "AdaptiveTrajectoryContext",
    "CanonicalMacroInterval",
    "TrajectoryRestartState",
    "advance_canonical_macro_interval",
    "source_conditioned_backward_euler_trial",
    "ScalarHistoryParityAudit",
    "ScalarHistoryOwnerSwapProblem",
    "ScalarHistoryOwnershipRegistry",
    "ScalarHistoryFeedbackOwner",
    "AcceptedStepTransaction",
    "AcceptedStepTransactionStatus",

    "AcceptedRadiationHistory",
    "CharacteristicHistoryGrid",
    "CharacteristicInterpolationStencil",
    "CharacteristicQuery",
    "CharacteristicStencilSwitch",
    "FutureHistoryEndpointError",
    "HistoryAppendCandidate",
    "HistoryStepLedger",
    "OriginalHyRecIncoming",
    "build_original_hyrec_queries",
    "construct_original_hyrec_incoming",
    "original_hyrec_incoming_jvp",
    "CausalHistoryAcceptedStepProblem",
    "CausalHistoryAcceptedStepResult",
    "CausalHistoryStepJVP",
    "CharacteristicConservationLedger",
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
