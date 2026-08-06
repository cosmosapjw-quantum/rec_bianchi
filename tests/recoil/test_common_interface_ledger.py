from __future__ import annotations

from dataclasses import replace
import json

import pytest

from full_bianchi_hyrec.recoil.common_interface_ledger import (
    CommonInterfaceLedger,
    EvidenceClass,
    GateCriterion,
    LedgerMetric,
    PacketLedgerRecord,
    ProvenanceLock,
    SnapshotLedger,
    StateClassification,
)


TARGETS = (1300.0, 1100.0, 900.0)


def _provenance(name: str) -> ProvenanceLock:
    return ProvenanceLock(
        name=name,
        relative_path=f"data/{name}.npz",
        sha256=(name.encode().hex() + "0" * 64)[:64],
        evidence_class=EvidenceClass.SOURCE_DERIVED,
    )


def _packet(target: float, side: str) -> PacketLedgerRecord:
    red = side == "red"
    return PacketLedgerRecord(
        packet_id=f"z{int(target)}-{side}",
        target_z=target,
        snapshot_z=target - 0.002 if target != 900.0 else 900.016,
        side=side,
        direction="com_to_native" if red else "native_to_com",
        interface_x=-21.25 if red else 21.25,
        interface_frequency_Hz=2.465e15 if red else 2.467e15,
        n_H_m3=2.5e8,
        history_index_left=10,
        history_index_right=11,
        solved_history_index=11,
        packet_sha256=(f"{int(target)}-{side}".encode().hex() + "0" * 64)[:64],
    )


def _metric(name: str, value: float = 0.0) -> LedgerMetric:
    return LedgerMetric(
        name=name,
        value=value,
        unit="1",
        evidence_class=EvidenceClass.SOLVER_DERIVED,
        criterion=GateCriterion.ABS_LE,
        limit=1.0e-11,
        scale=1.0,
    )


def _snapshot(target: float, *, signed_error: float = 0.0) -> SnapshotLedger:
    metrics = (
        _metric("photon_number_residual", signed_error),
        LedgerMetric(
            name="transported_face_energy_residual",
            value=0.0,
            unit="J/H",
            evidence_class=EvidenceClass.ALGEBRAIC,
            criterion=GateCriterion.EXACT_ZERO,
            limit=0.0,
            scale=1.0,
        ),
        LedgerMetric(
            name="interface_atom_source",
            value=0.0,
            unit="J/H",
            evidence_class=EvidenceClass.ALGEBRAIC,
            criterion=GateCriterion.EXACT_ZERO,
            limit=0.0,
            scale=1.0,
        ),
        LedgerMetric(
            name="minimum_occupation",
            value=1.0e-18,
            unit="1",
            evidence_class=EvidenceClass.SOLVER_DERIVED,
            criterion=GateCriterion.GT,
            limit=0.0,
            scale=1.0e-18,
        ),
        LedgerMetric(
            name="collision_entropy_production",
            value=-1.0,
            unit="arb/s",
            evidence_class=EvidenceClass.SOLVER_DERIVED,
            criterion=GateCriterion.LE,
            limit=0.0,
            scale=1.0,
        ),
        LedgerMetric(
            name="restart_exact",
            value=1.0,
            unit="bool",
            evidence_class=EvidenceClass.SOLVER_DERIVED,
            criterion=GateCriterion.EXACT_ONE,
            limit=1.0,
            scale=1.0,
        ),
    )
    return SnapshotLedger(
        target_z=target,
        snapshot_z=target - 0.002 if target != 900.0 else 900.016,
        state_classification=StateClassification.OPERATOR_VERIFICATION,
        q_activity=1.0,
        packets=(_packet(target, "red"), _packet(target, "blue")),
        metrics=metrics,
        provenance=(_provenance(f"snapshot-{int(target)}"),),
    )


def _ledger(errors: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> CommonInterfaceLedger:
    return CommonInterfaceLedger(
        schema="PR04C3_COMMON_INTERFACE_LEDGER_V1",
        snapshots=tuple(
            _snapshot(target, signed_error=error)
            for target, error in zip(TARGETS, errors, strict=True)
        ),
        global_provenance=(_provenance("network"), _provenance("background")),
        direct_state_remap_used=False,
        fitted_normalization_used=False,
    )


def test_common_ledger_requires_exact_ordered_three_lane_schema() -> None:
    ledger = _ledger()
    ledger.validate()
    assert tuple(snapshot.target_z for snapshot in ledger.snapshots) == TARGETS
    assert len(ledger.packet_ids) == 6
    assert ledger.componentwise_passed
    assert ledger.epsilon_common == 0.0

    with pytest.raises(ValueError, match="ordered target lanes"):
        replace(ledger, snapshots=tuple(reversed(ledger.snapshots))).validate()


def test_cross_snapshot_cancellation_cannot_rescue_component_failure() -> None:
    error = 2.0e-10
    ledger = _ledger((error, -error, 0.0))
    assert sum(
        snapshot.metric("photon_number_residual").value
        for snapshot in ledger.snapshots
    ) == 0.0
    assert not ledger.componentwise_passed
    assert ledger.epsilon_common == pytest.approx(20.0)
    failures = ledger.failed_components()
    assert {(row["target_z"], row["metric"]) for row in failures} == {
        (1300.0, "photon_number_residual"),
        (1100.0, "photon_number_residual"),
    }


def test_duplicate_packet_or_future_history_endpoint_is_rejected() -> None:
    ledger = _ledger()
    first = ledger.snapshots[0]
    duplicate = replace(first.packets[1], packet_id=first.packets[0].packet_id)
    with pytest.raises(ValueError, match="packet"):
        replace(first, packets=(first.packets[0], duplicate)).validate()

    with pytest.raises(ValueError, match="future history"):
        replace(first.packets[1], history_index_right=12)


def test_operator_verification_state_cannot_be_relabelled_as_trajectory() -> None:
    ledger = _ledger()
    with pytest.raises(ValueError, match="operator-verification"):
        replace(
            ledger.snapshots[0],
            state_classification=StateClassification.NATIVE_DERIVED_TRAJECTORY,
        )

    with pytest.raises(ValueError, match="direct state remap"):
        replace(ledger, direct_state_remap_used=True).validate()
    with pytest.raises(ValueError, match="fitted normalization"):
        replace(ledger, fitted_normalization_used=True).validate()


def test_canonical_roundtrip_and_digest_are_exact() -> None:
    ledger = _ledger()
    encoded = ledger.canonical_json()
    restored = CommonInterfaceLedger.from_payload(json.loads(encoded))
    assert restored == ledger
    assert restored.canonical_json() == encoded
    assert restored.sha256 == ledger.sha256
    assert restored.to_payload()["claim_level"] == "source_conditioned_operator_contract"
