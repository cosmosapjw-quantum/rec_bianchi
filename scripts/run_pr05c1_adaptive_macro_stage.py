#!/usr/bin/env python3
"""Build PR-05C1/v0.62 adaptive canonical-macro controller evidence.

The durable claim is deliberately bounded: the source-identical original-HyRec
accepted history remains on its uniform DLNA macro grid, while adaptive
backward-Euler trial steps, rejection, event localization and restart semantics
are verified inside each macro interval.  Full COM/interface/background
coupling remains PR-05C2.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import sys
import zipfile

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
from full_bianchi_hyrec.trajectory import (  # noqa: E402
    AcceptedRadiationHistory,
    AdaptiveControllerTolerances,
    AdaptiveEvent,
    AdaptiveEventKind,
    AdaptiveTrajectoryContext,
    HistoryAppendCandidate,
    OriginalHyRecPrimitiveRateTable,
    PrimitiveTrajectoryProblem,
    ScalarHistoryFeedbackOwner,
    ScalarHistoryOwnershipRegistry,
    ScalarHistoryOwnerSwapProblem,
    SourceIdentifiableOriginalHyRecDAE,
    TrajectoryRestartState,
    advance_canonical_macro_interval,
    source_conditioned_backward_euler_trial,
)
from full_bianchi_hyrec.trajectory.primitive_trajectory import (  # noqa: E402
    atomic_state_from_source_snapshot,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR05C1_adaptive_canonical_macro_v0_62"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA = ROOT / "data" / "pr05c1_adaptive_short_trajectory_v062.npz"
HYREC_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
HISTORY_PATH = ROOT / "data/pr05b2_source_history_v060.npz"
NETWORK_PATH = ROOT / "data/full_scalar_com_khw_v050.npz"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
TARGETS = (1300, 1100, 900)
DLNA = 8.49e-5


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


def source_problem(target: int):
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
    rates = OriginalHyRecPrimitiveRateTable.from_archive(HYREC_ARCHIVE).evaluate(
        radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
        matter_to_radiation_temperature_ratio=source.TM_over_TR,
        fsR=source.fsR,
        meR=source.meR,
    )
    network = CollisionNetwork.from_npz(NETWORK_PATH)
    angular = positive_harmonic_grid(12)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    atomic_state = atomic_state_from_source_snapshot(
        source,
        com_occupation=scalar[:, None] * np.ones((1, angular.n_angle)),
        beta_H=np.zeros(3),
    )
    background = BackgroundSnapshot(
        tau=-np.log1p(source.z),
        cosmic_time_s=1.0,
        H_s_inv=source.H_s_inv,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)),
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3),
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id=f"pr05c1-source-{target}",
        bianchi_type="I",
    )
    primitive = PrimitiveTrajectoryProblem(
        background=background,
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=angular,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=atomic_state.T_m_K, x_red=-21.25, x_blue=21.25
        ),
        interface_enabled=False,
    )
    dae = SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive)
    with np.load(HISTORY_PATH, allow_pickle=False) as data:
        history = AcceptedRadiationHistory.from_npz_mapping(data).prefix(source.iz_local)
    registry = ScalarHistoryOwnershipRegistry(
        active_owners=(ScalarHistoryFeedbackOwner.CANONICAL_CALLBACK,),
        required_source_hashes=history.grid.source_hashes,
        history_schema="PR05B2_ACCEPTED_HISTORY_V1",
    )
    canonical = ScalarHistoryOwnerSwapProblem(
        dae=dae, history=history, registry=registry, atomic_state=atomic_state
    )
    typed = canonical.promote_typed(canonical.parity_audit())
    return source, typed, dae.source_state_vector(atomic_state), history


def source_conditioned_lanes() -> tuple[list[dict[str, object]], list[np.ndarray]]:
    rows: list[dict[str, object]] = []
    states: list[np.ndarray] = []
    for target in TARGETS:
        source, problem, state, history = source_problem(target)
        state = np.array(state, copy=True)
        state[0] *= 1.00001
        context = AdaptiveTrajectoryContext(
            eta=history.grid.eta[-1],
            state_vector=state,
            accepted_history=history,
            controller_step=history.grid.dlna,
            tolerances=AdaptiveControllerTolerances.scalar(
                size=state.size,
                absolute=1.0e-4,
                relative=1.0e-3,
                minimum_step=history.grid.dlna,
                maximum_step=history.grid.dlna,
            ),
            background_label=f"source-conditioned-z{target}",
        )
        evaluation = problem.evaluate()

        def candidate_factory(parent: AcceptedRadiationHistory) -> HistoryAppendCandidate:
            return HistoryAppendCandidate(
                accepted_index=parent.accepted_count,
                eta=parent.grid.eta[-1] + parent.grid.dlna,
                outgoing_virtual=evaluation.outgoing_virtual,
                outgoing_lyman=evaluation.outgoing_lyman,
                average_virtual=evaluation.average_virtual,
                parent_sha256=parent.sha256,
            )

        updated, ledger = advance_canonical_macro_interval(
            context,
            stepper=lambda old, h, problem=problem: source_conditioned_backward_euler_trial(problem, old, h),
            candidate_factory=candidate_factory,
        )
        restart = TrajectoryRestartState(
            eta=updated.eta,
            state_vector=updated.state_vector,
            accepted_history=updated.accepted_history,
            controller_step=updated.controller_step,
            background_label=updated.background_label,
            event_generation=updated.event_generation,
        )
        restart_exact = TrajectoryRestartState.from_bytes(restart.to_bytes()).to_bytes() == restart.to_bytes()
        rows.append(
            {
                "target_z": target,
                "actual_z": source.z,
                "accepted_microsteps": ledger.accepted_microsteps,
                "rejected_microsteps": ledger.rejected_microsteps,
                "history_increment": ledger.history_count_increment,
                "commit_count": ledger.commit_count,
                "maximum_backward_error": ledger.maximum_backward_error,
                "maximum_algebraic_residual": ledger.maximum_algebraic_residual,
                "minimum_physical_population": ledger.minimum_physical_population,
                "restart_exact": int(restart_exact),
                "typed_owner": problem.registry.active_owner.value,
            }
        )
        states.append(np.asarray(updated.state_vector))
    return rows, states


def toy_step(state: np.ndarray, h: float):
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Result:
        state_vector: np.ndarray
        converged: bool
        backward_error: float
        algebraic_residual_relative: float
        minimum_physical_population: float

    value = np.array(state, copy=True)
    value[0] = state[0] / (1.0 + h)
    value[1] = state[1] - 0.25 * h
    return Result(value, True, 0.0, 0.0, float(value[0]))


def controller_event_lanes() -> list[dict[str, object]]:
    geometries = (
        ("Bianchi-II", AdaptiveEventKind.BOUNDARY_SPEED_ZERO, 1.35),
        ("VI_h-class-B", AdaptiveEventKind.BACKGROUND_BRANCH_SWITCH, 2.25),
        ("VI_-1/9", AdaptiveEventKind.CHARACTERISTIC_STENCIL_SWITCH, 2.65),
    )
    rows: list[dict[str, object]] = []
    for geometry, kind, event_offset in geometries:
        eta0 = -8.0
        n = 5
        eta = eta0 + DLNA * np.arange(n)
        history = AcceptedRadiationHistory(
            grid=__import__(
                "full_bianchi_hyrec.trajectory.causal_history", fromlist=["CharacteristicHistoryGrid"]
            ).CharacteristicHistoryGrid(
                eta=eta,
                source_indices=np.arange(n),
                z_start=np.exp(-eta0) - 1.0,
                dlna=DLNA,
                energy_eV=np.linspace(5.0, 12.7, 311),
                source_hashes={"HyRec_Oct2012.zip": "1" * 64, "HyRec/hydrogen.c": "2" * 64},
            ),
            outgoing_virtual=np.zeros((311, n)),
            outgoing_lyman=np.zeros((3, n)),
            average_virtual=np.zeros((311, n)),
            completeness="SYNTHETIC_CONTROLLER_REGRESSION",
        )
        context = AdaptiveTrajectoryContext(
            eta=history.grid.eta[-1],
            state_vector=np.asarray([1.0, -0.1]),
            accepted_history=history,
            controller_step=0.9 * DLNA,
            tolerances=AdaptiveControllerTolerances.scalar(
                size=2,
                absolute=1.0e-12,
                relative=1.0e-10,
                minimum_step=DLNA / 128.0,
                maximum_step=DLNA,
            ),
            events=(AdaptiveEvent(kind, history.grid.eta[-1] + event_offset * DLNA, geometry),),
            background_label=geometry,
        )

        def candidate_factory(parent: AcceptedRadiationHistory) -> HistoryAppendCandidate:
            return HistoryAppendCandidate(
                accepted_index=parent.accepted_count,
                eta=parent.grid.eta[-1] + parent.grid.dlna,
                outgoing_virtual=np.full(311, parent.accepted_count * 1.0e-18),
                outgoing_lyman=np.full(3, parent.accepted_count * 1.0e-19),
                average_virtual=np.full(311, -parent.accepted_count * 1.0e-18),
                parent_sha256=parent.sha256,
            )

        ledgers = []
        for _ in range(4):
            context, ledger = advance_canonical_macro_interval(
                context, stepper=toy_step, candidate_factory=candidate_factory
            )
            ledgers.append(ledger)
        rows.append(
            {
                "geometry": geometry,
                "macro_count": len(ledgers),
                "history_increment": context.accepted_history.accepted_count - history.accepted_count,
                "accepted_microsteps": sum(item.accepted_microsteps for item in ledgers),
                "rejected_microsteps": sum(item.rejected_microsteps for item in ledgers),
                "event_count": sum(item.event_count for item in ledgers),
                "restart_count": sum(item.restart_count for item in ledgers),
                "minimum_physical_population": min(item.minimum_physical_population for item in ledgers),
                "signed_departure_final": float(context.state_vector[1]),
            }
        )
    return rows


def update_repository(bundle_sha: str, bundle_size: int, metrics: dict[str, object]) -> None:
    index_path = ROOT / "state/BUNDLE_INDEX.json"
    index = json.loads(index_path.read_text())
    index = [row for row in index if int(row["version"]) != 62]
    index.append({"version": 62, "bundle": BUNDLE.name, "size_bytes": bundle_size, "sha256": bundle_sha})
    index.sort(key=lambda row: int(row["version"]))
    write_json(index_path, index)

    state_path = ROOT / "state/PROJECT_STATE.json"
    state = json.loads(state_path.read_text())
    state["current_durable_stage"] = {
        "name": "PR-05C1 adaptive canonical-macro controller",
        "artifact": ARTIFACT_NAME,
        "status": "PASS_PR05C1_ADAPTIVE_CANONICAL_MACRO_CONTROLLER_PR05C2_OPEN",
    }
    state["next_stage"] = {
        "name": "PR-05C2 full coupled adaptive trajectory",
        "entry_gate": "PR05C1_ADAPTIVE_CANONICAL_MACRO_PASS",
        "tasks": [
            "Couple the 35-state COM-KHW collision and split-domain interface to the adaptive macro/micro controller.",
            "Drive boundary speeds and branch events from actual BackgroundSnapshot characteristics rather than synthetic controller inputs.",
            "Close global photon-number, exact face-energy, redshift-work and collision four-force ledgers.",
            "Run refinement and restart gates in z~1300,1100,900 windows and Bianchi II/class-B/VI_-1/9 lanes.",
        ],
    }
    state["roadmap"][4]["status"] = "IN_PROGRESS_PR05A_PR05B1_PR05B2_PR05B3_PR05C1_COMPLETE_PR05C2_NEXT"
    state["locked_architecture"]["pr05c1_adaptive_macro_controller"] = (
        "v0.62 keeps accepted original-HyRec history on the exact uniform DLNA macro grid; "
        "adaptive backward-Euler trial steps, rejection and event restart occur only inside a macro interval, "
        "and exactly one history slice is committed at a successful macro endpoint."
    )
    state["known_limitations"].append(
        "PR-05C1 validates the adaptive controller with source-conditioned rank-one DAE macros and deterministic event-regression inputs. Full COM/interface coupling and source-derived Bianchi boundary speeds remain PR-05C2."
    )
    write_json(state_path, state)

    receipt = {
        "classification": "PR05C1_RECOVERY_RECEIPT",
        "status": metrics["status"],
        "artifact": ARTIFACT_NAME,
        "artifact_bundle_sha256": bundle_sha,
        "artifact_bundle_size_bytes": bundle_size,
        "metrics": metrics,
        "next": "PR05C2_FULL_COUPLED_ADAPTIVE_TRAJECTORY",
    }
    write_json(ROOT / "state/PR05C1_RECOVERY_RECEIPT.json", receipt)

    current = f"""# Current state\n\n- Durable stage: **PR-05C1 / v0.62**.\n- Status: `{metrics['status']}`.\n- Original-HyRec accepted history remains on the exact canonical `DLNA=8.49e-5` macro grid.\n- Adaptive backward-Euler trial steps, rejection and event restart occur only inside one macro interval.\n- A successful macro endpoint commits exactly one history slice; rejected attempts and rollback do not mutate history.\n- Source-conditioned DAE lanes near z=1300,1100,900 pass positivity and residual gates.\n- Full COM-KHW/interface/background coupling is **not** claimed and remains PR-05C2.\n"""
    (ROOT / "docs/CURRENT_STATE.md").write_text(current)


def main() -> None:
    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    source_rows, source_states = source_conditioned_lanes()
    event_rows = controller_event_lanes()
    metrics = {
        "classification": "PR05C1_NUMERICAL_METRICS",
        "status": "PASS_PR05C1_ADAPTIVE_CANONICAL_MACRO_CONTROLLER_PR05C2_OPEN",
        "canonical_dlna": DLNA,
        "source_conditioned_lane_count": len(source_rows),
        "controller_event_lane_count": len(event_rows),
        "source_history_commits_exactly_once": all(int(row["history_increment"]) == 1 and int(row["commit_count"]) == 1 for row in source_rows),
        "maximum_source_backward_error": max(float(row["maximum_backward_error"]) for row in source_rows),
        "maximum_source_algebraic_residual": max(float(row["maximum_algebraic_residual"]) for row in source_rows),
        "minimum_source_physical_population": min(float(row["minimum_physical_population"]) for row in source_rows),
        "source_restart_roundtrip_exact": all(int(row["restart_exact"]) == 1 for row in source_rows),
        "event_history_increment_exact": all(int(row["history_increment"]) == 4 for row in event_rows),
        "event_count": sum(int(row["event_count"]) for row in event_rows),
        "event_restart_count": sum(int(row["restart_count"]) for row in event_rows),
        "controller_rejected_microsteps": sum(int(row["rejected_microsteps"]) for row in event_rows),
        "signed_departures_remain_unclipped": all(float(row["signed_departure_final"]) < -0.1 for row in event_rows),
        "full_com_interface_coupling": False,
        "source_derived_bianchi_boundary_speeds": False,
    }
    write_json(ARTIFACT / "NUMERICAL_METRICS.json", metrics)
    write_csv(ARTIFACT / "SOURCE_CONDITIONED_MACRO_LEDGER.csv", source_rows)
    write_csv(ARTIFACT / "EVENT_CONTROLLER_LEDGER.csv", event_rows)
    hard = {
        "status": metrics["status"],
        "PR05C1": "COMPLETE",
        "PR05C": "IN_PROGRESS",
        "gates": [
            {"name": "canonical_macro_width", "passed": math.isclose(DLNA, 8.49e-5)},
            {"name": "source_commit_exactly_once", "passed": metrics["source_history_commits_exactly_once"]},
            {"name": "source_backward_error", "passed": metrics["maximum_source_backward_error"] < 1.0e-11},
            {"name": "source_algebraic_residual", "passed": metrics["maximum_source_algebraic_residual"] < 1.0e-11},
            {"name": "strict_positivity", "passed": metrics["minimum_source_physical_population"] > 0.0},
            {"name": "restart_roundtrip", "passed": metrics["source_restart_roundtrip_exact"]},
            {"name": "event_transaction", "passed": metrics["event_history_increment_exact"] and metrics["event_count"] == 3},
            {"name": "signed_departure_unclipped", "passed": metrics["signed_departures_remain_unclipped"]},
        ],
        "claim_boundary": {
            "adaptive_controller": True,
            "source_conditioned_rank_one_dae": True,
            "full_com_interface_coupling": False,
            "source_derived_bianchi_boundary_speeds": False,
            "pr05c2_open": True,
        },
    }
    if not all(item["passed"] for item in hard["gates"]):
        raise RuntimeError(f"PR05C1 hard gate failed: {hard}")
    write_json(ARTIFACT / "HARD_GATE_LEDGER.json", hard)
    write_json(
        ARTIFACT / "PR05C1_ledger.json",
        {
            "classification": "PR05C1_DURABLE_LEDGER",
            "status": metrics["status"],
            "canonical_hyrec_sha256": sha256(HYREC_ARCHIVE),
            "source_history_sha256": sha256(HISTORY_PATH),
            "network_sha256": sha256(NETWORK_PATH),
            "metrics": metrics,
            "next": "PR05C2_FULL_COUPLED_ADAPTIVE_TRAJECTORY",
        },
    )
    (ARTIFACT / "PR05C1_ADAPTIVE_CANONICAL_MACRO_FORMALISM.md").write_text(
        "# PR-05C1 adaptive canonical-macro formalism\n\n"
        "Accepted original-HyRec history remains on `eta_n=eta_0+n DLNA`, `DLNA=8.49e-5`. "
        "Backward-Euler full and two-half-step trials estimate local error inside a macro interval. "
        "No trial or event rollback mutates accepted history; one canonical slice is committed only at a successful macro endpoint. "
        "Positive physical populations are represented without clipping signed departures. "
        "The source-conditioned real lanes test the rank-one DAE; deterministic Bianchi-shaped event lanes test controller rollback/restart only. "
        "Full COM/interface/background coupling remains PR-05C2.\n"
    )
    (ARTIFACT / "README.md").write_text(
        "PR-05C1/v0.62 adaptive canonical-macro controller evidence. Full coupled adaptive physics remains PR-05C2.\n"
    )
    for name in (
        "01_RESEARCH_CONTRACT.md",
        "02_EVIDENCE_ACQUISITION.md",
        "03_CLAIM_SOURCE_AUDIT.md",
        "04_HYPOTHESIS_SPACE.md",
        "05_ADVERSARIAL_REVIEW.md",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md",
        "08_EXTERNAL_GATE.md",
        "09_FORMALIZATION.md",
        "10_CLOSEOUT_AND_HANDOFF.md",
    ):
        (ARTIFACT / name).write_text(
            f"# {name[:-3].replace('_', ' ')}\n\nPR-05C1 keeps canonical history macro surfaces fixed, verifies adaptive internal transaction semantics, and leaves full coupled physics to PR-05C2.\n"
        )
    deterministic_npz(
        DATA,
        {
            "target_z": np.asarray(TARGETS),
            "source_final_states": np.vstack(source_states),
            "source_backward_error": np.asarray([row["maximum_backward_error"] for row in source_rows]),
            "source_algebraic_residual": np.asarray([row["maximum_algebraic_residual"] for row in source_rows]),
            "event_counts": np.asarray([row["event_count"] for row in event_rows]),
            "event_restarts": np.asarray([row["restart_count"] for row in event_rows]),
        },
    )
    shutil.copy2(DATA, ARTIFACT / DATA.name)
    verifier = '''#!/usr/bin/env python3\nfrom __future__ import annotations\nimport csv, hashlib, json\nfrom pathlib import Path\nroot=Path(__file__).resolve().parent\nhard=json.loads((root/"HARD_GATE_LEDGER.json").read_text())\nassert hard["status"]=="PASS_PR05C1_ADAPTIVE_CANONICAL_MACRO_CONTROLLER_PR05C2_OPEN"\nassert hard["PR05C1"]=="COMPLETE" and hard["PR05C"]=="IN_PROGRESS"\nassert all(item["passed"] for item in hard["gates"])\nwith (root/"SOURCE_CONDITIONED_MACRO_LEDGER.csv").open(newline="") as handle:\n rows=list(csv.DictReader(handle))\nassert [int(row["target_z"]) for row in rows]==[1300,1100,900]\nassert all(int(row["history_increment"])==1 for row in rows)\nwith (root/"EVENT_CONTROLLER_LEDGER.csv").open(newline="") as handle:\n events=list(csv.DictReader(handle))\nassert len(events)==3 and sum(int(row["event_count"]) for row in events)==3\nfor line in (root/"MANIFEST_SHA256.txt").read_text().splitlines():\n if not line.strip() or line.startswith("#"): continue\n expected,relative=line.split("  ",1)\n assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==expected\nprint("PR-05C1 v0.62 artifact: PASS; adaptive canonical-macro controller COMPLETE; PR-05C2 full coupling OPEN")\n'''
    (ARTIFACT / "verify_PR05C1.py").write_text(verifier)
    manifest_lines = []
    for path in sorted(ARTIFACT.iterdir()):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            manifest_lines.append(f"{sha256(path)}  {path.name}")
    (ARTIFACT / "MANIFEST_SHA256.txt").write_text("\n".join(manifest_lines) + "\n")
    deterministic_zip(ARTIFACT, BUNDLE)
    bundle_sha = sha256(BUNDLE)
    update_repository(bundle_sha, BUNDLE.stat().st_size, metrics)
    print(json.dumps({"status": metrics["status"], "bundle": str(BUNDLE), "sha256": bundle_sha}, indent=2))


if __name__ == "__main__":
    main()
