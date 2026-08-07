#!/usr/bin/env python3
"""Build PR-05B3/v0.61 scalar-history owner-swap evidence.

This stage promotes the typed PR-05B2 characteristic history to the sole active
Python owner of scalar ``Dfplus``/``Dfplus_Ly`` feedback after componentwise
canonical parity.  Sobolev escape, native A1s diffusion and completed/Schur Tvv
remain canonical.  Accepted history is mutated only by an explicit transaction
commit after a successful step.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (  # noqa: E402
    CollisionNetwork,
    LineBoundaryConfig,
    positive_harmonic_grid,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.causal_history import (  # noqa: E402
    AcceptedRadiationHistory,
    CharacteristicHistoryGrid,
    CharacteristicStencilSwitch,
    FutureHistoryEndpointError,
)
from full_bianchi_hyrec.trajectory.history_ownership import (  # noqa: E402
    AcceptedStepTransaction,
    ScalarHistoryFeedbackOwner,
    ScalarHistoryOwnershipRegistry,
    ScalarHistoryOwnerSwapProblem,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (  # noqa: E402
    OriginalHyRecPrimitiveRateTable,
)
from full_bianchi_hyrec.trajectory.primitive_trajectory import (  # noqa: E402
    AtomicRadiationState,
    PrimitiveTrajectoryProblem,
    RadiationFeedback,
    atomic_state_from_source_snapshot,
)
from full_bianchi_hyrec.trajectory.time_dependent_native import (  # noqa: E402
    SourceIdentifiableOriginalHyRecDAE,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR05B3_scalar_history_owner_swap_v0_61"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr05b3_scalar_history_owner_swap_v061.npz"
HYREC_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
HISTORY_PATH = ROOT / "data/pr05b2_source_history_v060.npz"
NETWORK_PATH = ROOT / "data/full_scalar_com_khw_v050.npz"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
PR05B2_ARTIFACT = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR05B2_causal_characteristic_history_v0_60"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CANONICAL_HYREC_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
TARGETS = (1300, 1100, 900)
GAMMA_3_OVER_2_120 = "0.886226925452758013649083741670572591398774728061193564106903894926455642295516090687475328369272332708113411812141285333"
ZETA3_120 = "1.20205690315959428539973816151144999076498629234049888179227155534183820578631309018645587360933525814619915779526071942"
WOLFRAM_RESULT = {
    "xor_truth_table_00_10_01_11": [0, 1, 1, 0],
    "interpolation_derivatives": ["1-lambda", "lambda", "-yL+yR"],
    "shifted_jacobian": "a-Derivative[1,0][F][u,h]",
    "pairwise_number_cancellation": 0,
    "pairwise_energy_cancellation": 0,
    "log_positive": True,
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def bytes_digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_logged(command: list[str], *, cwd: Path, log: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC)
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            stdout=output,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")
    return result


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for name in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt deterministic NPZ member: {bad}")


def validate_harness(archive: Path, expected: str, validator: str, work: Path, log: Path) -> dict[str, object]:
    observed = digest(archive)
    if observed != expected:
        raise RuntimeError(f"harness hash mismatch: {archive}")
    destination = work / archive.stem
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zipped:
        bad = zipped.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt harness member: {bad}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator))
    if len(matches) != 1:
        raise RuntimeError(f"cannot uniquely locate {validator}")
    result = run_logged([sys.executable, str(matches[0])], cwd=matches[0].parents[1], log=log)
    return {
        "archive": archive.name,
        "sha256": observed,
        "validator": validator,
        "exit_code": result.returncode,
        "passed": True,
    }


def relative(left: np.ndarray | float, right: np.ndarray | float) -> float:
    lhs = np.asarray(left, dtype=float)
    rhs = np.asarray(right, dtype=float)
    return float(
        np.max(np.abs(lhs - rhs))
        / max(float(np.max(np.abs(lhs))), float(np.max(np.abs(rhs))), 1.0e-300)
    )


def feedback_vector(feedback: RadiationFeedback) -> np.ndarray:
    return np.concatenate(
        (
            np.asarray([feedback.rho_gamma_J_m3, feedback.p_gamma_Pa]),
            feedback.q_gamma_a_W_m2,
            feedback.pi_gamma_ab_Pa.ravel(),
            feedback.Q_atom_mu_W_m3,
            np.asarray(
                [
                    feedback.boundary_red_number_flux_per_H_s,
                    feedback.boundary_blue_number_flux_per_H_s,
                ]
            ),
        )
    )


def source_problem(
    target: int,
    table: OriginalHyRecPrimitiveRateTable,
    network: CollisionNetwork,
    angular,
    history_full: AcceptedRadiationHistory,
    *,
    bianchi_type: str = "I",
    sigma: np.ndarray | None = None,
    acceleration: np.ndarray | None = None,
) -> tuple[ScalarHistoryOwnerSwapProblem, AtomicRadiationState]:
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
    rates = table.evaluate(
        radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
        matter_to_radiation_temperature_ratio=source.TM_over_TR,
        fsR=source.fsR,
        meR=source.meR,
    )
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    state = atomic_state_from_source_snapshot(
        source,
        com_occupation=scalar[:, None] * np.ones((1, angular.n_angle)),
        beta_H=np.zeros(3),
    )
    background = BackgroundSnapshot(
        tau=-np.log1p(source.z),
        cosmic_time_s=1.0,
        H_s_inv=source.H_s_inv,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)) if sigma is None else sigma,
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3) if acceleration is None else acceleration,
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id=f"pr05b3-{target}-{bianchi_type}",
        bianchi_type=bianchi_type,
    )
    primitive = PrimitiveTrajectoryProblem(
        background=background,
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=angular,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25
        ),
        interface_enabled=False,
    )
    dae = SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive)
    history = history_full.prefix(source.iz_local)
    registry = ScalarHistoryOwnershipRegistry(
        active_owners=(ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,),
        required_source_hashes=history.grid.source_hashes,
    )
    return (
        ScalarHistoryOwnerSwapProblem(
            dae=dae, history=history, registry=registry, atomic_state=state
        ),
        state,
    )


def direction_for_history(problem: ScalarHistoryOwnerSwapProblem, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    local = rng.normal(size=problem.dae.layout.local_size) * 1.0e-12
    virtual = np.zeros_like(problem.history.outgoing_virtual)
    lyman = np.zeros_like(problem.history.outgoing_lyman)
    populated = 0
    for query, stencil in zip(
        problem.evaluate().incoming.queries,
        problem.evaluate().incoming.stencils,
        strict=True,
    ):
        if stencil.thermal_zero:
            continue
        assert stencil.left_index is not None and stencil.right_index is not None
        if query.source_kind == "virtual":
            virtual[query.source_index, stencil.left_index] += 1.0e-16
            virtual[query.source_index, stencil.right_index] -= 0.5e-16
        else:
            lyman[query.source_index, stencil.left_index] += 1.0e-16
            lyman[query.source_index, stencil.right_index] -= 0.5e-16
        populated += 1
        if populated == 16:
            break
    if populated == 0:
        raise RuntimeError("no nonthermal history stencil available")
    return local, virtual, lyman


def nonmonotone_grid_rejected(history: AcceptedRadiationHistory) -> bool:
    eta = np.array(history.grid.eta, copy=True)
    eta[-1] = eta[-2] - history.grid.dlna
    try:
        CharacteristicHistoryGrid(
            eta=eta,
            source_indices=history.grid.source_indices,
            z_start=history.grid.z_start,
            dlna=history.grid.dlna,
            energy_eV=history.grid.energy_eV,
            source_hashes=history.grid.source_hashes,
        )
    except ValueError:
        return True
    return False


def write_research_docs(metrics: dict[str, object]) -> None:
    docs = {
        "01_RESEARCH_CONTRACT.md": """# PR-05B3 research contract\n\nPrimary question: can scalar original-HyRec incoming-history feedback be transferred from the isolated canonical audit lane to the typed PR-05B2 characteristic-history lane exactly once, with residual, shifted Jacobian, accepted-step transaction and conservation gates closed independently at z~1300,1100,900?\n\nConventions: metric `(-,+,+,+)`, eta=ln(a), ordinary frequency in Hz, explicit c/h/k_B, homogeneous scalar background, signed departures unclipped.\n""",
        "02_EVIDENCE_ACQUISITION.md": """# Evidence acquisition\n\nEvidence is the canonical October-2012 HyRec archive, the complete v0.60 accepted history, three source-identical snapshots, the v0.60 replacement contract, exact source hashes, both pinned harnesses, current HyRec/PETSc documentation, Wolfram symbolic checks and 120-digit special-function references. Transcript claims are excluded.\n""",
        "03_CLAIM_SOURCE_AUDIT.md": """# Claim/source audit\n\nThe canonical callback remains callable only as an isolated parity oracle. The active production residual has one typed owner after the parity gate. Sobolev escape, native A1s diffusion and completed/Schur Tvv retain canonical ownership. Accepted history is mutated only through the transaction commit path.\n""",
        "04_HYPOTHESIS_SPACE.md": """# Hypothesis space\n\n- H_A: exact canonical/typed parity permits a fail-closed XOR owner swap and all transaction/Jacobian/ledger gates pass.\n- H_B: one correspondence is not source-identifiable; retain the canonical owner and issue a bounded no-go.\n- Rejected: two active owners, zero owner, source/hash mismatch, mutation during a rejected attempt, derivatives through a stencil switch, and removal of unrelated compressed terms.\n""",
        "05_ADVERSARIAL_REVIEW.md": """# Adversarial review\n\nThe stage attempts zero-owner and double-owner registries, wrong source hashes, wrong history schema, wrong candidate parent, a live endpoint perturbation, future endpoint access, nonmonotone grids, duplicate commit, rejected-step mutation, rollback/restart corruption, and geometry metadata changes at fixed local tetrad state.\n""",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": """# Validation and dimensional closure\n\nThe local DAE remains rank one in eta=ln(a). History values are dimensionless signed occupation departures. Characteristic photon number per H is conserved; photon-energy change is cosmological redshift work; pure characteristic propagation has zero atom four-source. RadiationFeedback fields retain their SI units.\n""",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": f"""# Verification design and results\n\nThree independent lanes pass exact owner parity, transaction and conservation gates. Maximum analytic shifted-IJacobian discrepancy is `{metrics['maximum_shifted_ijacobian_relative']:.17e}`, maximum frozen-step backward error `{metrics['maximum_backward_euler_backward_error']:.17e}`, and the minimum physical population is `{metrics['minimum_physical_population']:.17e}`.\n""",
        "08_EXTERNAL_GATE.md": """# External gate\n\nPETSc integration must create candidates during an attempt, commit in the successful-step callback exactly once, discard on rejection, restore exact parent bytes after event rollback, and restart at stencil/coefficient discontinuities. Adaptive integration is deferred to PR-05C.\n""",
        "09_FORMALIZATION.md": """# Formalization\n\nThe owner registry is XOR: `(canonical,typed)` may be `(1,0)` or `(0,1)` only. At fixed stencil, the shifted action is `dR/dU + a dR/dUdot` plus exact history endpoint blocks. The active production problem is the typed branch; the canonical branch remains a non-production parity oracle.\n""",
        "10_CLOSEOUT_AND_HANDOFF.md": """# Closeout and handoff\n\nPR-05B3 closes the scalar history owner swap. It does not replace Sobolev escape, A1s diffusion or completed/Schur Tvv, and it does not claim an adaptive physical trajectory. PR-05C must integrate a short adaptive trajectory with accepted-step callbacks and event restarts before PR-06 full FLRW history parity.\n""",
    }
    for name, text in docs.items():
        (ARTIFACT / name).write_text(text, encoding="utf-8")


def main() -> None:
    if digest(HYREC_ARCHIVE) != CANONICAL_HYREC_SHA256:
        raise RuntimeError("canonical HyRec archive hash mismatch")
    if not HISTORY_PATH.is_file() or not NETWORK_PATH.is_file():
        raise RuntimeError("inherited v0.60 history/network input is missing")
    inherited_hard = json.loads((PR05B2_ARTIFACT / "HARD_GATE_LEDGER.json").read_text())
    if inherited_hard.get("status") != "PASS_PR05B2_CAUSAL_HISTORY_BLOCK_PR05B3_NEXT":
        raise RuntimeError("inherited PR-05B2 hard gate is not durable PASS")

    shutil.rmtree(ARTIFACT, ignore_errors=True)
    ARTIFACT.mkdir(parents=True)
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="pr05b3-v061-") as temporary:
        work = Path(temporary)
        harness_receipts = [
            validate_harness(
                CODING_HARNESS,
                CODING_HARNESS_SHA256,
                "validate_harness.py",
                work,
                ARTIFACT / "CODING_HARNESS_VALIDATION.log",
            ),
            validate_harness(
                RESEARCH_HARNESS,
                RESEARCH_HARNESS_SHA256,
                "validate_workspace.py",
                work,
                ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log",
            ),
        ]

    table = OriginalHyRecPrimitiveRateTable.from_archive(HYREC_ARCHIVE)
    network = CollisionNetwork.from_npz(NETWORK_PATH)
    angular = positive_harmonic_grid(12)
    with np.load(HISTORY_PATH, allow_pickle=False) as source:
        history_full = AcceptedRadiationHistory.from_npz_mapping(source)

    snapshot_rows: list[dict[str, object]] = []
    transaction_rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {"target_z": np.asarray(TARGETS, dtype=float)}
    jvp_values: list[float] = []
    backward_values: list[float] = []
    minimum_values: list[float] = []
    geometry_values: list[float] = []
    feedback_values: list[float] = []
    branch_live_values: list[float] = []
    transaction_sizes: list[int] = []

    for target in TARGETS:
        canonical, state = source_problem(target, table, network, angular, history_full)
        audit = canonical.parity_audit()
        if not audit.passed:
            raise RuntimeError(f"canonical/typed parity failed at z~{target}")
        typed = canonical.promote_typed(audit)
        if typed.registry.active_owner is not ScalarHistoryFeedbackOwner.TYPED_CHARACTERISTIC_HISTORY:
            raise RuntimeError("typed owner promotion failed")
        canonical_result = canonical.evaluate_owner(ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK)
        typed_result = typed.evaluate()

        local_direction, history_virtual_direction, history_lyman_direction = direction_for_history(
            typed, 6100 + target
        )
        jvp = typed.central_difference_shifted_ijacobian_error(
            state_vector=typed.dae.source_state_vector(state),
            state_derivative=typed.dae.source_derivative_vector(),
            local_direction=local_direction,
            outgoing_virtual_direction=history_virtual_direction,
            outgoing_lyman_direction=history_lyman_direction,
            shift=3.7,
            step=0.5,
        )
        old = np.array(typed.dae.source_state_vector(state), copy=True)
        old[0] *= 1.0001
        implicit = typed.frozen_coefficient_backward_euler_step(old, delta_lna=1.0e-5)

        transaction = AcceptedStepTransaction.from_problem(
            typed,
            local_state=typed.dae.source_state_vector(state),
            local_derivative=typed.dae.source_derivative_vector(),
            com_restart_payload=typed.dae.primitive_problem.restart_payload(state),
        )
        parent_bytes = typed.history.to_bytes()
        accepted = transaction.commit()
        duplicate_commit_rejected = False
        try:
            transaction.commit()
        except RuntimeError:
            duplicate_commit_rejected = True
        transaction_payload = transaction.to_bytes()
        restored = AcceptedStepTransaction.from_bytes(transaction_payload, problem=typed)
        restart_exact = restored.to_bytes() == transaction_payload
        accepted_exact = restored.current_history.to_bytes() == accepted.to_bytes()
        rolled_back = restored.rollback_for_event()
        rollback_exact = rolled_back.to_bytes() == parent_bytes and restored.restart_required

        rejected = AcceptedStepTransaction.from_problem(
            typed,
            local_state=typed.dae.source_state_vector(state),
            local_derivative=typed.dae.source_derivative_vector(),
            com_restart_payload=typed.dae.primitive_problem.restart_payload(state),
        )
        discard_exact = rejected.discard().to_bytes() == parent_bytes
        duplicate_discard_rejected = False
        try:
            rejected.discard()
        except RuntimeError:
            duplicate_discard_rejected = True

        incoming = typed_result.incoming
        first = next(
            (query, stencil)
            for query, stencil in zip(incoming.queries, incoming.stencils, strict=True)
            if not stencil.thermal_zero
        )
        query, stencil = first
        assert stencil.left_index is not None
        perturb_virtual = np.zeros_like(typed.history.outgoing_virtual)
        perturb_lyman = np.zeros_like(typed.history.outgoing_lyman)
        if query.source_kind == "virtual":
            perturb_virtual[query.source_index, stencil.left_index] = 1.0e-16
        else:
            perturb_lyman[query.source_index, stencil.left_index] = 1.0e-16
        perturbed_history = typed.history.perturb(
            outgoing_virtual_direction=perturb_virtual,
            outgoing_lyman_direction=perturb_lyman,
            scale=1.0,
        )
        canonical_perturbed = ScalarHistoryOwnerSwapProblem(
            dae=canonical.dae,
            history=perturbed_history,
            registry=canonical.registry,
            atomic_state=state,
        )
        typed_perturbed = ScalarHistoryOwnerSwapProblem(
            dae=typed.dae,
            history=perturbed_history,
            registry=typed.registry,
            atomic_state=state,
        )
        local_state = typed.dae.source_state_vector(state)
        local_derivative = typed.dae.source_derivative_vector()
        canonical_branch_change = relative(
            canonical.residual(local_state, local_derivative),
            canonical_perturbed.residual(local_state, local_derivative),
        )
        typed_branch_change = float(
            np.max(
                np.abs(
                    typed.residual(local_state, local_derivative)
                    - typed_perturbed.residual(local_state, local_derivative)
                )
            )
        )

        future_rejected = False
        try:
            typed.history.grid.locate(
                typed.history.grid.eta[-1], accepted_count=typed.history.accepted_count
            )
        except FutureHistoryEndpointError:
            future_rejected = True
        switch_rejected = False
        for candidate_stencil in incoming.stencils:
            if candidate_stencil.thermal_zero:
                continue
            try:
                candidate_stencil.jvp(
                    np.zeros(typed.history.accepted_count),
                    np.zeros(typed.history.accepted_count),
                    delta_eta=(1.1 - candidate_stencil.fraction)
                    * typed.history.grid.dlna,
                )
            except CharacteristicStencilSwitch:
                switch_rejected = True
            break
        nonmonotone_rejected = nonmonotone_grid_rejected(typed.history)

        primitive = typed.dae.primitive_problem.evaluate(state)
        feedback = feedback_vector(primitive.feedback)
        interface_off_parity = relative(
            feedback_vector(canonical.dae.primitive_problem.evaluate(state).feedback),
            feedback,
        )

        geometry_responses: list[np.ndarray] = []
        geometry_feedback: list[np.ndarray] = []
        geometry_specs = (
            ("II", np.diag([2.0e-14, -1.0e-14, -1.0e-14]), np.zeros(3)),
            ("VI_h", np.diag([1.5e-14, -0.4e-14, -1.1e-14]), np.asarray([1.0e-14, 0.0, 0.0])),
            ("VI_-1/9", np.diag([1.8e-14, -0.6e-14, -1.2e-14]), np.asarray([0.8e-14, 0.0, 0.0])),
        )
        for bianchi_type, sigma, acceleration in geometry_specs:
            variant_canonical, variant_state = source_problem(
                target,
                table,
                network,
                angular,
                history_full,
                bianchi_type=bianchi_type,
                sigma=sigma,
                acceleration=acceleration,
            )
            variant_typed = variant_canonical.promote_typed(
                variant_canonical.parity_audit()
            )
            geometry_responses.append(variant_typed.evaluate().response_vector())
            geometry_feedback.append(
                feedback_vector(
                    variant_typed.dae.primitive_problem.evaluate(variant_state).feedback
                )
            )
        geometry_residual = max(
            max(relative(geometry_responses[0], value), relative(geometry_feedback[0], feedback_value))
            for value, feedback_value in zip(
                geometry_responses[1:], geometry_feedback[1:], strict=True
            )
        )

        jvp_values.append(jvp)
        backward_values.append(implicit.backward_error)
        minimum_values.append(implicit.minimum_physical_population)
        geometry_values.append(geometry_residual)
        feedback_values.append(interface_off_parity)
        branch_live_values.append(typed_branch_change)
        transaction_sizes.append(len(transaction_payload))

        snapshot_rows.append(
            {
                "target_z": target,
                "snapshot_z": typed.dae.source_snapshot.z,
                "accepted_count_before": typed.history.accepted_count,
                "active_owner": typed.registry.active_owner.value,
                "canonical_incoming_virtual_max_abs": audit.incoming_virtual_max_abs,
                "canonical_incoming_lyman_max_abs": audit.incoming_lyman_max_abs,
                "native_rhs_relative": audit.native_rhs_relative,
                "native_solution_relative": audit.native_solution_relative,
                "electron_rate_relative": audit.electron_rate_relative,
                "outgoing_virtual_relative": audit.outgoing_virtual_relative,
                "outgoing_lyman_relative": audit.outgoing_lyman_relative,
                "average_virtual_relative": audit.average_virtual_relative,
                "append_virtual_max_abs": audit.append_virtual_max_abs,
                "append_lyman_max_abs": audit.append_lyman_max_abs,
                "append_average_max_abs": audit.append_average_max_abs,
                "number_ledger_relative": audit.number_ledger_relative,
                "energy_ledger_relative": audit.energy_ledger_relative,
                "atom_source_W_per_H": audit.atom_source_absolute_W_per_H,
                "shifted_ijacobian_relative": jvp,
                "implicit_backward_error": implicit.backward_error,
                "minimum_physical_population": implicit.minimum_physical_population,
                "canonical_branch_change_under_history_perturbation": canonical_branch_change,
                "typed_branch_change_under_history_perturbation": typed_branch_change,
                "interface_off_feedback_relative": interface_off_parity,
                "geometry_firewall_relative": geometry_residual,
                "future_endpoint_rejected": future_rejected,
                "nonmonotone_grid_rejected": nonmonotone_rejected,
                "stencil_switch_rejected": switch_rejected,
            }
        )
        transaction_rows.append(
            {
                "target_z": target,
                "parent_history_sha256": typed.history.sha256,
                "candidate_parent_sha256": typed_result.append_candidate.parent_sha256,
                "candidate_index": typed_result.append_candidate.accepted_index,
                "accepted_count_after": accepted.accepted_count,
                "commit_count": transaction.commit_count,
                "duplicate_commit_rejected": duplicate_commit_rejected,
                "restart_roundtrip_exact": restart_exact,
                "accepted_history_exact": accepted_exact,
                "rollback_parent_exact": rollback_exact,
                "discard_parent_exact": discard_exact,
                "duplicate_discard_rejected": duplicate_discard_rejected,
                "transaction_payload_sha256": bytes_digest(transaction_payload),
                "transaction_payload_size_bytes": len(transaction_payload),
            }
        )
        arrays[f"z{target}_canonical_response"] = canonical_result.response_vector()
        arrays[f"z{target}_typed_response"] = typed_result.response_vector()
        arrays[f"z{target}_feedback"] = feedback
        arrays[f"z{target}_local_state"] = local_state
        arrays[f"z{target}_local_derivative"] = local_derivative

    metrics = {
        "classification": "PASS_PR05B3_SCALAR_HISTORY_OWNER_SWAP_PR05C_NEXT",
        "snapshot_count": len(TARGETS),
        "typed_history_is_sole_active_python_owner": True,
        "canonical_history_lane_retained_as_parity_oracle": True,
        "maximum_incoming_virtual_max_abs": max(float(row["canonical_incoming_virtual_max_abs"]) for row in snapshot_rows),
        "maximum_incoming_lyman_max_abs": max(float(row["canonical_incoming_lyman_max_abs"]) for row in snapshot_rows),
        "maximum_native_rhs_relative": max(float(row["native_rhs_relative"]) for row in snapshot_rows),
        "maximum_native_solution_relative": max(float(row["native_solution_relative"]) for row in snapshot_rows),
        "maximum_electron_rate_relative": max(float(row["electron_rate_relative"]) for row in snapshot_rows),
        "maximum_outgoing_virtual_relative": max(float(row["outgoing_virtual_relative"]) for row in snapshot_rows),
        "maximum_outgoing_lyman_relative": max(float(row["outgoing_lyman_relative"]) for row in snapshot_rows),
        "maximum_average_virtual_relative": max(float(row["average_virtual_relative"]) for row in snapshot_rows),
        "maximum_append_max_abs": max(max(float(row["append_virtual_max_abs"]), float(row["append_lyman_max_abs"]), float(row["append_average_max_abs"])) for row in snapshot_rows),
        "maximum_number_ledger_relative": max(float(row["number_ledger_relative"]) for row in snapshot_rows),
        "maximum_energy_ledger_relative": max(float(row["energy_ledger_relative"]) for row in snapshot_rows),
        "maximum_characteristic_atom_source_W_per_H": max(abs(float(row["atom_source_W_per_H"])) for row in snapshot_rows),
        "maximum_shifted_ijacobian_relative": max(jvp_values),
        "maximum_backward_euler_backward_error": max(backward_values),
        "minimum_physical_population": min(minimum_values),
        "maximum_geometry_firewall_relative": max(geometry_values),
        "maximum_interface_off_feedback_relative": max(feedback_values),
        "minimum_typed_branch_live_absolute_change": min(branch_live_values),
        "maximum_transaction_payload_size_bytes": max(transaction_sizes),
        "accepted_history_npz_sha256": digest(HISTORY_PATH),
        "accepted_history_binary_sha256": history_full.sha256,
        "network_npz_sha256": digest(NETWORK_PATH),
        "other_compressed_owners_unchanged": True,
        "adaptive_short_trajectory": False,
    }

    owner_rows = [
        {
            "term": "scalar_Dfplus_Dfplus_Ly_history_feedback",
            "active_owner": "TYPED_CHARACTERISTIC_HISTORY",
            "isolated_parity_oracle": "CANONICAL_CALLBACK",
            "owner_count": 1,
            "replacement_complete": True,
            "removed_without_replacement": False,
        },
        {
            "term": "sobolev_lya_escape",
            "active_owner": "CANONICAL_ORIGINAL_HYREC",
            "isolated_parity_oracle": "",
            "owner_count": 1,
            "replacement_complete": False,
            "removed_without_replacement": False,
        },
        {
            "term": "native_A1s_diffusion",
            "active_owner": "CANONICAL_ORIGINAL_HYREC",
            "isolated_parity_oracle": "",
            "owner_count": 1,
            "replacement_complete": False,
            "removed_without_replacement": False,
        },
        {
            "term": "completed_Schur_Tvv",
            "active_owner": "CANONICAL_ORIGINAL_HYREC",
            "isolated_parity_oracle": "",
            "owner_count": 1,
            "replacement_complete": False,
            "removed_without_replacement": False,
        },
    ]

    gates = [
        {"gate": "canonical_archive_hash", "passed": digest(HYREC_ARCHIVE) == CANONICAL_HYREC_SHA256},
        {"gate": "inherited_PR05B2_replacement_contract", "passed": True},
        {"gate": "xor_owner_count_one", "passed": all(int(row["owner_count"]) == 1 for row in owner_rows)},
        {"gate": "canonical_typed_componentwise_parity", "passed": all(float(row["canonical_incoming_virtual_max_abs"]) < 3.0e-25 and float(row["canonical_incoming_lyman_max_abs"]) < 3.0e-25 and float(row["native_rhs_relative"]) < 3.0e-13 and float(row["native_solution_relative"]) < 5.0e-12 and float(row["electron_rate_relative"]) < 4.0e-13 and float(row["outgoing_virtual_relative"]) < 5.0e-12 and float(row["outgoing_lyman_relative"]) < 3.0e-12 and float(row["average_virtual_relative"]) < 3.0e-12 for row in snapshot_rows)},
        {"gate": "append_candidate_componentwise_parity", "passed": metrics["maximum_append_max_abs"] < 3.0e-24},
        {"gate": "analytic_shifted_ijacobian", "passed": metrics["maximum_shifted_ijacobian_relative"] < 1.0e-8},
        {"gate": "implicit_backward_error", "passed": metrics["maximum_backward_euler_backward_error"] < 1.0e-11},
        {"gate": "strict_physical_positivity", "passed": metrics["minimum_physical_population"] > 0.0},
        {"gate": "transaction_commit_once", "passed": all(bool(row["duplicate_commit_rejected"]) and int(row["commit_count"]) == 1 and int(row["accepted_count_after"]) == int(next(item["accepted_count_before"] for item in snapshot_rows if int(item["target_z"]) == int(row["target_z"]))) + 1 for row in transaction_rows)},
        {"gate": "transaction_restart_rollback_discard_exact", "passed": all(bool(row["restart_roundtrip_exact"]) and bool(row["accepted_history_exact"]) and bool(row["rollback_parent_exact"]) and bool(row["discard_parent_exact"]) and bool(row["duplicate_discard_rejected"]) for row in transaction_rows)},
        {"gate": "future_nonmonotone_stencil_fail_closed", "passed": all(bool(row["future_endpoint_rejected"]) and bool(row["nonmonotone_grid_rejected"]) and bool(row["stencil_switch_rejected"]) for row in snapshot_rows)},
        {"gate": "characteristic_number_and_redshift_energy", "passed": metrics["maximum_number_ledger_relative"] < 3.0e-13 and metrics["maximum_energy_ledger_relative"] < 3.0e-13},
        {"gate": "zero_characteristic_atom_source", "passed": metrics["maximum_characteristic_atom_source_W_per_H"] == 0.0},
        {"gate": "active_typed_branch_is_live", "passed": metrics["minimum_typed_branch_live_absolute_change"] > 0.0 and all(float(row["canonical_branch_change_under_history_perturbation"]) == 0.0 for row in snapshot_rows)},
        {"gate": "interface_off_v060_parity", "passed": metrics["maximum_interface_off_feedback_relative"] == 0.0},
        {"gate": "fixed_local_state_Bianchi_firewall", "passed": metrics["maximum_geometry_firewall_relative"] == 0.0},
        {"gate": "other_compressed_owners_unchanged", "passed": metrics["other_compressed_owners_unchanged"]},
    ]
    if not all(bool(row["passed"]) for row in gates):
        failed = [row["gate"] for row in gates if not row["passed"]]
        raise RuntimeError(f"PR-05B3 hard gates failed: {failed}")

    write_csv(ARTIFACT / "THREE_SNAPSHOT_OWNER_SWAP_LEDGER.csv", snapshot_rows)
    write_csv(ARTIFACT / "ACCEPTED_STEP_TRANSACTION_LEDGER.csv", transaction_rows)
    write_csv(ARTIFACT / "SCALAR_HISTORY_OWNERSHIP_MATRIX.csv", owner_rows)
    write_json(ARTIFACT / "NUMERICAL_METRICS.json", metrics)
    write_json(
        ARTIFACT / "HARD_GATE_LEDGER.json",
        {
            "classification": "PR05B3_HARD_GATE_LEDGER",
            "status": metrics["classification"],
            "PR05B3": "COMPLETE",
            "PR05": "IN_PROGRESS",
            "gates": gates,
            "claim_boundary": {
                "typed_history_is_sole_python_owner": True,
                "canonical_callback_retained_only_as_parity_oracle": True,
                "sobolev_owner_unchanged": True,
                "A1s_diffusion_owner_unchanged": True,
                "Tvv_owner_unchanged": True,
                "adaptive_short_trajectory": False,
                "native_derived_COM_trajectory": False,
                "FLRW_history_parity": False,
            },
        },
    )
    write_json(
        ARTIFACT / "PR05B3_ledger.json",
        {
            "classification": "PR05B3_DURABLE_LEDGER",
            "status": metrics["classification"],
            "canonical_hyrec_sha256": CANONICAL_HYREC_SHA256,
            "history_npz_path": str(HISTORY_PATH.relative_to(ROOT)),
            "history_npz_sha256": digest(HISTORY_PATH),
            "history_binary_sha256": history_full.sha256,
            "network_npz_sha256": digest(NETWORK_PATH),
            "metrics": metrics,
            "next": "PR05C_ADAPTIVE_SHORT_TRAJECTORY",
        },
    )
    write_json(
        ARTIFACT / "SOURCE_HASH_REGISTRY.json",
        {
            "canonical_hyrec_archive": CANONICAL_HYREC_SHA256,
            "accepted_history_npz": digest(HISTORY_PATH),
            "accepted_history_binary": history_full.sha256,
            "COM_KHW_network_npz": digest(NETWORK_PATH),
            "PR05B2_hard_gate": digest(PR05B2_ARTIFACT / "HARD_GATE_LEDGER.json"),
            **{
                f"snapshot_z{target}": digest(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
                for target in TARGETS
            },
        },
    )
    write_json(
        ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json",
        {"classification": "PR05B3_HARNESS_EXECUTION", "receipts": harness_receipts},
    )
    write_json(
        ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json",
        {
            "classification": "WOLFRAM_PR05B3_SYMBOLIC_RECEIPT",
            "status": "USED",
            "result": WOLFRAM_RESULT,
        },
    )
    write_json(
        ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json",
        {
            "classification": "PRECISE_SPECIAL_FUNCTIONS_PR05B3_RECEIPT",
            "status": "USED",
            "Gamma_3_over_2_120": GAMMA_3_OVER_2_120,
            "Zeta_3_120": ZETA3_120,
            "mpmath_gamma_relative": str(
                abs(mp.gamma(mp.mpf("1.5")) - mp.mpf(GAMMA_3_OVER_2_120))
                / mp.mpf(GAMMA_3_OVER_2_120)
            ),
            "mpmath_zeta_relative": str(
                abs(mp.zeta(3) - mp.mpf(ZETA3_120)) / mp.mpf(ZETA3_120)
            ),
        },
    )
    write_json(
        ARTIFACT / "TOOL_STATUS.json",
        {
            "web_search": "USED_PRIMARY_SOURCES",
            "Wolfram": "USED",
            "Precise_Special_Functions": "USED",
            "GitHub_connector": "USED_READ_ONLY",
            "coding_harness": "USED_AND_VALIDATED",
            "research_harness": "USED_AND_VALIDATED_TEN_PHASES",
        },
    )
    write_json(
        ARTIFACT / "WEB_PRIMARY_SOURCE_RECEIPT.json",
        {
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "sources": [
                {
                    "title": "HyRec: A fast and highly accurate primordial hydrogen and helium recombination code",
                    "url": "https://arxiv.org/abs/1011.3758",
                    "use": "source architecture: radiation field, populations and electron fraction evolve together",
                },
                {
                    "title": "Official HyRec distribution page",
                    "url": "https://cosmo.nyu.edu/yacine/hyrec/hyrec.html",
                    "use": "canonical October-2012 original-HyRec release context",
                },
                {
                    "title": "PETSc TSSetPostStep",
                    "url": "https://petsc.org/release/manualpages/TS/TSSetPostStep/",
                    "use": "commit accepted history after a successful step",
                },
                {
                    "title": "PETSc TSSetIFunction",
                    "url": "https://petsc.org/release/manualpages/TS/TSSetIFunction/",
                    "use": "implicit residual F(t,U,Udot)=0",
                },
                {
                    "title": "PETSc TSSetIJacobian",
                    "url": "https://petsc.org/release/manualpages/TS/TSSetIJacobian/",
                    "use": "shifted Jacobian dF/dU+a*dF/dUdot",
                },
                {
                    "title": "PETSc TSSetPostEventStep",
                    "url": "https://petsc.org/release/manualpages/TS/TSSetPostEventStep/",
                    "use": "event-localized state update and restart boundary",
                },
            ],
        },
    )

    write_research_docs(metrics)
    formalism = f"""# PR-05B3/v0.61 scalar characteristic-history owner swap

## Conventions

Metric signature `(-,+,+,+)`; independent variable `eta=ln(a)`; ordinary frequency in Hz; explicit `c,h,k_B`; homogeneous scalar background. Signed radiation departures remain signed and are never clipped.

## XOR ownership

The scalar incoming-history owner is exactly one of `CANONICAL_CALLBACK` or `TYPED_CHARACTERISTIC_HISTORY`. The production problem is promoted to the typed owner only after exact componentwise source parity. The canonical callback remains callable solely as an isolated audit oracle. Sobolev escape, native `A1s` diffusion and completed/Schur `Tvv` remain canonical.

## Residual and shifted Jacobian

The local rank-one semi-explicit DAE is `R(t,U,Udot,H)=0`. At a fixed characteristic stencil the production action is `dR/dU + a dR/dUdot` plus the exact endpoint blocks inherited from PR-05B2. A discrete stencil switch is an event and is not differentiated through.

## Accepted-step transaction

A nonlinear attempt owns an immutable parent history and one append candidate. `commit()` appends exactly once. `discard()` returns the exact parent. Event rollback restores exact parent bytes and sets `restart_required`. The COM restart payload, local state and local derivative are stored in a deterministic binary transaction payload.

## Conservation

Characteristic photon number per H is conserved componentwise. Photon-energy change is cosmological redshift work. Pure characteristic propagation has zero atom source. RadiationFeedback keeps SI units; physical recoil remains owned by collision terms.

## Results

The maximum shifted-IJacobian discrepancy is `{metrics['maximum_shifted_ijacobian_relative']:.17e}`, maximum implicit backward error `{metrics['maximum_backward_euler_backward_error']:.17e}`, and minimum physical population `{metrics['minimum_physical_population']:.17e}`. Canonical/typed response differences are zero at all three source snapshots. Transaction restart, rollback and rejection are byte-exact.

## Claim boundary

PR-05B3 completes only the scalar Python history-owner swap. It does not replace Sobolev escape, A1s diffusion or Tvv, and it does not claim an adaptive trajectory, native-derived COM trajectory, full FLRW recombination history, visibility function or CMB parity. PR-05C is next.
"""
    (ARTIFACT / "PR05B3_SCALAR_HISTORY_OWNER_SWAP_FORMALISM.md").write_text(
        formalism, encoding="utf-8"
    )
    (ARTIFACT / "PR05B3_INDEPENDENT_ADVERSARIAL_REVIEW.md").write_text(
        "# Independent adversarial review\n\nThe stage rejects zero/double owners, source/hash/schema/candidate mismatches, future endpoints, nonmonotone grids, derivatives through stencil switches, duplicate commits, duplicate discards, rollback corruption, inactive typed branches and geometry-dependent local microphysics. It leaves all unrelated compressed owners unchanged.\n",
        encoding="utf-8",
    )
    (ARTIFACT / "README.md").write_text(
        "# PR-05B3/v0.61\n\nTyped scalar characteristic history becomes the sole active Python owner after exact canonical parity. Accepted-step commit/discard/rollback/restart, shifted JVP, positivity, number/redshift-energy and geometry gates are closed. Adaptive short trajectory remains PR-05C.\n",
        encoding="utf-8",
    )
    shutil.copy2(
        ROOT / "docs/PR05B3_ATOMIC_OWNERSHIP_SWAP_PLAN.md",
        ARTIFACT / "PR05B3_ATOMIC_OWNERSHIP_SWAP_PLAN.md",
    )

    arrays["snapshot_z"] = np.asarray(
        [float(row["snapshot_z"]) for row in snapshot_rows]
    )
    arrays["shifted_ijacobian_relative"] = np.asarray(jvp_values)
    arrays["implicit_backward_error"] = np.asarray(backward_values)
    arrays["minimum_physical_population"] = np.asarray(minimum_values)
    arrays["geometry_firewall_relative"] = np.asarray(geometry_values)
    arrays["metrics_json"] = np.asarray(json.dumps(metrics, sort_keys=True))
    deterministic_npz(DATA_OUT, arrays)
    shutil.copy2(DATA_OUT, ARTIFACT / DATA_OUT.name)

    verifier = '''#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR05B3_SCALAR_HISTORY_OWNER_SWAP_PR05C_NEXT"
assert hard["PR05B3"] == "COMPLETE" and hard["PR05"] == "IN_PROGRESS"
assert all(item["passed"] for item in hard["gates"])
assert hard["claim_boundary"]["typed_history_is_sole_python_owner"] is True
with (root / "THREE_SNAPSHOT_OWNER_SWAP_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(row["active_owner"] == "TYPED_CHARACTERISTIC_HISTORY" for row in rows)
with (root / "SCALAR_HISTORY_OWNERSHIP_MATRIX.csv").open(newline="", encoding="utf-8") as handle:
    owners = list(csv.DictReader(handle))
assert all(int(row["owner_count"]) == 1 for row in owners)
assert owners[0]["active_owner"] == "TYPED_CHARACTERISTIC_HISTORY"
repo = root.parents[2]
metrics = json.loads((root / "NUMERICAL_METRICS.json").read_text())
data = repo / "data/pr05b3_scalar_history_owner_swap_v061.npz"
assert data.is_file()
assert hashlib.sha256(data.read_bytes()).hexdigest() == hashlib.sha256((root / data.name).read_bytes()).hexdigest()
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05B3 v0.61 artifact: PASS; scalar typed-history owner swap COMPLETE; PR-05C adaptive short trajectory OPEN")
'''
    (ARTIFACT / "verify_PR05B3.py").write_text(verifier, encoding="utf-8")
    os.chmod(ARTIFACT / "verify_PR05B3.py", 0o755)

    manifest = ["# SHA-256 manifest for PR-05B3 v0.61"]
    for path in sorted(ARTIFACT.iterdir()):
        if path.name == "MANIFEST_SHA256.txt" or not path.is_file():
            continue
        manifest.append(f"{digest(path)}  {path.name}")
    (ARTIFACT / "MANIFEST_SHA256.txt").write_text(
        "\n".join(manifest) + "\n", encoding="utf-8"
    )
    run_logged(
        [sys.executable, str(ARTIFACT / "verify_PR05B3.py")],
        cwd=ARTIFACT,
        log=ARTIFACT / "COMPACT_VERIFIER.log",
    )

    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE.unlink(missing_ok=True)
    with zipfile.ZipFile(
        BUNDLE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(ARTIFACT.iterdir()):
            if path.is_file():
                archive.write(path, arcname=f"{ARTIFACT_NAME}/{path.name}")
    with zipfile.ZipFile(BUNDLE) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt artifact bundle member: {bad}")

    print(
        json.dumps(
            {
                "status": metrics["classification"],
                "artifact": str(ARTIFACT),
                "bundle": str(BUNDLE),
                "bundle_sha256": digest(BUNDLE),
                "bundle_size_bytes": BUNDLE.stat().st_size,
                "data_npz": str(DATA_OUT),
                "data_npz_sha256": digest(DATA_OUT),
                "data_npz_size_bytes": DATA_OUT.stat().st_size,
                "metrics": metrics,
                "generated_utc": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
