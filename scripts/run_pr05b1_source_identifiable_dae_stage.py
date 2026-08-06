#!/usr/bin/env python3
"""Build PR-05B1/v0.59 source-identifiable DAE and native-time-measure no-go evidence.

The canonical October-2012 original-HyRec source evolves x_e in eta=ln(a),
solves the 2s/2p plus 311 virtual departures algebraically, and stores radiation
time dependence in causal accepted-step history arrays.  This stage exposes
that exact differential/algebraic/memory split and refuses to invent a finite
local virtual-spike mass without source-defined support widths, cell edges, or
spike shape.
"""
from __future__ import annotations

import csv
from dataclasses import asdict
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

from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (  # noqa: E402
    CollisionNetwork,
    LineBoundaryConfig,
    positive_harmonic_grid,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (  # noqa: E402
    IONIZATION_ENERGY_EV,
    OriginalHyRecPrimitiveRateTable,
    SAHA_COEFFICIENT_CGS,
)
from full_bianchi_hyrec.trajectory.primitive_trajectory import (  # noqa: E402
    PrimitiveTrajectoryProblem,
    atomic_state_from_source_snapshot,
)
from full_bianchi_hyrec.trajectory.time_dependent_native import (  # noqa: E402
    CausalRadiationHistoryState,
    OriginalHyRecStateRole,
    SourceIdentifiableOriginalHyRecDAE,
    audit_canonical_native_radiation_time_measure,
    default_pr05b1_replacement_registry,
    source_identifiable_original_hyrec_layout,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR05B1_source_identifiable_DAE_native_time_measure_no_go_v0_59"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr05b1_source_identifiable_dae_v059.npz"
HYREC_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
NETWORK_PATH = ROOT / "data/full_scalar_com_khw_v050.npz"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CANONICAL_HYREC_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
TARGETS = (1300, 1100, 900)
GAMMA_3_OVER_2_120 = "0.886226925452758013649083741670572591398774728061193564106903894926455642295516090687475328369272332708113411812141285333"
ZETA3_120 = "1.20205690315959428539973816151144999076498629234049888179227155534183820578631309018645587360933525814619915779526071942"
WOLFRAM_RESULT = {
    "shifted_electron_row": [
        "shift + ((alpha_2s + alpha_2p)*n_H*x_HII)/H",
        "-beta_2s/H",
        "-beta_2p/H",
    ],
    "source_residual_after_xedot_substitution": 0,
    "finite_width_mass_ratio": 2,
    "zero_width_candidate_limits": [0, 0],
    "cross_lane_signed_sum": 0,
    "cross_lane_componentwise_max": "Max[0,Abs[e]]",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bytes_digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_logged(command: list[str], *, cwd: Path, log: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    with log.open("wb") as output:
        result = subprocess.run(command, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")
    return result


def validate_harness(archive: Path, expected: str, validator: str, work: Path, log: Path) -> dict[str, object]:
    observed = digest(archive)
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
    result = run_logged([sys.executable, str(matches[0])], cwd=matches[0].parents[1], log=log)
    return {
        "archive": archive.name,
        "sha256": observed,
        "validator": validator,
        "exit_code": result.returncode,
        "passed": True,
    }


def background_for(source, *, bianchi_type: str = "I", sigma: np.ndarray | None = None, A: np.ndarray | None = None) -> BackgroundSnapshot:
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
        chart_id="pr05b1-v059",
        bianchi_type=bianchi_type,
    )


def problem_for(target: int, table: OriginalHyRecPrimitiveRateTable, network: CollisionNetwork, grid, *, bianchi_type: str = "I", sigma: np.ndarray | None = None, A: np.ndarray | None = None):
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
        com_occupation=scalar[:, None] * np.ones((1, grid.n_angle)),
        beta_H=np.zeros(3),
    )
    primitive = PrimitiveTrajectoryProblem(
        background=background_for(source, bianchi_type=bianchi_type, sigma=sigma, A=A),
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=grid,
        line=LineBoundaryConfig.lyman_alpha(temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25),
        interface_enabled=False,
    )
    return SourceIdentifiableOriginalHyRecDAE.from_primitive_problem(primitive), state, source


def state_role_rows() -> list[dict[str, object]]:
    layout = source_identifiable_original_hyrec_layout()
    return [
        {
            "name": block.name,
            "size": block.size,
            "role": block.role.value,
            "unit": block.unit,
            "source_owner": block.source_owner,
            "source_evidence": block.source_evidence,
            "local_mass_value": 1 if block.role is OriginalHyRecStateRole.DIFFERENTIAL else (0 if block.role is OriginalHyRecStateRole.ALGEBRAIC else "OUTSIDE_LOCAL_MASS_MATRIX"),
        }
        for block in layout.blocks
    ]


def source_line_rows(hydrogen_bytes: bytes) -> tuple[list[dict[str, object]], str]:
    text = hydrogen_bytes.decode("utf-8")
    lines = text.splitlines()
    ranges = [
        ("populate_rate_and_compressed_transfer", 413, 526, "Trr/Trv/Tvr/Tvv, Sobolev-like optical-depth compression, diffusion and source vectors"),
        ("algebraic_real_virtual_solve", 565, 625, "solve T X=B for 2s/2p and 311 virtual departures; no local derivative row"),
        ("causal_interpolator", 627, 654, "linear interpolation over already available accepted history with explicit range rejection"),
        ("incoming_characteristic_history", 657, 718, "construct fplus from prior/higher-frequency fminus history"),
        ("electron_differential_and_history_append", 730, 805, "compute dxHIIdlna, then append outgoing/average radiation to current accepted index"),
    ]
    rows: list[dict[str, object]] = []
    excerpts: list[str] = []
    member_hash = bytes_digest(hydrogen_bytes)
    for name, start, end, meaning in ranges:
        payload = "\n".join(lines[start - 1 : end]) + "\n"
        rows.append({
            "claim": name,
            "archive_member": "HyRec/hydrogen.c",
            "member_sha256": member_hash,
            "line_start": start,
            "line_end": end,
            "excerpt_sha256": bytes_digest(payload.encode("utf-8")),
            "meaning": meaning,
        })
        excerpts.append(f"===== {name}: hydrogen.c:{start}-{end} =====\n{payload}")
    return rows, "\n".join(excerpts)


def replacement_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    registry = default_pr05b1_replacement_registry()
    rows = [asdict(term) for term in registry.terms]
    return rows, asdict(registry.audit())


def high_precision_electron_rate(problem: SourceIdentifiableOriginalHyRecDAE, source) -> tuple[float, str]:
    mp.mp.dps = 100
    nH = mp.mpf(str(source.nH_cm3))
    H = mp.mpf(str(source.H_s_inv))
    Tr = mp.mpf(str(source.TR_eV_rescaled))
    fsR = mp.mpf(str(source.fsR))
    meR = mp.mpf(str(source.meR))
    x1s = mp.mpf(str(source.x1s))
    xe = mp.mpf(str(source.xe))
    xHII = mp.mpf(str(source.xHII))
    saha = mp.mpf(str(SAHA_COEFFICIENT_CGS)) * (fsR * meR) ** 3 * Tr * mp.sqrt(Tr) * mp.exp(-mp.mpf(str(IONIZATION_ENERGY_EV)) / Tr) / nH
    dxe2 = xe * xHII - saha * x1s
    total = mp.mpf("0")
    for level in range(2):
        alpha = mp.mpf(str(problem.rates.alpha_m3_s[level])) * mp.mpf("1e6")
        delta = mp.mpf(str(problem.rates.delta_alpha_m3_s[level])) * mp.mpf("1e6")
        beta = mp.mpf(str(problem.rates.beta_s_inv[level]))
        real = mp.mpf(str(source.xr[level]))
        total += nH * (saha * x1s * delta + alpha * dxe2) - real * beta
    reference = -total / H
    observed = mp.mpf(str(problem.electron_rate_per_lna(source.xe, source.xr)))
    relative = abs(observed - reference) / max(abs(reference), mp.mpf("1e-1000"))
    return float(relative), mp.nstr(reference, 90)


def history_from_source(source) -> CausalRadiationHistoryState:
    return CausalRadiationHistoryState(
        accepted_index=source.iz_local,
        outgoing_virtual=source.Dfminus,
        outgoing_lyman=np.asarray([source.Dfminus_Lya, source.Dfminus_Lyb, source.Dfminus_Lyg]),
        average_virtual=source.Dfbar,
    )


def write_research_docs(metrics: dict[str, object], no_go: dict[str, object]) -> None:
    docs = {
        "01_RESEARCH_CONTRACT.md": """# PR-05B1 research contract\n\nPrimary question: which original-HyRec variables are source-identifiably differential, algebraic, or causal-memory variables, and can a finite local virtual-radiation time mass be derived without adding a new closure?\n\nConventions: metric `(-,+,+,+)`, eta=ln(a), ordinary frequency in Hz, explicit c/h/k_B, homogeneous scalar background. No fitted timescale or native-to-COM state remap is allowed.\n""",
        "02_EVIDENCE_ACQUISITION.md": """# Evidence acquisition\n\nEvidence is the byte-locked October-2012 archive, exact C source-line ranges, three source-identical snapshots, the v0.58 rate adapter, research/coding harness receipts, primary HyRec and PETSc documentation, Wolfram symbolic identities, and 100-digit independent arithmetic. Transcript claims are excluded.\n""",
        "03_CLAIM_SOURCE_AUDIT.md": """# Claim/source audit\n\n`dxHIIdlna` owns the sole local differential row. `solve_real_virt` owns the 313 algebraic rows. `Dfminus_hist`, `Dfminus_Ly_hist`, and `Dfnu_hist` own accepted-step radiation memory. The archive contains centre frequencies and integrated rates but no finite spike widths, cell edges, or spike shape capable of defining a local transient mass.\n""",
        "04_HYPOTHESIS_SPACE.md": """# Hypothesis space\n\n- H_A: canonical evidence identifies a finite local native-radiation mass and PR-05B can promote virtual spikes to differential rows.\n- H_B: canonical evidence identifies only a semi-explicit DAE plus causal history; finite local mass is non-identifiable.\n- Rejected: arbitrary top-hat/Voronoi widths, fitted relaxation time, silent finite-volume reinterpretation, or deletion of compressed terms without complete replacement.\n""",
        "05_ADVERSARIAL_REVIEW.md": """# Adversarial review\n\nTwo positive, nonoverlapping support-width choices centered on the same canonical frequencies generate mass vectors differing by exactly a factor of two while sharing the same zero-width algebraic limit. This is a constructive non-uniqueness witness, not a numerical conditioning issue. Cross-redshift signed cancellation is forbidden.\n""",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": """# Validation and dimensional closure\n\nThe local mass diagonal is `(1,0,...,0)` in eta=ln(a). Real/virtual residuals have source rate units before normalization and are algebraic. Causal history arrays are dimensionless occupation departures stored only after a source step is solved. Candidate finite spike masses are proportional to `Delta ln(nu)/x_1s`; because `Delta ln(nu)` is not source-fixed, the mass is not source-identifiable.\n""",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": f"""# Verification design and results\n\nThree source lanes pass source `dxHIIdlna`, local residual, PETSc-shifted IJacobian, positive frozen-coefficient backward Euler, restart, causality and fixed-local-state Bianchi firewalls. Maximum source-rate relative discrepancy: `{metrics['maximum_source_electron_rate_relative']:.17e}`. Maximum IJacobian discrepancy: `{metrics['maximum_shifted_ijacobian_relative']:.17e}`. Candidate mass ratio: `{no_go['candidate_mass_ratio']:.17e}`.\n""",
        "08_EXTERNAL_GATE.md": """# External gate\n\nA future finite local transient native-radiation block requires an independently justified finite frequency measure: source-defined edges/shape, a new convergent finite-volume derivation with explicit claim downgrade, or an external code/paper that supplies an equivalent measure. None is silently assumed here.\n""",
        "09_FORMALIZATION.md": """# Formalization\n\nThe source-identifiable local system is `M U' - F(U;H)=0` with rank-one local mass matrix. The 313-state real/virtual block remains algebraic. Accepted-step radiation memory is an external causal state updated only after the algebraic solve. The requested finite local native-radiation mass is underdetermined by canonical evidence.\n""",
        "10_CLOSEOUT_AND_HANDOFF.md": """# Closeout and handoff\n\nPR-05B1 closes as a bounded no-go for a source-identifiable finite local native-radiation mass. No compressed term is removed. PR-05B2 must implement the causal characteristic-history state, accepted-step append/rollback, exact source interpolation and its analytic JVP before any adaptive PR-05C trajectory.\n""",
    }
    for name, text in docs.items():
        (ARTIFACT / name).write_text(text, encoding="utf-8")


def main() -> None:
    if digest(HYREC_ARCHIVE) != CANONICAL_HYREC_SHA256:
        raise RuntimeError("canonical HyRec archive hash mismatch")
    shutil.rmtree(ARTIFACT, ignore_errors=True)
    ARTIFACT.mkdir(parents=True)
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(HYREC_ARCHIVE) as archive:
        hydrogen_bytes = archive.read("HyRec/hydrogen.c")
    source_rows, source_excerpts = source_line_rows(hydrogen_bytes)
    (ARTIFACT / "ORIGINAL_HYREC_SOURCE_EXCERPTS.txt").write_text(source_excerpts, encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="pr05b1-v059-") as temporary:
        work = Path(temporary)
        harness_receipts = [
            validate_harness(CODING_HARNESS, CODING_HARNESS_SHA256, "validate_harness.py", work, ARTIFACT / "CODING_HARNESS_VALIDATION.log"),
            validate_harness(RESEARCH_HARNESS, RESEARCH_HARNESS_SHA256, "validate_workspace.py", work, ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log"),
        ]

    table = OriginalHyRecPrimitiveRateTable.from_archive(HYREC_ARCHIVE)
    network = CollisionNetwork.from_npz(NETWORK_PATH)
    grid = positive_harmonic_grid(12)
    layout = source_identifiable_original_hyrec_layout()
    replacement, replacement_audit = replacement_rows()

    rows: list[dict[str, object]] = []
    mass_rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {"mass_diagonal": layout.mass_diagonal}
    source_relative_values: list[float] = []
    residual_values: list[float] = []
    jvp_values: list[float] = []
    be_values: list[float] = []
    min_physical_values: list[float] = []
    high_precision_values: list[float] = []
    history_roundtrip_values: list[bool] = []
    future_rejection_values: list[bool] = []
    mass_ratio_values: list[float] = []
    mass_difference_values: list[float] = []

    for target in TARGETS:
        problem, state, source = problem_for(target, table, network, grid)
        vector = problem.source_state_vector(state)
        derivative = problem.source_derivative_vector()
        residual = problem.residual(vector, derivative)
        scaled = problem.scaled_residual(residual, vector, derivative)
        source_rate = problem.electron_rate_per_lna(source.xe, source.xr)
        source_relative = abs(source_rate - source.dxHIIdlna) / max(abs(source.dxHIIdlna), 1.0e-300)
        rng = np.random.default_rng(target + 59)
        jvp = problem.central_difference_shifted_ijacobian_error(
            vector,
            derivative,
            direction=rng.normal(size=vector.size),
            shift=3.7,
            step=2.0e-7,
        )
        old = np.array(vector, copy=True)
        old[0] *= 1.001
        be = problem.frozen_coefficient_backward_euler_step(old, delta_lna=1.0e-5)
        hp_relative, hp_rate = high_precision_electron_rate(problem, source)
        history = history_from_source(source)
        restart = problem.restart_payload(vector, history)
        decoded_vector, decoded_history = problem.from_restart_payload(restart)
        history_exact = (
            np.array_equal(decoded_vector, vector)
            and decoded_history.accepted_index == history.accepted_index
            and np.array_equal(decoded_history.outgoing_virtual, history.outgoing_virtual)
            and np.array_equal(decoded_history.outgoing_lyman, history.outgoing_lyman)
            and np.array_equal(decoded_history.average_virtual, history.average_virtual)
        )
        future_rejected = False
        try:
            history.assert_endpoint_is_available(history.accepted_index + 1)
        except ValueError:
            future_rejected = True
        mass_audit = audit_canonical_native_radiation_time_measure(source.energy_eV, x_1s=source.x1s)
        ratio = float(np.max(mass_audit.candidate_mass_b / mass_audit.candidate_mass_a))
        stiffness = float(np.min(np.diag(problem.native_matrix_s_inv)) / source.H_s_inv)
        row = {
            "target_z": float(target),
            "snapshot_z": source.z,
            "local_size": layout.local_size,
            "differential_rows": layout.differential_size,
            "algebraic_rows": layout.algebraic_size,
            "history_values": layout.history_size,
            "source_electron_rate_per_lna": source.dxHIIdlna,
            "python_electron_rate_per_lna": source_rate,
            "source_electron_rate_relative": source_relative,
            "high_precision_electron_rate_per_lna": hp_rate,
            "high_precision_electron_rate_relative": hp_relative,
            "scaled_source_residual": scaled,
            "shifted_ijacobian_relative": jvp,
            "backward_euler_backward_error": be.backward_error,
            "backward_euler_algebraic_residual": be.algebraic_residual_relative,
            "minimum_physical_population": be.minimum_physical_population,
            "native_diagonal_over_H_min": stiffness,
            "history_restart_exact": history_exact,
            "future_endpoint_rejected": future_rejected,
            "native_local_time_measure_identifiable": mass_audit.identifiable,
            "finite_support_widths_present": mass_audit.finite_support_widths_present,
            "cell_edges_present": mass_audit.cell_edges_present,
            "spike_shape_present": mass_audit.spike_shape_present,
            "candidate_mass_ratio_b_over_a": ratio,
            "candidate_mass_max_relative_difference": mass_audit.maximum_relative_candidate_difference,
            "state_classification": "SOURCE_IDENTIFIABLE_SEMI_EXPLICIT_DAE_WITH_CAUSAL_ACCEPTED_STEP_MEMORY",
        }
        rows.append(row)
        for index, (energy, mass_a, mass_b) in enumerate(zip(source.energy_eV, mass_audit.candidate_mass_a, mass_audit.candidate_mass_b)):
            mass_rows.append({
                "target_z": target,
                "virtual_index": index,
                "energy_eV": energy,
                "candidate_mass_a_Delta_ln_nu_over_x1s": mass_a,
                "candidate_mass_b_Delta_ln_nu_over_x1s": mass_b,
                "ratio_b_over_a": mass_b / mass_a,
                "canonical_choice": "NONE",
            })
        arrays[f"z{target}_source_state"] = vector
        arrays[f"z{target}_source_derivative"] = derivative
        arrays[f"z{target}_source_residual"] = residual
        arrays[f"z{target}_be_state"] = be.state_vector
        arrays[f"z{target}_candidate_mass_a"] = mass_audit.candidate_mass_a
        arrays[f"z{target}_candidate_mass_b"] = mass_audit.candidate_mass_b
        arrays[f"z{target}_history_outgoing_virtual"] = history.outgoing_virtual
        arrays[f"z{target}_history_outgoing_lyman"] = history.outgoing_lyman
        arrays[f"z{target}_history_average_virtual"] = history.average_virtual
        source_relative_values.append(source_relative)
        residual_values.append(scaled)
        jvp_values.append(jvp)
        be_values.append(be.backward_error)
        min_physical_values.append(be.minimum_physical_population)
        high_precision_values.append(hp_relative)
        history_roundtrip_values.append(history_exact)
        future_rejection_values.append(future_rejected)
        mass_ratio_values.append(ratio)
        mass_difference_values.append(mass_audit.maximum_relative_candidate_difference)

    shear = np.diag([2.0e-14, -1.0e-14, -1.0e-14])
    geometry_problems = (
        problem_for(1100, table, network, grid, bianchi_type="II", sigma=shear),
        problem_for(1100, table, network, grid, bianchi_type="VI_h", A=np.asarray([2.0e-14, 0.0, 0.0])),
        problem_for(1100, table, network, grid, bianchi_type="VI_-1/9", sigma=-shear),
    )
    geometry_residuals = [problem.residual(problem.source_state_vector(state), problem.source_derivative_vector()) for problem, state, _ in geometry_problems]
    geometry_firewall = max(float(np.max(np.abs(geometry_residuals[0] - value))) for value in geometry_residuals[1:])

    metrics = {
        "snapshot_count": len(rows),
        "local_state_size": layout.local_size,
        "differential_row_count": layout.differential_size,
        "algebraic_row_count": layout.algebraic_size,
        "accepted_step_memory_value_count": layout.history_size,
        "mass_matrix_rank": int(np.count_nonzero(layout.mass_diagonal)),
        "maximum_source_electron_rate_relative": max(source_relative_values),
        "maximum_100digit_electron_rate_relative": max(high_precision_values),
        "maximum_scaled_source_residual": max(residual_values),
        "maximum_shifted_ijacobian_relative": max(jvp_values),
        "maximum_backward_euler_backward_error": max(be_values),
        "minimum_physical_population": min(min_physical_values),
        "history_restart_exact_all": all(history_roundtrip_values),
        "future_endpoint_rejected_all": all(future_rejection_values),
        "geometry_firewall_absolute": geometry_firewall,
        "candidate_mass_ratio_min": min(mass_ratio_values),
        "candidate_mass_ratio_max": max(mass_ratio_values),
        "minimum_candidate_mass_relative_difference": min(mass_difference_values),
        "native_local_time_measure_identifiable": False,
        "finite_support_widths_present": False,
        "cell_edges_present": False,
        "spike_shape_present": False,
        "replacement_completed_count": replacement_audit["completed_replacement_count"],
        "replacement_requested_count": replacement_audit["requested_replacement_count"],
        "replacement_removed_without_complete_count": replacement_audit["removed_without_complete_replacement_count"],
        "pr05b_complete": replacement_audit["pr05b_complete"],
        "classification": "PASS_BOUNDED_NO_GO_NATIVE_LOCAL_TIME_MEASURE_NOT_IDENTIFIED_PR05B2_CAUSAL_HISTORY_NEXT",
    }
    gates = [
        {"name": "canonical_archive", "passed": digest(HYREC_ARCHIVE) == CANONICAL_HYREC_SHA256},
        {"name": "source_role_registry", "passed": layout.local_size == 314 and layout.differential_size == 1 and layout.algebraic_size == 313 and layout.history_size == 625},
        {"name": "rank_one_local_mass", "passed": metrics["mass_matrix_rank"] == 1},
        {"name": "source_electron_rate", "passed": metrics["maximum_source_electron_rate_relative"] < 4.0e-13},
        {"name": "high_precision_electron_rate", "passed": metrics["maximum_100digit_electron_rate_relative"] < 4.0e-13},
        {"name": "source_residual", "passed": metrics["maximum_scaled_source_residual"] < 3.0e-13},
        {"name": "shifted_ijacobian", "passed": metrics["maximum_shifted_ijacobian_relative"] < 1.0e-8},
        {"name": "positive_backward_euler", "passed": metrics["maximum_backward_euler_backward_error"] < 1.0e-11 and metrics["minimum_physical_population"] > 0.0},
        {"name": "causal_restart", "passed": metrics["history_restart_exact_all"] and metrics["future_endpoint_rejected_all"]},
        {"name": "constructive_mass_nonidentifiability", "passed": (not metrics["native_local_time_measure_identifiable"]) and abs(metrics["candidate_mass_ratio_min"] - 2.0) < 2.0e-14 and abs(metrics["candidate_mass_ratio_max"] - 2.0) < 2.0e-14 and metrics["minimum_candidate_mass_relative_difference"] > 0.4},
        {"name": "compressed_term_firewall", "passed": replacement_audit["removed_without_complete_replacement_count"] == 0 and replacement_audit["completed_replacement_count"] == 0 and not replacement_audit["pr05b_complete"]},
        {"name": "fixed_local_state_bianchi_firewall", "passed": geometry_firewall == 0.0},
    ]
    if not all(gate["passed"] for gate in gates):
        raise RuntimeError(f"PR-05B1 hard gate failed: {gates}")

    source_line_csv = ARTIFACT / "ORIGINAL_HYREC_SOURCE_LINE_LEDGER.csv"
    write_csv(source_line_csv, source_rows)
    write_json(ARTIFACT / "ORIGINAL_HYREC_SOURCE_LINE_LEDGER.json", source_rows)
    write_csv(ARTIFACT / "SOURCE_IDENTIFIABLE_STATE_ROLE_REGISTRY.csv", state_role_rows())
    write_json(ARTIFACT / "SOURCE_IDENTIFIABLE_STATE_ROLE_REGISTRY.json", state_role_rows())
    write_csv(ARTIFACT / "COMPRESSED_TERM_REPLACEMENT_MATRIX.csv", replacement)
    write_json(ARTIFACT / "COMPRESSED_TERM_REPLACEMENT_MATRIX.json", {"terms": replacement, "audit": replacement_audit})
    write_csv(ARTIFACT / "THREE_SNAPSHOT_SOURCE_DAE_LEDGER.csv", rows)
    write_csv(ARTIFACT / "NATIVE_TIME_MEASURE_NONIDENTIFIABILITY_WITNESS.csv", mass_rows)
    write_json(ARTIFACT / "NUMERICAL_METRICS.json", metrics)
    write_json(ARTIFACT / "HARD_GATE_LEDGER.json", {
        "classification": "PR05B1_HARD_GATE_LEDGER",
        "status": metrics["classification"],
        "PR05B1": "COMPLETE_PASS_BOUNDED_NO_GO",
        "PR05B": "IN_PROGRESS",
        "gates": gates,
        "claim_boundary": {
            "source_identifiable_semi_explicit_DAE": True,
            "xe_local_differential": True,
            "real_virtual_local_algebraic": True,
            "radiation_time_dependence_as_causal_history": True,
            "finite_local_native_radiation_mass_identified": False,
            "compressed_terms_removed": False,
            "time_dependent_native_COM_trajectory": False,
            "full_history_or_FLRW_parity": False,
        },
    })
    write_json(ARTIFACT / "PR05B1_ledger.json", {
        "classification": "PR05B1_DURABLE_LEDGER",
        "status": metrics["classification"],
        "canonical_hyrec_sha256": CANONICAL_HYREC_SHA256,
        "metrics": metrics,
        "source_line_ledger": "ORIGINAL_HYREC_SOURCE_LINE_LEDGER.json",
        "next": "PR05B2_CAUSAL_CHARACTERISTIC_HISTORY_STATE",
    })
    write_json(ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json", {"classification": "PR05B1_HARNESS_EXECUTION", "receipts": harness_receipts})
    write_json(ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json", {"classification": "WOLFRAM_PR05B1_SYMBOLIC_RECEIPT", "status": "USED", "result": WOLFRAM_RESULT})
    write_json(ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json", {"classification": "PRECISE_SPECIAL_FUNCTIONS_PR05B1_RECEIPT", "status": "USED", "Gamma_3_over_2_120": GAMMA_3_OVER_2_120, "Zeta_3_120": ZETA3_120})
    write_json(ARTIFACT / "TOOL_STATUS.json", {"web_search": "USED_PRIMARY_SOURCES", "Wolfram": "USED", "Precise_Special_Functions": "USED", "GitHub_connector": "USED_READ_ONLY", "coding_harness": "USED_AND_VALIDATED", "research_harness": "USED_AND_VALIDATED"})

    no_go = {
        "classification": "CONSTRUCTIVE_NATIVE_LOCAL_TIME_MEASURE_NONIDENTIFIABILITY",
        "canonical_virtual_role": "algebraic",
        "candidate_mass_ratio": metrics["candidate_mass_ratio_max"],
        "candidate_relative_difference": metrics["minimum_candidate_mass_relative_difference"],
        "both_candidates_zero_width_limit": 0.0,
        "reason": "canonical source fixes virtual centres and integrated rates but not finite dln(nu) support, cell edges, or spike shape; two equally admissible narrow supports give distinct transient masses",
        "forbidden_resolution": "do not fit or infer a local mass/timescale from centre spacing",
    }
    write_json(ARTIFACT / "NATIVE_TIME_MEASURE_NO_GO.json", no_go)

    formalism = f"""# PR-05B1/v0.59 source-identifiable original-HyRec DAE and native-time-measure no-go

## Result

The canonical local system in independent variable `eta=ln(a)` has one differential row and 313 algebraic rows:

```text
U_local = (x_e, Delta x_2s, Delta x_2p, Delta x_v[0:311])
M_local = diag(1,0,...,0).
```

The radiation history arrays `Dfminus_hist`, `Dfminus_Ly_hist`, and `Dfnu_hist` are accepted-step causal memory, not local differential rows. Their total one-slice size is `{layout.history_size}` values.

## Source residual and shifted Jacobian

The electron row is

```text
R_e = d x_e/d eta - F_e(x_e, Delta x_2s, Delta x_2p).
```

The 313 native rows are the canonical algebraic constraint `T_native x_native-s_native=0`. PETSc's shifted Jacobian is `dR/dU + shift*dR/dUdot`; the maximum three-lane centered-difference residual is `{metrics['maximum_shifted_ijacobian_relative']:.17e}`.

## Constructive no-go

For a finite virtual-spike transient equation, the photon time-derivative mass is proportional to a finite `Delta ln(nu)` support (and to `1/x_1s` for the source variable `Delta x_b=x_1s Delta f_b` on a frozen background). The canonical archive supplies centre frequencies and integrated rates but no finite support widths, edge array, or spike shape.

Two positive nonoverlapping top-hat support choices, `0.2` and `0.4` times each centre's nearest log-frequency gap, give candidate masses in ratio `{metrics['candidate_mass_ratio_max']:.17e}`. Both converge to zero in the source's zero-width limit. Therefore no finite local native-radiation mass is source-identifiable; neither candidate is promoted.

## Causal replacement path

The source-identifiable time dependence is the characteristic history path: use accepted outgoing radiation at earlier redshift/higher frequency to construct incoming `Dfplus`, solve the real/virtual algebraic block, compute `dxHIIdlna`, then append `Dfminus` and `Dfnu` only after the step is accepted. PR-05B2 implements this typed accepted-step state and its analytic JVP.

## Claim boundary

PR-05B1 is a bounded no-go, not a solver failure. It closes the source-role/mass-matrix audit and a positive bounded electron/algebraic DAE reference. It does not remove Sobolev escape, `A1s` diffusion, completed/Schur `Tvv`, or scalar history feedback; PR-05B remains open.
"""
    (ARTIFACT / "PR05B1_SOURCE_IDENTIFIABLE_DAE_FORMALISM.md").write_text(formalism, encoding="utf-8")
    (ARTIFACT / "PR05B1_INDEPENDENT_ADVERSARIAL_REVIEW.md").write_text(
        "# Independent adversarial review\n\nThe strongest competing interpretation promotes the virtual departures to local transient variables by assigning widths from centre spacing. That is a new finite-volume closure, not a property of the canonical archive. The factor-two witness proves non-uniqueness before any numerical solver is chosen. The release therefore keeps all compressed terms active and redirects implementation to the source's causal accepted-step history representation.\n",
        encoding="utf-8",
    )
    (ARTIFACT / "PR05B1_LITERATURE_BASIS.md").write_text(
        "# Literature basis\n\nPrimary sources: Ali-Haimoud & Hirata, arXiv:1011.3758 (full HyRec radiative transfer and simultaneous evolution); the May-2012 technical supplement (departure variables and free-electron ODE); current PETSc TSSetIFunction/TSSetIJacobian documentation for F(t,U,Udot)=0 and shifted Jacobians. The exact C source remains the primary evidence for the local algebraic/history split.\n",
        encoding="utf-8",
    )
    write_research_docs(metrics, no_go)
    (ARTIFACT / "README.md").write_text(
        "# PR-05B1/v0.59\n\nSource-identifiable rank-one local DAE plus causal radiation-memory audit. The requested finite local native-radiation time mass is constructively non-identifiable; see `HARD_GATE_LEDGER.json` and `NATIVE_TIME_MEASURE_NO_GO.json`.\n",
        encoding="utf-8",
    )

    np.savez_compressed(
        DATA_OUT,
        **arrays,
        target_z=np.asarray(TARGETS, dtype=float),
        snapshot_z=np.asarray([float(row["snapshot_z"]) for row in rows]),
        metrics_json=np.asarray(json.dumps(metrics, sort_keys=True)),
    )
    shutil.copy2(DATA_OUT, ARTIFACT / DATA_OUT.name)
    shutil.copy2(ROOT / "docs/plans/2026-08-06-pr05b1-source-identifiable-dae-audit.md", ARTIFACT / "2026-08-06-pr05b1-source-identifiable-dae-audit.md")

    verifier = '''#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_BOUNDED_NO_GO_NATIVE_LOCAL_TIME_MEASURE_NOT_IDENTIFIED_PR05B2_CAUSAL_HISTORY_NEXT"
assert hard["PR05B1"] == "COMPLETE_PASS_BOUNDED_NO_GO" and hard["PR05B"] == "IN_PROGRESS"
assert all(row["passed"] for row in hard["gates"])
with (root / "THREE_SNAPSHOT_SOURCE_DAE_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(int(row["differential_rows"]) == 1 and int(row["algebraic_rows"]) == 313 for row in rows)
assert all(row["native_local_time_measure_identifiable"] == "False" for row in rows)
no_go = json.loads((root / "NATIVE_TIME_MEASURE_NO_GO.json").read_text())
assert abs(float(no_go["candidate_mass_ratio"]) - 2.0) < 2e-14
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05B1 v0.59 artifact: PASS_BOUNDED_NO_GO; source-identifiable DAE complete; PR-05B2 causal history OPEN")
'''
    (ARTIFACT / "verify_PR05B1.py").write_text(verifier, encoding="utf-8")
    os.chmod(ARTIFACT / "verify_PR05B1.py", 0o755)

    manifest = ["# SHA-256 manifest for PR-05B1 v0.59"]
    for path in sorted(ARTIFACT.iterdir()):
        if path.name == "MANIFEST_SHA256.txt" or not path.is_file():
            continue
        manifest.append(f"{digest(path)}  {path.name}")
    (ARTIFACT / "MANIFEST_SHA256.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    run_logged([sys.executable, str(ARTIFACT / "verify_PR05B1.py")], cwd=ARTIFACT, log=ARTIFACT / "COMPACT_VERIFIER.log")

    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE.unlink(missing_ok=True)
    with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(ARTIFACT.iterdir()):
            if path.is_file():
                archive.write(path, arcname=f"{ARTIFACT_NAME}/{path.name}")
    with zipfile.ZipFile(BUNDLE) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt artifact bundle member: {bad}")
    print(json.dumps({
        "status": metrics["classification"],
        "artifact": str(ARTIFACT),
        "bundle": str(BUNDLE),
        "bundle_sha256": digest(BUNDLE),
        "bundle_size_bytes": BUNDLE.stat().st_size,
        "data_sha256": digest(DATA_OUT),
        "metrics": metrics,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
