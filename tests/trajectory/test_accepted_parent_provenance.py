from __future__ import annotations

import hashlib

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.accepted_parent import (
    AcceptedRadiationParent,
    ParentEvidenceClass,
    ProductionParentRequirements,
)
from full_bianchi_hyrec.trajectory.physical_continuation import (
    build_production_continuation_adapter,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _requirements(index: int = 17) -> ProductionParentRequirements:
    return ProductionParentRequirements(
        accepted_history_index=index,
        accepted_history_sha256=_digest("history"),
        atomic_state_sha256=_digest("atomic"),
        background_sequence_sha256=_digest("background"),
        network_sha256=_digest("network"),
        interface_sha256=_digest("interface"),
        branch_id="Bianchi_II:expanding:orthogonal",
    )


def _parent(evidence: ParentEvidenceClass) -> AcceptedRadiationParent:
    req = _requirements()
    return AcceptedRadiationParent(
        occupation=np.full((3, 2), 1.0e-8),
        evidence_class=evidence,
        accepted_history_index=req.accepted_history_index,
        accepted_history_sha256=req.accepted_history_sha256,
        atomic_state_sha256=req.atomic_state_sha256,
        background_sequence_sha256=req.background_sequence_sha256,
        network_sha256=req.network_sha256,
        interface_sha256=req.interface_sha256,
        branch_id=req.branch_id,
        metadata={"canonical_eta": 0.6072662349590596},
    )


@pytest.mark.parametrize(
    "evidence",
    [ParentEvidenceClass.OPERATOR_VERIFICATION, ParentEvidenceClass.MANUFACTURED],
)
def test_nonphysical_parent_fails_closed_at_production_macro_entry(evidence) -> None:
    parent = _parent(evidence)
    with pytest.raises(PermissionError, match="SOURCE_DERIVED_ACCEPTED"):
        build_production_continuation_adapter(
            problem=object(),
            parent=parent,
            requirements=_requirements(),
        )


def test_source_derived_parent_hash_and_byte_round_trip_are_exact() -> None:
    parent = _parent(ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED)
    payload = parent.to_bytes()
    recovered = AcceptedRadiationParent.from_bytes(payload)

    assert recovered.to_bytes() == payload
    assert recovered.sha256 == parent.sha256
    assert np.array_equal(recovered.occupation, parent.occupation)
    assert recovered.metadata == parent.metadata
    recovered.validate_for_production(_requirements())


def test_source_derived_parent_rejects_stale_history_or_hash() -> None:
    parent = _parent(ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED)
    stale = _requirements(index=18)
    with pytest.raises(ValueError, match="accepted_history_index"):
        parent.validate_for_production(stale)

    req = _requirements()
    mismatched = ProductionParentRequirements(
        accepted_history_index=req.accepted_history_index,
        accepted_history_sha256=req.accepted_history_sha256,
        atomic_state_sha256=req.atomic_state_sha256,
        background_sequence_sha256=_digest("other-background"),
        network_sha256=req.network_sha256,
        interface_sha256=req.interface_sha256,
        branch_id=req.branch_id,
    )
    with pytest.raises(ValueError, match="background_sequence_sha256"):
        parent.validate_for_production(mismatched)
