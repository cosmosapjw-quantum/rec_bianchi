#!/usr/bin/env python3
"""Build PR-05C2C1B2B1D/v0.72 parent-provenance/provider evidence.

This bounded stage implements the two prerequisites selected by the dual-harness
blocker audit:

* R1: a fail-closed accepted-parent provenance boundary that prevents
  operator-verification/manufactured radiation states from entering production
  macro continuation; and
* R2: a read-only orthogonal Bianchi-II background-evolution provider pilot
  derived from the uploaded ``bianchireview87`` class-A equations.

It intentionally does *not* construct a physical source-derived accepted parent,
select a preconditioner, or claim a converged physical macro trajectory.  Those
belong to R3 and later stages.
"""
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
import tarfile
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
    BackgroundChartEventRequired,
    BackgroundFamilyNotValidatedError,
    BackgroundSnapshotSequence,
    BianchiIINormalizedState,
    BianchiReviewBianchiIIProvider,
    OrthogonalGammaLawMatter,
    TiltedPerfectFluidRequest,
    UnsupportedBackgroundBranchError,
)
from full_bianchi_hyrec.background.evolution_provider import (  # noqa: E402
    BIANCHI_REVIEW_ARCHIVE_SHA256,
    BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256,
    BIANCHI_REVIEW_TYPE_IX_D_SOURCE_SHA256,
)
from full_bianchi_hyrec.trajectory.accepted_parent import (  # noqa: E402
    AcceptedRadiationParent,
    ParentEvidenceClass,
    ProductionParentRequirements,
)

VERSION = 72
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1D_parent_provenance_background_provider_v0_72"
STATUS = (
    "PASS_PR05C2C1B2B1D_PARENT_PROVENANCE_FIREWALL_"
    "BIANCHI_II_PROVIDER_PILOT_R3_OPEN"
)
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c1b2b1d_parent_provider_v072.npz"
FORMALISM = ROOT / "docs" / "PR05C2C1B2B1D_PARENT_PROVIDER_FORMALISM.md"
REPORT = ROOT / "docs" / "PR05C2C1B2B1D_RESEARCH_REPORT.md"
NEXT_PLAN = ROOT / "docs" / "PR05C2C1B2B1E_SOURCE_DERIVED_PARENT_PLAN.md"
LOCKED_BACKGROUND = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
SOLVER_ARCHIVE = (
    ROOT / "archive" / "inputs" / "bianchi_background_solver_v87" /
    "bianchireview87.tar.gz"
)
RESEARCH_HARNESS = (
    ROOT / "archive" / "inputs" / "research_harnesses" /
    "physmath-research-harness-gpt56.zip"
)
CODING_HARNESS = (
    ROOT / "archive" / "inputs" / "research_harnesses" /
    "physmath-coding-harness-gpt56.zip"
)
RESEARCH_HARNESS_SHA256 = (
    "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
)
CODING_HARNESS_SHA256 = (
    "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
)
TAU0 = 0.6072662349590596
DELTA_ETA = 8.49e-5
GAMMA = 4.0 / 3.0
PROVIDER_ABSOLUTE_GATE = 1.0e-5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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


def validate_harness(
    archive: Path,
    expected_sha256: str,
    validator_name: str,
    work: Path,
    log: Path,
) -> dict[str, object]:
    observed = sha256(archive)
    if observed != expected_sha256:
        raise RuntimeError(f"harness hash mismatch: {archive}")
    destination = work / archive.stem
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise RuntimeError(f"corrupt harness: {archive}")
        zipped.extractall(destination)
    validators = list(destination.rglob(validator_name))
    if len(validators) != 1:
        raise RuntimeError(f"cannot uniquely locate {validator_name}")
    result = subprocess.run(
        [sys.executable, str(validators[0])],
        cwd=validators[0].parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"harness validation failed: {archive}")
    return {
        "archive": archive.name,
        "sha256": observed,
        "validator": validator_name,
        "passed": True,
    }


def locked_sequence() -> BackgroundSnapshotSequence:
    return BackgroundSnapshotSequence.from_npz(
        LOCKED_BACKGROUND, "Bianchi_II_large_shear"
    )


def normalized_state(snapshot) -> np.ndarray:
    H = snapshot.H_s_inv
    sigma = snapshot.sigma_s_inv / H
    curvature = snapshot.N_s_inv / H
    return np.asarray(
        [
            -0.5 * sigma[0, 0],
            (sigma[1, 1] - sigma[2, 2]) / (2.0 * math.sqrt(3.0)),
            curvature[0, 0],
        ],
        dtype=float,
    )


def requirements(index: int = 17) -> ProductionParentRequirements:
    return ProductionParentRequirements(
        accepted_history_index=index,
        accepted_history_sha256=digest_text("history-v072-schema-witness"),
        atomic_state_sha256=digest_text("atomic-v072-schema-witness"),
        background_sequence_sha256=digest_text("background-v072-schema-witness"),
        network_sha256=digest_text("network-v072-schema-witness"),
        interface_sha256=digest_text("interface-v072-schema-witness"),
        branch_id="Bianchi_II:expanding:orthogonal",
    )


def parent(evidence: ParentEvidenceClass) -> AcceptedRadiationParent:
    expected = requirements()
    return AcceptedRadiationParent(
        occupation=np.full((3, 2), 1.0e-8),
        evidence_class=evidence,
        accepted_history_index=expected.accepted_history_index,
        accepted_history_sha256=expected.accepted_history_sha256,
        atomic_state_sha256=expected.atomic_state_sha256,
        background_sequence_sha256=expected.background_sequence_sha256,
        network_sha256=expected.network_sha256,
        interface_sha256=expected.interface_sha256,
        branch_id=expected.branch_id,
        metadata={
            "canonical_eta": TAU0,
            "evidence_note": "schema witness only; not a reconstructed physical parent",
        },
    )


def firewall_evidence() -> tuple[list[dict[str, object]], dict[str, object], np.ndarray]:
    rows: list[dict[str, object]] = []
    for evidence in ParentEvidenceClass:
        candidate = parent(evidence)
        outcome = "ACCEPT"
        error_type = ""
        try:
            candidate.validate_for_production(requirements())
        except Exception as exc:  # audit records exact fail-closed class
            outcome = "REJECT"
            error_type = type(exc).__name__
        rows.append(
            {
                "evidence_class": evidence.value,
                "production_outcome": outcome,
                "error_type": error_type,
                "accepted_history_index": candidate.accepted_history_index,
                "parent_sha256": candidate.sha256,
                "claim_class": (
                    "SCHEMA_WITNESS_NOT_PHYSICAL_PARENT"
                    if evidence is ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED
                    else "NONPRODUCTION_FIXTURE"
                ),
            }
        )

    source_parent = parent(ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED)
    payload = source_parent.to_bytes()
    recovered = AcceptedRadiationParent.from_bytes(payload)
    stale_rejected = False
    stale = requirements(index=requirements().accepted_history_index + 1)
    try:
        source_parent.validate_for_production(stale)
    except ValueError:
        stale_rejected = True

    outcomes = {row["evidence_class"]: row["production_outcome"] for row in rows}
    metrics = {
        "operator_verification_rejected": outcomes[ParentEvidenceClass.OPERATOR_VERIFICATION.value] == "REJECT",
        "manufactured_rejected": outcomes[ParentEvidenceClass.MANUFACTURED.value] == "REJECT",
        "source_derived_schema_witness_accepted": outcomes[ParentEvidenceClass.SOURCE_DERIVED_ACCEPTED.value] == "ACCEPT",
        "byte_round_trip_exact": recovered.to_bytes() == payload,
        "sha256_round_trip_exact": recovered.sha256 == source_parent.sha256,
        "stale_history_index_rejected": stale_rejected,
        "physical_source_derived_parent_constructed": False,
        "physical_parent_reconstruction_next": True,
    }
    return rows, metrics, np.frombuffer(payload, dtype=np.uint8).copy()


def provider_evidence() -> tuple[list[dict[str, object]], dict[str, object], dict[str, np.ndarray]]:
    locked = locked_sequence()
    start = locked.snapshot_at_tau(TAU0)
    reference = locked.snapshot_at_tau(TAU0 + DELTA_ETA)
    provider = BianchiReviewBianchiIIProvider()
    sequence = provider.snapshots(
        family="II",
        eta_grid=np.asarray([TAU0, TAU0 + DELTA_ETA]),
        initial_state=BianchiIINormalizedState.from_snapshot(start),
        matter_parameters=OrthogonalGammaLawMatter(gamma=GAMMA),
        H_anchor_s_inv=start.H_s_inv,
        eta_anchor=TAU0,
        cosmic_time_anchor_s=start.cosmic_time_s,
    )
    predicted = sequence.snapshot_at_tau(TAU0 + DELTA_ETA)
    start_state = normalized_state(start)
    reference_state = normalized_state(reference)
    predicted_state = normalized_state(predicted)
    absolute_error = np.abs(predicted_state - reference_state)

    names = ("Sigma_plus", "Sigma_minus", "N1")
    rows: list[dict[str, object]] = []
    for index, name in enumerate(names):
        rows.append(
            {
                "quantity": name,
                "start": float(start_state[index]),
                "reference_end": float(reference_state[index]),
                "provider_end": float(predicted_state[index]),
                "absolute_error": float(absolute_error[index]),
                "pilot_gate": PROVIDER_ABSOLUTE_GATE,
                "passed": int(absolute_error[index] < PROVIDER_ABSOLUTE_GATE),
            }
        )
    H_relative_error = abs(predicted.H_s_inv / reference.H_s_inv - 1.0)
    locked_cosmic_time_difference = abs(
        (predicted.cosmic_time_s - start.cosmic_time_s)
        / (reference.cosmic_time_s - start.cosmic_time_s)
        - 1.0
    )
    midpoint_H = 0.5 * (start.H_s_inv + predicted.H_s_inv)
    trapezoid_dt = DELTA_ETA / midpoint_H
    provider_time_increment = predicted.cosmic_time_s - start.cosmic_time_s
    time_reconstruction_error = abs(provider_time_increment / trapezoid_dt - 1.0)
    max_constraint = max(abs(value) for value in predicted.constraint_residuals.values())

    ix_event = False
    try:
        provider.snapshots(
            family="IX",
            eta_grid=[0.0, DELTA_ETA],
            initial_state=object(),
            matter_parameters=OrthogonalGammaLawMatter(gamma=GAMMA),
            H_anchor_s_inv=1.0,
            eta_anchor=0.0,
        )
    except BackgroundChartEventRequired as exc:
        ix_event = exc.event.required_chart == "type_ix_D_normalized"

    exceptional_fail_closed = False
    try:
        provider.snapshots(
            family="VI*_-1/9",
            eta_grid=[0.0, DELTA_ETA],
            initial_state=object(),
            matter_parameters=TiltedPerfectFluidRequest(
                gamma=GAMMA,
                beta=np.asarray([0.1, 0.0, 0.0]),
            ),
            H_anchor_s_inv=1.0,
            eta_anchor=0.0,
        )
    except UnsupportedBackgroundBranchError:
        exceptional_fail_closed = True

    unvalidated_family_fail_closed = False
    try:
        provider.snapshots(
            family="V",
            eta_grid=[0.0, DELTA_ETA],
            initial_state=object(),
            matter_parameters=OrthogonalGammaLawMatter(gamma=GAMMA),
            H_anchor_s_inv=1.0,
            eta_anchor=0.0,
        )
    except BackgroundFamilyNotValidatedError:
        unvalidated_family_fail_closed = True

    archive_hash_ok = sha256(SOLVER_ARCHIVE) == BIANCHI_REVIEW_ARCHIVE_SHA256
    with tarfile.open(SOLVER_ARCHIVE, "r:gz") as handle:
        class_a_handle = handle.extractfile("./bianchi/charts/class_a.py")
        ix_handle = handle.extractfile("./bianchi/charts/type_ix_d.py")
        if class_a_handle is None or ix_handle is None:
            raise RuntimeError("uploaded solver source members missing")
        class_a_hash_ok = (
            hashlib.sha256(class_a_handle.read()).hexdigest()
            == BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256
        )
        ix_hash_ok = (
            hashlib.sha256(ix_handle.read()).hexdigest()
            == BIANCHI_REVIEW_TYPE_IX_D_SOURCE_SHA256
        )

    metrics = {
        "state_absolute_error_max": float(np.max(absolute_error)),
        "H_relative_error": float(H_relative_error),
        "locked_cosmic_time_increment_relative_difference_diagnostic": float(locked_cosmic_time_difference),
        "time_reconstruction_trapezoid_relative_error": float(time_reconstruction_error),
        "constraint_residual_absmax": float(max_constraint),
        "provider_pilot_gate": PROVIDER_ABSOLUTE_GATE,
        "provider_pilot_passed": bool(np.max(absolute_error) < PROVIDER_ABSOLUTE_GATE),
        "archive_hash_locked": archive_hash_ok,
        "class_a_source_hash_locked": class_a_hash_ok,
        "type_ix_D_source_hash_locked": ix_hash_ok,
        "Bianchi_IX_D_event_required": ix_event,
        "exceptional_tilted_VI_minus_1_over_9_fail_closed": exceptional_fail_closed,
        "unvalidated_family_fail_closed": unvalidated_family_fail_closed,
        "provider_validated_scope": "orthogonal Bianchi II pilot only",
        "all_11_family_production_support_claimed": False,
    }
    arrays = {
        "tau": np.asarray([TAU0, TAU0 + DELTA_ETA]),
        "start_normalized_state": start_state,
        "reference_end_normalized_state": reference_state,
        "provider_end_normalized_state": predicted_state,
        "absolute_error": absolute_error,
        "H_s_inv": np.asarray([start.H_s_inv, predicted.H_s_inv]),
        "q": np.asarray([start.q, predicted.q]),
        "cosmic_time_s": np.asarray([start.cosmic_time_s, predicted.cosmic_time_s]),
    }
    return rows, metrics, arrays


def write_provider_plot(rows: list[dict[str, object]], output: Path) -> None:
    labels = [str(row["quantity"]) for row in rows]
    reference = np.asarray([float(row["reference_end"]) for row in rows])
    predicted = np.asarray([float(row["provider_end"]) for row in rows])
    errors = np.asarray([float(row["absolute_error"]) for row in rows])
    x = np.arange(len(labels))
    figure, axes = plt.subplots(1, 2, figsize=(9.2, 4.1))
    axes[0].plot(x, reference, "o-", label="locked v0.48")
    axes[0].plot(x, predicted, "s--", label="provider")
    axes[0].set_xticks(x, labels)
    axes[0].set_ylabel("Hubble-normalized state")
    axes[0].set_title("Bianchi-II one-macro endpoint")
    axes[0].legend()
    axes[1].bar(x, errors)
    axes[1].axhline(PROVIDER_ABSOLUTE_GATE, linestyle="--", label="pilot gate")
    axes[1].set_yscale("log")
    axes[1].set_xticks(x, labels)
    axes[1].set_ylabel("absolute error")
    axes[1].set_title("Provider − locked reference")
    axes[1].legend()
    figure.tight_layout()
    figure.savefig(output, dpi=220)
    plt.close(figure)


def formalism_text(metrics: dict[str, object]) -> str:
    template = r"""# PR-05C2C1B2B1D parent-provenance and background-provider formalism

## Scope and conventions

This stage is a prerequisite stage, not a physical trajectory result.  It keeps
metric signature `(-,+,+,+)`, ordinary frequency in Hz, explicit `c,h,k_B`, and
homogeneous hydrogen-frame tetrad variables.

## R1: production parent provenance

A production macro parent is the tuple

```text
(occupation bytes, evidence class, accepted-history index/hash,
 atomic-state hash, background-sequence hash, network hash,
 interface hash, branch id, scalar metadata).
```

Only `SOURCE_DERIVED_ACCEPTED` may enter the production continuation factory.
`OPERATOR_VERIFICATION` and `MANUFACTURED` remain legal audit fixtures but fail
closed at the production boundary.  Exact byte serialization uses canonical
little-endian float64 occupation bytes and canonical sorted JSON metadata.

The accepted object used by this stage is a *schema witness only*.  It proves
that valid provenance is accepted and stale/mismatched provenance is rejected;
it is not a reconstructed physical parent.  Physical reconstruction is R3.

## R2: orthogonal Bianchi-II provider pilot

The provider evolves

\[
 K=N_1^2/12,\quad
 \Sigma^2=\Sigma_+^2+\Sigma_-^2,\quad
 \Omega=1-\Sigma^2-K,
\]

\[
 q=2\Sigma^2+\frac12(3\gamma-2)\Omega,
\]

\[
 \Sigma_+'=-(2-q)\Sigma_+ + N_1^2/3,
 \quad
 \Sigma_-'=-(2-q)\Sigma_-,
\]

\[
 N_1'=(q-4\Sigma_+)N_1,
 \quad
 (\ln H)'=-(1+q),
 \quad
 t'=H^{-1}.
\]

Physical tensors are reconstructed as

\[
 \sigma_{\hat a\hat b}=H\,\Sigma_{\hat a\hat b},
 \qquad N_{\hat a\hat b}=H\,\bar N_{\hat a\hat b},
 \qquad A_{\hat a}=0.
\]

The pilot is validated only for the expanding orthogonal Bianchi-II branch.
Bianchi IX requests emit a D-normalized H-zero event, tilted exceptional
`VI_-1/9` fails closed, and all other family labels remain registry/smoke only.

## Numerical closure

Maximum normalized-state endpoint error is `__MAX_ERROR__` against the locked
v0.48 one-macro reference.  No all-family or finite-tilt provider claim is made.
"""
    return template.replace(
        "__MAX_ERROR__",
        f"{metrics['background_provider']['state_absolute_error_max']:.17e}",
    )


def report_text(metrics: dict[str, object]) -> str:
    firewall = metrics["parent_firewall"]
    provider = metrics["background_provider"]
    return f"""# PR-05C2C1B2B1D research report

## Decision

`{STATUS}`

The dual-harness blocker audit identified an invalid parent provenance as the
first blocker, ahead of nonlinear continuation or preconditioner work.  This
stage implements the corresponding fail-closed boundary and a narrow dynamic
background provider pilot.

## Results

- operator-verification parent rejected: `{firewall['operator_verification_rejected']}`
- manufactured parent rejected: `{firewall['manufactured_rejected']}`
- exact parent byte round trip: `{firewall['byte_round_trip_exact']}`
- stale history index rejected: `{firewall['stale_history_index_rejected']}`
- physical source-derived parent constructed: `{firewall['physical_source_derived_parent_constructed']}`
- Bianchi-II provider maximum endpoint error: `{provider['state_absolute_error_max']:.17e}`
- provider constraint residual maximum: `{provider['constraint_residual_absmax']:.17e}`
- Bianchi IX D-chart event: `{provider['Bianchi_IX_D_event_required']}`
- tilted exceptional VI_-1/9 fail closed: `{provider['exceptional_tilted_VI_minus_1_over_9_fail_closed']}`

## Claim boundary

This stage does not prove an accepted recombination trajectory, a physical COM
interior parent, tilted provider support, all-11 provider support, or a selected
preconditioner.  It makes those later tests meaningful by ensuring that only a
source-derived accepted state can enter production and by providing a validated
Bianchi-II dynamic background path.
"""


def next_plan_text() -> str:
    return """# PR-05C2C1B2B1E source-derived accepted-parent reconstruction plan

## Objective

Construct one physical accepted parent at `z~1100`, Bianchi II from the previous
accepted atomic/radiation history.  Do not reuse the operator-verification
fixture or cached v0.64 endpoints.

## Required state

- accepted HyRec history bytes and index
- electron and real/virtual atomic populations
- angle-frequency occupation
- dynamic `BackgroundSnapshotSequence` from the validated provider
- direct thermodynamic-network provenance
- red/blue interface accumulators
- limiter/upwind/event branch
- one-/two-photon/Raman source registry

## Transaction

1. Read an immutable accepted parent prefix.
2. Advance internal microsteps with dynamic background interpolation.
3. Reject/rollback without mutating accepted history.
4. Localize every branch/face-speed/topology event.
5. Commit exactly one canonical history slice only after all physical gates pass.

## Hard gates

- evidence class `SOURCE_DERIVED_ACCEPTED`
- all provenance hashes exact
- strict positivity without clipping
- photon number and exact face energy below `1e-11`
- source ownership and photon--atom four-force closure
- deterministic restart and rollback byte identity
- accepted history count `+1`
- no preconditioner or Rust selection until this parent exists
"""


def artifact_verifier_source() -> str:
    return f'''#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
metrics=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert metrics["status"]=={STATUS!r}
firewall=metrics["parent_firewall"]
provider=metrics["background_provider"]
assert firewall["operator_verification_rejected"]
assert firewall["manufactured_rejected"]
assert firewall["byte_round_trip_exact"]
assert firewall["stale_history_index_rejected"]
assert not firewall["physical_source_derived_parent_constructed"]
assert provider["provider_pilot_passed"]
assert provider["state_absolute_error_max"]<1.0e-5
assert provider["constraint_residual_absmax"]<1.0e-11
assert provider["archive_hash_locked"]
assert provider["class_a_source_hash_locked"]
assert provider["type_ix_D_source_hash_locked"]
assert provider["Bianchi_IX_D_event_required"]
assert provider["exceptional_tilted_VI_minus_1_over_9_fail_closed"]
assert provider["unvalidated_family_fail_closed"]
assert not provider["all_11_family_production_support_claimed"]
assert len(list(csv.DictReader((ROOT/"PARENT_PROVENANCE_FIREWALL.csv").open())))==3
assert len(list(csv.DictReader((ROOT/"BIANCHI_II_PROVIDER_PILOT.csv").open())))==3
with np.load(ROOT/"pr05c2c1b2b1d_parent_provider_v072.npz") as data:
    assert data["provider_end_normalized_state"].shape==(3,)
    assert data["accepted_parent_payload"].dtype==np.uint8
manifest={{}}
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1); manifest[name]=digest
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(metrics["status"])
'''


def write_bundle_index() -> None:
    index_path = ROOT / "state" / "BUNDLE_INDEX.json"
    rows = json.loads(index_path.read_text(encoding="utf-8"))
    rows = [row for row in rows if int(row.get("version", -999)) != VERSION]
    rows.append(
        {
            "bundle": BUNDLE.name,
            "sha256": sha256(BUNDLE),
            "size_bytes": BUNDLE.stat().st_size,
            "version": VERSION,
        }
    )
    rows.sort(key=lambda row: (int(row.get("version", -1)), str(row.get("bundle", ""))))
    write_json(index_path, rows)


def main() -> None:
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="pr05c2c1b2b1d-harness-") as temporary:
        work = Path(temporary)
        harnesses = {
            "research": validate_harness(
                RESEARCH_HARNESS,
                RESEARCH_HARNESS_SHA256,
                "validate_workspace.py",
                work,
                EXPANDED / "RESEARCH_HARNESS_VALIDATION.log",
            ),
            "coding": validate_harness(
                CODING_HARNESS,
                CODING_HARNESS_SHA256,
                "validate_harness.py",
                work,
                EXPANDED / "CODING_HARNESS_VALIDATION.log",
            ),
        }

    firewall_rows, firewall_metrics, parent_payload = firewall_evidence()
    provider_rows, provider_metrics, provider_arrays = provider_evidence()
    metrics = {
        "classification": "PR05C2C1B2B1D_NUMERICAL_METRICS",
        "status": STATUS,
        "parent_firewall": firewall_metrics,
        "background_provider": provider_metrics,
        "R1_complete": True,
        "R2_complete": True,
        "R3_source_derived_parent_reconstruction_open": True,
        "continuation_or_preconditioner_selected": False,
        "all_11_provider_support_claimed": False,
    }

    write_csv(EXPANDED / "PARENT_PROVENANCE_FIREWALL.csv", firewall_rows)
    write_csv(EXPANDED / "BIANCHI_II_PROVIDER_PILOT.csv", provider_rows)
    write_json(EXPANDED / "NUMERICAL_METRICS.json", metrics)
    write_json(EXPANDED / "HARNESS_EXECUTION_RECEIPT.json", harnesses)
    write_json(
        EXPANDED / "SOURCE_PROVENANCE.json",
        {
            "uploaded_solver_archive": str(SOLVER_ARCHIVE.relative_to(ROOT)),
            "archive_sha256": BIANCHI_REVIEW_ARCHIVE_SHA256,
            "class_a_source_sha256": BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256,
            "type_ix_D_source_sha256": BIANCHI_REVIEW_TYPE_IX_D_SOURCE_SHA256,
            "locked_v048_background_sha256": sha256(LOCKED_BACKGROUND),
        },
    )
    write_json(
        EXPANDED / "PR05C2C1B2B1D_ledger.json",
        {
            "classification": "PR05C2C1B2B1D_DURABLE_LEDGER",
            "status": STATUS,
            "stage": "PR-05C2C1B2B1D/v0.72",
            "R1_parent_provenance_firewall": "COMPLETE",
            "R2_orthogonal_Bianchi_II_provider_pilot": "COMPLETE",
            "R3_source_derived_parent_reconstruction": "OPEN",
            "metrics": metrics,
            "claim": "production parent provenance and one dynamic background provider lane are fail-closed and verified",
            "not_claimed": [
                "physical source-derived accepted parent",
                "accepted physical macro trajectory",
                "finite-tilt or all-family provider validation",
                "preconditioner or Rust selection",
            ],
            "next": "PR05C2C1B2B1E_SOURCE_DERIVED_ACCEPTED_PARENT_RECONSTRUCTION",
        },
    )
    write_json(
        EXPANDED / "HARD_GATE_LEDGER.json",
        {
            "R1_parent_provenance_firewall": "COMPLETE",
            "R2_orthogonal_Bianchi_II_provider_pilot": "COMPLETE",
            "R3_source_derived_parent_reconstruction": "OPEN",
            "operator_verification_parent_in_production": "FORBIDDEN",
            "all_11_provider_claim": "FORBIDDEN",
            "tilted_exceptional_VI_minus_1_over_9": "UNSUPPORTED_FAIL_CLOSED",
            "Bianchi_IX_H_zero": "D_NORMALIZED_EVENT_REQUIRED",
            "preconditioner_selection": "DEFERRED",
            "Rust_backend": "DEFERRED",
        },
    )
    write_json(
        EXPANDED / "CLAIM_BOUNDARY.json",
        {
            "implemented": [
                "content-addressed production-parent provenance boundary",
                "exact parent serialization and stale-provenance rejection",
                "orthogonal expanding Bianchi-II dynamic provider pilot",
                "SI H/sigma/N/time reconstruction",
                "IX and exceptional branch fail-closed events",
            ],
            "not_claimed": [
                "physical source-derived accepted parent",
                "accepted physical macro trajectory",
                "finite-tilt provider validation",
                "all-11 provider validation",
                "preconditioner selection",
                "Rust parity or speedup",
            ],
        },
    )

    arrays = dict(provider_arrays)
    arrays["accepted_parent_payload"] = parent_payload
    deterministic_npz(EXPANDED / DATA.name, arrays)
    deterministic_npz(DATA, arrays)
    write_provider_plot(provider_rows, EXPANDED / "BIANCHI_II_PROVIDER_PILOT.png")

    FORMALISM.write_text(formalism_text(metrics), encoding="utf-8")
    REPORT.write_text(report_text(metrics), encoding="utf-8")
    NEXT_PLAN.write_text(next_plan_text(), encoding="utf-8")
    for document in (FORMALISM, REPORT, NEXT_PLAN):
        shutil.copy2(document, EXPANDED / document.name)

    verifier = EXPANDED / "verify_PR05C2C1B2B1D.py"
    verifier.write_text(artifact_verifier_source(), encoding="utf-8")
    verifier.chmod(0o755)
    manifest_paths = sorted(
        path for path in EXPANDED.iterdir()
        if path.is_file() and path.name != "MANIFEST_SHA256.txt"
    )
    (EXPANDED / "MANIFEST_SHA256.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in manifest_paths),
        encoding="utf-8",
    )
    verification = subprocess.run([sys.executable, str(verifier)], cwd=EXPANDED)
    if verification.returncode:
        raise SystemExit(verification.returncode)
    deterministic_zip(EXPANDED, BUNDLE)
    write_bundle_index()
    print(STATUS)
    print(f"artifact_sha256={sha256(BUNDLE)}")
    print(f"data_sha256={sha256(DATA)}")
    print(f"generated_utc={datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
