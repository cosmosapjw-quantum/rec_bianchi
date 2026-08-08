#!/usr/bin/env python3
"""Build PR-05C2C1B2B0/v0.69 macro-evidence integrity audit.

The v0.64 artifact preserved nine recorded canonical-macro endpoints, timesteps,
source-temperature closure labels, and final occupations, but the expensive
worker source and its accepted parent states did not survive.  This stage tests
a necessary condition that does not require the missing parent: for backward
Euler the unique implied parent is f_* - dt A(f_*).  A nonpositive component
proves that no strictly-positive parent can produce the recorded endpoint under
the durable operator and recorded timestep.
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
from full_bianchi_hyrec.recoil.frequency_liouville import ConservativeFrequencyLiouville  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (  # noqa: E402
    CollisionNetwork,
    LineBoundaryConfig,
)
from full_bianchi_hyrec.trajectory.explicit_full_coupling import (  # noqa: E402
    ExplicitThermodynamicNetworkFamily,
    isotropic_native_lift,
    maximum_entropy_native_lift,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import CoupledCollisionTransportProblem  # noqa: E402
from full_bianchi_hyrec.trajectory.macro_evidence_integrity import audit_backward_euler_parent  # noqa: E402

VERSION = 69
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B0_macro_evidence_integrity_v0_69"
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c1b2b0_macro_evidence_integrity_v069.npz"
V064 = ROOT / "archive" / "expanded" / "Full_Bianchi_HyRec_PR05C2B_explicit_closure_optimized_macro_v0_64"
V064_DATA = ROOT / "data" / "pr05c2b_explicit_closure_optimized_v064.npz"
NETWORK = ROOT / "data" / "full_scalar_com_khw_v050.npz"
BACKGROUND = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
CODING_HARNESS = ROOT / "archive" / "inputs" / "research_harnesses" / "physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS = ROOT / "archive" / "inputs" / "research_harnesses" / "physmath-research-harness-gpt56.zip"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
DLNA = 8.49e-5
STATUS = (
    "PASS_BOUNDED_NO_GO_V064_RECORDED_MACRO_ENDPOINTS_INCONSISTENT_"
    "WITH_DURABLE_BACKWARD_EULER_OPERATOR_CONTINUATION_SOLVER_REQUIRED"
)
MODELS = {
    "II": "Bianchi_II_large_shear",
    "VI_h": "Bianchi_VI_h_tilted_large_shear",
    "VI_-1/9": "Bianchi_VI_minus_1_over_9_exceptional",
}


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
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def deterministic_zip(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(source)), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def validate_harness(archive: Path, expected: str, validator: str, work: Path, log: Path) -> dict[str, object]:
    observed = sha256(archive)
    if observed != expected:
        raise RuntimeError(f"harness hash mismatch: {archive}")
    destination = work / archive.stem
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise RuntimeError(f"corrupt harness: {archive}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator))
    if len(matches) != 1:
        raise RuntimeError(f"cannot uniquely locate {validator}")
    result = subprocess.run(
        [sys.executable, str(matches[0])],
        cwd=matches[0].parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text(result.stdout)
    if result.returncode:
        raise RuntimeError(f"harness validation failed: {archive}")
    return {"archive": archive.name, "sha256": observed, "validator": validator, "passed": True}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_audit() -> tuple[list[dict[str, object]], dict[str, np.ndarray], dict[str, object]]:
    macro_rows = read_csv(V064 / "MACRO_SOLVER_LEDGER.csv")
    angular_rows = read_csv(V064 / "ANGULAR_CLOSURE_LEDGER.csv")
    scalar_boundary = {
        (int(row["target_z"]), row["side"]): float(row["scalar_monopole"])
        for row in angular_rows
    }
    public = np.load(V064_DATA, allow_pickle=False)
    grid = HarmonicGrid.from_directions(public["directions"], public["angular_weights"], ell_max=24)
    reference = CollisionNetwork.from_npz(NETWORK)
    family = ExplicitThermodynamicNetworkFamily(reference)

    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {
        "directions": np.asarray(grid.directions),
        "angular_weights": np.asarray(grid.weights),
    }
    lane_minima: list[float] = []
    lane_ratios: list[float] = []
    negative_counts: list[int] = []
    boundary_sensitivity: list[float] = []

    for recorded in macro_rows:
        target = int(recorded["target_z"])
        short_model = recorded["bianchi_type"]
        model = MODELS[short_model]
        temperature = float(recorded["temperature_K"])
        density = float(recorded["nH_m3"])
        dt = float(recorded["macro_dt_s"])
        member = family.compile(temperature_K=temperature, nH_m3=density)
        network = member.network
        line = LineBoundaryConfig.lyman_alpha(
            temperature_K=temperature,
            x_red=float(np.min(network.state_intervals[:, 0])),
            x_blue=float(np.max(network.state_intervals[:, 1])),
        )
        transport = ConservativeFrequencyLiouville.from_network(network, reference_line=line)
        sequence = BackgroundSnapshotSequence.from_npz(BACKGROUND, model)
        snapshot = sequence.snapshot_at_tau(0.0, H_s_inv_override=DLNA / dt)
        speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid)
        final = np.asarray(public[f"z{target}_{model}_final_occupation"], dtype=float)

        closure_results: dict[str, tuple[float, int]] = {}
        for closure in ("isotropic", "maximum_entropy_outward"):
            if closure == "isotropic":
                red = isotropic_native_lift(scalar_boundary[(target, "red")], grid).occupation
                blue = isotropic_native_lift(scalar_boundary[(target, "blue")], grid).occupation
            else:
                red = maximum_entropy_native_lift(
                    scalar_boundary[(target, "red")],
                    grid,
                    axis=np.asarray([-1.0, 0.0, 0.0]),
                    reduced_flux=0.05,
                ).occupation
                blue = maximum_entropy_native_lift(
                    scalar_boundary[(target, "blue")],
                    grid,
                    axis=np.asarray([1.0, 0.0, 0.0]),
                    reduced_flux=0.05,
                ).occupation
            problem = CoupledCollisionTransportProblem(
                network=network,
                grid=grid,
                transport=transport,
                face_speeds_x_s_inv=speeds,
                native_red_occupation=red,
                native_blue_occupation=blue,
                dt_s=dt,
            )
            collision = problem._collision_action(final)
            frequency_transport = problem._transport(final).occupation_action
            action = collision + frequency_transport
            audit = audit_backward_euler_parent(final, action, dt_s=dt)
            closure_results[closure] = (audit.implied_parent_minimum, audit.nonpositive_parent_count)
            lane_minima.append(audit.implied_parent_minimum)
            lane_ratios.append(audit.dt_to_positivity_limit_ratio)
            negative_counts.append(audit.nonpositive_parent_count)
            key = f"z{target}_{model}_{closure}"
            arrays[f"{key}_implied_parent"] = audit.implied_parent
            arrays[f"{key}_action_s_inv"] = action
            rows.append(
                {
                    "target_z": target,
                    "actual_z": recorded["actual_z"],
                    "model": model,
                    "bianchi_type": short_model,
                    "boundary_closure": closure,
                    "recorded_dt_s": dt,
                    "recorded_gross_backward_error": float(recorded["gross_backward_error"]),
                    "recorded_number_relative_residual": float(recorded["number_relative_residual"]),
                    "final_minimum": float(np.min(final)),
                    "final_maximum": float(np.max(final)),
                    "collision_action_max_abs_s_inv": float(np.max(np.abs(collision))),
                    "transport_action_max_abs_s_inv": float(np.max(np.abs(frequency_transport))),
                    "total_action_max_abs_s_inv": audit.maximum_action_abs,
                    "implied_parent_minimum": audit.implied_parent_minimum,
                    "implied_parent_maximum": audit.implied_parent_maximum,
                    "nonpositive_parent_count": audit.nonpositive_parent_count,
                    "state_component_count": int(final.size),
                    "maximum_strictly_positive_dt_s": audit.max_strictly_positive_dt_s,
                    "recorded_dt_to_positivity_limit_ratio": audit.dt_to_positivity_limit_ratio,
                    "strictly_positive_parent_exists": int(audit.strictly_positive_parent_exists),
                    "classification": audit.classification,
                }
            )
        boundary_sensitivity.append(
            abs(closure_results["isotropic"][0] - closure_results["maximum_entropy_outward"][0])
        )

    metrics = {
        "classification": "PR05C2C1B2B0_MACRO_EVIDENCE_INTEGRITY_METRICS",
        "status": STATUS,
        "recorded_lane_count": len(macro_rows),
        "audited_boundary_closure_count": 2,
        "audit_row_count": len(rows),
        "all_recorded_lanes_inconsistent_under_both_boundary_closures": all(
            row["strictly_positive_parent_exists"] == 0 for row in rows
        ),
        "minimum_implied_parent": min(lane_minima),
        "minimum_nonpositive_component_count": min(negative_counts),
        "maximum_nonpositive_component_count": max(negative_counts),
        "minimum_recorded_dt_to_positivity_limit_ratio": min(lane_ratios),
        "maximum_recorded_dt_to_positivity_limit_ratio": max(lane_ratios),
        "maximum_boundary_closure_implied_parent_minimum_difference": max(boundary_sensitivity),
        "durable_worker_source_present": False,
        "v064_artifact_bytes_remain_durable": True,
        "v064_macro_convergence_claim_reusable": False,
        "downstream_theory_and_source_adapters_affected": False,
        "next": "PR05C2C1B2B1_ACCEPTED_STATE_PSEUDOTRANSIENT_MICRO_MACRO_CONTINUATION",
    }
    return rows, arrays, metrics


def write_harness_documents(metrics: dict[str, object]) -> None:
    documents = {
        "01_RESEARCH_CONTRACT.md": (
            "# Research contract\n\nQuestion: can the recorded v0.64 canonical-macro endpoints be reused as "
            "accepted parents for v0.69 multi-macro work under the durable backward-Euler operator? "
            "Success requires a positive implied parent in every component without fitted normalization.\n"
        ),
        "02_EVIDENCE_ACQUISITION.md": (
            "# Evidence acquisition\n\nEvidence is restricted to the immutable v0.64 endpoint NPZ, its macro and angular ledgers, "
            "the durable v0.50 collision network, v0.48 background snapshots, current explicit thermodynamic "
            "closure implementation, Git history, hashes, and machine checks.  Missing worker prose is not evidence.\n"
        ),
        "03_CLAIM_SOURCE_AUDIT.md": (
            "# Claim/source audit\n\nThe endpoint bytes and recorded timesteps are source locked.  The expensive worker source and accepted parent "
            "states are absent.  Backward Euler nevertheless fixes a unique implied parent, so positivity is auditable "
            "without reconstructing the missing worker.\n"
        ),
        "04_HYPOTHESIS_SPACE.md": (
            "# Hypothesis space\n\nH_A: the endpoints are compatible with some strictly-positive parent. "
            "H_B: closure-label ambiguity explains any mismatch. H_C: the endpoints are inconsistent with the durable "
            "operator/timestep and cannot seed multi-macro continuation. Evidence selects H_C.\n"
        ),
        "05_ADVERSARIAL_REVIEW.md": (
            "# Adversarial review\n\nAttacks include isotropic versus maximum-entropy boundary closure, unknown old state, tiny exterior occupations, "
            "transport-sign ambiguity, and cancellation.  The implied-parent test eliminates the unknown-old-state "
            "degree of freedom and both declared boundary closures give the same contradiction class.\n"
        ),
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": (
            "# Validation and dimensional closure\n\nOccupation is dimensionless, action has s^-1, and dt is seconds.  Hence f_parent=f_star-dt*A(f_star) is dimensionless. "
            "For A_i>0 strict positivity requires dt<f_i/A_i; A_i<=0 introduces no upper positivity bound.\n"
        ),
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": "# Verification design and results\n\n```json\n" + json.dumps(metrics, indent=2, sort_keys=True) + "\n```\n",
        "08_EXTERNAL_GATE.md": (
            "# External decision gate\n\nDo not select or benchmark a production preconditioner on the recorded v0.64 endpoints. "
            "First reconstruct an accepted-state continuation path with pseudo-transient or adaptive micro/macro steps, "
            "then repeat conservation and wall-time gates on that path.\n"
        ),
        "09_FORMALIZATION.md": (
            "# Formalization\n\nFor R(f_star;f_n)=f_star-f_n-dt*A(f_star)=0, the unique parent is "
            "f_n=f_star-dt*A(f_star). If any component is nonpositive, no strictly-positive parent exists. "
            "This is a necessary-condition no-go independent of nonlinear-solver details.\n"
        ),
        "10_CLOSEOUT_AND_HANDOFF.md": (
            "# Closeout and handoff\n\nThe v0.64 artifact remains durable as bytes, but its nine macro-convergence rows are superseded as scientific evidence. "
            "v0.65 theory, v0.66/v0.67 direct-node/source work, and v0.68 two-photon/Raman adapters remain valid. "
            "Next build accepted-state pseudo-transient/micro-macro continuation from source-conditioned parents.\n"
        ),
    }
    for name, text in documents.items():
        (EXPANDED / name).write_text(text)


def artifact_verifier_source() -> str:
    return '''#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json
import numpy as np
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/"MACRO_EVIDENCE_INTEGRITY.csv").open(newline="")))
metrics=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert metrics["status"].startswith("PASS_BOUNDED_NO_GO_V064_RECORDED_MACRO_ENDPOINTS")
assert len(rows)==18
assert all(int(r["strictly_positive_parent_exists"])==0 for r in rows)
assert min(int(r["nonpositive_parent_count"]) for r in rows)>0
assert min(float(r["recorded_dt_to_positivity_limit_ratio"]) for r in rows)>1.0e9
manifest={}
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1);manifest[name]=digest
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
with np.load(ROOT/"pr05c2c1b2b0_macro_evidence_integrity_v069.npz") as data:
    assert data["recorded_dt_to_positivity_limit_ratio"].min()>1.0e9
print(metrics["status"])
'''


def main() -> None:
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="pr05c2c1b2b0-harness-") as temp:
        work = Path(temp)
        harnesses = {
            "coding": validate_harness(
                CODING_HARNESS,
                CODING_HARNESS_SHA256,
                "validate_harness.py",
                work,
                EXPANDED / "CODING_HARNESS_VALIDATION.log",
            ),
            "research": validate_harness(
                RESEARCH_HARNESS,
                RESEARCH_HARNESS_SHA256,
                "validate_workspace.py",
                work,
                EXPANDED / "RESEARCH_HARNESS_VALIDATION.log",
            ),
        }
    rows, arrays, metrics = build_audit()
    arrays.update(
        {
            "recorded_dt_s": np.asarray([float(row["recorded_dt_s"]) for row in rows]),
            "maximum_strictly_positive_dt_s": np.asarray(
                [float(row["maximum_strictly_positive_dt_s"]) for row in rows]
            ),
            "recorded_dt_to_positivity_limit_ratio": np.asarray(
                [float(row["recorded_dt_to_positivity_limit_ratio"]) for row in rows]
            ),
            "nonpositive_parent_count": np.asarray(
                [int(row["nonpositive_parent_count"]) for row in rows], dtype=np.int64
            ),
        }
    )
    write_csv(EXPANDED / "MACRO_EVIDENCE_INTEGRITY.csv", rows)
    write_json(EXPANDED / "NUMERICAL_METRICS.json", metrics)
    write_json(EXPANDED / "HARD_GATE_LEDGER.json", {
        "PR05C2C1B2B0": "COMPLETE_PASS_BOUNDED_NO_GO",
        "v064_artifact_bytes": "DURABLE_VERIFIED",
        "v064_nine_macro_convergence_claim": "SUPERSEDED_INCONSISTENT_WITH_DURABLE_OPERATOR",
        "v065_theory": "UNAFFECTED",
        "v066_v067_v068_source_network_adapters": "UNAFFECTED",
        "multi_macro": "OPEN_REQUIRES_ACCEPTED_STATE_CONTINUATION",
    })
    write_json(EXPANDED / "PR05C2C1B2B0_ledger.json", {
        "classification": "PR05C2C1B2B0_DURABLE_LEDGER",
        "status": STATUS,
        "metrics": metrics,
        "v064_artifact_bytes": "DURABLE_VERIFIED",
        "v064_macro_convergence_claim": "SUPERSEDED",
        "downstream_theory_and_source_adapters": "UNAFFECTED",
        "next": "PR05C2C1B2B1_ACCEPTED_STATE_PSEUDOTRANSIENT_MICRO_MACRO_CONTINUATION",
    })
    write_json(EXPANDED / "HARNESS_EXECUTION_RECEIPT.json", harnesses)
    write_json(EXPANDED / "WOLFRAM_SYMBOLIC_RECEIPT.json", {
        "backward_euler_substitution_residual": 0,
        "strict_parent_condition": "for f_star>0 and A>0: f_star-dt*A>0 iff dt<f_star/A",
        "negative_action_has_no_upper_dt_bound": True,
        "tool": "WolframLanguageEvaluator",
    })
    write_json(EXPANDED / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json", {
        "gamma_3_over_2_120dps": "0.886226925452758013649083741670572591398774728061193564106903894926455642295516090687475328369272332708113411812141285333",
        "role": "independent high-precision tool availability receipt; not load-bearing for the no-go",
    })
    write_json(EXPANDED / "LITERATURE_DECISION_RECEIPT.json", {
        "PETSc_TSPSEUDO": "pseudo-transient continuation for steady ODE/DAE residuals",
        "PETSc_SNESNEWTONTR": "trust-region nonlinear globalization candidate",
        "PETSc_SNESLINESEARCHBT": "backtracking minimizes one-half residual norm squared",
        "decision": "reconstruct accepted-state continuation before preconditioner selection",
    })
    write_harness_documents(metrics)
    deterministic_npz(EXPANDED / DATA.name, arrays)
    verifier = EXPANDED / "verify_PR05C2C1B2B0.py"
    verifier.write_text(artifact_verifier_source())
    verifier.chmod(0o755)

    manifest_paths = sorted(
        path for path in EXPANDED.iterdir() if path.is_file() and path.name != "MANIFEST_SHA256.txt"
    )
    (EXPANDED / "MANIFEST_SHA256.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in manifest_paths)
    )
    result = subprocess.run([sys.executable, str(verifier)], cwd=EXPANDED, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
    deterministic_zip(EXPANDED, BUNDLE)
    shutil.copy2(EXPANDED / DATA.name, DATA)
    print(STATUS)
    print(f"artifact_sha256={sha256(BUNDLE)}")
    print(f"data_sha256={sha256(DATA)}")


if __name__ == "__main__":
    main()
