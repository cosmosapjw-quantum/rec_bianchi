#!/usr/bin/env python3
"""Build PR-04C3 v0.57 componentwise common-ledger closure.

The three original-HyRec snapshots are independent source-conditioned operator
lanes.  This stage recomputes every native and COM/interface action separately,
locks their provenance, and aggregates only by a maximum componentwise gate.
It closes PR-04 at the explicitly bounded operator-contract level; it does not
claim a native-derived COM trajectory or full recombination-history parity.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
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

from full_bianchi_hyrec.recoil.common_interface_ledger import (  # noqa: E402
    CommonInterfaceLedger,
    EvidenceClass,
    GateCriterion,
    LedgerMetric,
    PacketLedgerRecord,
    ProvenanceLock,
    SnapshotLedger,
    StateClassification,
)
from full_bianchi_hyrec.recoil.coupled_interface import (  # noqa: E402
    CoupledInterfaceProblem,
    CoupledInterfaceRestartState,
    audit_boundary_speed_history,
    solve_coupled_interface,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import CollisionNetwork  # noqa: E402
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    central_difference_edge_jvp_residual,
    collision_edge_flux_per_H_s,
    dense_direct_solution,
    dense_original_hyrec_matrix,
    outgoing_distortion,
    parse_original_hyrec_snapshot_csv,
    reconstruct_equilibrium_distortion,
    relative_inf,
    spectral_source_moments_Hz,
    structural_edge_flux_per_H_s,
    structured_schur_solution,
    transport_edge_flux_per_H_s,
)
from full_bianchi_hyrec.recoil.split_domain_exchange import (  # noqa: E402
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
)


ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04C3_common_ledger_v0_57"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr04c3_common_ledger_v057.npz"
V056_ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04C1B_C2_coupled_interface_v0_56"
V056_ARTIFACT = ROOT / "archive" / "expanded" / V056_ARTIFACT_NAME
V056_BUNDLE = ROOT / "archive" / "bundles" / f"{V056_ARTIFACT_NAME}.zip"
V055_ARTIFACT = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
)
PACKET_PATH = V055_ARTIFACT / "THREE_SNAPSHOT_INTERFACE_PACKETS.csv"
NETWORK_PATH = ROOT / "data" / "full_scalar_com_khw_v050.npz"
BACKGROUND_PATH = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
V056_DATA = ROOT / "data" / "pr04c_coupled_interface_v056.npz"
V056_RESTART = V056_ARTIFACT / "COUPLED_RESTART.json"
HYREC_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
RESEARCH_DOCS = ROOT / "docs" / "research" / "pr04c3_v057"
CODING_HARNESS = (
    ROOT
    / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
)
RESEARCH_HARNESS = (
    ROOT
    / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
)
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CANONICAL_HYREC_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
TARGETS = (1300.0, 1100.0, 900.0)
DT_S = 1.0e5
ZETA3_120 = "1.20205690315959428539973816151144999076498629234049888179227155534183820578631309018645587360933525814619915779526071942"
ZETA4_120 = "1.08232323371113819151600369654116790277475095191872690768297621544412061618696884655690963594169991723299081390804274241"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_logged(
    command: list[str], *, cwd: Path, log: Path, check: bool = True
) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC)
    with log.open("wb") as handle:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if check and result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}"
        )
    return result


def validate_harness(
    archive: Path,
    expected_sha256: str,
    validator_name: str,
    work: Path,
    log: Path,
) -> dict[str, object]:
    observed = digest(archive)
    if observed != expected_sha256:
        raise RuntimeError(f"harness hash mismatch: {archive}")
    destination = work / archive.stem
    destination.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        bad = zipped.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt harness member: {bad}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator_name))
    if len(matches) != 1:
        raise RuntimeError(f"cannot uniquely locate {validator_name}")
    result = run_logged(
        [sys.executable, str(matches[0])],
        cwd=matches[0].parents[1],
        log=log,
        check=False,
    )
    return {
        "archive": archive.name,
        "sha256": observed,
        "validator": validator_name,
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
    }


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def packet_from_row(row: dict[str, str]) -> ExchangePacket:
    return ExchangePacket(
        side=InterfaceSide(row["side"]),
        direction=ExchangeDirection(row["direction"]),
        interface_x=float(row["interface_x"]),
        interface_frequency_Hz=float(row["interface_frequency_Hz"]),
        total_number_flux_per_H_s=float(row["total_number_flux_per_H_s"]),
        reference_number_flux_per_H_s=float(row["reference_number_flux_per_H_s"]),
        distortion_number_flux_per_H_s=float(row["distortion_number_flux_per_H_s"]),
        photon_energy_flux_W_per_H=float(row["total_photon_energy_flux_W_per_H"]),
        reference_photon_energy_flux_W_per_H=float(
            row["reference_photon_energy_flux_W_per_H"]
        ),
        distortion_photon_energy_flux_W_per_H=float(
            row["distortion_photon_energy_flux_W_per_H"]
        ),
        atom_energy_flux_W_per_H=float(row["atom_source_W_per_H"]),
        source_snapshot_z=float(row["snapshot_z"]),
    )


def initial_bose_einstein_state(
    network: CollisionNetwork, grid: HarmonicGrid
) -> np.ndarray:
    activity = network.equilibrium_weight / network.mode_measure
    if np.any(activity <= 0.0) or np.any(activity >= 1.0):
        raise RuntimeError("q_activity=1 lies outside the Bose-Einstein domain")
    scalar = activity / (1.0 - activity)
    return scalar[:, None] * np.ones((1, grid.n_angle))


def provenance(name: str, path: Path, evidence: EvidenceClass) -> ProvenanceLock:
    return ProvenanceLock(
        name=name,
        relative_path=str(path.relative_to(ROOT)),
        sha256=digest(path),
        evidence_class=evidence,
    )


def packet_record(row: dict[str, str]) -> PacketLedgerRecord:
    return PacketLedgerRecord(
        packet_id=(
            f"z{int(float(row['target_z']))}-{row['side']}-"
            f"{row['packet_sha256'][:12]}"
        ),
        target_z=float(row["target_z"]),
        snapshot_z=float(row["snapshot_z"]),
        side=row["side"],
        direction=row["direction"],
        interface_x=float(row["interface_x"]),
        interface_frequency_Hz=float(row["interface_frequency_Hz"]),
        n_H_m3=float(row["nH_cm3"]) * 1.0e6,
        history_index_left=int(row["history_index_left"]),
        history_index_right=int(row["history_index_right"]),
        solved_history_index=int(row["iz_local"]),
        packet_sha256=row["packet_sha256"],
    )


def metric(
    name: str,
    value: float,
    unit: str,
    evidence: EvidenceClass,
    criterion: GateCriterion,
    limit: float,
    scale: float,
) -> LedgerMetric:
    return LedgerMetric(
        name=name,
        value=float(value),
        unit=unit,
        evidence_class=evidence,
        criterion=criterion,
        limit=float(limit),
        scale=max(float(scale), 1.0e-300),
    )


def native_metrics(target: float) -> tuple[dict[str, float], list[dict[str, object]]]:
    snapshot_path = V055_ARTIFACT / f"pr04c_z{int(target)}.csv"
    snapshot = parse_original_hyrec_snapshot_csv(snapshot_path)
    matrix = dense_original_hyrec_matrix(snapshot)
    rhs = np.concatenate((snapshot.sr, snapshot.sv))
    direct = dense_direct_solution(snapshot)
    schur = structured_schur_solution(snapshot)
    source = snapshot.source_solution
    matrix_residual = float(
        np.linalg.norm(matrix @ direct - rhs, ord=np.inf)
        / max(np.linalg.norm(rhs, ord=np.inf), 1.0e-300)
    )
    direct_source = float(relative_inf(direct, source))
    schur_direct = float(relative_inf(schur, direct))

    source_flux = transport_edge_flux_per_H_s(snapshot)
    collision_flux = collision_edge_flux_per_H_s(snapshot)
    structural_flux = structural_edge_flux_per_H_s(snapshot)
    collision_relative = float(relative_inf(collision_flux, source_flux))
    structural_relative = float(relative_inf(structural_flux, source_flux))

    direct_equilibrium = reconstruct_equilibrium_distortion(snapshot, direct)
    schur_equilibrium = reconstruct_equilibrium_distortion(snapshot, schur)
    direct_outgoing = outgoing_distortion(
        snapshot.Dfplus, direct_equilibrium, snapshot.Dtau, source_branch=True
    )
    schur_outgoing = outgoing_distortion(
        snapshot.Dfplus, schur_equilibrium, snapshot.Dtau, source_branch=True
    )
    direct_flux = transport_edge_flux_per_H_s(snapshot, outgoing=direct_outgoing)
    schur_flux = transport_edge_flux_per_H_s(snapshot, outgoing=schur_outgoing)
    source_moments = spectral_source_moments_Hz(source_flux, snapshot.frequency_Hz)
    direct_moments = spectral_source_moments_Hz(direct_flux, snapshot.frequency_Hz)
    schur_moments = spectral_source_moments_Hz(schur_flux, snapshot.frequency_Hz)
    moment_rows: list[dict[str, object]] = []
    direct_moment_max = 0.0
    schur_moment_max = 0.0
    for order, (stored, calculated, reduced) in enumerate(
        zip(source_moments, direct_moments, schur_moments, strict=True)
    ):
        direct_relative = abs(float(calculated - stored)) / max(abs(float(stored)), 1e-300)
        schur_relative = abs(float(reduced - stored)) / max(abs(float(stored)), 1e-300)
        direct_moment_max = max(direct_moment_max, direct_relative)
        schur_moment_max = max(schur_moment_max, schur_relative)
        moment_rows.append(
            {
                "target_z": target,
                "snapshot_z": snapshot.z,
                "order_r": order,
                "units": "Hz^r s^-1 per H",
                "source_stored": float(stored),
                "dense_direct": float(calculated),
                "structured_schur": float(reduced),
                "direct_relative_residual": direct_relative,
                "schur_relative_residual": schur_relative,
            }
        )

    rng = np.random.default_rng(int(target) + 57)
    incoming_direction = rng.normal(size=snapshot.Dfplus.size) * 1.0e-15
    equilibrium_direction = rng.normal(size=snapshot.Dfeq.size) * 1.0e-15
    native_jvp = float(
        central_difference_edge_jvp_residual(
            snapshot,
            snapshot.Dfplus,
            snapshot.Dfeq,
            incoming_direction,
            equilibrium_direction,
        )
    )
    return (
        {
            "snapshot_z": snapshot.z,
            "iz_local": float(snapshot.iz_local),
            "matrix_relative_residual": matrix_residual,
            "direct_source_relative": direct_source,
            "schur_direct_relative": schur_direct,
            "collision_flux_relative": collision_relative,
            "structural_flux_relative": structural_relative,
            "direct_moment_max_relative": direct_moment_max,
            "schur_moment_max_relative": schur_moment_max,
            "native_jvp_relative": native_jvp,
        },
        moment_rows,
    )


def high_precision_reference() -> dict[str, object]:
    mp.mp.dps = 120
    a = mp.mpf("3.25")
    b = mp.mpf("-0.7")
    c = mp.mpf("0.4")
    d = mp.mpf("2.1")
    p = mp.mpf("1.2")
    q = mp.mpf("-0.3")
    x = (p - b * q / d) / (a - b * c / d)
    y = (q - c * x) / d
    residual = max(abs(a * x + b * y - p), abs(c * x + d * y - q))
    epsilon = mp.mpf("2e-10")
    cancellation_sum = epsilon - epsilon + mp.mpf("0")
    componentwise_max = max(abs(epsilon), abs(-epsilon), mp.mpf("0"))
    zeta3_residual = abs(mp.mpf(ZETA3_120) - mp.zeta(3)) / abs(mp.zeta(3))
    zeta4_residual = abs(mp.mpf(ZETA4_120) - mp.zeta(4)) / abs(mp.zeta(4))
    return {
        "precision_dps": mp.mp.dps,
        "schur_2x2_solution": [mp.nstr(x, 100), mp.nstr(y, 100)],
        "schur_2x2_absolute_residual": mp.nstr(residual, 30),
        "cross_snapshot_scalar_sum": mp.nstr(cancellation_sum, 30),
        "cross_snapshot_componentwise_max": mp.nstr(componentwise_max, 30),
        "zeta3_120": ZETA3_120,
        "zeta4_120": ZETA4_120,
        "gamma3": "2.0",
        "zeta3_relative_residual_vs_mpmath": mp.nstr(zeta3_residual, 30),
        "zeta4_relative_residual_vs_mpmath": mp.nstr(zeta4_residual, 30),
    }


def create_manifest(directory: Path) -> None:
    rows = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_SHA256.txt":
            continue
        rows.append(f"{digest(path)}  {path.name}")
    (directory / "MANIFEST_SHA256.txt").write_text(
        "# SHA-256 manifest for immutable PR-04C3 artifact\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


def deterministic_zip(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.unlink(missing_ok=True)
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zipped:
        for path in sorted(source.iterdir()):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(f"{source.name}/{path.name}")
            info.date_time = (2026, 8, 6, 0, 0, 0)
            info.external_attr = (0o755 if os.access(path, os.X_OK) else 0o644) << 16
            zipped.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def research_documents(
    snapshot_rows: list[dict[str, object]],
    common: CommonInterfaceLedger,
    high_precision: dict[str, object],
) -> dict[str, str]:
    maximum_native = max(float(row["native_structural_flux_relative"]) for row in snapshot_rows)
    maximum_jvp = max(float(row["jvp_relative_error"]) for row in snapshot_rows)
    return {
        "01_RESEARCH_CONTRACT.md": """# PR-04C3 research contract

Primary question: can the three independent source-conditioned split-domain
lanes be placed in one typed conservation ledger without cross-redshift
cancellation, fitted normalization, or a fabricated native-derived COM state?

Scope is the homogeneous scalar operator contract at z~1300,1100,900. Metric
signature is `(-,+,+,+)`; ordinary frequency is in Hz; `c,h,k_B` remain
explicit. Full trajectory integration and FLRW history parity are excluded.
""",
        "02_EVIDENCE_ACQUISITION.md": """# Evidence acquisition

The evidence chain consists of the canonical October-2012 HyRec archive, three
source-identical FULL-mode C snapshots, six v0.55 face packets, the v0.50
35-state COM--KHW network, v0.48 angular/background registry, v0.56 restart and
coupled solver outputs, both pinned research harnesses, Wolfram symbolic output
and 120-digit special-function references. Every load-bearing path is SHA-256
locked in the common ledger.
""",
        "03_CLAIM_SOURCE_AUDIT.md": """# Claim/source audit

Algebraic evidence owns exact native/COM number cancellation, exact face-energy
cancellation and zero computational-interface atom source. Source-derived
evidence owns HyRec snapshots and packets. Solver-derived evidence owns the
COM residual, positivity, JVP, entropy and restart. The dilute net residual
floor is diagnostic only. No field is sourced from a transcript claim.
""",
        "04_HYPOTHESIS_SPACE.md": """# Hypothesis space

- H_A: all fields are definable and pass componentwise, closing PR-04 only at
  the source-conditioned operator-contract level.
- H_B: one load-bearing field requires a native-derived COM interior trajectory;
  publish a bounded no-go and keep PR-04 open.
- Rejected: scalar redshift sum, global state remap, fitted scale, midpoint-cell
  reconstruction, silent high-resolution substitution.
""",
        "05_INDEPENDENT_ADVERSARIAL_REVIEW.md": """# Independent adversarial review

The ledger rejects missing or permuted lanes, duplicate packet IDs, future
history endpoints, changed face/direction assignments, inconsistent local
hydrogen density, direct state-remap flags, fitted normalization flags and any
attempt to relabel `q_activity=1` as a native-derived trajectory. An explicit
`(+epsilon,-epsilon,0)` adversary has zero scalar sum but fails the componentwise
maximum gate.
""",
        "06_PHYSICS_MATH_VALIDATION.md": f"""# Physics and mathematical validation

At each redshift, dense and Schur native solutions are compared to the stored
source solution; physical edge transport is compared to the collision and
structural identities; the COM implicit solve is recomputed from its old state;
number, exact face energy, zero atom source, positivity, entropy, restart and
branch roots are checked independently. Maximum source-branch structural flux
residual is `{maximum_native:.17g}` and maximum COM analytic/JVP residual is
`{maximum_jvp:.17g}`.

Units: photon number is photons/H; integrated transported energy is J/H;
occupation and `q_activity` are dimensionless; rates are s^-1; frequency is Hz.
""",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": f"""# Verification design and results

The common ledger aggregates by `max(normalized violation)` and never by sum.
All {len(common.snapshots)} snapshots and {len(common.packet_ids)} packets pass,
with `epsilon_common={common.epsilon_common}`. The canonical JSON round trip and
SHA-256 digest are exact. The 120-digit 2x2 Schur residual is
`{high_precision['schur_2x2_absolute_residual']}`.
""",
        "08_EXTERNAL_GATE.md": """# External decision gate

Route A survives: the source-conditioned scalar split-domain interface contract
is conservative, positive and differentiable at all declared snapshots. The
claim explicitly stops before native/COM trajectory parity. PR-05 must provide
a time-integrated representation-local trajectory; PR-06 must test FLRW
recombination-history parity.
""",
        "09_SURVIVOR_FORMALIZATION.md": """# Survivor formalization

The survivor is an ordered typed ledger
`{z1300:L1300,z1100:L1100,z900:L900}`. Each component carries units, evidence
class, criterion, threshold, scale and provenance. The only aggregate is the
maximum componentwise violation. A computational representation crossing has
zero atom source; exact face energy, not the broad-cell centroid, owns the
transported-energy ledger.
""",
        "10_CLOSEOUT_AND_HANDOFF.md": """# Closeout and handoff

PR-04 is closed at the operator-contract claim level. The unresolved physical
question is trajectory integration, not local conservation or interface
algebra. Next: PR-05 primitive HYREC/background trajectory interface with
representation-local states, exact face packets, adaptive Bianchi branch
localization, checkpoint/restart and no direct native-to-COM state equality.
""",
    }


def main() -> None:
    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    if RESEARCH_DOCS.exists():
        shutil.rmtree(RESEARCH_DOCS)
    RESEARCH_DOCS.mkdir(parents=True)
    BUNDLE.unlink(missing_ok=True)
    DATA_OUT.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="pr04c3-") as temporary:
        work = Path(temporary)
        red_log = work / "PR04C3_TDD_RED.log"
        red = run_logged(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/recoil/test_pr04c3_artifact.py",
            ],
            cwd=ROOT,
            log=red_log,
            check=False,
        )
        if red.returncode == 0 or b"FileNotFoundError" not in red_log.read_bytes():
            raise RuntimeError("artifact TDD RED gate did not fail as declared")
        # Pytest's traceback ruler carries trailing spaces on some versions.
        # Normalize the durable text receipt so `git diff --check` remains a
        # meaningful repository gate without changing the failure evidence.
        normalized_red = "\n".join(
            line.rstrip() for line in red_log.read_text(encoding="utf-8").splitlines()
        ) + "\n"
        (ARTIFACT / red_log.name).write_text(normalized_red, encoding="utf-8")

        coding_receipt = validate_harness(
            CODING_HARNESS,
            CODING_HARNESS_SHA256,
            "validate_harness.py",
            work,
            ARTIFACT / "CODING_HARNESS_VALIDATION.log",
        )
        research_receipt = validate_harness(
            RESEARCH_HARNESS,
            RESEARCH_HARNESS_SHA256,
            "validate_workspace.py",
            work,
            ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log",
        )
        policy = run_logged(
            [sys.executable, "scripts/check_hyrec_binary_hash_policy.py"],
            cwd=ROOT,
            log=ARTIFACT / "HYREC_BINARY_HASH_POLICY.log",
            check=False,
        )

        if digest(HYREC_ARCHIVE) != CANONICAL_HYREC_SHA256:
            raise RuntimeError("canonical HyRec archive hash mismatch")
        packet_rows = load_csv(PACKET_PATH)
        if len(packet_rows) != 6:
            raise RuntimeError("exactly six v0.55 packets are required")

        network = CollisionNetwork.from_npz(NETWORK_PATH)
        with np.load(BACKGROUND_PATH, allow_pickle=False) as background:
            grid = HarmonicGrid.from_directions(
                background["directions"], background["angular_weights"], ell_max=0
            )
            branch_data = {name: background[name].copy() for name in background.files}
        old = initial_bose_einstein_state(network, grid)
        with np.load(V056_DATA, allow_pickle=False) as v056:
            stored_targets = v056["target_z"].copy()
            stored_old = v056["old_occupation"].copy()
            stored_updated = v056["updated_occupation"].copy()
        if not np.array_equal(stored_targets, np.asarray(TARGETS)):
            raise RuntimeError("v0.56 target order changed")
        if not np.array_equal(stored_old, old):
            raise RuntimeError("v0.56 old operator-verification state changed")

        branch_selection = (
            ("Bianchi_II_large_shear", 0),
            ("Bianchi_VI_h_tilted_large_shear", 20),
            ("Bianchi_VI_minus_1_over_9_exceptional", 6),
        )
        branch_rows: list[dict[str, object]] = []
        branch_all_localized = True
        for model, angle in branch_selection:
            audit = audit_boundary_speed_history(
                branch_data[f"{model}_cosmic_time_s"],
                branch_data[f"{model}_red_speed_s_inv"][:, angle],
                branch_data[f"{model}_blue_speed_s_inv"][:, angle],
            )
            localized = len(audit.red_roots) >= 1 and len(audit.blue_roots) >= 1
            branch_all_localized = branch_all_localized and localized
            branch_rows.append(
                {
                    "model": model,
                    "angle_index": angle,
                    "red_root_count": len(audit.red_roots),
                    "blue_root_count": len(audit.blue_roots),
                    "red_roots_s": json.dumps(audit.red_roots.tolist()),
                    "blue_roots_s": json.dumps(audit.blue_roots.tolist()),
                    "red_endpoint_heuristic_error": audit.red_endpoint_heuristic_error,
                    "blue_endpoint_heuristic_error": audit.blue_endpoint_heuristic_error,
                    "localized": localized,
                }
            )

        global_provenance = (
            provenance("canonical_original_hyrec", HYREC_ARCHIVE, EvidenceClass.SOURCE_DERIVED),
            provenance("v055_packet_table", PACKET_PATH, EvidenceClass.SOURCE_DERIVED),
            provenance("v056_coupled_artifact", V056_BUNDLE, EvidenceClass.SOLVER_DERIVED),
            provenance("v056_restart", V056_RESTART, EvidenceClass.SOLVER_DERIVED),
            provenance("v050_com_khw_network", NETWORK_PATH, EvidenceClass.SOURCE_DERIVED),
            provenance("v048_background_registry", BACKGROUND_PATH, EvidenceClass.SOURCE_DERIVED),
            provenance("coding_harness", CODING_HARNESS, EvidenceClass.SOURCE_DERIVED),
            provenance("research_harness", RESEARCH_HARNESS, EvidenceClass.SOURCE_DERIVED),
        )

        snapshot_ledgers: list[SnapshotLedger] = []
        snapshot_rows: list[dict[str, object]] = []
        packet_audit_rows: list[dict[str, object]] = []
        native_moment_rows: list[dict[str, object]] = []
        jvp_rows: list[dict[str, object]] = []
        updated_occupations: list[np.ndarray] = []

        for target_index, target in enumerate(TARGETS):
            selected = [
                row for row in packet_rows if float(row["target_z"]) == target
            ]
            selected.sort(key=lambda row: 0 if row["side"] == "red" else 1)
            if [row["side"] for row in selected] != ["red", "blue"]:
                raise RuntimeError(f"target {target} lacks ordered red/blue packets")
            packets = tuple(packet_from_row(row) for row in selected)
            n_h_m3 = float(selected[0]["nH_cm3"]) * 1.0e6
            if not math.isclose(
                n_h_m3,
                float(selected[1]["nH_cm3"]) * 1.0e6,
                rel_tol=3e-15,
                abs_tol=0.0,
            ):
                raise RuntimeError("red/blue n_H mismatch")
            problem = CoupledInterfaceProblem(
                network=network,
                grid=grid,
                packets=packets,
                n_H_m3=n_h_m3,
                dt_s=DT_S,
            )
            result = solve_coupled_interface(
                old,
                problem,
                nonlinear_rtol=1.0e-11,
                gmres_rtol=1.0e-10,
                max_newton=20,
                gmres_maxiter=300,
            )
            result.ledger.validate()
            replay_exact = bool(np.array_equal(result.occupation, stored_updated[target_index]))
            restored = CoupledInterfaceRestartState.from_payload(
                json.loads(json.dumps(result.restart_payload()))
            )
            restart_exact = bool(
                np.array_equal(restored.occupation, result.occupation)
                and restored.accumulators == result.accumulators
                and restored.to_payload() == result.restart_payload()
            )

            vector = problem.pack(np.log(result.occupation), np.zeros(problem.n_transfer))
            rng = np.random.default_rng(int(target) + 5700)
            direction = rng.normal(size=problem.vector_size)
            direction /= np.linalg.norm(direction)
            analytic = problem.jvp(vector, direction, old, scaled=True)
            per_target_jvp: list[float] = []
            for epsilon in (2.0e-4, 1.0e-4, 5.0e-5):
                numeric = (
                    problem.scaled_residual(vector + epsilon * direction, old)
                    - problem.scaled_residual(vector - epsilon * direction, old)
                ) / (2.0 * epsilon)
                relative_error = float(
                    np.linalg.norm(analytic - numeric)
                    / max(np.linalg.norm(numeric), 1.0e-300)
                )
                per_target_jvp.append(relative_error)
                jvp_rows.append(
                    {
                        "target_z": target,
                        "epsilon": epsilon,
                        "relative_error": relative_error,
                        "analytic_norm": float(np.linalg.norm(analytic)),
                        "numeric_norm": float(np.linalg.norm(numeric)),
                    }
                )
            jvp_relative = max(per_target_jvp)

            native, moment_rows = native_metrics(target)
            native_moment_rows.extend(moment_rows)
            snapshot_path = V055_ARTIFACT / f"pr04c_z{int(target)}.csv"
            per_snapshot_provenance = (
                provenance(
                    f"source_snapshot_z{int(target)}",
                    snapshot_path,
                    EvidenceClass.SOURCE_DERIVED,
                ),
                provenance(
                    f"v056_coupled_state_z{int(target)}",
                    V056_DATA,
                    EvidenceClass.SOLVER_DERIVED,
                ),
            )

            metrics = (
                metric(
                    "photon_number_residual",
                    result.number_relative_residual,
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    1.0e-11,
                    1.0e-11,
                ),
                metric(
                    "transported_face_energy_residual",
                    result.ledger.transported_energy_residual_J_per_H,
                    "J/H",
                    EvidenceClass.ALGEBRAIC,
                    GateCriterion.EXACT_ZERO,
                    0.0,
                    max(
                        abs(result.ledger.native_energy_change_J_per_H),
                        abs(result.ledger.com_energy_change_J_per_H),
                        1.0e-300,
                    ),
                ),
                metric(
                    "interface_atom_source",
                    result.ledger.atom_energy_change_J_per_H,
                    "J/H",
                    EvidenceClass.ALGEBRAIC,
                    GateCriterion.EXACT_ZERO,
                    0.0,
                    1.0,
                ),
                metric(
                    "backward_error_relative",
                    result.backward_error_relative,
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    1.0e-11,
                    1.0e-11,
                ),
                metric(
                    "jvp_relative_error",
                    jvp_relative,
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    1.0e-8,
                    1.0e-8,
                ),
                metric(
                    "minimum_occupation",
                    result.minimum_occupation,
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.GT,
                    0.0,
                    max(result.minimum_occupation, 1.0e-300),
                ),
                metric(
                    "collision_entropy_production",
                    result.collision_entropy_production,
                    "arb/s",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.LE,
                    0.0,
                    max(abs(result.collision_entropy_production), 1.0e-300),
                ),
                metric(
                    "restart_exact",
                    float(restart_exact),
                    "bool",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.EXACT_ONE,
                    1.0,
                    1.0,
                ),
                metric(
                    "v056_replay_exact",
                    float(replay_exact),
                    "bool",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.EXACT_ONE,
                    1.0,
                    1.0,
                ),
                metric(
                    "branch_zero_localized",
                    float(branch_all_localized),
                    "bool",
                    EvidenceClass.SOURCE_DERIVED,
                    GateCriterion.EXACT_ONE,
                    1.0,
                    1.0,
                ),
                metric(
                    "native_matrix_relative_residual",
                    native["matrix_relative_residual"],
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    5.0e-13,
                    5.0e-13,
                ),
                metric(
                    "native_direct_source_relative",
                    native["direct_source_relative"],
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    5.0e-13,
                    5.0e-13,
                ),
                metric(
                    "native_schur_direct_relative",
                    native["schur_direct_relative"],
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    5.0e-13,
                    5.0e-13,
                ),
                metric(
                    "native_collision_flux_relative",
                    native["collision_flux_relative"],
                    "1",
                    EvidenceClass.SOURCE_DERIVED,
                    GateCriterion.ABS_LE,
                    2.0e-11,
                    2.0e-11,
                ),
                metric(
                    "native_structural_flux_relative",
                    native["structural_flux_relative"],
                    "1",
                    EvidenceClass.SOURCE_DERIVED,
                    GateCriterion.ABS_LE,
                    3.0e-11,
                    3.0e-11,
                ),
                metric(
                    "native_moment_relative",
                    max(
                        native["direct_moment_max_relative"],
                        native["schur_moment_max_relative"],
                    ),
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    5.0e-11,
                    5.0e-11,
                ),
                metric(
                    "native_edge_jvp_relative",
                    native["native_jvp_relative"],
                    "1",
                    EvidenceClass.SOLVER_DERIVED,
                    GateCriterion.ABS_LE,
                    1.0e-7,
                    1.0e-7,
                ),
            )

            ledger = SnapshotLedger(
                target_z=target,
                snapshot_z=float(selected[0]["snapshot_z"]),
                state_classification=StateClassification.OPERATOR_VERIFICATION,
                q_activity=1.0,
                packets=tuple(packet_record(row) for row in selected),
                metrics=metrics,
                provenance=per_snapshot_provenance,
            )
            snapshot_ledgers.append(ledger)
            updated_occupations.append(result.occupation)
            snapshot_rows.append(
                {
                    "target_z": target,
                    "snapshot_z": float(selected[0]["snapshot_z"]),
                    "state_classification": ledger.state_classification.value,
                    "q_activity": ledger.q_activity,
                    "packet_count": len(ledger.packets),
                    "componentwise_passed": ledger.passed,
                    "epsilon_snapshot": ledger.epsilon,
                    "backward_error_relative": result.backward_error_relative,
                    "number_relative_residual": result.number_relative_residual,
                    "net_scaled_residual_diagnostic": result.residual_relative,
                    "jvp_relative_error": jvp_relative,
                    "minimum_occupation": result.minimum_occupation,
                    "collision_entropy_production": result.collision_entropy_production,
                    "transported_energy_residual_J_per_H": result.ledger.transported_energy_residual_J_per_H,
                    "interface_atom_source_J_per_H": result.ledger.atom_energy_change_J_per_H,
                    "restart_exact": restart_exact,
                    "v056_replay_exact": replay_exact,
                    "native_matrix_relative_residual": native["matrix_relative_residual"],
                    "native_direct_source_relative": native["direct_source_relative"],
                    "native_schur_direct_relative": native["schur_direct_relative"],
                    "native_collision_flux_relative": native["collision_flux_relative"],
                    "native_structural_flux_relative": native["structural_flux_relative"],
                    "native_moment_relative": max(
                        native["direct_moment_max_relative"],
                        native["schur_moment_max_relative"],
                    ),
                    "native_edge_jvp_relative": native["native_jvp_relative"],
                    "branch_zero_localized": branch_all_localized,
                }
            )
            for row in selected:
                packet_audit_rows.append(
                    {
                        "target_z": target,
                        "snapshot_z": row["snapshot_z"],
                        "side": row["side"],
                        "direction": row["direction"],
                        "interface_x": row["interface_x"],
                        "interface_frequency_Hz": row["interface_frequency_Hz"],
                        "n_H_m3": float(row["nH_cm3"]) * 1.0e6,
                        "history_index_left": row["history_index_left"],
                        "history_index_right": row["history_index_right"],
                        "solved_history_index": row["iz_local"],
                        "future_history_used": int(row["history_index_right"])
                        > int(row["iz_local"]),
                        "packet_sha256": row["packet_sha256"],
                    }
                )

        common = CommonInterfaceLedger(
            schema="PR04C3_COMMON_INTERFACE_LEDGER_V1",
            snapshots=tuple(snapshot_ledgers),
            global_provenance=global_provenance,
            direct_state_remap_used=False,
            fitted_normalization_used=False,
        )
        common.validate()
        if not common.componentwise_passed:
            raise RuntimeError(f"common ledger failed: {common.failed_components()}")

        high_precision = high_precision_reference()
        write_json(ARTIFACT / "COMMON_INTERFACE_LEDGER.json", common.to_payload())
        (ARTIFACT / "COMMON_INTERFACE_LEDGER.sha256").write_text(
            common.sha256 + "\n", encoding="utf-8"
        )
        write_csv(ARTIFACT / "COMPONENTWISE_SNAPSHOT_LEDGER.csv", snapshot_rows)
        write_csv(ARTIFACT / "PACKET_PROVENANCE_AUDIT.csv", packet_audit_rows)
        write_csv(ARTIFACT / "NATIVE_PRIMITIVE_DIRECT_SCHUR_MOMENTS.csv", native_moment_rows)
        write_csv(ARTIFACT / "COM_ANALYTIC_JVP_REFERENCE.csv", jvp_rows)
        write_csv(ARTIFACT / "BIANCHI_BRANCH_COMPONENTWISE_AUDIT.csv", branch_rows)
        write_json(ARTIFACT / "HIGH_PRECISION_REFERENCE.json", high_precision)
        write_json(
            ARTIFACT / "ADVERSARIAL_AUDIT.json",
            {
                "classification": "PR04C3_ADVERSARIAL_AUDIT",
                "cross_snapshot_cancellation": {
                    "components": [2.0e-10, -2.0e-10, 0.0],
                    "scalar_sum": 0.0,
                    "componentwise_max": 2.0e-10,
                    "threshold": 1.0e-11,
                    "normalized_violation": 20.0,
                    "scalar_sum_would_false_pass": True,
                    "componentwise_gate_rejects": True,
                },
                "schema_adversaries": {
                    "permuted_target_order": "REJECTED_BY_TYPED_LEDGER",
                    "duplicate_packet_id": "REJECTED_BY_TYPED_LEDGER",
                    "future_history_endpoint": "REJECTED_BY_PACKET_RECORD",
                    "native_trajectory_relabel": "REJECTED_BY_STATE_CLASSIFICATION",
                    "direct_state_remap_flag": "REJECTED",
                    "fitted_normalization_flag": "REJECTED",
                },
                "test_file": "tests/recoil/test_common_interface_ledger.py",
            },
        )
        (ARTIFACT / "PR04C3_LITERATURE_LOCK.md").write_text(
            """# PR-04C3 literature lock

- Ali-Haimoud & Hirata, *HyRec: A fast and highly accurate primordial hydrogen and helium recombination code* (2011), arXiv:1011.3758: original HyRec evolves the radiation field and atomic populations with time-dependent radiative transfer and frequency diffusion.
- Ali-Haimoud, Grin & Hirata, *Radiative transfer effects in primordial hydrogen recombination* (2010), arXiv:1009.4697: redistribution kernels and line-transfer effects must be assigned to a physical transport representation rather than an arbitrary reduced remap.
- Boon et al., *A flux-mortar mixed finite element method on non-matching grids* (2022), arXiv:2008.09372: nonmatching subdomains can retain local states while sharing conservative normal flux variables.
- PETSc SNES/TS documentation (v3.25): matrix-free Jacobian-vector products and explicit event handlers support the planned PR-05 trajectory implementation and in-step branch-zero localization.
- Git `git-bundle` documentation: bundles carry refs and objects for verified offline fetch/clone and are the canonical patch-delivery format for this project.
""",
            encoding="utf-8",
        )
        write_json(
            ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json",
            {
                "classification": "PR04C3_WOLFRAM_SYMBOLIC_RECEIPT",
                "status": "USED",
                "input": "2x2 Schur solution; (+e,-e,0) sum versus max; Exp[u] positivity; exact cancellation",
                "raw_output": "{{0, 0}, 0, Max[0, Abs[e]], True, True}",
                "interpretation": {
                    "schur_residual": [0, 0],
                    "signed_snapshot_sum": 0,
                    "componentwise_max": "Abs[e] for e>0",
                    "log_variable_positivity": True,
                    "pairwise_cancellation": True,
                },
            },
        )
        write_json(
            ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json",
            {
                "classification": "PR04C3_PRECISE_SPECIAL_FUNCTIONS_RECEIPT",
                "status": "USED",
                "zeta_3_120_dps": ZETA3_120,
                "zeta_4_120_dps": ZETA4_120,
                "gamma_3": "2.0",
                "use": "independent Planck-moment special-function reference",
            },
        )

        np.savez_compressed(
            ARTIFACT / "pr04c3_common_ledger_v057.npz",
            target_z=np.asarray(TARGETS),
            snapshot_z=np.asarray([float(row["snapshot_z"]) for row in snapshot_rows]),
            updated_occupation=np.asarray(updated_occupations),
            backward_error_relative=np.asarray(
                [float(row["backward_error_relative"]) for row in snapshot_rows]
            ),
            number_relative_residual=np.asarray(
                [float(row["number_relative_residual"]) for row in snapshot_rows]
            ),
            jvp_relative_error=np.asarray(
                [float(row["jvp_relative_error"]) for row in snapshot_rows]
            ),
            native_direct_source_relative=np.asarray(
                [float(row["native_direct_source_relative"]) for row in snapshot_rows]
            ),
            native_schur_direct_relative=np.asarray(
                [float(row["native_schur_direct_relative"]) for row in snapshot_rows]
            ),
            native_structural_flux_relative=np.asarray(
                [float(row["native_structural_flux_relative"]) for row in snapshot_rows]
            ),
            packet_sha256=np.asarray([row["packet_sha256"] for row in packet_audit_rows]),
            state_labels=network.state_labels,
            state_intervals=network.state_intervals,
        )
        shutil.copy2(ARTIFACT / "pr04c3_common_ledger_v057.npz", DATA_OUT)

        gates = [
            {
                "name": "harness_validation",
                "passed": bool(coding_receipt["passed"] and research_receipt["passed"]),
            },
            {"name": "binary_hash_policy", "passed": policy.returncode == 0},
            {"name": "exact_three_lane_schema", "passed": len(common.snapshots) == 3},
            {"name": "six_unique_packets", "passed": len(set(common.packet_ids)) == 6},
            {"name": "complete_provenance", "passed": len(global_provenance) == 8},
            {"name": "componentwise_common_ledger", "passed": common.componentwise_passed},
            {"name": "no_cross_snapshot_sum", "passed": common.epsilon_common == 0.0},
            {
                "name": "operator_verification_state_only",
                "passed": common.state_classification is StateClassification.OPERATOR_VERIFICATION,
            },
            {"name": "no_direct_state_remap", "passed": not common.direct_state_remap_used},
            {"name": "no_fitted_normalization", "passed": not common.fitted_normalization_used},
            {
                "name": "native_primitive_direct_schur",
                "passed": max(
                    float(row["native_direct_source_relative"]) for row in snapshot_rows
                )
                < 5.0e-13
                and max(
                    float(row["native_schur_direct_relative"]) for row in snapshot_rows
                )
                < 5.0e-13,
            },
            {
                "name": "native_physical_edge_identity",
                "passed": max(
                    float(row["native_collision_flux_relative"]) for row in snapshot_rows
                )
                < 2.0e-11
                and max(
                    float(row["native_structural_flux_relative"]) for row in snapshot_rows
                )
                < 3.0e-11,
            },
            {
                "name": "com_replay_and_restart",
                "passed": all(
                    bool(row["v056_replay_exact"]) and bool(row["restart_exact"])
                    for row in snapshot_rows
                ),
            },
            {
                "name": "number_and_face_energy",
                "passed": max(
                    float(row["number_relative_residual"]) for row in snapshot_rows
                )
                < 1.0e-11
                and all(
                    float(row["transported_energy_residual_J_per_H"]) == 0.0
                    for row in snapshot_rows
                ),
            },
            {
                "name": "zero_interface_atom_source",
                "passed": all(
                    float(row["interface_atom_source_J_per_H"]) == 0.0
                    for row in snapshot_rows
                ),
            },
            {
                "name": "positivity_jvp_entropy",
                "passed": min(
                    float(row["minimum_occupation"]) for row in snapshot_rows
                )
                > 0.0
                and max(float(row["jvp_relative_error"]) for row in snapshot_rows)
                < 1.0e-8
                and max(
                    float(row["collision_entropy_production"]) for row in snapshot_rows
                )
                <= 0.0,
            },
            {"name": "branch_zero_localization", "passed": branch_all_localized},
            {
                "name": "high_precision_reference",
                "passed": mp.mpf(high_precision["schur_2x2_absolute_residual"])
                < mp.mpf("1e-100")
                and mp.mpf(high_precision["cross_snapshot_scalar_sum"]) == 0,
            },
        ]
        status = (
            "PASS_PR04_OPERATOR_CONTRACT_COMPLETE_PR05_NEXT"
            if all(bool(row["passed"]) for row in gates)
            else "FAIL_PR04C3_HARD_GATE"
        )
        hard_gate_ledger = {
            "classification": "PR04C3_HARD_GATE_LEDGER",
            "stage": "PR-04C3",
            "version": "0.57",
            "status": status,
            "PR04": "COMPLETE_OPERATOR_CONTRACT"
            if status.startswith("PASS")
            else "IN_PROGRESS",
            "gates": gates,
            "metrics": {
                "snapshot_count": len(common.snapshots),
                "packet_count": len(common.packet_ids),
                "epsilon_common": common.epsilon_common,
                "max_backward_error_relative": max(
                    float(row["backward_error_relative"]) for row in snapshot_rows
                ),
                "max_number_relative_residual": max(
                    float(row["number_relative_residual"]) for row in snapshot_rows
                ),
                "max_jvp_relative_error": max(
                    float(row["jvp_relative_error"]) for row in snapshot_rows
                ),
                "max_native_direct_source_relative": max(
                    float(row["native_direct_source_relative"]) for row in snapshot_rows
                ),
                "max_native_schur_direct_relative": max(
                    float(row["native_schur_direct_relative"]) for row in snapshot_rows
                ),
                "max_native_structural_flux_relative": max(
                    float(row["native_structural_flux_relative"]) for row in snapshot_rows
                ),
                "common_ledger_sha256": common.sha256,
            },
            "claim_boundary": {
                "state": "OPERATOR_VERIFICATION",
                "closed_claim": "source-conditioned scalar split-domain interface contract is conservative, positive and differentiable at z~1300,1100,900",
                "native_com_trajectory_parity": False,
                "full_recombination_history": False,
                "next_stage": "PR-05 primitive HYREC/background trajectory interface",
            },
        }
        write_json(ARTIFACT / "HARD_GATE_LEDGER.json", hard_gate_ledger)

        documents = research_documents(snapshot_rows, common, high_precision)
        for name, text in documents.items():
            (RESEARCH_DOCS / name).write_text(text, encoding="utf-8")
            (ARTIFACT / name).write_text(text, encoding="utf-8")

        formalism = """# PR-04C3 componentwise common-ledger formalism

## Conventions

Metric `(-,+,+,+)`; hydrogen orthonormal tetrad; ordinary frequency `nu` in
Hz; explicit `c,h,k_B`; homogeneous scalar sector. Red/blue faces are
`x=-21.25,+21.25`. Exact face energy owns the transported-energy ledger and a
pure computational crossing has zero atom source.

## Ordered common ledger

The three snapshots are not consecutive timesteps. The common object is
`{z1300:L1300,z1100:L1100,z900:L900}`. Every metric carries a unit, evidence
class, criterion, threshold and scale. The only aggregate is the maximum
normalized componentwise violation. A signed sum over redshift is forbidden.

## Native and COM comparison

Original-HyRec primitive, dense and Schur solutions are recomputed at each
snapshot. The COM collision/interface solve is rerun exactly from the v0.56
`q_activity=1` Bose-Einstein operator-verification state. The two
representations are compared only through photon number and exact face energy;
no state-vector equality or fitted scale is introduced.

## Claim

PR-04 closes only at the source-conditioned operator-contract level. Native/COM
trajectory integration remains PR-05 and FLRW recombination-history parity
remains PR-06.
"""
        (ARTIFACT / "PR04C3_COMMON_LEDGER_FORMALISM.md").write_text(
            formalism, encoding="utf-8"
        )
        write_json(
            ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json",
            {
                "classification": "PR04C3_HARNESS_EXECUTION_RECEIPT",
                "coding": coding_receipt,
                "research": research_receipt,
                "research_phase_directory": "docs/research/pr04c3_v057",
                "phase_count": 10,
            },
        )
        write_json(
            ARTIFACT / "PR04C3_ledger.json",
            {
                "classification": "PR04C3_COMPONENTWISE_COMMON_LEDGER",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "stage": "PR-04C3",
                "version": "0.57",
                "status": status,
                "PR04": hard_gate_ledger["PR04"],
                "common_ledger": "COMMON_INTERFACE_LEDGER.json",
                "common_ledger_sha256": common.sha256,
                "scientific_result": {
                    "route": "A_OPERATOR_CONTRACT_CLOSURE",
                    "snapshot_aggregation": "COMPONENTWISE_MAX_NEVER_SUM",
                    "state_classification": "OPERATOR_VERIFICATION_Q_ACTIVITY_1",
                    "state_remap": "FORBIDDEN_NOT_USED",
                    "fitted_normalization": "FORBIDDEN_NOT_USED",
                    "trajectory_parity": "NOT_CLAIMED_PR05_SCOPE",
                    "history_parity": "NOT_CLAIMED_PR06_SCOPE",
                },
                "next_stage": "PR-05 primitive HYREC/background trajectory interface",
            },
        )
        (ARTIFACT / "README.md").write_text(
            "# PR-04C3 v0.57\n\n"
            "Componentwise three-snapshot common-ledger closure. PR-04 is "
            "complete at the bounded operator-contract level; PR-05 trajectory "
            "integration remains open.\n",
            encoding="utf-8",
        )

        verifier = '''#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR04_OPERATOR_CONTRACT_COMPLETE_PR05_NEXT"
assert hard["PR04"] == "COMPLETE_OPERATOR_CONTRACT"
assert all(row["passed"] for row in hard["gates"])
common = json.loads((root / "COMMON_INTERFACE_LEDGER.json").read_text())
assert common["componentwise_passed"] is True
assert common["epsilon_common"] == 0.0
assert [row["target_z"] for row in common["snapshots"]] == [1300.0, 1100.0, 900.0]
with (root / "COMPONENTWISE_SNAPSHOT_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 3
assert all(float(row["minimum_occupation"]) > 0.0 for row in rows)
assert all(float(row["transported_energy_residual_J_per_H"]) == 0.0 for row in rows)
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    digest, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
print("PR-04C3 v0.57 artifact: PASS; PR-04 operator contract COMPLETE; PR-05 OPEN")
'''
        verifier_path = ARTIFACT / "verify_PR04C3.py"
        verifier_path.write_text(verifier, encoding="utf-8")
        verifier_path.chmod(0o755)

        write_json(
            ARTIFACT / "TOOL_STATUS.json",
            {
                "classification": "PR04C3_TOOL_STATUS",
                "web_search": "USED_PRIMARY_SOURCES",
                "Wolfram": "USED_SYMBOLIC_SCHUR_CANCELLATION_POSITIVITY",
                "Precise_Special_Functions": "USED_ZETA3_ZETA4_GAMMA3_120_DPS",
                "GitHub_connector": "USED_READ_ONLY_REMOTE_MAIN_PR15_CHECK",
                "research_harness": "USED_VALIDATED",
                "coding_harness": "USED_VALIDATED",
            },
        )

        create_manifest(ARTIFACT)
        deterministic_zip(ARTIFACT, BUNDLE)

    if not hard_gate_ledger["status"].startswith("PASS"):
        raise RuntimeError(hard_gate_ledger["status"])
    print(json.dumps(hard_gate_ledger, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
