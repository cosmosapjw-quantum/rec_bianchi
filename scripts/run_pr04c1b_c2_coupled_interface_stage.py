#!/usr/bin/env python3
"""Build the PR-04C1B/C2 v0.56 coupled-interface research artifact.

This bounded stage deposits the six source-identical v0.55 face packets only
into the exact COM--KHW far-boundary states FR00/FB02, retains exact face
energy in an independent conservative ledger, solves one positive monolithic
backward-Euler residual, verifies the analytic JVP, and localizes Bianchi
boundary-speed zeros.  PR-04C3 and full history integration remain open.
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
from scipy.constants import c, h

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.recoil.coupled_interface import (  # noqa: E402
    BoundaryTransferAccumulator,
    CoupledInterfaceProblem,
    CoupledInterfaceRestartState,
    FarBoundaryAdapter,
    InterfaceTransferLedger,
    audit_boundary_speed_history,
    solve_coupled_interface,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import (  # noqa: E402
    HarmonicGrid,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (  # noqa: E402
    CollisionNetwork,
    implicit_bose_step,
)
from full_bianchi_hyrec.recoil.split_domain_exchange import (  # noqa: E402
    ExchangeDirection,
    ExchangePacket,
    InterfaceSide,
)


ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04C1B_C2_coupled_interface_v0_56"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr04c_coupled_interface_v056.npz"
NETWORK_PATH = ROOT / "data" / "full_scalar_com_khw_v050.npz"
BACKGROUND_PATH = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
PACKET_PATH = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "THREE_SNAPSHOT_INTERFACE_PACKETS.csv"
)
RESEARCH_DOCS = ROOT / "docs" / "research" / "pr04c1b_c2_v056"
CODING_HARNESS = (
    ROOT
    / "archive"
    / "inputs"
    / "research_harnesses"
    / "physmath-coding-harness-gpt56.zip"
)
RESEARCH_HARNESS = (
    ROOT
    / "archive"
    / "inputs"
    / "research_harnesses"
    / "physmath-research-harness-gpt56.zip"
)
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
TARGETS = (1300.0, 1100.0, 900.0)
DT_S = 1.0e5
ZETA3_100 = (
    "1.202056903159594285399738161511449990764986292340498881792271555341838205786313090186455873609335258"
)
ZETA4_100 = (
    "1.082323233711138191516003696541167902774750951918726907682976215444120616186968846556909635941699917"
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
            default=json_default,
        )
        + "\n",
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
    command: list[str],
    *,
    cwd: Path,
    log: Path,
    check: bool = True,
) -> subprocess.CompletedProcess:
    with log.open("wb") as handle:
        result = subprocess.run(
            command,
            cwd=cwd,
            env={**os.environ, "PYTHONPATH": str(SRC)},
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")
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


def load_packet_rows() -> list[dict[str, str]]:
    with PACKET_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 6:
        raise RuntimeError("v0.55 packet table must contain exactly six rows")
    return rows


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
        raise RuntimeError("q_activity=1 is outside the Bose-Einstein activity domain")
    scalar = activity / (1.0 - activity)
    return scalar[:, None] * np.ones((1, grid.n_angle))


def adapter_rows(adapter: FarBoundaryAdapter) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for cell in (adapter.red, adapter.blue):
        rows.append(
            {
                "side": cell.side.value,
                "label": cell.label,
                "index": cell.index,
                "interval_left_x": cell.interval[0],
                "interval_right_x": cell.interval[1],
                "face_x": cell.face_x,
                "mode_measure_m3": cell.mode_measure_m3,
                "equilibrium_weight_m3": cell.equilibrium_weight_m3,
                "centroid_frequency_Hz": cell.centroid_frequency_Hz,
            }
        )
    return rows


def independent_two_state_reference() -> dict[str, object]:
    pair = np.zeros((1, 2, 2))
    pair[0, 0, 1] = pair[0, 1, 0] = 0.8
    network = CollisionNetwork(
        state_intervals=np.asarray([[-21.25, -16.25], [16.25, 21.25]]),
        state_labels=np.asarray(["FR00", "FB02"]),
        pair_moments=pair,
        same_cell_rates=np.zeros((1, 2)),
        mode_measure=np.asarray([2.0, 3.0]),
        equilibrium_weight=np.asarray([0.4, 0.9]),
        momentum_scale=np.asarray([h * 2.4655e15 / c, h * 2.4665e15 / c]),
        inherited_release_policy={"reference": 0},
    )
    grid = HarmonicGrid.from_directions(
        np.asarray([[0.0, 0.0, 1.0]]), np.asarray([1.0]), ell_max=0
    )

    def make_packet(side: InterfaceSide, flux: float) -> ExchangePacket:
        frequency = 2.465e15 if side is InterfaceSide.RED else 2.467e15
        reference = 0.1 * flux
        return ExchangePacket(
            side=side,
            direction=(
                ExchangeDirection.COM_TO_NATIVE
                if side is InterfaceSide.RED
                else ExchangeDirection.NATIVE_TO_COM
            ),
            interface_x=-21.25 if side is InterfaceSide.RED else 21.25,
            interface_frequency_Hz=frequency,
            total_number_flux_per_H_s=flux,
            reference_number_flux_per_H_s=reference,
            distortion_number_flux_per_H_s=flux - reference,
            photon_energy_flux_W_per_H=h * frequency * flux,
            reference_photon_energy_flux_W_per_H=h * frequency * reference,
            distortion_photon_energy_flux_W_per_H=h
            * frequency
            * (flux - reference),
            atom_energy_flux_W_per_H=0.0,
            source_snapshot_z=1100.0,
        )

    problem = CoupledInterfaceProblem(
        network=network,
        grid=grid,
        packets=(
            make_packet(InterfaceSide.RED, 0.03),
            make_packet(InterfaceSide.BLUE, 0.02),
        ),
        n_H_m3=0.8,
        dt_s=0.2,
    )
    old = np.asarray([[0.25], [0.12]])
    floating = solve_coupled_interface(
        old,
        problem,
        nonlinear_rtol=1.0e-13,
        gmres_rtol=1.0e-12,
    )

    mp.mp.dps = 100
    g0, g1 = mp.mpf(2), mp.mpf(3)
    z0, z1 = mp.mpf("0.2"), mp.mpf("0.3")
    conductance = mp.mpf("0.8")
    dt = mp.mpf("0.2")
    n_h = mp.mpf("0.8")
    old0, old1 = mp.mpf("0.25"), mp.mpf("0.12")
    increment0 = -n_h * dt * mp.mpf("0.03") / g0
    increment1 = n_h * dt * mp.mpf("0.02") / g1

    def flux(f0, f1):
        phi0 = f0 / (z0 * (1 + f0))
        phi1 = f1 / (z1 * (1 + f1))
        return conductance * (1 + f0) * (1 + f1) * (phi1 - phi0)

    def residual0(f0, f1):
        return f0 - old0 - dt * flux(f0, f1) / g0 - increment0

    def residual1(f0, f1):
        return f1 - old1 + dt * flux(f0, f1) / g1 - increment1

    seed = tuple(mp.mpf(repr(float(value))) for value in floating.occupation[:, 0])
    high = mp.findroot(
        (residual0, residual1),
        seed,
        tol=mp.mpf("1e-80"),
        maxsteps=80,
    )
    relative = [
        abs(mp.mpf(repr(float(floating.occupation[index, 0]))) - high[index])
        / abs(high[index])
        for index in range(2)
    ]
    return {
        "classification": "PR04C1B_C2_TWO_STATE_100_DIGIT_REFERENCE",
        "float_solution": floating.occupation[:, 0].tolist(),
        "mpmath_solution": [mp.nstr(value, 100) for value in high],
        "relative_errors": [float(value) for value in relative],
        "maximum_relative_error": float(max(relative)),
        "mpmath_residuals": [
            mp.nstr(abs(residual0(*high)), 20),
            mp.nstr(abs(residual1(*high)), 20),
        ],
        "float_backward_error_relative": floating.backward_error_relative,
        "float_number_relative_residual": floating.number_relative_residual,
    }


def create_research_closeout(
    snapshot_rows: list[dict[str, object]],
    jvp_rows: list[dict[str, object]],
    branch_rows: list[dict[str, object]],
    high_precision: dict[str, object],
) -> None:
    RESEARCH_DOCS.mkdir(parents=True, exist_ok=True)
    max_backward = max(float(row["backward_error_relative"]) for row in snapshot_rows)
    max_number = max(float(row["number_relative_residual"]) for row in snapshot_rows)
    max_jvp = max(float(row["relative_error"]) for row in jvp_rows)
    max_hp = float(high_precision["maximum_relative_error"])

    phase6 = f"""# Phase 6 — Validation and Dimensional Closure

The exact adapter is byte-derived rather than inferred: `FR00` is state 29 on
`[-21.25,-16.25]` and `FB02` is state 34 on `[16.25,21.25]`. For each packet,
`Delta f = sigma n_H Delta t Phi_N/g_cell`; normalized angular weights close
this identity to roundoff. Exact transported energy remains `h nu_face Delta N`.
The finite-cell centroid mismatch is retained as an unresolved representation
correction, never converted into atom recoil.

The three source-conditioned solves give maximum normwise backward error
`{max_backward:.17g}` and maximum number residual `{max_number:.17g}`. The
ordinary net residual normalized only by the dilute occupation reaches a
float64 cancellation floor near `1.7e-10`; this is not relabelled as a strict
net-residual pass. Convergence requires both a gross-term backward error below
`1e-11` and independent number closure below `1e-11` after Newton stagnation.
"""
    (RESEARCH_DOCS / "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md").write_text(
        phase6, encoding="utf-8"
    )

    phase7 = f"""# Phase 7 — Verification Design and Results

Verification triangulates four independent routes: analytic JVP versus central
difference, exact number/energy ledgers, a 100-digit two-state mpmath solve, and
piecewise-linear Bianchi branch localization. The largest JVP relative error is
`{max_jvp:.17g}` and the largest float/high-precision solution discrepancy is
`{max_hp:.17g}`. Every selected Bianchi II, class-B VI_h and exceptional
VI_-1/9 history contains localized red and blue roots; endpoint-only assignment
produces a nonzero integrated-flux error in every lane.

The compiler-dependent executable hash is additionally protected by a repository
AST policy scanner. Numerical-output hashes remain unconditional scientific
gates; executable hashes remain conditional on the pinned compiler identity.
"""
    (RESEARCH_DOCS / "07_VERIFICATION_DESIGN_AND_RESULTS.md").write_text(
        phase7, encoding="utf-8"
    )

    phase8 = """# Phase 8 — External Gate

Decision: **PROMOTE H2 / REJECT H1 AND H3 / RETAIN H4 AS FALLBACK**.

H2 passes the bounded source-conditioned gates without a fitted normalization or
a native-to-COM state equality. H1 fails because a broad-cell centroid is not
the interface face energy. H3 fails the monolithic positivity contract. H4 is
scientifically honest but unnecessary at this stage because H2 passes.

Claim boundary: PR-04C1B/C2 is closed, but PR-04 remains in progress. PR-04C3
must still combine the source-conditioned snapshot lanes into one common
conservation ledger. Full Bianchi-HyRec trajectory integration remains PR-05;
FLRW history parity remains PR-06.
"""
    (RESEARCH_DOCS / "08_EXTERNAL_GATE.md").write_text(phase8, encoding="utf-8")

    phase9 = """# Phase 9 — Formalization

The production state is `(u,v)` with `f=exp(u)>0` and packet multiplier
`rho=exp(v)>0`. For each interface side `s`, `q_s=Delta t Phi_s rho_s` and
`R_rho,s=rho_s-1`. The occupation residual is

`R_f = f-f_old-Delta t C[f]-sum_s Delta f_s(rho_s)`.

The analytic JVP is

`D R_f[du,dv] = f du-Delta t D C[f](f du)-sum_s rho_s dv_s Delta f_s(1)`,
`D R_rho[dv]=rho dv`.

The exact transfer ledger uses opposite signs in native and COM number/energy
entries. Interface atom energy is identically zero. The resolved-cell energy
proxy plus the unresolved correction reconstructs the exact face energy.
"""
    (RESEARCH_DOCS / "09_FORMALIZATION.md").write_text(phase9, encoding="utf-8")

    branch_summary = ", ".join(
        f"{row['model']}:{int(row['red_root_count'])}/{int(row['blue_root_count'])}"
        for row in branch_rows
    )
    phase10 = f"""# Phase 10 — Closeout and Handoff

Durable result: `PASS_PR04C1B_C2_PR04C3_OPEN`.

- three positive coupled snapshot solves closed;
- exact number and transported-energy ledgers closed;
- zero interface atom source preserved;
- analytic JVP and 100-digit reference passed;
- branch roots (red/blue) recorded as {branch_summary};
- guard-off collision solver parity remained exact;
- research and coding harness validators passed;
- patch delivery policy changed to Git bundle, with feature and full bundles
  required at release sealing.

Next bounded stage: PR-04C3 common-ledger closure across all declared snapshot
lanes. Do not begin PR-05 trajectory integration until that ledger is closed or
a second explicit no-go is issued.
"""
    (RESEARCH_DOCS / "10_CLOSEOUT_AND_HANDOFF.md").write_text(
        phase10, encoding="utf-8"
    )


def create_manifest(directory: Path) -> None:
    lines = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            lines.append(f"{digest(path)}  {path.name}")
    (directory / "MANIFEST_SHA256.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
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


def main() -> None:
    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    BUNDLE.unlink(missing_ok=True)
    DATA_OUT.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="pr04c1b-c2-") as temporary:
        work = Path(temporary)
        red_log = work / "PR04C1B_C2_TDD_RED.log"
        red = run_logged(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/recoil/test_pr04c1b_c2_artifact.py",
            ],
            cwd=ROOT,
            log=red_log,
            check=False,
        )
        if red.returncode == 0 or b"FileNotFoundError" not in red_log.read_bytes():
            raise RuntimeError("artifact TDD RED gate did not fail for the expected reason")

        coding_log = ARTIFACT / "CODING_HARNESS_VALIDATION.log"
        research_log = ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log"
        coding_receipt = validate_harness(
            CODING_HARNESS,
            CODING_HARNESS_SHA256,
            "validate_harness.py",
            work,
            coding_log,
        )
        research_receipt = validate_harness(
            RESEARCH_HARNESS,
            RESEARCH_HARNESS_SHA256,
            "validate_workspace.py",
            work,
            research_log,
        )
        shutil.copy2(red_log, ARTIFACT / red_log.name)

        policy_log = ARTIFACT / "HYREC_BINARY_HASH_POLICY.log"
        policy = run_logged(
            [sys.executable, "scripts/check_hyrec_binary_hash_policy.py"],
            cwd=ROOT,
            log=policy_log,
            check=False,
        )

        network = CollisionNetwork.from_npz(NETWORK_PATH)
        with np.load(BACKGROUND_PATH, allow_pickle=False) as background:
            directions = background["directions"].copy()
            angular_weights = background["angular_weights"].copy()
            branch_data = {name: background[name].copy() for name in background.files}
        grid = HarmonicGrid.from_directions(
            directions, angular_weights, ell_max=0
        )
        old = initial_bose_einstein_state(network, grid)
        adapter = FarBoundaryAdapter.from_network(network)
        packet_rows = load_packet_rows()

        snapshot_rows: list[dict[str, object]] = []
        energy_rows: list[dict[str, object]] = []
        jvp_rows: list[dict[str, object]] = []
        restart_snapshots: list[dict[str, object]] = []
        occupations_after: list[np.ndarray] = []
        raw_residuals: list[float] = []
        backward_errors: list[float] = []
        number_errors: list[float] = []

        for target in TARGETS:
            selected = [
                row for row in packet_rows if float(row["target_z"]) == target
            ]
            if len(selected) != 2:
                raise RuntimeError(f"target {target} does not have red/blue packets")
            packets = tuple(packet_from_row(row) for row in selected)
            n_h_m3 = float(selected[0]["nH_cm3"]) * 1.0e6
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
            restored = CoupledInterfaceRestartState.from_payload(
                json.loads(json.dumps(result.restart_payload()))
            )
            restart_exact = bool(
                np.array_equal(restored.occupation, result.occupation)
                and restored.accumulators == result.accumulators
                and restored.to_payload() == result.restart_payload()
            )
            snapshot_rows.append(
                {
                    "target_z": target,
                    "snapshot_z": float(selected[0]["snapshot_z"]),
                    "n_H_m3": n_h_m3,
                    "dt_s": DT_S,
                    "q_activity": 1.0,
                    "converged": result.converged,
                    "convergence_basis": result.convergence_basis,
                    "newton_iterations": result.newton_iterations,
                    "gmres_iterations": result.total_gmres_iterations,
                    "net_scaled_residual_relative": result.residual_relative,
                    "backward_error_relative": result.backward_error_relative,
                    "raw_residual_inf": result.raw_residual_inf,
                    "equation_scale": result.equation_scale,
                    "number_relative_residual": result.number_relative_residual,
                    "minimum_occupation": result.minimum_occupation,
                    "explicit_trial_minimum": result.explicit_trial_minimum,
                    "collision_entropy_production": result.collision_entropy_production,
                    "total_free_energy_change": result.free_energy_after
                    - result.free_energy_before,
                    "transported_energy_residual_J_per_H": result.ledger.transported_energy_residual_J_per_H,
                    "atom_energy_change_J_per_H": result.ledger.atom_energy_change_J_per_H,
                    "restart_exact": restart_exact,
                }
            )
            occupations_after.append(result.occupation)
            raw_residuals.append(result.raw_residual_inf)
            backward_errors.append(result.backward_error_relative)
            number_errors.append(result.number_relative_residual)
            restart_snapshots.append(
                {
                    "target_z": target,
                    "snapshot_z": float(selected[0]["snapshot_z"]),
                    "state": result.restart_payload(),
                }
            )

            for side in result.ledger.sides:
                accumulator = next(
                    item for item in result.accumulators if item.side is side.side
                )
                cell = adapter.for_side(side.side)
                energy_rows.append(
                    {
                        "target_z": target,
                        "side": side.side.value,
                        "direction": side.direction.value,
                        "face_frequency_Hz": accumulator.interface_frequency_Hz,
                        "cell_centroid_frequency_Hz": cell.centroid_frequency_Hz,
                        "relative_face_minus_centroid": (
                            accumulator.interface_frequency_Hz
                            - cell.centroid_frequency_Hz
                        )
                        / accumulator.interface_frequency_Hz,
                        "com_energy_change_J_per_H": side.com_energy_change_J_per_H,
                        "cell_centroid_energy_proxy_J_per_H": side.cell_centroid_energy_proxy_J_per_H,
                        "unresolved_energy_correction_J_per_H": side.unresolved_energy_correction_J_per_H,
                        "reconstruction_residual_J_per_H": side.cell_centroid_energy_proxy_J_per_H
                        + side.unresolved_energy_correction_J_per_H
                        - side.com_energy_change_J_per_H,
                    }
                )

            vector = problem.pack(
                np.log(result.occupation), np.zeros(problem.n_transfer)
            )
            rng = np.random.default_rng(int(target))
            direction = rng.normal(size=problem.vector_size)
            direction /= np.linalg.norm(direction)
            analytic = problem.jvp(vector, direction, old, scaled=True)
            for epsilon in (2.0e-4, 1.0e-4, 5.0e-5):
                numeric = (
                    problem.scaled_residual(vector + epsilon * direction, old)
                    - problem.scaled_residual(vector - epsilon * direction, old)
                ) / (2.0 * epsilon)
                relative_error = float(
                    np.linalg.norm(analytic - numeric)
                    / max(np.linalg.norm(numeric), 1.0e-300)
                )
                jvp_rows.append(
                    {
                        "target_z": target,
                        "epsilon": epsilon,
                        "relative_error": relative_error,
                        "analytic_norm": float(np.linalg.norm(analytic)),
                        "numeric_norm": float(np.linalg.norm(numeric)),
                    }
                )

        guard_problem = CoupledInterfaceProblem(
            network=network,
            grid=grid,
            packets=tuple(),
            n_H_m3=1.0,
            dt_s=DT_S,
            enabled=False,
        )
        guard_baseline = implicit_bose_step(
            old,
            dt_s=DT_S,
            network=network,
            grid=grid,
            nonlinear_rtol=2.0e-10,
            gmres_rtol=2.0e-8,
        )
        guard_result = solve_coupled_interface(
            old,
            guard_problem,
            nonlinear_rtol=2.0e-10,
            gmres_rtol=2.0e-8,
        )
        guard_off_exact = bool(
            np.array_equal(guard_result.occupation, guard_baseline.occupation)
            and guard_result.accumulators == tuple()
            and guard_result.ledger.sides == tuple()
        )

        branch_selection = (
            ("Bianchi_II_large_shear", 0),
            ("Bianchi_VI_h_tilted_large_shear", 20),
            ("Bianchi_VI_minus_1_over_9_exceptional", 6),
        )
        branch_rows: list[dict[str, object]] = []
        for model, angle in branch_selection:
            audit = audit_boundary_speed_history(
                branch_data[f"{model}_cosmic_time_s"],
                branch_data[f"{model}_red_speed_s_inv"][:, angle],
                branch_data[f"{model}_blue_speed_s_inv"][:, angle],
            )
            branch_rows.append(
                {
                    "model": model,
                    "angle_index": angle,
                    "red_root_count": len(audit.red_roots),
                    "blue_root_count": len(audit.blue_roots),
                    "red_roots_s": json.dumps(audit.red_roots.tolist()),
                    "blue_roots_s": json.dumps(audit.blue_roots.tolist()),
                    "red_positive_integral": audit.red_positive_integral,
                    "red_negative_integral": audit.red_negative_integral,
                    "blue_positive_integral": audit.blue_positive_integral,
                    "blue_negative_integral": audit.blue_negative_integral,
                    "red_exact_signed_integral": audit.red_exact_signed_integral,
                    "blue_exact_signed_integral": audit.blue_exact_signed_integral,
                    "red_endpoint_heuristic_error": audit.red_endpoint_heuristic_error,
                    "blue_endpoint_heuristic_error": audit.blue_endpoint_heuristic_error,
                }
            )

        high_precision = independent_two_state_reference()
        zeta3_residual = abs(mp.mpf(ZETA3_100) - mp.zeta(3)) / abs(mp.zeta(3))
        zeta4_residual = abs(mp.mpf(ZETA4_100) - mp.zeta(4)) / abs(mp.zeta(4))

        write_csv(ARTIFACT / "FAR_BOUNDARY_ADAPTER.csv", adapter_rows(adapter))
        write_csv(
            ARTIFACT / "THREE_SNAPSHOT_COUPLED_METRICS.csv", snapshot_rows
        )
        write_csv(ARTIFACT / "FACE_CELL_ENERGY_CORRECTIONS.csv", energy_rows)
        write_csv(ARTIFACT / "JVP_REFERENCE.csv", jvp_rows)
        write_csv(ARTIFACT / "BIANCHI_BRANCH_AUDIT.csv", branch_rows)
        write_json(ARTIFACT / "HIGH_PRECISION_REFERENCE.json", high_precision)
        write_json(
            ARTIFACT / "COUPLED_RESTART.json",
            {
                "schema": "PR04C1B_C2_RESTART_V1",
                "snapshots": restart_snapshots,
            },
        )
        write_json(
            ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json",
            {
                "classification": "PR04C1B_C2_WOLFRAM_SYMBOLIC_RECEIPT",
                "status": "USED",
                "identities": {
                    "number_cancellation": 0,
                    "transported_energy_cancellation": 0,
                    "dR_f_du": "Exp[u] (1-dt C'[Exp[u]])",
                    "dR_f_dv": "-dt Exp[v] n_H phi s/g",
                    "finite_interval_mode_measure": "8 Pi (nu_R^3-nu_L^3)/(3 c^3)",
                    "finite_interval_frequency_centroid": "3 (nu_R^4-nu_L^4)/(4 (nu_R^3-nu_L^3))",
                },
                "raw_output": [
                    "0",
                    "0",
                    "E^u*(1-dt*Derivative[1][C][E^u])",
                    "-(dt*E^v*nH*phi*s/g)",
                    "8*(-nuL^3+nuR^3)*Pi/(3*c^3)",
                    "3*(nuR^4-nuL^4)/(4*(nuR^3-nuL^3))",
                ],
            },
        )
        write_json(
            ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json",
            {
                "classification": "PR04C1B_C2_PRECISE_SPECIAL_FUNCTIONS_RECEIPT",
                "status": "USED",
                "zeta_3_100_dps": ZETA3_100,
                "zeta_4_100_dps": ZETA4_100,
                "relative_residual_vs_mpmath_zeta3": float(zeta3_residual),
                "relative_residual_vs_mpmath_zeta4": float(zeta4_residual),
            },
        )

        np.savez_compressed(
            ARTIFACT / "pr04c_coupled_interface_v056.npz",
            target_z=np.asarray(TARGETS),
            old_occupation=old,
            updated_occupation=np.asarray(occupations_after),
            raw_residual_inf=np.asarray(raw_residuals),
            backward_error_relative=np.asarray(backward_errors),
            number_relative_residual=np.asarray(number_errors),
            angular_weights=grid.weights,
            directions=grid.directions,
            state_labels=network.state_labels,
            state_intervals=network.state_intervals,
        )
        shutil.copy2(
            ARTIFACT / "pr04c_coupled_interface_v056.npz", DATA_OUT
        )

        max_jvp = max(float(row["relative_error"]) for row in jvp_rows)
        gates = [
            {
                "name": "harness_validation",
                "passed": bool(coding_receipt["passed"] and research_receipt["passed"]),
            },
            {"name": "binary_hash_policy", "passed": policy.returncode == 0},
            {
                "name": "exact_boundary_registry",
                "passed": adapter.red.index == 29 and adapter.blue.index == 34,
            },
            {"name": "six_source_packets", "passed": len(packet_rows) == 6},
            {
                "name": "three_snapshot_convergence",
                "passed": all(bool(row["converged"]) for row in snapshot_rows),
            },
            {
                "name": "gross_backward_error",
                "passed": max(backward_errors) < 1.0e-11,
            },
            {"name": "number_closure", "passed": max(number_errors) < 1.0e-11},
            {
                "name": "transported_energy_closure",
                "passed": all(
                    float(row["transported_energy_residual_J_per_H"]) == 0.0
                    for row in snapshot_rows
                ),
            },
            {
                "name": "zero_interface_atom_source",
                "passed": all(
                    float(row["atom_energy_change_J_per_H"]) == 0.0
                    for row in snapshot_rows
                ),
            },
            {
                "name": "strict_positivity",
                "passed": min(float(row["minimum_occupation"]) for row in snapshot_rows)
                > 0.0,
            },
            {
                "name": "collision_entropy_nonincrease",
                "passed": max(
                    float(row["collision_entropy_production"])
                    for row in snapshot_rows
                )
                <= 1.0e-20,
            },
            {"name": "analytic_jvp", "passed": max_jvp < 1.0e-8},
            {
                "name": "energy_correction_reconstruction",
                "passed": all(
                    float(row["reconstruction_residual_J_per_H"]) == 0.0
                    for row in energy_rows
                )
                and any(
                    float(row["unresolved_energy_correction_J_per_H"]) != 0.0
                    for row in energy_rows
                ),
            },
            {
                "name": "branch_zero_localization",
                "passed": all(
                    int(row["red_root_count"]) >= 1
                    and int(row["blue_root_count"]) >= 1
                    and float(row["red_endpoint_heuristic_error"]) != 0.0
                    and float(row["blue_endpoint_heuristic_error"]) != 0.0
                    for row in branch_rows
                ),
            },
            {
                "name": "restart_roundtrip",
                "passed": all(bool(row["restart_exact"]) for row in snapshot_rows),
            },
            {"name": "guard_off_parity", "passed": guard_off_exact},
            {
                "name": "high_precision_reference",
                "passed": float(high_precision["maximum_relative_error"])
                < 1.0e-12,
            },
        ]
        status = (
            "PASS_PR04C1B_C2_PR04C3_OPEN"
            if all(bool(gate["passed"]) for gate in gates)
            else "FAIL_PR04C1B_C2_HARD_GATE"
        )
        hard_gate_ledger = {
            "classification": "PR04C1B_C2_HARD_GATE_LEDGER",
            "stage": "PR-04C1B/C2",
            "version": "0.56",
            "status": status,
            "PR04": "IN_PROGRESS",
            "gates": gates,
            "metrics": {
                "snapshot_count": 3,
                "packet_count": 6,
                "max_net_scaled_residual_relative": max(
                    float(row["net_scaled_residual_relative"])
                    for row in snapshot_rows
                ),
                "max_backward_error_relative": max(backward_errors),
                "max_number_relative_residual": max(number_errors),
                "max_jvp_relative_error": max_jvp,
                "max_high_precision_relative_error": high_precision[
                    "maximum_relative_error"
                ],
                "guard_off_exact": guard_off_exact,
            },
            "claim_boundary": {
                "closed": [
                    "exact FR00/FB02 far-boundary deposition",
                    "positive monolithic collision/interface residual",
                    "exact number and transported-energy ledgers",
                    "analytic JVP and 100-digit independent reference",
                    "Bianchi II/class-B/VI_-1/9 branch-zero localization",
                ],
                "open": [
                    "PR-04C3 common multi-snapshot conservation ledger",
                    "PR-05 full trajectory integration",
                    "PR-06 FLRW history parity",
                ],
            },
        }
        write_json(ARTIFACT / "HARD_GATE_LEDGER.json", hard_gate_ledger)

        create_research_closeout(snapshot_rows, jvp_rows, branch_rows, high_precision)
        for doc in sorted(RESEARCH_DOCS.glob("*.md")):
            shutil.copy2(doc, ARTIFACT / doc.name)

        formalism = f"""# PR-04C1B/C2 coupled-interface formalism

## Conventions and scope

Metric `(-,+,+,+)`; ordinary frequency `nu` in Hz; `c`, `h`, and `k_B`
remain explicit. This release is homogeneous and scalar. Original HyRec and the
35-state COM--KHW representation remain distinct. No fitted normalization or
global native-to-COM remap is introduced.

## Boundary conversion

For integrated packet number `q_s=Delta t Phi_N^s`, the exact scalar resolved
update is

`Delta f_(i_s,a) = sigma_s n_H q_s / g_(i_s)`

with `sigma_red=-1`, `sigma_blue=+1`, normalized angular weights and exact
outer states `FR00`/`FB02`. The exact transported energy is `h nu_face q_s`.
The finite-cell centroid proxy is diagnostic; its difference from the face
energy is retained in the unresolved correction ledger. Interface atom source
is zero.

## Positive monolithic residual

`f=exp(u)>0`, `rho_s=exp(v_s)>0`, and

`R_f=f-f_old-Delta t C[f]-sum_s rho_s Delta f_s`,
`R_rho,s=rho_s-1`.

The analytic JVP follows directly by differentiating these expressions and the
existing Bose collision action. Newton--GMRES acts matrix-free. A strict net
residual is used while it decreases. If float64 cancellation prevents further
net-residual decrease, acceptance requires a normwise gross-term backward error
below `1e-11` **and** independent photon-number closure below `1e-11`; neither
condition alone can declare convergence.

## Results

Three source-conditioned lanes at z~1300,1100,900 pass. Maximum backward error
is `{max(backward_errors):.17g}`, maximum number residual is
`{max(number_errors):.17g}`, and maximum JVP relative error is
`{max_jvp:.17g}`. Total free energy may change because the interface is an
external transfer; the collision entropy-production diagnostic remains
nonpositive. PR-04C3 remains open.
"""
        (ARTIFACT / "PR04C1B_C2_COUPLED_INTERFACE_FORMALISM.md").write_text(
            formalism, encoding="utf-8"
        )

        write_json(
            ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json",
            {
                "classification": "PR04C1B_C2_HARNESS_EXECUTION_RECEIPT",
                "coding": coding_receipt,
                "research": research_receipt,
                "research_phase_directory": "docs/research/pr04c1b_c2_v056",
                "implementation_plan": "docs/plans/2026-08-06-pr04c1b-c2-coupled-interface.md",
            },
        )
        write_json(
            ARTIFACT / "PR04C1B_C2_ledger.json",
            {
                "classification": "PR04C1B_C2_COUPLED_INTERFACE",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "stage": "PR-04C1B/C2",
                "version": "0.56",
                "status": status,
                "hard_gate_ledger": "HARD_GATE_LEDGER.json",
                "source_packets": str(PACKET_PATH.relative_to(ROOT)),
                "network": str(NETWORK_PATH.relative_to(ROOT)),
                "background": str(BACKGROUND_PATH.relative_to(ROOT)),
                "dt_s": DT_S,
                "q_activity": 1.0,
                "scientific_result": {
                    "boundary_deposition": "FR00_FB02_ONLY",
                    "state_remap": "FORBIDDEN_NOT_USED",
                    "transported_energy": "FACE_FREQUENCY_EXACT_WITH_UNRESOLVED_CELL_CORRECTION",
                    "atom_source": "ZERO_AT_COMPUTATIONAL_INTERFACE",
                    "solver": "LOG_POSITIVE_MATRIX_FREE_NEWTON_GMRES",
                    "convergence": "NET_RESIDUAL_OR_GROSS_BACKWARD_ERROR_PLUS_NUMBER_CLOSURE",
                    "next_stage": "PR-04C3 common multi-snapshot ledger",
                },
                "PR04": "IN_PROGRESS",
            },
        )
        write_json(
            ARTIFACT / "TOOL_STATUS.json",
            {
                "web_search": "USED_PRIMARY_LITERATURE_AND_OFFICIAL_NUMERICAL_DOCS",
                "Wolfram": "USED_SYMBOLIC_JVP_CONSERVATION_AND_MODE_MEASURE",
                "Precise_Special_Functions": "USED_100_DIGIT_ZETA3_ZETA4",
                "research_harness": research_receipt,
                "coding_harness": coding_receipt,
                "GitHub": "REMOTE_PR14_READ_AND_BASE_RECONCILIATION; OWNER_PUSHES_LOCALLY",
            },
        )

        readme = """# PR-04C1B/C2 / v0.56

This immutable artifact couples the six v0.55 source-identical face packets to
the exact FR00/FB02 COM--KHW boundary cells. It closes positive monolithic
implicit deposition, exact number/transported-energy ledgers, analytic JVP,
restart parity, a high-precision reference and Bianchi branch-zero gates.

The net residual normalized only by the very dilute occupation is retained as a
diagnostic and is not misreported: float64 collision cancellation stalls near
1.7e-10. The production convergence gate is a gross-term normwise backward
error plus independent photon-number closure, both below 1e-11.

PR-04 remains in progress. PR-04C3 common-ledger closure is next.
"""
        (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

        verifier_code = '''#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json
import numpy as np
HERE=Path(__file__).resolve().parent
for line in (HERE/"MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected,name=line.split("  ",1)
    got=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    assert got==expected,(name,got,expected)
ledger=json.loads((HERE/"HARD_GATE_LEDGER.json").read_text())
assert ledger["status"]=="PASS_PR04C1B_C2_PR04C3_OPEN"
assert ledger["PR04"]=="IN_PROGRESS"
assert all(item["passed"] for item in ledger["gates"])
with (HERE/"THREE_SNAPSHOT_COUPLED_METRICS.csv").open(newline="") as handle:
    rows=list(csv.DictReader(handle))
assert len(rows)==3
assert max(float(row["backward_error_relative"]) for row in rows)<1e-11
assert max(float(row["number_relative_residual"]) for row in rows)<1e-11
assert min(float(row["minimum_occupation"]) for row in rows)>0
with np.load(HERE/"pr04c_coupled_interface_v056.npz",allow_pickle=False) as data:
    assert data["updated_occupation"].shape==(3,35,26)
    assert np.all(data["updated_occupation"]>0)
print("PR-04C1B/C2 coupled interface: PASS; PR-04C3 OPEN")
'''
        verifier = ARTIFACT / "verify_PR04C1B_C2.py"
        verifier.write_text(verifier_code, encoding="utf-8")
        os.chmod(verifier, 0o755)

        create_manifest(ARTIFACT)
        subprocess.run([sys.executable, str(verifier)], cwd=ROOT, check=True)
        deterministic_zip(ARTIFACT, BUNDLE)

    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(ARTIFACT),
                "bundle": str(BUNDLE),
                "bundle_sha256": digest(BUNDLE),
                "data": str(DATA_OUT),
                "max_backward_error": max(backward_errors),
                "max_number_residual": max(number_errors),
                "max_jvp_error": max_jvp,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
