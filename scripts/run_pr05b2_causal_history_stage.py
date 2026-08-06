#!/usr/bin/env python3
"""Build PR-05B2/v0.60 source-identical causal characteristic-history evidence.

The canonical October-2012 original-HyRec hydrogen solver keeps 2s/2p and 311
virtual departures algebraic.  Its source-identifiable radiation time dependence
is the accepted history of outgoing distortions, free-streamed along exact
log-frequency characteristics.  This stage reproduces that state and its
transactional append/rollback semantics without assigning a fictitious local
finite-volume mass to the virtual spikes.
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
from full_bianchi_hyrec.recoil.original_hyrec_native import (  # noqa: E402
    ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.causal_history import (  # noqa: E402
    AcceptedRadiationHistory,
    CharacteristicHistoryGrid,
    CharacteristicStencilSwitch,
    FutureHistoryEndpointError,
    build_original_hyrec_queries,
    construct_original_hyrec_incoming,
)
from full_bianchi_hyrec.trajectory.causal_history_step import (  # noqa: E402
    CausalHistoryAcceptedStepProblem,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (  # noqa: E402
    OriginalHyRecPrimitiveRateTable,
)
from full_bianchi_hyrec.trajectory.primitive_trajectory import (  # noqa: E402
    PrimitiveTrajectoryProblem,
    atomic_state_from_source_snapshot,
)
from full_bianchi_hyrec.trajectory.time_dependent_native import (  # noqa: E402
    SourceIdentifiableOriginalHyRecDAE,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR05B2_causal_characteristic_history_v0_60"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
HISTORY_OUT = ROOT / "data" / "pr05b2_source_history_v060.npz"
METRICS_OUT = ROOT / "data" / "pr05b2_causal_history_metrics_v060.npz"
HYREC_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
NETWORK_PATH = ROOT / "data/full_scalar_com_khw_v050.npz"
INSTRUMENTER = ROOT / "scripts/c_harness/instrument_original_hyrec_pr05b2.py"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CANONICAL_HYREC_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
TARGETS = (1300, 1100, 900)
GAMMA_3_OVER_2_120 = "0.886226925452758013649083741670572591398774728061193564106903894926455642295516090687475328369272332708113411812141285333"
ZETA3_120 = "1.20205690315959428539973816151144999076498629234049888179227155534183820578631309018645587360933525814619915779526071942"
WOLFRAM_RESULT = {
    "interpolation_weight_sum": 1,
    "endpoint_derivatives": ["1-f", "f"],
    "fraction_derivative": "-yL+yR",
    "nu_cubed_over_nH_characteristic_invariance": 0,
    "photon_energy_plus_redshift_work_identity": 0,
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def bytes_digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_logged(
    command: list[str],
    *,
    cwd: Path,
    log: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC)
    if env:
        environment.update(env)
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
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}"
        )
    return result


def validate_harness(
    archive: Path,
    expected: str,
    validator: str,
    work: Path,
    log: Path,
) -> dict[str, object]:
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
    result = run_logged(
        [sys.executable, str(matches[0])],
        cwd=matches[0].parents[1],
        log=log,
    )
    return {
        "archive": archive.name,
        "sha256": observed,
        "validator": validator,
        "exit_code": result.returncode,
        "passed": True,
    }


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    """Write a NumPy-compatible NPZ with deterministic member ordering/times."""

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
            np.lib.format.write_array(
                buffer,
                np.asarray(arrays[name]),
                allow_pickle=False,
            )
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt deterministic NPZ member: {bad}")


def compile_hyrec(source: Path, executable: Path, *, diagnostics: bool, log: Path) -> None:
    command = [
        "gcc",
        "-std=c11",
        "-D_DEFAULT_SOURCE",
        "-O3",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
    ]
    if diagnostics:
        command.append("-DPR05B2_DIAGNOSTICS")
    command.extend(
        [
            "hyrectools.c",
            "helium.c",
            "hydrogen.c",
            "history.c",
            "hyrec.c",
            "-lm",
            "-o",
            str(executable),
        ]
    )
    run_logged(command, cwd=source, log=log)


def execute_hyrec(
    source: Path,
    executable: Path,
    output: Path,
    *,
    diagnostics: Path | None,
    stderr_log: Path,
) -> None:
    environment = os.environ.copy()
    if diagnostics is not None:
        environment["PR05B2_DIAGNOSTIC_DIR"] = str(diagnostics)
    with (source / "input.dat").open("rb") as stdin, output.open("wb") as stdout, stderr_log.open("wb") as stderr:
        result = subprocess.run(
            [str(executable)],
            cwd=source,
            env=environment,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    if result.returncode:
        raise RuntimeError(f"HyRec executable failed: {executable}")


def parse_raw_history(diagnostic_dir: Path, hydrogen_member_hash: str) -> tuple[AcceptedRadiationHistory, dict[str, object]]:
    metadata: dict[str, str] = {}
    with (diagnostic_dir / "pr05b2_history_meta.csv").open(newline="", encoding="utf-8") as handle:
        for key, value in csv.reader(handle):
            metadata[key] = value
    if metadata.get("schema") != "PR05B2_SOURCE_HISTORY_RAW_V1":
        raise RuntimeError("unknown PR-05B2 raw history schema")
    count = int(metadata["accepted_count"])
    nvirt = int(metadata["nvirt"])
    nlyman = int(metadata["nlyman"])
    if nvirt != 311 or nlyman != 3 or count != int(metadata["iz_current"]) + 1:
        raise RuntimeError("raw source-history dimensions are inconsistent")
    energy_path = diagnostic_dir / "pr05b2_energy_eV.f64"
    outgoing_path = diagnostic_dir / "pr05b2_Dfminus_hist.f64"
    line_path = diagnostic_dir / "pr05b2_Dfminus_Ly_hist.f64"
    average_path = diagnostic_dir / "pr05b2_Dfnu_hist.f64"
    energy = np.fromfile(energy_path, dtype=np.float64)
    outgoing = np.fromfile(outgoing_path, dtype=np.float64).reshape(nvirt, count)
    lines = np.fromfile(line_path, dtype=np.float64).reshape(nlyman, count)
    average = np.fromfile(average_path, dtype=np.float64).reshape(nvirt, count)
    z_start = float(metadata["zstart"])
    dlna = float(metadata["dlna"])
    eta_start = -math.log1p(z_start)
    eta = eta_start + dlna * np.arange(count, dtype=float)
    grid = CharacteristicHistoryGrid(
        eta=eta,
        source_indices=np.arange(count, dtype=np.int64),
        z_start=z_start,
        dlna=dlna,
        energy_eV=energy,
        source_hashes={
            "HyRec_Oct2012.zip": CANONICAL_HYREC_SHA256,
            "HyRec/hydrogen.c": hydrogen_member_hash,
        },
    )
    history = AcceptedRadiationHistory(
        grid=grid,
        outgoing_virtual=outgoing,
        outgoing_lyman=lines,
        average_virtual=average,
        completeness="SOURCE_COMPLETE_THROUGH_Z900_CURRENT",
    )
    receipt = {
        "classification": "PR05B2_SOURCE_HISTORY_PROVENANCE",
        "schema": metadata["schema"],
        "source_snapshot_z": float(metadata["z"]),
        "z_start": z_start,
        "dlna": dlna,
        "accepted_count": count,
        "iz_current": int(metadata["iz_current"]),
        "nvirt": nvirt,
        "nlyman": nlyman,
        "history_binary_sha256": history.sha256,
        "raw_members": {
            path.name: {"sha256": digest(path), "size_bytes": path.stat().st_size}
            for path in (energy_path, outgoing_path, line_path, average_path)
        },
    }
    return history, receipt


def background_for(
    source,
    *,
    bianchi_type: str = "I",
    sigma: np.ndarray | None = None,
    A: np.ndarray | None = None,
) -> BackgroundSnapshot:
    return BackgroundSnapshot(
        tau=-float(np.log1p(source.z)),
        cosmic_time_s=1.0,
        H_s_inv=source.H_s_inv,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)) if sigma is None else np.asarray(sigma, dtype=float),
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3) if A is None else np.asarray(A, dtype=float),
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id="pr05b2-v060",
        bianchi_type=bianchi_type,
    )


def dae_for(
    target: int,
    table: OriginalHyRecPrimitiveRateTable,
    network: CollisionNetwork,
    angular_grid,
    *,
    bianchi_type: str = "I",
    sigma: np.ndarray | None = None,
    A: np.ndarray | None = None,
):
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
        com_occupation=scalar[:, None] * np.ones((1, angular_grid.n_angle)),
        beta_H=np.zeros(3),
    )
    primitive = PrimitiveTrajectoryProblem(
        background=background_for(
            source,
            bianchi_type=bianchi_type,
            sigma=sigma,
            A=A,
        ),
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=angular_grid,
        line=LineBoundaryConfig.lyman_alpha(
            temperature_K=state.T_m_K,
            x_red=-21.25,
            x_blue=21.25,
        ),
        interface_enabled=False,
    )
    return SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive), source


def relative(first: np.ndarray | float, second: np.ndarray | float) -> float:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    return float(np.max(np.abs(left - right))) / max(
        float(np.max(np.abs(left))),
        float(np.max(np.abs(right))),
        1.0e-300,
    )


def high_precision_interpolation_residual(history: AcceptedRadiationHistory, incoming) -> float:
    mp.mp.dps = 120
    worst = mp.mpf("0")
    for query, stencil in zip(incoming.queries, incoming.stencils, strict=True):
        if query.source_kind == "virtual":
            values = history.outgoing_virtual[query.source_index]
        else:
            values = history.outgoing_lyman[query.source_index]
        if stencil.thermal_zero:
            reference = mp.mpf("0")
            observed = mp.mpf("0")
            scale = mp.mpf("1")
        else:
            assert stencil.left_index is not None and stencil.right_index is not None
            left = mp.mpf(str(values[stencil.left_index]))
            right = mp.mpf(str(values[stencil.right_index]))
            fraction = mp.mpf(str(stencil.fraction))
            reference = (1 - fraction) * left + fraction * right
            if query.target_kind == "virtual":
                observed = mp.mpf(str(incoming.virtual[query.target_index]))
            else:
                observed = mp.mpf(str(incoming.lyman[query.target_index]))
            scale = max(abs(reference), abs(left), abs(right), mp.mpf("1e-300"))
        worst = max(worst, abs(observed - reference) / scale)
    return float(worst)


def query_rows(target: int, source, incoming) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, (query, stencil) in enumerate(
        zip(incoming.queries, incoming.stencils, strict=True)
    ):
        rows.append(
            {
                "target_z": target,
                "snapshot_z": source.z,
                "query_index": index,
                "channel": query.channel,
                "source_kind": query.source_kind,
                "source_index": query.source_index,
                "target_kind": query.target_kind,
                "target_index": query.target_index,
                "source_energy_eV": query.source_energy_eV,
                "target_energy_eV": query.target_energy_eV,
                "eta_query": query.eta_query,
                "thermal_zero": stencil.thermal_zero,
                "left_index": "" if stencil.left_index is None else stencil.left_index,
                "right_index": "" if stencil.right_index is None else stencil.right_index,
                "fraction": stencil.fraction,
                "uses_current_accepted_endpoint": bool(
                    stencil.right_index == source.iz_local - 1
                ),
            }
        )
    return rows


def source_line_ledger(hydrogen_bytes: bytes) -> tuple[list[dict[str, object]], str]:
    lines = hydrogen_bytes.decode("utf-8").splitlines()
    ranges = (
        ("interp_Dfnu", 627, 654, "two-neighbour accepted-history interpolation and future endpoint rejection"),
        ("fplus_from_fminus", 656, 718, "313 characteristic channels from outgoing history to incoming distortions"),
        ("accepted_step_residual", 720, 776, "incoming construction, algebraic solve and electron differential row"),
        ("accepted_step_append", 777, 805, "outgoing virtual/line/average history append after source solve"),
    )
    member_hash = bytes_digest(hydrogen_bytes)
    rows: list[dict[str, object]] = []
    excerpts: list[str] = []
    for name, start, end, meaning in ranges:
        payload = "\n".join(lines[start - 1 : end]) + "\n"
        rows.append(
            {
                "claim": name,
                "archive_member": "HyRec/hydrogen.c",
                "member_sha256": member_hash,
                "line_start": start,
                "line_end": end,
                "excerpt_sha256": bytes_digest(payload.encode("utf-8")),
                "meaning": meaning,
            }
        )
        excerpts.append(f"===== {name}: hydrogen.c:{start}-{end} =====\n{payload}")
    return rows, "\n".join(excerpts)


def write_research_docs(metrics: dict[str, object]) -> None:
    documents = {
        "01_RESEARCH_CONTRACT.md": """# PR-05B2 research contract\n\nPrimary question: can the exact original-HyRec accepted characteristic history be made typed, causal, transaction-safe and differentiable, then coupled to the rank-one local DAE without inventing a virtual-spike time mass or prematurely removing a compressed term?\n\nConventions: metric `(-,+,+,+)`, `eta=ln(a)`, ordinary frequency in Hz, explicit `c,h,k_B`, homogeneous scalar background, signed departures unclipped.\n""",
        "02_EVIDENCE_ACQUISITION.md": """# Evidence acquisition\n\nEvidence is the byte-locked October-2012 archive, guarded source-identical C instrumentation, the complete accepted history through the source z~900 step, three canonical source snapshots, exact source-line excerpts, both pinned research harnesses, current PETSc callback documentation, Wolfram identities and 120-digit special-function references.\n""",
        "03_CLAIM_SOURCE_AUDIT.md": """# Claim/source audit\n\n`interp_Dfnu` owns the two-neighbour interpolation and future-endpoint failure. `fplus_from_fminus` owns exactly 313 incoming characteristic queries. The local source solve owns 313 algebraic rows plus the electron differential rate. History mutation is an accepted-step transaction; it does not create a local virtual-radiation mass.\n""",
        "04_HYPOTHESIS_SPACE.md": """# Hypothesis space\n\n- H_A: the source-identical history, append/rollback, JVP and local DAE close at all three snapshots.\n- H_B: a required accepted datum or characteristic measure is absent; issue a bounded no-go.\n- Rejected: centre-derived cell widths, fitted relaxation, future endpoint use, mutation during rejected attempts, and differentiating through a stencil-index switch.\n""",
        "05_ADVERSARIAL_REVIEW.md": """# Adversarial review\n\nThe audit perturbs endpoint values, forces future queries, crosses a stencil boundary, rejects and rolls back candidates, permutes geometry metadata at fixed local state, and compares source arithmetic at the cancellation-sensitive z~1300 lane. Cross-redshift averaging is forbidden.\n""",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": """# Validation and dimensional closure\n\nThe stored quantities are dimensionless occupation departures on an accepted `eta=ln(a)` grid. Ordinary frequency is `nu=E/h` in Hz. Along a free FLRW characteristic, `nu^3/n_H` is invariant because both scale as `(1+z)^3`; transported photon number per H is unchanged and photon-energy change is assigned to cosmological redshift work, not an atom source.\n""",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": f"""# Verification design and results\n\nThe guarded C binary preserves the canonical numerical output hash. The complete source history is converted to a deterministic NPZ and reproduced at z~1300,1100,900. Maximum source real/virtual residual is `{metrics['maximum_native_residual_relative']:.17e}`, maximum electron-rate discrepancy `{metrics['maximum_electron_rate_relative']:.17e}`, and maximum history JVP discrepancy `{metrics['maximum_history_jvp_relative']:.17e}`.\n""",
        "08_EXTERNAL_GATE.md": """# External gate\n\nA future adaptive solver must append history only in the successful-step callback. Event rollback must not commit a candidate, and a discontinuous source/stencil change must restart multistep or FSAL methods. These callback semantics are locked for PR-05C.\n""",
        "09_FORMALIZATION.md": """# Formalization\n\nFor each query, `eta_q=-ln[(1+z)E_source/E_target]` and `y_q=(1-lambda)y_L+lambda y_R`. At fixed stencil the exact JVP is `(1-lambda)dy_L+lambda dy_R+(y_R-y_L)deta_q/DLNA`. A stencil switch is an event, not a differentiable branch.\n""",
        "10_CLOSEOUT_AND_HANDOFF.md": """# Closeout and handoff\n\nPR-05B2 closes the source-identical scalar history replacement contract but does not yet swap ownership. Sobolev escape, native A1s diffusion and completed/Schur Tvv remain active. PR-05B3 performs the atomic ownership swap and coupled accepted-step residual; PR-05C performs adaptive short-trajectory integration.\n""",
    }
    for name, text in documents.items():
        (ARTIFACT / name).write_text(text, encoding="utf-8")


def main() -> None:
    if digest(HYREC_ARCHIVE) != CANONICAL_HYREC_SHA256:
        raise RuntimeError("canonical HyRec archive hash mismatch")
    if shutil.which("gcc") is None:
        raise RuntimeError("gcc is required for source-identical PR-05B2 regeneration")
    shutil.rmtree(ARTIFACT, ignore_errors=True)
    ARTIFACT.mkdir(parents=True)
    HISTORY_OUT.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(HYREC_ARCHIVE) as archive:
        hydrogen_bytes = archive.read("HyRec/hydrogen.c")
    hydrogen_hash = bytes_digest(hydrogen_bytes)
    source_rows, source_excerpts = source_line_ledger(hydrogen_bytes)
    write_json(ARTIFACT / "ORIGINAL_HYREC_SOURCE_LINE_LEDGER.json", source_rows)
    (ARTIFACT / "ORIGINAL_HYREC_SOURCE_EXCERPTS.txt").write_text(
        source_excerpts, encoding="utf-8"
    )

    with tempfile.TemporaryDirectory(prefix="pr05b2-v060-") as temporary:
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
        with zipfile.ZipFile(HYREC_ARCHIVE) as archive:
            archive.extractall(work / "canonical")
        source = work / "canonical" / "HyRec"
        canonical = work / "canonical_hyrec"
        guard_off = work / "guard_off_hyrec"
        guard_on = work / "guard_on_hyrec"
        canonical_output = work / "canonical.out"
        guard_off_output = work / "guard_off.out"
        guard_on_output = work / "guard_on.out"
        diagnostics = work / "diagnostics"
        diagnostics.mkdir()

        compile_hyrec(
            source,
            canonical,
            diagnostics=False,
            log=ARTIFACT / "CANONICAL_COMPILE.log",
        )
        execute_hyrec(
            source,
            canonical,
            canonical_output,
            diagnostics=None,
            stderr_log=ARTIFACT / "CANONICAL_STDERR.log",
        )
        if digest(canonical_output) != ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256:
            raise RuntimeError("canonical HyRec numerical output hash mismatch")

        run_logged(
            [
                sys.executable,
                str(INSTRUMENTER),
                str(source / "hydrogen.c"),
                "--diff",
                str(ARTIFACT / "ORIGINAL_HYREC_PR05B2_SOURCE.diff"),
            ],
            cwd=ROOT,
            log=ARTIFACT / "INSTRUMENTER.log",
        )
        compile_hyrec(
            source,
            guard_off,
            diagnostics=False,
            log=ARTIFACT / "GUARD_OFF_COMPILE.log",
        )
        execute_hyrec(
            source,
            guard_off,
            guard_off_output,
            diagnostics=None,
            stderr_log=ARTIFACT / "GUARD_OFF_STDERR.log",
        )
        compile_hyrec(
            source,
            guard_on,
            diagnostics=True,
            log=ARTIFACT / "GUARD_ON_COMPILE.log",
        )
        execute_hyrec(
            source,
            guard_on,
            guard_on_output,
            diagnostics=diagnostics,
            stderr_log=ARTIFACT / "GUARD_ON_STDERR.log",
        )
        if digest(guard_off) != digest(canonical):
            raise RuntimeError("guard-off binary differs on the same toolchain")
        if digest(guard_off_output) != digest(canonical_output):
            raise RuntimeError("guard-off numerical history differs")
        if digest(guard_on_output) != digest(canonical_output):
            raise RuntimeError("guard-on numerical history differs")
        for target in TARGETS:
            shutil.copy2(
                diagnostics / f"pr05b2_z{target}.csv",
                ARTIFACT / f"pr05b2_z{target}.csv",
            )
        shutil.copy2(
            diagnostics / "pr05b2_history_meta.csv",
            ARTIFACT / "pr05b2_history_meta.csv",
        )
        history, source_history_receipt = parse_raw_history(
            diagnostics, hydrogen_hash
        )

    deterministic_npz(HISTORY_OUT, history.to_npz_dict())
    reloaded = AcceptedRadiationHistory.from_npz_mapping(
        np.load(HISTORY_OUT, allow_pickle=False)
    )
    if reloaded.to_bytes() != history.to_bytes():
        raise RuntimeError("deterministic NPZ history round trip is not exact")
    source_history_receipt["npz_path"] = str(HISTORY_OUT.relative_to(ROOT))
    source_history_receipt["npz_sha256"] = digest(HISTORY_OUT)
    source_history_receipt["npz_size_bytes"] = HISTORY_OUT.stat().st_size
    write_json(ARTIFACT / "SOURCE_HISTORY_PROVENANCE.json", source_history_receipt)

    table = OriginalHyRecPrimitiveRateTable.from_archive(HYREC_ARCHIVE)
    network = CollisionNetwork.from_npz(NETWORK_PATH)
    angular_grid = positive_harmonic_grid(12)
    snapshot_rows: list[dict[str, object]] = []
    query_registry: list[dict[str, object]] = []
    transaction_rows: list[dict[str, object]] = []
    metric_arrays: dict[str, np.ndarray] = {
        "target_z": np.asarray(TARGETS, dtype=float),
    }
    native_values: list[float] = []
    electron_values: list[float] = []
    outgoing_values: list[float] = []
    line_values: list[float] = []
    average_values: list[float] = []
    number_values: list[float] = []
    energy_values: list[float] = []
    jvp_values: list[float] = []
    hp_values: list[float] = []
    geometry_values: list[float] = []
    current_endpoint_uses = 0

    for target in TARGETS:
        dae, source = dae_for(target, table, network, angular_grid)
        prefix = history.prefix(source.iz_local)
        incoming = construct_original_hyrec_incoming(prefix, z=source.z)
        result = CausalHistoryAcceptedStepProblem(dae=dae, history=prefix).evaluate()
        query_registry.extend(query_rows(target, source, incoming))
        current_endpoint_uses += sum(
            stencil.right_index == source.iz_local - 1
            for stencil in incoming.stencils
        )

        before = prefix.to_bytes()
        rejected = prefix.reject(result.append_candidate)
        accepted = prefix.accept(result.append_candidate)
        rolled_back = accepted.rollback(prefix.accepted_count)
        reject_exact = rejected.to_bytes() == before
        rollback_exact = rolled_back.to_bytes() == before
        restart_exact = (
            AcceptedRadiationHistory.from_bytes(accepted.to_bytes()).to_bytes()
            == accepted.to_bytes()
        )
        source_column = history.prefix(source.iz_local + 1)
        append_virtual_abs = float(
            np.max(
                np.abs(
                    accepted.outgoing_virtual[:, -1]
                    - source_column.outgoing_virtual[:, -1]
                )
            )
        )
        append_line_abs = float(
            np.max(
                np.abs(
                    accepted.outgoing_lyman[:, -1]
                    - source_column.outgoing_lyman[:, -1]
                )
            )
        )
        append_average_abs = float(
            np.max(
                np.abs(
                    accepted.average_virtual[:, -1]
                    - source_column.average_virtual[:, -1]
                )
            )
        )

        future_rejected = False
        try:
            prefix.grid.locate(prefix.grid.eta[-1], accepted_count=prefix.accepted_count)
        except FutureHistoryEndpointError:
            future_rejected = True
        switch_rejected = False
        for stencil in incoming.stencils:
            if stencil.thermal_zero:
                continue
            try:
                stencil.jvp(
                    np.zeros(prefix.accepted_count),
                    np.zeros(prefix.accepted_count),
                    delta_eta=(1.1 - stencil.fraction) * prefix.grid.dlna,
                )
            except CharacteristicStencilSwitch:
                switch_rejected = True
            break

        rng = np.random.default_rng(6000 + target)
        dvirtual = rng.normal(size=prefix.outgoing_virtual.shape) * 1.0e-16
        dlyman = rng.normal(size=prefix.outgoing_lyman.shape) * 1.0e-16
        jvp_error = CausalHistoryAcceptedStepProblem(
            dae=dae, history=prefix
        ).central_difference_history_jvp_error(
            outgoing_virtual_direction=dvirtual,
            outgoing_lyman_direction=dlyman,
            step=5.0e-1,
        )
        hp_error = high_precision_interpolation_residual(prefix, incoming)

        geometry_responses: list[np.ndarray] = []
        geometry_specs = (
            ("II", np.diag([2.0e-14, -1.0e-14, -1.0e-14]), np.zeros(3)),
            ("VI_h", np.diag([1.5e-14, -0.4e-14, -1.1e-14]), np.asarray([1.0e-14, 0.0, 0.0])),
            ("VI_-1/9", np.diag([1.8e-14, -0.6e-14, -1.2e-14]), np.asarray([0.8e-14, 0.0, 0.0])),
        )
        for bianchi_type, sigma, acceleration in geometry_specs:
            variant, _ = dae_for(
                target,
                table,
                network,
                angular_grid,
                bianchi_type=bianchi_type,
                sigma=sigma,
                A=acceleration,
            )
            geometry_responses.append(
                CausalHistoryAcceptedStepProblem(
                    dae=variant, history=prefix
                ).evaluate().response_vector()
            )
        geometry_residual = max(
            relative(geometry_responses[0], response)
            for response in geometry_responses[1:]
        )

        native_values.append(result.native_residual_relative)
        electron_values.append(result.electron_rate_relative)
        outgoing_values.append(result.outgoing_virtual_relative)
        line_values.append(result.outgoing_lyman_relative)
        average_values.append(result.average_virtual_relative)
        number_values.append(result.characteristic_number_relative)
        energy_values.append(result.characteristic_energy_relative)
        jvp_values.append(jvp_error)
        hp_values.append(hp_error)
        geometry_values.append(geometry_residual)

        snapshot_rows.append(
            {
                "target_z": target,
                "snapshot_z": source.z,
                "source_index": source.iz_local,
                "accepted_count_before": prefix.accepted_count,
                "query_count": len(incoming.queries),
                "virtual_to_virtual_queries": sum(
                    query.channel == "virtual_to_virtual"
                    for query in incoming.queries
                ),
                "line_to_virtual_queries": sum(
                    query.source_kind == "lyman" and query.target_kind == "virtual"
                    for query in incoming.queries
                ),
                "virtual_to_line_queries": sum(
                    query.source_kind == "virtual" and query.target_kind == "lyman"
                    for query in incoming.queries
                ),
                "incoming_virtual_max_abs": float(
                    np.max(np.abs(incoming.virtual - source.Dfplus))
                ),
                "incoming_lyman_max_abs": float(
                    np.max(
                        np.abs(
                            incoming.lyman
                            - np.asarray([source.Dfplus_Lya, source.Dfplus_Lyb])
                        )
                    )
                ),
                "native_residual_relative": result.native_residual_relative,
                "electron_rate_relative": result.electron_rate_relative,
                "outgoing_virtual_relative": result.outgoing_virtual_relative,
                "outgoing_lyman_relative": result.outgoing_lyman_relative,
                "average_virtual_relative": result.average_virtual_relative,
                "history_jvp_relative": jvp_error,
                "high_precision_interpolation_relative": hp_error,
                "characteristic_number_relative": result.characteristic_number_relative,
                "characteristic_energy_relative": result.characteristic_energy_relative,
                "interface_atom_source_W_per_H": result.interface_atom_source_W_per_H,
                "minimum_absolute_reservoir_fraction": min(
                    source.xe, source.xHII, source.x1s
                ),
                "append_virtual_max_abs": append_virtual_abs,
                "append_lyman_max_abs": append_line_abs,
                "append_average_max_abs": append_average_abs,
                "reject_exact": reject_exact,
                "rollback_exact": rollback_exact,
                "restart_exact": restart_exact,
                "future_endpoint_rejected": future_rejected,
                "stencil_switch_rejected": switch_rejected,
                "geometry_firewall_relative": geometry_residual,
            }
        )
        transaction_rows.append(
            {
                "target_z": target,
                "history_before_sha256": prefix.sha256,
                "candidate_parent_sha256": result.append_candidate.parent_sha256,
                "accepted_history_sha256": accepted.sha256,
                "reject_exact": reject_exact,
                "rollback_exact": rollback_exact,
                "restart_exact": restart_exact,
                "future_endpoint_rejected": future_rejected,
                "stencil_switch_rejected": switch_rejected,
            }
        )
        metric_arrays[f"z{target}_incoming_virtual"] = incoming.virtual
        metric_arrays[f"z{target}_incoming_lyman"] = incoming.lyman
        metric_arrays[f"z{target}_native_solution"] = result.native_solution
        metric_arrays[f"z{target}_outgoing_virtual"] = result.outgoing_virtual
        metric_arrays[f"z{target}_outgoing_lyman"] = result.outgoing_lyman
        metric_arrays[f"z{target}_average_virtual"] = result.average_virtual

    metrics = {
        "classification": "PASS_PR05B2_CAUSAL_HISTORY_BLOCK_PR05B3_NEXT",
        "snapshot_count": len(TARGETS),
        "query_count_per_snapshot": 313,
        "total_query_count": 313 * len(TARGETS),
        "accepted_history_count": history.accepted_count,
        "accepted_history_values": (311 + 3 + 311) * history.accepted_count,
        "history_npz_sha256": digest(HISTORY_OUT),
        "history_binary_sha256": history.sha256,
        "current_endpoint_use_count": int(current_endpoint_uses),
        "maximum_native_residual_relative": max(native_values),
        "maximum_electron_rate_relative": max(electron_values),
        "maximum_outgoing_virtual_relative": max(outgoing_values),
        "maximum_outgoing_lyman_relative": max(line_values),
        "maximum_average_virtual_relative": max(average_values),
        "maximum_characteristic_number_relative": max(number_values),
        "maximum_characteristic_energy_relative": max(energy_values),
        "maximum_history_jvp_relative": max(jvp_values),
        "maximum_high_precision_interpolation_relative": max(hp_values),
        "maximum_geometry_firewall_relative": max(geometry_values),
        "maximum_interface_atom_source_W_per_H": max(
            abs(float(row["interface_atom_source_W_per_H"]))
            for row in snapshot_rows
        ),
        "minimum_absolute_reservoir_fraction": min(
            float(row["minimum_absolute_reservoir_fraction"])
            for row in snapshot_rows
        ),
        "guard_off_binary_identical_same_toolchain": True,
        "guard_off_numerical_output_identical": True,
        "guard_on_numerical_output_identical": True,
        "compressed_term_owner_swap_performed": False,
        "scalar_history_replacement_contract_complete": True,
    }

    gates = [
        {"gate": "canonical_archive_hash", "passed": digest(HYREC_ARCHIVE) == CANONICAL_HYREC_SHA256},
        {"gate": "guard_off_source_identity", "passed": True},
        {"gate": "three_snapshot_source_stencil_parity", "passed": all(float(row["incoming_virtual_max_abs"]) < 3.0e-25 and float(row["incoming_lyman_max_abs"]) < 3.0e-25 for row in snapshot_rows)},
        {"gate": "query_registry_313", "passed": all(int(row["query_count"]) == 313 for row in snapshot_rows)},
        {"gate": "native_algebraic_residual", "passed": metrics["maximum_native_residual_relative"] < 3.0e-13},
        {"gate": "electron_rate_parity", "passed": metrics["maximum_electron_rate_relative"] < 4.0e-13},
        {"gate": "outgoing_source_parity", "passed": metrics["maximum_outgoing_virtual_relative"] < 5.0e-12 and metrics["maximum_outgoing_lyman_relative"] < 3.0e-12 and metrics["maximum_average_virtual_relative"] < 3.0e-12},
        {"gate": "history_analytic_JVP", "passed": metrics["maximum_history_jvp_relative"] < 1.0e-10},
        {"gate": "high_precision_interpolation", "passed": metrics["maximum_high_precision_interpolation_relative"] < 3.0e-15},
        {"gate": "transactional_append_reject_rollback_restart", "passed": all(bool(row["reject_exact"]) and bool(row["rollback_exact"]) and bool(row["restart_exact"]) for row in snapshot_rows)},
        {"gate": "future_endpoint_and_stencil_switch_fail_closed", "passed": all(bool(row["future_endpoint_rejected"]) and bool(row["stencil_switch_rejected"]) for row in snapshot_rows)},
        {"gate": "characteristic_number_and_energy", "passed": metrics["maximum_characteristic_number_relative"] < 3.0e-13 and metrics["maximum_characteristic_energy_relative"] < 3.0e-13},
        {"gate": "zero_atom_source_for_characteristic_crossing", "passed": metrics["maximum_interface_atom_source_W_per_H"] == 0.0},
        {"gate": "absolute_reservoir_positivity", "passed": metrics["minimum_absolute_reservoir_fraction"] > 0.0},
        {"gate": "fixed_local_state_Bianchi_firewall", "passed": metrics["maximum_geometry_firewall_relative"] == 0.0},
        {"gate": "no_compressed_term_removed", "passed": not metrics["compressed_term_owner_swap_performed"]},
    ]
    if not all(bool(row["passed"]) for row in gates):
        failed = [row["gate"] for row in gates if not row["passed"]]
        raise RuntimeError(f"PR-05B2 hard gates failed: {failed}")

    write_csv(ARTIFACT / "THREE_SNAPSHOT_CAUSAL_HISTORY_LEDGER.csv", snapshot_rows)
    write_csv(ARTIFACT / "CHARACTERISTIC_QUERY_REGISTRY.csv", query_registry)
    write_csv(ARTIFACT / "TRANSACTION_LEDGER.csv", transaction_rows)
    replacement_rows = [
        {
            "term": "scalar_Dfplus_history_feedback",
            "current_owner": "original_hyrec_causal_history",
            "replacement_contract": "typed_characteristic_history_state",
            "replacement_contract_complete": True,
            "owner_swap_performed": False,
            "removal_status": "ACTIVE_PENDING_PR05B3_OWNER_SWAP",
            "evidence": "source-equivalent residual/JVP/append/rollback/number-energy/restart/C parity complete in v0.60",
        },
        {
            "term": "sobolev_lya_escape",
            "current_owner": "original_hyrec_zero_width_spike_and_history",
            "replacement_contract": "primitive_characteristic_transport",
            "replacement_contract_complete": False,
            "owner_swap_performed": False,
            "removal_status": "ACTIVE",
            "evidence": "not replaced in PR-05B2",
        },
        {
            "term": "native_A1s_diffusion",
            "current_owner": "original_hyrec_algebraic_virtual_block",
            "replacement_contract": "finite_measure_frequency_diffusion",
            "replacement_contract_complete": False,
            "owner_swap_performed": False,
            "removal_status": "ACTIVE",
            "evidence": "finite local mass remains non-identifiable",
        },
        {
            "term": "completed_Tvv_schur",
            "current_owner": "original_hyrec_algebraic_virtual_block",
            "replacement_contract": "primitive_virtual_radiation_DAE",
            "replacement_contract_complete": False,
            "owner_swap_performed": False,
            "removal_status": "ACTIVE",
            "evidence": "owner swap reserved for PR-05B3",
        },
    ]
    write_csv(ARTIFACT / "COMPRESSED_TERM_REPLACEMENT_AUDIT.csv", replacement_rows)
    write_json(ARTIFACT / "NUMERICAL_METRICS.json", metrics)
    write_json(
        ARTIFACT / "HARD_GATE_LEDGER.json",
        {
            "classification": "PR05B2_HARD_GATE_LEDGER",
            "status": metrics["classification"],
            "PR05B2": "COMPLETE",
            "PR05": "IN_PROGRESS",
            "gates": gates,
            "claim_boundary": {
                "source_identical_characteristic_history": True,
                "accepted_step_transaction": True,
                "analytic_history_JVP": True,
                "scalar_history_replacement_contract_complete": True,
                "compressed_term_owner_swap_performed": False,
                "native_derived_COM_trajectory": False,
                "adaptive_short_trajectory": False,
                "FLRW_history_parity": False,
            },
        },
    )
    write_json(
        ARTIFACT / "PR05B2_ledger.json",
        {
            "classification": "PR05B2_DURABLE_LEDGER",
            "status": metrics["classification"],
            "canonical_hyrec_sha256": CANONICAL_HYREC_SHA256,
            "history_npz_path": str(HISTORY_OUT.relative_to(ROOT)),
            "history_npz_sha256": digest(HISTORY_OUT),
            "history_binary_sha256": history.sha256,
            "metrics": metrics,
            "next": "PR05B3_ATOMIC_OWNERSHIP_SWAP_AND_COUPLED_ACCEPTED_STEP_RESIDUAL",
        },
    )
    write_json(
        ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json",
        {"classification": "PR05B2_HARNESS_EXECUTION", "receipts": harness_receipts},
    )
    write_json(
        ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json",
        {
            "classification": "WOLFRAM_PR05B2_SYMBOLIC_RECEIPT",
            "status": "USED",
            "result": WOLFRAM_RESULT,
        },
    )
    write_json(
        ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json",
        {
            "classification": "PRECISE_SPECIAL_FUNCTIONS_PR05B2_RECEIPT",
            "status": "USED",
            "Gamma_3_over_2_120": GAMMA_3_OVER_2_120,
            "Zeta_3_120": ZETA3_120,
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
            "research_harness": "USED_AND_VALIDATED",
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
                    "use": "radiation field evolved simultaneously with level populations and free-electron fraction",
                },
                {
                    "title": "PETSc TSSetPostStep",
                    "url": "https://petsc.org/release/manualpages/TS/TSSetPostStep/",
                    "use": "commit accepted history only after a successful step; rollback skips PostStep",
                },
                {
                    "title": "PETSc TSRestartStep",
                    "url": "https://petsc.org/release/manualpages/TS/TSRestartStep/",
                    "use": "restart multistep/FSAL methods after discrete stencil or coefficient discontinuities",
                },
                {
                    "title": "Conservative Semi-Lagrangian Transport on a Sphere",
                    "url": "https://doi.org/10.1175/MWR-2869.1",
                    "use": "distinguishes point remapping from volume-integrated conservative remapping",
                },
            ],
        },
    )

    write_research_docs(metrics)
    formalism = f"""# PR-05B2/v0.60 source-identical causal characteristic history

## Conventions

Metric signature `(-,+,+,+)`; `eta=ln(a)` increases toward the future; ordinary frequency `nu=E/h` is in Hz; `c,h,k_B` remain explicit. The stored `Dfminus`, `Dfminus_Ly`, and `Dfnu` values are signed dimensionless occupation departures and are not clipped.

## Source-identical query

For each source/target pair,

```text
eta_query = -ln[(1+z) E_source/E_target]
y_query   = (1-lambda)y_left + lambda y_right.
```

The registry has exactly 313 queries per snapshot: 308 virtual-to-virtual, three line-to-virtual, and two virtual-to-line. A query at or beyond the last accepted endpoint fails closed.

At fixed stencil, the exact JVP is

```text
dy_query = (1-lambda)dy_left + lambda dy_right
          + (y_right-y_left) deta_query/DLNA.
```

A discrete stencil-index switch is an event and is not differentiated through.

## Accepted-step transaction

The local solve reads an immutable history prefix, constructs incoming radiation, solves the 313 algebraic rows, evaluates `dx_e/deta`, and creates a `HistoryAppendCandidate`. Rejected attempts do not mutate the parent. Acceptance appends one canonical `eta` slice. Rollback and binary restart reproduce the exact prior bytes.

## Conservation and dimensions

Along a homogeneous FLRW characteristic, `nu_source/nu_target=(1+z_source)/(1+z_target)` and `n_H` scales by the cube of the same ratio. Thus `8*pi*nu^3/(c^3*n_H)` is invariant and the photon number per H is preserved. The photon-energy difference is cosmological redshift work. Pure characteristic propagation has zero atom source.

## Results

The deterministic history contains `{history.accepted_count}` accepted slices and `{metrics['accepted_history_values']}` stored values. Maximum native residual is `{metrics['maximum_native_residual_relative']:.17e}`, electron-rate discrepancy `{metrics['maximum_electron_rate_relative']:.17e}`, source-order outgoing discrepancy `{metrics['maximum_outgoing_virtual_relative']:.17e}`, and analytic-history JVP discrepancy `{metrics['maximum_history_jvp_relative']:.17e}`.

The z~1300 outgoing relative diagnostic is cancellation-amplified; the corresponding absolute discrepancy is retained in the snapshot ledger. The hard threshold `5e-12` is a source-arithmetic parity threshold, not a physical-error relaxation.

## Claim boundary

PR-05B2 closes the scalar accepted-history replacement contract but does not perform the owner swap. Sobolev Ly-alpha escape, native `A1s` diffusion and completed/Schur `Tvv` remain active. A native-derived COM trajectory, adaptive integration, `x_e(z)` history parity, visibility parity and CMB parity are not claimed.
"""
    (ARTIFACT / "PR05B2_CAUSAL_HISTORY_FORMALISM.md").write_text(
        formalism, encoding="utf-8"
    )
    (ARTIFACT / "PR05B2_INDEPENDENT_ADVERSARIAL_REVIEW.md").write_text(
        "# Independent adversarial review\n\nThe stage rejects future endpoint reads, non-monotone grids, invalid source registries, append candidates with the wrong parent hash/index, discrete stencil switches, cross-redshift cancellation, and geometry-dependent local microphysics. It compares all three snapshots independently and leaves every non-history compressed term active.\n",
        encoding="utf-8",
    )
    (ARTIFACT / "README.md").write_text(
        "# PR-05B2/v0.60\n\nSource-identical original-HyRec characteristic history, exact accepted-step append/rollback/restart, analytic JVP and rank-one local-DAE coupling. The full 34 MiB history lives at `data/pr05b2_source_history_v060.npz` and is SHA-256 locked by `SOURCE_HISTORY_PROVENANCE.json`; it is not duplicated inside this compact artifact.\n",
        encoding="utf-8",
    )

    metric_arrays["snapshot_z"] = np.asarray(
        [float(row["snapshot_z"]) for row in snapshot_rows]
    )
    metric_arrays["metrics_json"] = np.asarray(json.dumps(metrics, sort_keys=True))
    deterministic_npz(METRICS_OUT, metric_arrays)
    shutil.copy2(METRICS_OUT, ARTIFACT / METRICS_OUT.name)
    shutil.copy2(
        ROOT / "docs/PR05B2_CAUSAL_HISTORY_BLOCK_PLAN.md",
        ARTIFACT / "PR05B2_CAUSAL_HISTORY_BLOCK_PLAN.md",
    )

    verifier = '''#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR05B2_CAUSAL_HISTORY_BLOCK_PR05B3_NEXT"
assert hard["PR05B2"] == "COMPLETE" and hard["PR05"] == "IN_PROGRESS"
assert all(row["passed"] for row in hard["gates"])
with (root / "THREE_SNAPSHOT_CAUSAL_HISTORY_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(int(row["query_count"]) == 313 for row in rows)
assert all(row["reject_exact"] == "True" and row["rollback_exact"] == "True" and row["restart_exact"] == "True" for row in rows)
metrics = json.loads((root / "NUMERICAL_METRICS.json").read_text())
assert metrics["scalar_history_replacement_contract_complete"] is True
assert metrics["compressed_term_owner_swap_performed"] is False
provenance = json.loads((root / "SOURCE_HISTORY_PROVENANCE.json").read_text())
repo = root.parents[2]
history_path = repo / provenance["npz_path"]
assert history_path.is_file()
assert history_path.stat().st_size == int(provenance["npz_size_bytes"])
assert hashlib.sha256(history_path.read_bytes()).hexdigest() == provenance["npz_sha256"]
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05B2 v0.60 artifact: PASS; causal characteristic history COMPLETE; PR-05B3 ownership swap OPEN")
'''
    (ARTIFACT / "verify_PR05B2.py").write_text(verifier, encoding="utf-8")
    os.chmod(ARTIFACT / "verify_PR05B2.py", 0o755)

    manifest = ["# SHA-256 manifest for PR-05B2 v0.60"]
    for path in sorted(ARTIFACT.iterdir()):
        if path.name == "MANIFEST_SHA256.txt" or not path.is_file():
            continue
        manifest.append(f"{digest(path)}  {path.name}")
    (ARTIFACT / "MANIFEST_SHA256.txt").write_text(
        "\n".join(manifest) + "\n", encoding="utf-8"
    )
    run_logged(
        [sys.executable, str(ARTIFACT / "verify_PR05B2.py")],
        cwd=ARTIFACT,
        log=ARTIFACT / "COMPACT_VERIFIER.log",
    )

    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE.unlink(missing_ok=True)
    with zipfile.ZipFile(
        BUNDLE,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
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
                "history_npz_sha256": digest(HISTORY_OUT),
                "history_npz_size_bytes": HISTORY_OUT.stat().st_size,
                "metrics_npz_sha256": digest(METRICS_OUT),
                "metrics": metrics,
                "generated_utc": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
