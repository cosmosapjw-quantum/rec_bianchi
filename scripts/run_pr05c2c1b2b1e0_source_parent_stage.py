#!/usr/bin/env python3
"""Build PR-05C2C1B2B1E0/v0.73 source-derived bootstrap-parent evidence."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.background import (  # noqa: E402
    BackgroundSnapshotSequence,
    BianchiIINormalizedState,
    BianchiReviewBianchiIIProvider,
    OrthogonalGammaLawMatter,
)
from full_bianchi_hyrec.recoil.frequency_liouville import (  # noqa: E402
    ConservativeFrequencyLiouville,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig  # noqa: E402
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.causal_history import AcceptedRadiationHistory  # noqa: E402
from full_bianchi_hyrec.trajectory.direct_thermodynamic import (  # noqa: E402
    load_direct_network_node,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (  # noqa: E402
    CoupledCollisionTransportProblem,
)
from full_bianchi_hyrec.trajectory.physical_continuation import (  # noqa: E402
    build_production_continuation_adapter,
)
from full_bianchi_hyrec.trajectory.source_derived_parent import (  # noqa: E402
    build_source_derived_bootstrap_parent,
)

VERSION = 73
STAGE = "PR-05C2C1B2B1E0/v0.73"
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1E0_source_derived_bootstrap_parent_v0_73"
STATUS = (
    "PASS_PR05C2C1B2B1E0_SOURCE_DERIVED_BOOTSTRAP_PARENT_"
    "COUPLED_SINGLE_MACRO_OPEN"
)
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c1b2b1e0_source_derived_parent_v073.npz"
FORMALISM = ROOT / "docs" / "PR05C2C1B2B1E0_SOURCE_DERIVED_PARENT_FORMALISM.md"
REPORT = ROOT / "docs" / "PR05C2C1B2B1E0_RESEARCH_REPORT.md"
NEXT_PLAN = ROOT / "docs" / "PR05C2C1B2B1E1_SINGLE_MACRO_CONTINUATION_PLAN.md"
HISTORY_PATH = ROOT / "data/pr05b2_source_history_v060.npz"
NODE_PATH = ROOT / "data/z1100_direct_network_node.npz"
BACKGROUND_PATH = ROOT / "data/pr01c_background_snapshots_v048.npz"
SOURCE_PATH = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "pr04c_z1100.csv"
)
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
TAU0 = 0.6072662349590596
BRANCH_ID = "Bianchi_II:expanding:orthogonal"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for key in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(arrays[key]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{key}.npy", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, buffer.getvalue(), compresslevel=9)


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
            archive.writestr(info, path.read_bytes(), compresslevel=9)


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
        [sys.executable, str(matches[0])], cwd=matches[0].parents[1],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    log.write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"harness validation failed: {archive}")
    return {"archive": archive.name, "sha256": observed, "validator": validator, "passed": True}


def build_evidence():
    source = parse_original_hyrec_boundary_snapshot_csv(SOURCE_PATH)
    with np.load(HISTORY_PATH, allow_pickle=False) as data:
        full_history = AcceptedRadiationHistory.from_npz_mapping(data)
    history = full_history.prefix(source.trajectory.iz_local + 1)
    node = load_direct_network_node(NODE_PATH)
    with np.load(BACKGROUND_PATH, allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(data["directions"], data["angular_weights"], ell_max=3)
    locked = BackgroundSnapshotSequence.from_npz(BACKGROUND_PATH, "Bianchi_II_large_shear")
    start = locked.snapshot_at_tau(TAU0)
    provider = BianchiReviewBianchiIIProvider()
    sequence = provider.snapshots(
        family="II",
        eta_grid=np.asarray([TAU0, TAU0 + history.grid.dlna]),
        initial_state=BianchiIINormalizedState.from_snapshot(start),
        matter_parameters=OrthogonalGammaLawMatter(gamma=4.0 / 3.0),
        H_anchor_s_inv=start.H_s_inv,
        eta_anchor=TAU0,
        cosmic_time_anchor_s=start.cosmic_time_s,
    )
    result = build_source_derived_bootstrap_parent(
        history=history,
        source_snapshot=source.trajectory,
        source_snapshot_sha256=sha256(SOURCE_PATH),
        network_node=node,
        angular_grid=grid,
        background_sequence=sequence,
        background_tau=TAU0,
        branch_id=BRANCH_ID,
    )
    result.parent.validate_for_production(result.requirements)

    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=node.temperature_K, x_red=-21.25, x_blue=21.25
    )
    snapshot = sequence.snapshot_at_tau(TAU0, H_s_inv_override=source.trajectory.H_s_inv)
    transport = ConservativeFrequencyLiouville.from_network(node.network, reference_line=line)
    speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid, line=line)
    canonical_dt = history.grid.dlna / source.trajectory.H_s_inv
    problem = CoupledCollisionTransportProblem(
        network=node.network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=result.interface_samples[0].total_occupation,
        native_blue_occupation=result.interface_samples[1].total_occupation,
        dt_s=canonical_dt,
    )
    adapter = build_production_continuation_adapter(
        problem=problem, parent=result.parent, requirements=result.requirements
    )
    assessment = adapter.assess(result.parent.occupation.ravel())
    q1 = node.network.activity_weight / (1.0 - node.network.activity_weight)
    locked_boundary_rel = max(
        abs(sample.total_occupation / expected.total_occupation - 1.0)
        for sample, expected in zip(result.interface_samples, source.boundaries, strict=True)
    )
    point_rows = []
    for index, (sample, label, x) in enumerate(
        zip(result.samples, node.network.state_labels, node.network.centers, strict=True)
    ):
        point_rows.append({
            "state_index": index,
            "state_label": str(label),
            "x_center": float(x),
            **sample.record(),
            "activity": float(result.activity[index]),
            "q1_occupation": float(q1[index]),
        })
    interface_rows = []
    for side, sample, expected in zip(("red", "blue"), result.interface_samples, source.boundaries, strict=True):
        interface_rows.append({
            "side": side,
            **sample.record(),
            "locked_total_occupation": expected.total_occupation,
            "locked_relative_difference": abs(sample.total_occupation / expected.total_occupation - 1.0),
        })
    metrics = {
        "classification": "PR05C2C1B2B1E0_NUMERICAL_METRICS",
        "status": STATUS,
        "accepted_history_index": result.parent.accepted_history_index,
        "accepted_history_count": history.accepted_count,
        "accepted_history_sha256": history.sha256,
        "parent_sha256": result.parent.sha256,
        "atomic_state_sha256": result.atomic_state_sha256,
        "background_sequence_sha256": result.background_sequence_sha256,
        "network_sha256": result.parent.network_sha256,
        "interface_sha256": result.interface_sha256,
        "minimum_occupation": float(np.min(result.parent.occupation)),
        "maximum_occupation": float(np.max(result.parent.occupation)),
        "isotropy_residual": float(np.max(np.ptp(result.parent.occupation, axis=1))),
        "minimum_activity": float(np.min(result.activity)),
        "median_activity": float(np.median(result.activity)),
        "maximum_activity": float(np.max(result.activity)),
        "median_parent_to_q1_ratio": float(np.median(result.parent.occupation[:, 0] / q1)),
        "point_characteristic_count": len(result.samples),
        "interface_point_count": len(result.interface_samples),
        "locked_boundary_relative_difference_max": locked_boundary_rel,
        "canonical_dt_s": canonical_dt,
        "initial_physical_gross_backward_error": assessment.gross_backward_error,
        "initial_photon_number_relative_residual": assessment.number_relative_residual,
        "initial_physical_acceptance_metric": assessment.convergence_metric,
        "production_parent_validation_passed": True,
        "coupled_macro_endpoint": False,
        "history_commit_performed": False,
        "claim_boundary": "BOOTSTRAP_PARENT_NOT_COUPLED_MACRO_ENDPOINT",
    }
    arrays = {
        "occupation": result.parent.occupation,
        "scalar_occupation": result.parent.occupation[:, 0],
        "activity": result.activity,
        "q1_occupation": q1,
        "state_centers": node.network.centers,
        "state_intervals": node.network.state_intervals,
        "target_frequencies_Hz": np.asarray([sample.target_frequency_Hz for sample in result.samples]),
        "target_energies_eV_rescaled": np.asarray([sample.target_energy_eV_rescaled for sample in result.samples]),
        "source_indices": np.asarray([sample.source_index for sample in result.samples], dtype=np.int64),
        "eta_queries": np.asarray([sample.eta_query for sample in result.samples]),
        "parent_payload": np.frombuffer(result.parent.to_bytes(), dtype=np.uint8),
    }
    return result, metrics, point_rows, interface_rows, arrays


def write_plot(metrics: dict[str, object], arrays: dict[str, np.ndarray], output: Path) -> None:
    x = arrays["state_centers"]
    scalar = arrays["scalar_occupation"]
    q1 = arrays["q1_occupation"]
    activity = arrays["activity"]
    figure, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    axes[0].semilogy(x, scalar, "o-", label="source-derived bootstrap")
    axes[0].semilogy(x, q1, "s--", label="superseded q=1 fixture")
    axes[0].set_xlabel("Doppler coordinate x")
    axes[0].set_ylabel("occupation")
    axes[0].set_title("Accepted scalar history on COM centres")
    axes[0].legend()
    axes[1].plot(x, activity, "o-")
    axes[1].axhline(1.0, linestyle="--", label="q=1 fixture")
    axes[1].set_xlabel("Doppler coordinate x")
    axes[1].set_ylabel("Bose activity")
    axes[1].set_title("Source-derived activity profile")
    axes[1].legend()
    figure.suptitle(
        f"Bootstrap parent only; macro acceptance={metrics['initial_physical_acceptance_metric']:.3e}"
    )
    figure.tight_layout()
    figure.savefig(output, dpi=220)
    plt.close(figure)


def formalism_text(metrics: dict[str, object]) -> str:
    return rf"""# PR-05C2C1B2B1E0 source-derived bootstrap-parent formalism

## Scope

This stage constructs a positive angle-frequency parent at the accepted scalar
original-HyRec slice `iz={metrics['accepted_history_index']}`.  It is an initial
state for the next coupled macro, not a coupled macro endpoint.

## Point-characteristic reconstruction

For target ordinary frequency `nu_t`, convert to the source-rescaled energy

\[
 E_t = h\nu_t/(f_{{sR}}^2m_{{eR}}).
\]

Choose the least canonical native centre `E_s>E_t` and query the accepted
history at

\[
 \eta_q=-\ln[(1+z_t)E_s/E_t].
\]

The distortion is linearly interpolated on the canonical accepted `ln(a)` grid
and added to the Planck occupation at `E_t`.  No native cell edges and no
native-to-COM conservative remap are inferred.

## Angular initial-data axiom

The accepted scalar field is lifted isotropically in the hydrogen frame.  This
is the explicit scalar/unpolarized initial-data axiom of v0.65, not recovered
original-HyRec angular information.

## Provenance and claim boundary

The parent is bound to exact history, atomic state, dynamic Bianchi-II provider
sequence, direct network and interface hashes.  It passes the v0.72 production
firewall.  Its metadata is permanently marked
`BOOTSTRAP_PARENT_NOT_COUPLED_MACRO_ENDPOINT`; no history append occurs here.

Minimum occupation: `{metrics['minimum_occupation']:.17e}`.
Median activity: `{metrics['median_activity']:.17e}`.
Initial canonical-macro physical acceptance metric: `{metrics['initial_physical_acceptance_metric']:.17e}`.
"""


def report_text(metrics: dict[str, object]) -> str:
    return f"""# PR-05C2C1B2B1E0 research report

## Decision

`{STATUS}`

The parent-provenance blocker is resolved at the initial-data level.  The
previous q=1 operator fixture is replaced by a deterministic state evaluated
from the accepted original-HyRec scalar history at all 35 COM centres, with an
explicit isotropic hydrogen-frame lift over 26 directions.

## Evidence

- parent SHA-256: `{metrics['parent_sha256']}`
- accepted history index: `{metrics['accepted_history_index']}`
- point-characteristic queries: `{metrics['point_characteristic_count']}`
- minimum occupation: `{metrics['minimum_occupation']:.17e}`
- median activity: `{metrics['median_activity']:.8f}`
- median increase over q=1 fixture: `{metrics['median_parent_to_q1_ratio']:.8f}`
- isotropy residual: `{metrics['isotropy_residual']:.17e}`
- production provenance validation: `{metrics['production_parent_validation_passed']}`

## Adversarial result

The valid parent is not already a physical macro root.  Its initial canonical
macro acceptance metric is `{metrics['initial_physical_acceptance_metric']:.17e}`.
Therefore the next stage must solve one dynamic coupled macro; this stage does
not commit a history slice or select a preconditioner.
"""


def next_plan_text() -> str:
    return """# PR-05C2C1B2B1E1 single-macro continuation plan

## Objective

Advance the v0.73 source-derived bootstrap parent through exactly one canonical
`z~1100` Bianchi-II macro interval.

## Required execution order

1. Load and validate the v0.73 parent and all provenance hashes.
2. Use the dynamic Bianchi-II provider at every internal evaluation.
3. Couple one-/two-photon/Raman source, native characteristic transport,
   nonlinear COM collision and red/blue interface ledgers.
4. Use safeguarded pseudo-transient/Newton continuation without mutating the
   accepted history during internal iterations.
5. Localize every face-speed, topology, limiter and branch event.
6. Commit exactly one history slice only after all physical gates pass.

## Hard gates

- strict positivity without clipping
- gross residual, photon number and exact face energy below `1e-11`
- analytic JVP below `1e-8`
- photon--atom four-force and source ownership closure
- reject/rollback byte identity and deterministic restart
- accepted history count exactly `+1`

Preconditioner bake-off is permitted only after the same parent/residual path is
established.  Rust remains parity-only until the Python reference converges.
"""


def verifier_source() -> str:
    return f'''#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert m["status"]=={STATUS!r}
assert m["production_parent_validation_passed"]
assert not m["coupled_macro_endpoint"]
assert not m["history_commit_performed"]
assert m["minimum_occupation"]>0.0
assert m["isotropy_residual"]==0.0
assert 900.0<m["median_activity"]<1100.0
assert m["median_parent_to_q1_ratio"]>100.0
assert m["initial_physical_acceptance_metric"]>1.0e-11
assert len(list(csv.DictReader((ROOT/"POINT_CHARACTERISTIC_SAMPLES.csv").open())))==35
assert len(list(csv.DictReader((ROOT/"INTERFACE_SAMPLES.csv").open())))==2
with np.load(ROOT/"{DATA.name}") as data:
    assert data["occupation"].shape==(35,26)
    assert np.min(data["occupation"])>0.0
    assert data["parent_payload"].dtype==np.uint8
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(m["status"])
'''


def update_bundle_index() -> None:
    path = ROOT / "state/BUNDLE_INDEX.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in rows if int(row.get("version", -1)) != VERSION]
    rows.append({"bundle": BUNDLE.name, "sha256": sha256(BUNDLE), "size_bytes": BUNDLE.stat().st_size, "version": VERSION})
    rows.sort(key=lambda row: (int(row.get("version", -1)), str(row.get("bundle", ""))))
    write_json(path, rows)


def main() -> None:
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="pr05c2c1b2b1e0-harness-") as tmp:
        work = Path(tmp)
        harness = {
            "research": validate_harness(RESEARCH_HARNESS, RESEARCH_HARNESS_SHA256, "validate_workspace.py", work, EXPANDED / "RESEARCH_HARNESS_VALIDATION.log"),
            "coding": validate_harness(CODING_HARNESS, CODING_HARNESS_SHA256, "validate_harness.py", work, EXPANDED / "CODING_HARNESS_VALIDATION.log"),
        }
    result, metrics, point_rows, interface_rows, arrays = build_evidence()
    write_json(EXPANDED / "NUMERICAL_METRICS.json", metrics)
    write_csv(EXPANDED / "POINT_CHARACTERISTIC_SAMPLES.csv", point_rows)
    write_csv(EXPANDED / "INTERFACE_SAMPLES.csv", interface_rows)
    write_json(EXPANDED / "HARNESS_EXECUTION_RECEIPT.json", harness)
    write_json(EXPANDED / "SOURCE_PROVENANCE.json", {
        "history_path": str(HISTORY_PATH.relative_to(ROOT)), "history_sha256": sha256(HISTORY_PATH),
        "source_path": str(SOURCE_PATH.relative_to(ROOT)), "source_sha256": sha256(SOURCE_PATH),
        "network_path": str(NODE_PATH.relative_to(ROOT)), "network_sha256": sha256(NODE_PATH),
        "background_path": str(BACKGROUND_PATH.relative_to(ROOT)), "background_sha256": sha256(BACKGROUND_PATH),
    })
    write_json(EXPANDED / "PR05C2C1B2B1E0_ledger.json", {
        "classification": "PR05C2C1B2B1E0_DURABLE_LEDGER", "stage": STAGE,
        "status": STATUS, "parent_sha256": result.parent.sha256,
        "source_derived_bootstrap_parent": "COMPLETE",
        "coupled_single_macro": "OPEN",
        "claim": "accepted scalar-history bootstrap parent is positive, deterministic and provenance locked",
        "not_claimed": ["coupled macro endpoint", "history append", "selected preconditioner", "multi-macro trajectory"],
        "next": "PR05C2C1B2B1E1_SINGLE_DYNAMIC_COUPLED_MACRO",
    })
    write_json(EXPANDED / "HARD_GATE_LEDGER.json", {
        "source_history_endpoint_accepted": True,
        "future_history_endpoint": "FORBIDDEN",
        "instantaneous_native_to_COM_remap": "NOT_USED",
        "isotropic_initial_data_axiom": "EXPLICIT",
        "production_parent_validation": "PASS",
        "coupled_macro_acceptance": "OPEN",
        "preconditioner_selection": "DEFERRED_TO_SINGLE_MACRO_PATH",
    })
    write_json(EXPANDED / "CLAIM_BOUNDARY.json", {
        "implemented": ["point-characteristic scalar-history evaluation", "positive isotropic bootstrap parent", "exact provenance hashes", "production firewall entry"],
        "not_claimed": ["original-HyRec angular reconstruction", "conservative native-to-COM remap", "coupled macro endpoint", "history commit"],
    })
    deterministic_npz(EXPANDED / DATA.name, arrays); deterministic_npz(DATA, arrays)
    write_plot(metrics, arrays, EXPANDED / "SOURCE_DERIVED_PARENT_PROFILE.png")
    FORMALISM.write_text(formalism_text(metrics), encoding="utf-8")
    REPORT.write_text(report_text(metrics), encoding="utf-8")
    NEXT_PLAN.write_text(next_plan_text(), encoding="utf-8")
    for doc in (FORMALISM, REPORT, NEXT_PLAN): shutil.copy2(doc, EXPANDED / doc.name)
    verifier = EXPANDED / "verify_PR05C2C1B2B1E0.py"
    verifier.write_text(verifier_source(), encoding="utf-8"); verifier.chmod(0o755)
    manifest = sorted(path for path in EXPANDED.iterdir() if path.is_file() and path.name != "MANIFEST_SHA256.txt")
    (EXPANDED / "MANIFEST_SHA256.txt").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in manifest), encoding="utf-8")
    check = subprocess.run([sys.executable, str(verifier)], cwd=EXPANDED)
    if check.returncode: raise SystemExit(check.returncode)
    deterministic_zip(EXPANDED, BUNDLE); update_bundle_index()
    print(STATUS); print(f"parent_sha256={result.parent.sha256}"); print(f"artifact_sha256={sha256(BUNDLE)}"); print(f"generated_utc={datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
