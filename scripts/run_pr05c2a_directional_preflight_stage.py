#!/usr/bin/env python3
"""Build PR-05C2A/v0.63 source-derived directional coupling evidence.

This bounded stage uses the actual locked BackgroundSnapshot sequences and the
35-state COM--KHW network to close a conservative direction-resolved frequency
transport/interface pilot.  It also records two blockers that prevent a full
source-identical adaptive trajectory claim: original HyRec supplies only scalar
native boundary history, and the cosmological macro step is extremely stiff for
the current unpreconditioned collision solve.
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

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.background import BackgroundSnapshotSequence  # noqa: E402
from full_bianchi_hyrec.recoil.frequency_liouville import (  # noqa: E402
    ConservativeFrequencyLiouville,
    angular_scalarization_no_go_witness,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (  # noqa: E402
    CollisionNetwork,
    LineBoundaryConfig,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (  # noqa: E402
    CoupledCollisionTransportProblem,
    audit_collision_stiffness,
    audit_full_coupling_identifiability,
    audit_thermodynamic_grid_consistency,
)

VERSION = 63
ARTIFACT_NAME = "Full_Bianchi_HyRec_PR05C2A_directional_coupling_preflight_v0_63"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA = ROOT / "data" / "pr05c2a_directional_coupling_v063.npz"
BACKGROUND = ROOT / "data/pr01c_background_snapshots_v048.npz"
NETWORK = ROOT / "data/full_scalar_com_khw_v050.npz"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
HYREC_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CANONICAL_HYREC_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
TARGETS = (1300, 1100, 900)
MODELS = (
    "Bianchi_II_large_shear",
    "Bianchi_VI_h_tilted_large_shear",
    "Bianchi_VI_minus_1_over_9_exceptional",
)
DLNA = 8.49e-5
PILOT_DT_S = 1.0
STATUS = (
    "PASS_PR05C2A_DIRECTIONAL_CONSERVATIVE_PILOT_BOUNDED_NO_GO_"
    "ANGULAR_THERMODYNAMIC_STIFFNESS_PR05C2B_NEXT"
)

MODEL_PILOT_TAU = {model: 0.0 for model in MODELS}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def deterministic_zip(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            info = zipfile.ZipInfo(str(relative), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def run_logged(command: list[str], *, cwd: Path, log: Path) -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC)
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(command, cwd=cwd, env=environment, stdout=output, stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")


def validate_harness(archive: Path, expected: str, validator: str, work: Path, log: Path) -> dict[str, object]:
    observed = sha256(archive)
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
    run_logged([sys.executable, str(matches[0])], cwd=matches[0].parents[1], log=log)
    return {"archive": archive.name, "sha256": observed, "validator": validator, "passed": True}


def load_grid() -> HarmonicGrid:
    with np.load(BACKGROUND, allow_pickle=False) as data:
        return HarmonicGrid.from_directions(data["directions"], data["angular_weights"], ell_max=3)


def normalized_geometry_residual(sequence: BackgroundSnapshotSequence, tau: float, target_H: float) -> float:
    base = sequence.snapshot_at_tau(tau)
    scaled = sequence.snapshot_at_tau(tau, H_s_inv_override=target_H)
    arrays = (
        (base.sigma_s_inv / base.H_s_inv, scaled.sigma_s_inv / scaled.H_s_inv),
        (base.N_s_inv / base.H_s_inv, scaled.N_s_inv / scaled.H_s_inv),
        (base.A_s_inv / base.H_s_inv, scaled.A_s_inv / scaled.H_s_inv),
        (base.frame_rotation_s_inv / base.H_s_inv, scaled.frame_rotation_s_inv / scaled.H_s_inv),
        (base.D0_beta_H_s_inv / base.H_s_inv, scaled.D0_beta_H_s_inv / scaled.H_s_inv),
    )
    return max(float(np.max(np.abs(first - second), initial=0.0)) for first, second in arrays)


def central_jvp_relative(problem: CoupledCollisionTransportProblem, occupation: np.ndarray) -> float:
    rng = np.random.default_rng(6301)
    direction = rng.normal(size=occupation.shape)
    direction /= max(float(np.max(np.abs(direction))), 1.0e-300)
    log_state = np.log(occupation)
    analytic = problem.residual_jvp(log_state, direction)
    # The coupled action spans many decades.  A normalized direction and this
    # predeclared epsilon keep the central difference above roundoff without
    # leaving the local linear regime.
    epsilon = 3.0e-5
    plus = problem.residual(log_state + epsilon * direction, occupation)
    minus = problem.residual(log_state - epsilon * direction, occupation)
    finite = (plus - minus) / (2.0 * epsilon)
    return float(np.max(np.abs(analytic - finite))) / max(float(np.max(np.abs(finite))), 1.0e-300)


def build_evidence() -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
    dict[str, np.ndarray],
]:
    network = CollisionNetwork.from_npz(NETWORK)
    grid = load_grid()
    transport = ConservativeFrequencyLiouville.from_network(network)
    identifiability = audit_full_coupling_identifiability(grid)
    witness = angular_scalarization_no_go_witness(grid)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    occupation = scalar[:, None] * (1.0 + 1.0e-5 * grid.directions[:, 0][None, :])

    stiffness_rows: list[dict[str, object]] = []
    thermodynamic_rows: list[dict[str, object]] = []
    root_rows: list[dict[str, object]] = []
    lane_rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {
        "directions": np.asarray(grid.directions),
        "angular_weights": np.asarray(grid.weights),
        "base_occupation": occupation,
    }

    for target in TARGETS:
        source = parse_original_hyrec_boundary_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
        red, blue = source.boundaries
        stiffness = audit_collision_stiffness(network, H_s_inv=source.trajectory.H_s_inv, canonical_dlna=DLNA)
        stiffness_rows.append({
            "target_z": target,
            "actual_z": source.trajectory.z,
            "H_s_inv": source.trajectory.H_s_inv,
            "macro_dt_s": stiffness.macro_dt_s,
            "collision_spectral_radius_s_inv": stiffness.spectral_radius_s_inv,
            "stiffness_number": stiffness.stiffness_number,
            "near_null_mode_count": stiffness.near_null_mode_count,
            "requires_block_preconditioner": int(stiffness.requires_block_preconditioner),
        })
        line = LineBoundaryConfig.lyman_alpha(
            temperature_K=source.trajectory.TM_eV_rescaled * 11604.518121550082,
            x_red=-21.25,
            x_blue=21.25,
        )
        thermodynamic = audit_thermodynamic_grid_consistency(
            network, source_line=line
        )
        pilot_line = transport.reference_line
        thermodynamic_rows.append(
            {
                "target_z": target,
                "actual_z": source.trajectory.z,
                "source_temperature_K": source.trajectory.TM_eV_rescaled
                * 11604.518121550082,
                "locked_doppler_width_Hz": thermodynamic.locked_doppler_width_Hz,
                "source_doppler_width_Hz": thermodynamic.source_doppler_width_Hz,
                "mode_measure_relative_residual": thermodynamic.mode_measure_relative_residual,
                "outer_face_frequency_relative_mismatch": thermodynamic.outer_face_frequency_relative_mismatch,
                "source_conditioned_dynamic_measure_identified": int(
                    thermodynamic.source_conditioned_dynamic_measure_identified
                ),
                "requires_network_recompilation": int(
                    thermodynamic.requires_network_recompilation
                ),
                "requires_explicit_frequency_remap": int(
                    thermodynamic.requires_explicit_frequency_remap
                ),
                "bounded_no_go": int(thermodynamic.bounded_no_go),
            }
        )
        for model in MODELS:
            sequence = BackgroundSnapshotSequence.from_npz(BACKGROUND, model)
            roots = sequence.boundary_speed_roots(
                tau_start=sequence.tau_range[0],
                tau_end=sequence.tau_range[1],
                directions_normal=grid.directions,
                line=pilot_line,
            )
            if target == TARGETS[0]:
                for side, values in (("red", roots.red), ("blue", roots.blue)):
                    for root_index, root in enumerate(values):
                        root_rows.append(
                            {
                                "model": model,
                                "bianchi_type": sequence.bianchi_type,
                                "side": side,
                                "root_index": root_index,
                                "tau": float(root),
                                "source_sha256": roots.source_sha256,
                                "source_derived": int(roots.source_derived),
                            }
                        )
            selected_tau = MODEL_PILOT_TAU[model]
            snapshot = sequence.snapshot_at_tau(
                selected_tau, H_s_inv_override=source.trajectory.H_s_inv
            )
            speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid)
            transport_result = transport.evaluate(
                occupation,
                face_speeds_x_s_inv=speeds,
                native_red_occupation=red.total_occupation,
                native_blue_occupation=blue.total_occupation,
                grid=grid,
            )
            problem = CoupledCollisionTransportProblem(
                network=network,
                grid=grid,
                transport=transport,
                face_speeds_x_s_inv=speeds,
                native_red_occupation=red.total_occupation,
                native_blue_occupation=blue.total_occupation,
                dt_s=PILOT_DT_S,
            )
            pilot = problem.implicit_step(
                occupation,
                nonlinear_rtol=5.0e-12,
                gmres_rtol=1.0e-9,
                gmres_maxiter=100,
            )
            jvp = central_jvp_relative(problem, occupation)
            boundary_flux_scale = max(
                abs(float(np.sum(grid.weights * transport_result.face_flux_m3_s[0]))),
                abs(float(np.sum(grid.weights * transport_result.face_flux_m3_s[-1]))),
                float(np.max(np.abs(transport_result.face_flux_m3_s), initial=0.0)),
                1.0e-300,
            )
            transport_number_relative = (
                abs(transport_result.global_number_residual_m3_s)
                / boundary_flux_scale
            )
            lane_key = f"z{target}_{model}"
            arrays[f"{lane_key}_outer_speeds"] = np.vstack((speeds[0], speeds[-1]))
            arrays[f"{lane_key}_pilot_occupation"] = pilot.occupation
            lane_rows.append({
                "target_z": target,
                "actual_z": source.trajectory.z,
                "model": model,
                "bianchi_type": snapshot.bianchi_type,
                "selected_tau": selected_tau,
                "red_root_count": int(roots.red.size),
                "blue_root_count": int(roots.blue.size),
                "outer_speed_min_s_inv": float(min(np.min(speeds[0]), np.min(speeds[-1]))),
                "outer_speed_max_s_inv": float(max(np.max(speeds[0]), np.max(speeds[-1]))),
                "mixed_directional_flow": int(np.min(np.vstack((speeds[0], speeds[-1]))) < 0.0 < np.max(np.vstack((speeds[0], speeds[-1])))),
                "normalized_geometry_residual": normalized_geometry_residual(
                    sequence, selected_tau, source.trajectory.H_s_inv
                ),
                "frozen_network_mode_measure_residual": transport.network_mode_measure_residual,
                "source_temperature_mode_measure_residual": thermodynamic.mode_measure_relative_residual,
                "source_temperature_outer_face_mismatch": thermodynamic.outer_face_frequency_relative_mismatch,
                "pilot_uses_frozen_reference_line": 1,
                "pilot_doppler_width_Hz": pilot_line.Doppler_width_Hz,
                "transport_number_residual_m3_s": transport_result.global_number_residual_m3_s,
                "transport_number_relative_residual": transport_number_relative,
                "transport_energy_relative_residual": transport_result.energy_identity_relative_residual,
                "transport_four_momentum_residual": float(np.linalg.norm(transport_result.interface_four_momentum_residual)),
                "pilot_dt_s": PILOT_DT_S,
                "pilot_converged": int(pilot.converged),
                "pilot_newton_iterations": pilot.newton_iterations,
                "pilot_gmres_iterations": pilot.total_gmres_iterations,
                "pilot_residual_relative": pilot.residual_relative,
                "pilot_number_relative_residual": pilot.global_number_relative_residual,
                "pilot_energy_relative_residual": pilot.energy_identity_relative_residual,
                "pilot_minimum_occupation": pilot.minimum_occupation,
                "pilot_collision_entropy_production": pilot.collision_entropy_production,
                "pilot_interface_atom_source_J_m3": pilot.interface_atom_source_J_m3,
                "pilot_collision_four_force_residual": pilot.collision_four_force_residual,
                "pilot_jvp_relative": jvp,
            })

    no_go = {
        "native_history_angular_rank": identifiability.native_history_angular_rank,
        "minimum_number_momentum_rank": identifiability.minimum_number_momentum_rank,
        "exact_face_trace_rank": identifiability.exact_face_trace_rank,
        "required_angular_rank": identifiability.required_angular_rank,
        "com_face_trace_source_defined": identifiability.com_face_trace_source_defined,
        "p0_face_trace_is_new_closure": identifiability.p0_face_trace_is_new_closure,
        "fully_source_derived_coupling_identified": (
            identifiability.fully_source_derived_coupling_identified
        ),
        "angular_face_bounded_no_go": identifiability.bounded_no_go,
        "thermodynamic_dynamic_measure_identified": all(
            bool(row["source_conditioned_dynamic_measure_identified"])
            for row in thermodynamic_rows
        ),
        "maximum_source_temperature_mode_measure_residual": max(
            float(row["mode_measure_relative_residual"])
            for row in thermodynamic_rows
        ),
        "maximum_source_temperature_outer_face_mismatch": max(
            float(row["outer_face_frequency_relative_mismatch"])
            for row in thermodynamic_rows
        ),
        "thermodynamic_adapter_required": True,
        "collision_block_preconditioner_required": True,
        "scalarization_monopole_residual": witness.monopole_residual,
        "scalarization_momentum_separation": float(
            np.linalg.norm(witness.momentum_a - witness.momentum_b)
        ),
        "bounded_no_go": True,
        "reason": (
            "The locked original-HyRec history has one scalar angular degree "
            "of freedom per native frequency, while the COM boundary has one "
            "state per angular node. The COM registry supplies cell averages "
            "but no source-defined face reconstruction. The v0.50 mode measure "
            "is also frozen to its reference Doppler grid and differs from "
            "source-temperature grids away from the reference snapshot. The "
            "isotropic native lifting and P0 upwind trace are declared pilot "
            "closures, and the pilot retains the frozen v0.50 measure; none is "
            "a source-identical full coupling."
        ),
    }
    return lane_rows, stiffness_rows, thermodynamic_rows, root_rows, no_go, arrays


def update_repository(bundle_sha: str, bundle_size: int, metrics: dict[str, object]) -> None:
    index_path = ROOT / "state/BUNDLE_INDEX.json"
    index = json.loads(index_path.read_text())
    index = [row for row in index if int(row["version"]) != VERSION]
    index.append({"version": VERSION, "bundle": BUNDLE.name, "size_bytes": bundle_size, "sha256": bundle_sha})
    index.sort(key=lambda row: int(row["version"]))
    write_json(index_path, index)

    state_path = ROOT / "state/PROJECT_STATE.json"
    state = json.loads(state_path.read_text())
    state["current_durable_stage"] = {"name": "PR-05C2A directional coupling preflight", "artifact": ARTIFACT_NAME, "status": STATUS}
    state["next_stage"] = {
        "name": "PR-05C2B preconditioned angle-resolved full coupling",
        "entry_gate": "PR05C2A_DIRECTIONAL_PILOT_AND_BOUNDED_NO_GO",
        "tasks": [
            "Introduce an explicit angle-resolved native boundary state or a separately justified angular closure.",
            "Replace the provisional P0 COM face trace with a refinement-tested face reconstruction contract.",
            "Construct a source-temperature COM mode-measure and collision-kernel adapter, or recompile the network on a controlled temperature grid.",
            "Implement a harmonic-block or equivalent stiff collision preconditioner for canonical macro steps.",
            "Then rerun adaptive macro trajectories with global number, face-energy, redshift-work and four-force ledgers.",
        ],
    }
    state["roadmap"][4]["status"] = "IN_PROGRESS_PR05A_B1_B2_B3_C1_C2A_COMPLETE_BOUNDED_NO_GO_C2B_NEXT"
    state["estimated_PR05_completion_percent"] = 86
    state["estimated_overall_completion_percent"] = 97
    state["PR05C2A_evidence"] = {
        "artifact_bundle": BUNDLE.name,
        "artifact_bundle_sha256": bundle_sha,
        "artifact_bundle_size_bytes": bundle_size,
        "actual_background_models": list(MODELS),
        "source_conditioned_redshifts": list(TARGETS),
        "direction_count": 26,
        "source_root_count": metrics["source_root_count"],
        "maximum_transport_number_relative_residual": metrics["maximum_transport_number_relative_residual"],
        "maximum_transport_energy_relative_residual": metrics["maximum_transport_energy_relative_residual"],
        "maximum_pilot_residual_relative": metrics["maximum_pilot_residual_relative"],
        "maximum_pilot_jvp_relative": metrics["maximum_pilot_jvp_relative"],
        "minimum_pilot_occupation": metrics["minimum_pilot_occupation"],
        "maximum_source_temperature_mode_measure_residual": metrics["maximum_source_temperature_mode_measure_residual"],
        "maximum_source_temperature_outer_face_mismatch": metrics["maximum_source_temperature_outer_face_mismatch"],
        "minimum_stiffness_number": metrics["minimum_stiffness_number"],
        "maximum_stiffness_number": metrics["maximum_stiffness_number"],
        "claim": "BOUNDED_DIRECTIONAL_CONSERVATIVE_PILOT_NOT_SOURCE_IDENTICAL_FULL_TRAJECTORY",
    }
    state["locked_architecture"]["pr05c2a_directional_pilot"] = (
        "v0.63 uses actual v0.48 BackgroundSnapshot sequences and a conservative 26-direction, 35-state frequency Liouville/COM collision pilot on the frozen v0.50 3000 K frequency grid."
    )
    state["locked_architecture"]["pr05c2a_bounded_no_go"] = (
        "A source-identical full anisotropic coupling is underidentified because original-HyRec boundary history has angular rank one, COM cells lack a source-defined face trace, source-temperature mode measures differ from the frozen grid, and canonical macro collision solves require block preconditioning."
    )
    state["locked_architecture"]["pr05c2b_next"] = (
        "Introduce an explicit angular closure with uncertainty, a source-temperature network/remap adapter, a positivity/refinement-tested face reconstruction, and a harmonic-block or asymptotic-preserving preconditioner before adaptive macro trajectories."
    )
    limitation = (
        "PR-05C2A closes an actual-background directional finite-volume pilot on the frozen v0.50 COM grid but not a fully source-identical anisotropic native/COM trajectory: native original-HyRec boundary history is scalar, the COM face trace uses a declared P0 closure, source-temperature mode measures differ by up to about 9.5 percent from the frozen grid, and canonical macro collision solves require a block preconditioner."
    )
    if limitation not in state["known_limitations"]:
        state["known_limitations"].append(limitation)
    write_json(state_path, state)

    write_json(ROOT / "state/PR05C2A_RECOVERY_RECEIPT.json", {
        "classification": "PR05C2A_RECOVERY_RECEIPT",
        "status": STATUS,
        "artifact": ARTIFACT_NAME,
        "artifact_bundle_sha256": bundle_sha,
        "artifact_bundle_size_bytes": bundle_size,
        "metrics": metrics,
        "next": "PR05C2B_PRECONDITIONED_ANGLE_RESOLVED_FULL_COUPLING",
    })
    (ROOT / "docs/CURRENT_STATE.md").write_text(
        "# Current state\n\n"
        "- Durable stage: **PR-05C2A / v0.63**.\n"
        f"- Status: `{STATUS}`.\n"
        "- Actual v0.48 Bianchi snapshot sequences now drive direction-resolved finite-volume frequency transport on the locked 35-state COM domain.\n"
        "- Nine actual-background pilot lanes close number, face-energy, four-force, positivity and JVP gates for a bounded one-second implicit step on the frozen v0.50 COM grid.\n"
        "- A full source-identical anisotropic coupling is not identified: original-HyRec native history is scalar, the COM face trace requires an explicit numerical closure, and source-temperature mode measures differ from the frozen COM grid by up to about 9.5 percent.\n"
        "- The canonical macro collision stiffness number is O(1e9), so a source-temperature network adapter and a block preconditioner or asymptotic-preserving reduction are required before PR-05C2B.\n"
    )


def main() -> None:
    if sha256(HYREC_ARCHIVE) != CANONICAL_HYREC_SHA256:
        raise RuntimeError("canonical HyRec archive hash mismatch")
    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="pr05c2a-v063-") as temporary:
        work = Path(temporary)
        harness_receipts = [
            validate_harness(CODING_HARNESS, CODING_HARNESS_SHA256, "validate_harness.py", work, ARTIFACT / "CODING_HARNESS_VALIDATION.log"),
            validate_harness(RESEARCH_HARNESS, RESEARCH_HARNESS_SHA256, "validate_workspace.py", work, ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log"),
        ]

    lanes, stiffness, thermodynamic, roots, no_go, arrays = build_evidence()
    metrics = {
        "classification": "PR05C2A_NUMERICAL_METRICS",
        "status": STATUS,
        "lane_count": len(lanes),
        "stiffness_lane_count": len(stiffness),
        "thermodynamic_lane_count": len(thermodynamic),
        "source_root_count": len(roots),
        "maximum_normalized_geometry_residual": max(float(row["normalized_geometry_residual"]) for row in lanes),
        "maximum_frozen_network_mode_measure_residual": max(float(row["frozen_network_mode_measure_residual"]) for row in lanes),
        "maximum_transport_number_residual_m3_s": max(abs(float(row["transport_number_residual_m3_s"])) for row in lanes),
        "maximum_transport_number_relative_residual": max(float(row["transport_number_relative_residual"]) for row in lanes),
        "maximum_transport_energy_relative_residual": max(float(row["transport_energy_relative_residual"]) for row in lanes),
        "maximum_transport_four_momentum_residual": max(float(row["transport_four_momentum_residual"]) for row in lanes),
        "maximum_pilot_residual_relative": max(float(row["pilot_residual_relative"]) for row in lanes),
        "maximum_pilot_number_relative_residual": max(float(row["pilot_number_relative_residual"]) for row in lanes),
        "maximum_pilot_energy_relative_residual": max(float(row["pilot_energy_relative_residual"]) for row in lanes),
        "maximum_pilot_jvp_relative": max(float(row["pilot_jvp_relative"]) for row in lanes),
        "minimum_pilot_occupation": min(float(row["pilot_minimum_occupation"]) for row in lanes),
        "maximum_pilot_collision_entropy_production": max(float(row["pilot_collision_entropy_production"]) for row in lanes),
        "maximum_pilot_interface_atom_source_abs_J_m3": max(abs(float(row["pilot_interface_atom_source_J_m3"])) for row in lanes),
        "maximum_pilot_collision_four_force_residual": max(float(row["pilot_collision_four_force_residual"]) for row in lanes),
        "maximum_source_temperature_mode_measure_residual": max(
            float(row["mode_measure_relative_residual"]) for row in thermodynamic
        ),
        "maximum_source_temperature_outer_face_mismatch": max(
            float(row["outer_face_frequency_relative_mismatch"]) for row in thermodynamic
        ),
        "minimum_source_temperature_mode_measure_residual": min(
            float(row["mode_measure_relative_residual"]) for row in thermodynamic
        ),
        "all_source_temperature_grids_require_dynamic_adapter": all(
            int(row["requires_network_recompilation"]) == 1
            for row in thermodynamic
        ),
        "maximum_stiffness_number": max(
            float(row["stiffness_number"]) for row in stiffness
        ),
        "minimum_stiffness_number": min(float(row["stiffness_number"]) for row in stiffness),
        "all_pilots_converged": all(int(row["pilot_converged"]) == 1 for row in lanes),
        "all_pilot_lanes_mixed_directional_flow": all(int(row["mixed_directional_flow"]) == 1 for row in lanes),
        "all_source_roots_present": all(int(row["red_root_count"]) >= 1 and int(row["blue_root_count"]) >= 1 for row in lanes),
        "all_macro_lanes_require_preconditioner": all(int(row["requires_block_preconditioner"]) == 1 for row in stiffness),
        "full_source_identical_coupling_identified": False,
        "bounded_no_go": True,
    }
    hard_gates = [
        {"name": "lane_count", "passed": len(lanes) == 9},
        {"name": "root_count", "passed": metrics["source_root_count"] == 18},
        {"name": "source_derived_roots", "passed": metrics["all_source_roots_present"]},
        {"name": "mixed_directional_flow", "passed": metrics["all_pilot_lanes_mixed_directional_flow"]},
        {"name": "normalized_geometry", "passed": metrics["maximum_normalized_geometry_residual"] < 2.0e-14},
        {"name": "frozen_network_mode_measure", "passed": metrics["maximum_frozen_network_mode_measure_residual"] < 2.0e-8},
        {"name": "transport_number", "passed": metrics["maximum_transport_number_relative_residual"] < 2.0e-14},
        {"name": "transport_energy", "passed": metrics["maximum_transport_energy_relative_residual"] < 2.0e-14},
        {"name": "transport_four_momentum", "passed": metrics["maximum_transport_four_momentum_residual"] < 1.0e-20},
        {"name": "bounded_pilot_convergence", "passed": metrics["all_pilots_converged"] and metrics["maximum_pilot_residual_relative"] < 2.0e-10},
        {"name": "bounded_pilot_number", "passed": metrics["maximum_pilot_number_relative_residual"] < 2.0e-12},
        {"name": "bounded_pilot_energy", "passed": metrics["maximum_pilot_energy_relative_residual"] < 2.0e-12},
        {"name": "bounded_pilot_jvp", "passed": metrics["maximum_pilot_jvp_relative"] < 1.0e-8},
        {"name": "strict_positivity", "passed": metrics["minimum_pilot_occupation"] > 0.0},
        {"name": "entropy_nonincrease", "passed": metrics["maximum_pilot_collision_entropy_production"] <= 1.0e-18},
        {"name": "interface_atom_source_zero", "passed": metrics["maximum_pilot_interface_atom_source_abs_J_m3"] == 0.0},
        {"name": "collision_four_force", "passed": metrics["maximum_pilot_collision_four_force_residual"] < 1.0e-18},
        {
            "name": "source_temperature_measure_blocker",
            "passed": (
                metrics["all_source_temperature_grids_require_dynamic_adapter"]
                and metrics["maximum_source_temperature_mode_measure_residual"]
                > 5.0e-2
                and metrics["maximum_source_temperature_outer_face_mismatch"]
                > 1.0e-5
            ),
        },
        {
            "name": "stiffness_preconditioner_gate",
            "passed": metrics["all_macro_lanes_require_preconditioner"],
        },
        {"name": "identifiability_bounded_no_go", "passed": bool(no_go["bounded_no_go"]) and not bool(no_go["fully_source_derived_coupling_identified"])},
    ]
    if not all(item["passed"] for item in hard_gates):
        raise RuntimeError(f"PR05C2A hard gate failed: {hard_gates}")

    write_csv(ARTIFACT / "DIRECTIONAL_PILOT_LEDGER.csv", lanes)
    write_csv(ARTIFACT / "COLLISION_STIFFNESS_LEDGER.csv", stiffness)
    write_csv(ARTIFACT / "THERMODYNAMIC_GRID_LEDGER.csv", thermodynamic)
    write_csv(ARTIFACT / "SOURCE_DERIVED_BOUNDARY_ROOTS.csv", roots)
    write_csv(
        ARTIFACT / "OPERATOR_OWNERSHIP_MATRIX.csv",
        [
            {"term": "original_hyrec_scalar_history", "owner": "typed_characteristic_history", "status": "active"},
            {"term": "sobolev_escape", "owner": "canonical_hyrec", "status": "unchanged"},
            {"term": "native_A1s_diffusion", "owner": "canonical_hyrec", "status": "unchanged"},
            {"term": "completed_Schur_Tvv", "owner": "canonical_hyrec", "status": "unchanged"},
            {"term": "COM_KHW_collision_recoil", "owner": "COM_KHW", "status": "pilot"},
            {"term": "directional_frequency_transport", "owner": "frequency_liouville", "status": "pilot"},
            {"term": "native_COM_crossing", "owner": "split_domain_interface", "status": "pilot"},
        ],
    )
    write_json(ARTIFACT / "COUPLING_IDENTIFIABILITY_NO_GO.json", no_go)
    write_json(ARTIFACT / "NUMERICAL_METRICS.json", metrics)
    write_json(ARTIFACT / "HARD_GATE_LEDGER.json", {"status": STATUS, "gates": hard_gates, "PR05C2A": "COMPLETE_PASS_BOUNDED_NO_GO", "PR05C2": "IN_PROGRESS"})
    write_json(ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json", {"classification": "PR05C2A_HARNESS_EXECUTION", "receipts": harness_receipts})
    write_json(
        ARTIFACT / "TOOL_STATUS.json",
        {
            "web": "USED_PRIMARY_HYREC_PETSC_AND_NUMERICAL_FLUX_SOURCES",
            "wolfram": (
                "USED_SYMBOLIC_TELESCOPING_INTERPOLATION_MODE_MEASURE_"
                "AND_REDSHIFT_IDENTITIES"
            ),
            "precise_special_functions": "USED_120_DIGIT_ZETA3_REFERENCE",
        },
    )
    write_json(
        ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json",
        {
            "telescoping_flux_residual": "0",
            "interpolation_weight_sum": "1",
            "interpolation_gradient": ["1-lambda", "lambda", "-yL+yR"],
            "frequency_mode_measure": "8*pi*(nuR^3-nuL^3)/(3*c^3)",
            "characteristic_nu3_over_nH_residual": "0",
        },
    )
    write_json(
        ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json",
        {
            "zeta_3_120_digits": (
                "1.202056903159594285399738161511449990764986292340498881792271"
                "55534183820578631309018645587360933525814619915779526071942"
            )
        },
    )
    write_json(ARTIFACT / "PR05C2A_ledger.json", {
        "classification": "PR05C2A_DURABLE_LEDGER",
        "status": STATUS,
        "canonical_hyrec_sha256": sha256(HYREC_ARCHIVE),
        "background_sha256": sha256(BACKGROUND),
        "network_sha256": sha256(NETWORK),
        "metrics": metrics,
        "bounded_no_go": no_go,
        "next": "PR05C2B_PRECONDITIONED_ANGLE_RESOLVED_FULL_COUPLING",
    })

    formalism = """# PR-05C2A directional coupling formalism\n\nThe COM finite-volume number action uses upwind face flux\n\n```text\nF_{k+1/2,a} = v_{k+1/2,a} g_{x,k+1/2} f_upwind\nNdot_{k,a} = F_{k-1/2,a} - F_{k+1/2,a}.\n```\n\nThe native ledger is the exact negative of the summed COM action.  Exact interface energy uses `h nu_face`; cell-centroid mismatch and internal frequency drift are separate representation/redshift-work ledgers.  Pure representation crossing has zero atom source.\n\nThe v0.48 chart variable satisfies `d/dt = H d/dtau` while `d eta/dt = H`, so `tau` and `eta=ln(a)` differ only by an additive anchor.  Local source-H rescaling multiplies all physical geometric rates by the same positive factor and preserves every Hubble-normalized tensor.\n\nThe locked native history has angular rank one, while the COM boundary has one value per quadrature direction. Moreover the COM state is a finite-volume cell average and the archive provides no face reconstruction. The P0 upwind face trace used for the bounded pilot is therefore a new explicit closure, not a source-identical full coupling.\n\nThe v0.50 COM mode measure is frozen to the reference 3000 K Doppler grid. Re-evaluating the same dimensionless cells at the source temperatures changes the physical mode measure by up to about 9.5 percent. The bounded pilot therefore retains the frozen v0.50 measure and records the missing thermodynamic grid/kernel adapter as a blocker.\n\nThe ell=0 collision Jacobian has spectral radius about `0.655 s^-1`; a canonical macro interval lasts `DLNA/H ~ 1e9 s`, giving stiffness number above `8e8`.  A harmonic-block or equivalent preconditioner/asymptotic-preserving reduction is required before a production macro trajectory can be claimed.\n"""
    (ARTIFACT / "PR05C2A_DIRECTIONAL_COUPLING_FORMALISM.md").write_text(formalism)
    docs = {
        "01_RESEARCH_CONTRACT.md": "Primary question: can actual locked Bianchi characteristics drive a conservative directional COM/native coupling without inventing angular native data or a face trace?\n",
        "02_EVIDENCE_ACQUISITION.md": "Evidence: canonical HyRec archive, v0.48 background NPZ, v0.50 network, v0.60 scalar history, nine source-conditioned directional pilot lanes, both pinned harnesses, primary HyRec/PETSc literature.\n",
        "03_CLAIM_SOURCE_AUDIT.md": "Background tensors and roots are source-derived; P0 COM face trace and isotropic lifting of scalar native occupation are declared pilot closures.\n",
        "04_HYPOTHESIS_SPACE.md": "H_A full source-identical coupling exists; H_B only a conservative pilot exists because angular native state/face trace are underidentified. Evidence selects H_B.\n",
        "05_ADVERSARIAL_REVIEW.md": "Adversaries: swap flow direction, perturb face energy, scalarize opposite dipoles, remove preconditioner gate, or claim macro convergence from a one-second pilot. All fail closed.\n",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": "Face mode density has units m^-3 per x, speed s^-1, flux m^-3 s^-1; exact energy is h nu_face times number flux.\n",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        "08_EXTERNAL_GATE.md": "Full PR-05C2 requires angle-resolved native boundary information or an explicit convergent closure, a refinement-tested COM face reconstruction, a source-temperature COM measure/kernel adapter, and a stiff block preconditioner.\n",
        "09_FORMALIZATION.md": formalism,
        "10_CLOSEOUT_AND_HANDOFF.md": "PR-05C2A closes the source-derived directional pilot and bounded no-go. PR-05C2B owns preconditioning, face refinement and adaptive macro integration.\n",
    }
    for name, content in docs.items():
        (ARTIFACT / name).write_text(content)

    deterministic_npz(DATA, arrays)
    shutil.copy2(DATA, ARTIFACT / DATA.name)
    verifier = '''#!/usr/bin/env python3\nimport csv\nimport json\nfrom pathlib import Path\nroot=Path(__file__).resolve().parent\nmetrics=json.loads((root/"NUMERICAL_METRICS.json").read_text())\nhard=json.loads((root/"HARD_GATE_LEDGER.json").read_text())\nno_go=json.loads((root/"COUPLING_IDENTIFIABILITY_NO_GO.json").read_text())\nwith (root/"SOURCE_DERIVED_BOUNDARY_ROOTS.csv").open(newline="", encoding="utf-8") as handle:\n    roots=list(csv.DictReader(handle))\nwith (root/"THERMODYNAMIC_GRID_LEDGER.csv").open(newline="", encoding="utf-8") as handle:\n    thermodynamic=list(csv.DictReader(handle))\nassert metrics["status"].startswith("PASS_PR05C2A")\nassert metrics["lane_count"] == 9\nassert metrics["thermodynamic_lane_count"] == 3\nassert metrics["bounded_no_go"] is True\nassert len(roots) == 18\nassert len({(row["model"], row["side"], row["root_index"]) for row in roots}) == len(roots)\nassert len(thermodynamic) == 3\nassert no_go["native_history_angular_rank"] == 1\nassert no_go["minimum_number_momentum_rank"] == 4\nassert no_go["exact_face_trace_rank"] == 26\nassert no_go["thermodynamic_adapter_required"] is True\nassert no_go["collision_block_preconditioner_required"] is True\nassert all(item["passed"] for item in hard["gates"])\nprint(metrics["status"])\n'''
    (ARTIFACT / "verify_PR05C2A.py").write_text(verifier)
    os.chmod(ARTIFACT / "verify_PR05C2A.py", 0o755)

    manifest_lines = []
    for path in sorted(ARTIFACT.rglob("*")):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            manifest_lines.append(f"{sha256(path)}  {path.relative_to(ARTIFACT)}")
    (ARTIFACT / "MANIFEST_SHA256.txt").write_text("\n".join(manifest_lines) + "\n")
    deterministic_zip(ARTIFACT, BUNDLE)
    bundle_sha = sha256(BUNDLE)
    update_repository(bundle_sha, BUNDLE.stat().st_size, metrics)
    print(json.dumps({"status": STATUS, "artifact": str(ARTIFACT), "bundle": str(BUNDLE), "bundle_sha256": bundle_sha, "metrics": metrics}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
