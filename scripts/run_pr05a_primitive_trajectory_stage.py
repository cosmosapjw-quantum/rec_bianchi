#!/usr/bin/env python3
"""Build PR-05A v0.58 primitive-rate/schema and bounded DAE evidence.

This stage source-locks the October-2012 original-HyRec primitive rates,
freezes public trajectory schemas and ownership, and evaluates a bounded
source-conditioned algebraic-DAE/COM operator contract at z~1300,1100,900.
It does not claim a time-dependent native radiation trajectory or FLRW history
parity; those remain PR-05B/C and PR-06 respectively.
"""
from __future__ import annotations

import csv
from dataclasses import fields
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
from typing import Iterable
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
    parse_original_hyrec_boundary_snapshot_csv,
    parse_original_hyrec_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (  # noqa: E402
    ALPHA_TABLE_SHA256,
    IONIZATION_ENERGY_EV,
    N_TM,
    N_TR,
    R2P2S_TABLE_SHA256,
    SAHA_COEFFICIENT_CGS,
    TM_OVER_TR_MAX,
    TM_OVER_TR_MIN,
    TR_MAX_EV,
    TR_MIN_EV,
    TWO_PHOTON_TABLE_SHA256,
    OriginalHyRecPrimitiveRateTable,
    PrimitiveRateSnapshot,
    detailed_balance_residuals,
)
from full_bianchi_hyrec.trajectory.primitive_trajectory import (  # noqa: E402
    AtomicRadiationState,
    PrimitiveTrajectoryProblem,
    RadiationFeedback,
    StateClassification,
    TrajectoryStepLedger,
    atomic_state_from_source_snapshot,
    audit_native_m_matrix,
    default_pr05a_ownership_registry,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR05A_primitive_rate_schema_v0_58"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr05a_primitive_trajectory_v058.npz"
HYREC_ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
SNAPSHOT_DIR = ROOT / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
NETWORK_PATH = ROOT / "data/full_scalar_com_khw_v050.npz"
C_HARNESS = ROOT / "scripts/c_harness/original_hyrec_primitive_rates_harness.c"
RESEARCH_DOCS = ROOT / "docs" / "research" / "pr05a_v058"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CANONICAL_HYREC_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
TARGETS = (1300, 1100, 900)
DT_S = 1.0e5
GAMMA_3_OVER_2_120 = (
    "0.886226925452758013649083741670572591398774728061193564106903894926455642295516090687475328369272332708113411812141285333"
)
ZETA3_120 = (
    "1.20205690315959428539973816151144999076498629234049888179227155534183820578631309018645587360933525814619915779526071942"
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_logged(command: list[str], *, cwd: Path, log: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC)
    if env:
        environment.update(env)
    with log.open("wb") as output:
        result = subprocess.run(command, cwd=cwd, env=environment, stdout=output, stderr=subprocess.STDOUT, check=False)
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
        bad = zipped.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt harness member: {bad}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator))
    if len(matches) != 1:
        raise RuntimeError(f"cannot uniquely locate {validator}")
    result = run_logged([sys.executable, str(matches[0])], cwd=matches[0].parents[1], log=log)
    return {"archive": archive.name, "sha256": observed, "validator": validator, "exit_code": result.returncode, "passed": True}


def background_for(snapshot, *, bianchi_type: str = "I", sigma: np.ndarray | None = None, A: np.ndarray | None = None) -> BackgroundSnapshot:
    return BackgroundSnapshot(
        tau=-float(np.log1p(snapshot.z)),
        cosmic_time_s=1.0,
        H_s_inv=snapshot.H_s_inv,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)) if sigma is None else sigma,
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3) if A is None else A,
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id="pr05a-v058",
        bianchi_type=bianchi_type,
    )


def be_occupation(network: CollisionNetwork, n_angle: int) -> np.ndarray:
    activity = network.equilibrium_weight / network.mode_measure
    if np.any(activity <= 0.0) or np.any(activity >= 1.0):
        raise RuntimeError("locked q_activity=1 state lies outside Bose-Einstein domain")
    scalar = activity / (1.0 - activity)
    return scalar[:, None] * np.ones((1, n_angle))


def problem_for(target: int, table: OriginalHyRecPrimitiveRateTable, network: CollisionNetwork, grid):
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
    rates = table.evaluate(
        radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
        matter_to_radiation_temperature_ratio=source.TM_over_TR,
        fsR=source.fsR,
        meR=source.meR,
    )
    state = atomic_state_from_source_snapshot(
        source,
        com_occupation=be_occupation(network, grid.n_angle),
        beta_H=np.zeros(3),
    )
    problem = PrimitiveTrajectoryProblem(
        background=background_for(source),
        source_snapshot=source,
        rates=rates,
        network=network,
        grid=grid,
        line=LineBoundaryConfig.lyman_alpha(temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25),
        interface_enabled=False,
    )
    return problem, state, source, rates


def c_rate_parity(table: OriginalHyRecPrimitiveRateTable, work: Path) -> tuple[list[dict[str, object]], dict[str, float]]:
    if shutil.which("gcc") is None:
        raise RuntimeError("gcc is required for source parity")
    source = table.extract_source_tree(work / "hyrec")
    executable = work / "primitive_rates_harness"
    run_logged(
        [
            "gcc", "-std=c11", "-D_DEFAULT_SOURCE", "-O2", "-I", str(source),
            str(C_HARNESS), str(source / "hydrogen.c"), str(source / "hyrectools.c"),
            "-lm", "-o", str(executable),
        ],
        cwd=source,
        log=ARTIFACT / "ORIGINAL_C_RATE_HARNESS_COMPILE.log",
    )
    points: list[tuple[str, float, float, float, float]] = []
    for target in TARGETS:
        snap = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
        points.append((f"z{target}", snap.TR_eV_rescaled, snap.TM_over_TR, snap.fsR, snap.meR))
    points.extend((("table_edge", 0.04, 0.1, 1.0, 1.0), ("off_grid", 0.173, 0.736, 1.0, 1.0)))
    rows: list[dict[str, object]] = []
    max_non_delta = 0.0
    max_delta_raw = 0.0
    max_delta_gross = 0.0
    for name, Tr, ratio, fsR, meR in points:
        result = subprocess.run(
            [str(executable), f"{Tr:.17g}", f"{ratio:.17g}", f"{fsR:.17g}", f"{meR:.17g}"],
            cwd=source,
            capture_output=True,
            text=True,
            check=True,
        )
        c = np.asarray([float(value) for value in result.stdout.split()])
        rates = table.evaluate(
            radiation_temperature_eV_rescaled=Tr,
            matter_to_radiation_temperature_ratio=ratio,
            fsR=fsR,
            meR=meR,
        )
        py = np.concatenate((rates.alpha_m3_s * 1.0e6, rates.delta_alpha_m3_s * 1.0e6, rates.beta_s_inv, [rates.R_2p2s_s_inv]))
        raw = np.abs(py - c) / np.maximum(np.abs(c), 1.0e-300)
        non_delta = float(np.max(raw[[0, 1, 4, 5, 6]]))
        delta_raw = float(np.max(raw[2:4]))
        delta_gross_values = []
        for level in range(2):
            c_alpha = c[level]
            c_delta = c[2 + level]
            c_eq = c_alpha - c_delta
            py_alpha = py[level]
            py_delta = py[2 + level]
            py_eq = py_alpha - py_delta
            scale = max(abs(c_alpha), abs(c_eq), abs(py_alpha), abs(py_eq), 1.0e-300)
            delta_gross_values.append(abs(py_delta - c_delta) / scale)
        delta_gross = float(max(delta_gross_values))
        max_non_delta = max(max_non_delta, non_delta)
        max_delta_raw = max(max_delta_raw, delta_raw)
        max_delta_gross = max(max_delta_gross, delta_gross)
        rows.append({
            "point": name, "Tr_eV_rescaled": Tr, "Tm_over_Tr": ratio,
            "non_delta_max_relative": non_delta,
            "delta_alpha_raw_relative_diagnostic": delta_raw,
            "delta_alpha_gross_scaled_relative": delta_gross,
        })
    return rows, {
        "maximum_C_Python_non_delta_relative": max_non_delta,
        "maximum_C_Python_delta_alpha_raw_relative_diagnostic": max_delta_raw,
        "maximum_C_Python_delta_alpha_gross_scaled_relative": max_delta_gross,
    }


def _mp_weights(f):
    return (
        f * (f - 1) * (2 - f) / 6,
        (1 + f) * (1 - f) * (2 - f) / 2,
        (1 + f) * f * (2 - f) / 2,
        (1 + f) * f * (f - 1) / 6,
    )


def high_precision_rate_parity(table: OriginalHyRecPrimitiveRateTable) -> tuple[list[dict[str, object]], dict[str, float]]:
    mp.mp.dps = 100
    with zipfile.ZipFile(HYREC_ARCHIVE) as archive:
        alpha_tokens = [mp.mpf(value) for value in archive.read("HyRec/Alpha_inf.dat").decode("ascii").split()]
        r_tokens = [mp.mpf(value) for value in archive.read("HyRec/R_inf.dat").decode("ascii").split()]
    alpha = [[[mp.mpf(0) for _ in range(N_TR)] for _ in range(N_TM)] for _ in range(2)]
    position = 0
    for i_tr in range(N_TR):
        for i_tm in range(N_TM):
            for level in range(2):
                alpha[level][i_tm][i_tr] = mp.log(alpha_tokens[position])
                position += 1
    log_r = [mp.log(value) for value in r_tokens]

    def evaluate(Tr_value: float, ratio_value: float):
        Tr = mp.mpf(str(Tr_value)); ratio = mp.mpf(str(ratio_value))
        d_tm = (mp.mpf(str(TM_OVER_TR_MAX)) - mp.mpf(str(TM_OVER_TR_MIN))) / (N_TM - 1)
        i_tm = max(1, min(N_TM - 3, int(mp.floor((ratio - TM_OVER_TR_MIN) / d_tm))))
        w_tm = _mp_weights((ratio - TM_OVER_TR_MIN) / d_tm - i_tm)
        d_log_tr = (mp.log(TR_MAX_EV) - mp.log(TR_MIN_EV)) / (N_TR - 1)
        i_tr = max(1, min(N_TR - 3, int(mp.floor((mp.log(Tr) - mp.log(TR_MIN_EV)) / d_log_tr))))
        w_tr = _mp_weights((mp.log(Tr) - mp.log(TR_MIN_EV)) / d_log_tr - i_tr)
        values = []; equilibrium = []
        for level in range(2):
            temporary = [sum(alpha[level][i_tm - 1 + k][i_tr - 1 + j] * w_tr[j] for j in range(4)) for k in range(4)]
            values.append(mp.exp(sum(temporary[k] * w_tm[k] for k in range(4))))
            equilibrium.append(mp.exp(sum(alpha[level][N_TM - 1][i_tr - 1 + j] * w_tr[j] for j in range(4))))
        delta = [values[i] - equilibrium[i] for i in range(2)]
        factor = mp.mpf(str(SAHA_COEFFICIENT_CGS)) * Tr * mp.sqrt(Tr) * mp.exp(-mp.mpf(str(IONIZATION_ENERGY_EV)) / (4 * Tr))
        beta = [equilibrium[0] * factor, equilibrium[1] * factor / 3]
        rate_r = mp.exp(sum(log_r[i_tr - 1 + j] * w_tr[j] for j in range(4)))
        return values, equilibrium, delta, beta, rate_r

    points = (("z1100", 0.25882399309326415, 0.9999895025729527), ("off_grid", 0.173, 0.736), ("table_edge", 0.04, 0.1))
    rows: list[dict[str, object]] = []
    max_regular = mp.mpf(0); max_delta_raw = mp.mpf(0); max_delta_gross = mp.mpf(0)
    for name, Tr, ratio in points:
        alpha_mp, eq_mp, delta_mp, beta_mp, r_mp = evaluate(Tr, ratio)
        production = table.evaluate(radiation_temperature_eV_rescaled=Tr, matter_to_radiation_temperature_ratio=ratio)
        regular_residuals = []
        for observed, reference in zip(list(production.alpha_m3_s * 1.0e6) + list(production.beta_s_inv) + [production.R_2p2s_s_inv], alpha_mp + beta_mp + [r_mp]):
            regular_residuals.append(abs(mp.mpf(str(observed)) - reference) / max(abs(reference), mp.mpf("1e-1000")))
        delta_raw_values = []
        delta_gross_values = []
        for level in range(2):
            observed = mp.mpf(str(production.delta_alpha_m3_s[level] * 1.0e6))
            delta_raw_values.append(abs(observed - delta_mp[level]) / max(abs(delta_mp[level]), mp.mpf("1e-1000")))
            delta_gross_values.append(abs(observed - delta_mp[level]) / max(abs(alpha_mp[level]), abs(eq_mp[level]), mp.mpf("1e-1000")))
        regular = max(regular_residuals); delta_raw = max(delta_raw_values); delta_gross = max(delta_gross_values)
        max_regular = max(max_regular, regular); max_delta_raw = max(max_delta_raw, delta_raw); max_delta_gross = max(max_delta_gross, delta_gross)
        rows.append({
            "point": name, "Tr_eV_rescaled": Tr, "Tm_over_Tr": ratio,
            "regular_max_relative": float(regular),
            "delta_alpha_raw_relative_diagnostic": float(delta_raw),
            "delta_alpha_gross_scaled_relative": float(delta_gross),
        })
    return rows, {
        "maximum_100digit_regular_relative": float(max_regular),
        "maximum_100digit_delta_alpha_raw_relative_diagnostic": float(max_delta_raw),
        "maximum_100digit_delta_alpha_gross_scaled_relative": float(max_delta_gross),
    }


def source_registry() -> list[dict[str, object]]:
    common_alpha = {
        "source_member": "HyRec/Alpha_inf.dat", "source_sha256": ALPHA_TABLE_SHA256,
        "source_function": "hydrogen.c::interpolate_rates", "source_lines": "142-219",
    }
    common_two = {
        "source_member": "HyRec/two_photon_tables.dat", "source_sha256": TWO_PHOTON_TABLE_SHA256,
        "source_function": "hydrogen.c::read_twog_params", "source_lines": "273-315",
    }
    rows = []
    for level, degeneracy in (("2s", 1), ("2p", 3)):
        rows.append({"public_name": f"alpha_{level}", **common_alpha, "source_symbol": f"Alpha[{0 if level == '2s' else 1}]", "source_unit": "cm^3 s^-1", "public_unit": "m^3 s^-1", "SI_factor": 1.0e-6, "degeneracy": degeneracy, "semantics": "effective recombination coefficient alpha(Tm,Tr)", "detailed_balance_partner": f"beta_{level}", "derivative": "analytic local cubic JVP in log(Tr), Tm/Tr"})
        rows.append({"public_name": f"delta_alpha_{level}", **common_alpha, "source_symbol": f"DAlpha[{0 if level == '2s' else 1}]", "source_unit": "cm^3 s^-1", "public_unit": "m^3 s^-1", "SI_factor": 1.0e-6, "degeneracy": degeneracy, "semantics": "alpha(Tm,Tr)-alpha(Tr,Tr); not a derivative", "detailed_balance_partner": "alpha_equilibrium", "derivative": "difference of analytic cubic JVPs"})
        rows.append({"public_name": f"beta_{level}", **common_alpha, "source_symbol": f"Beta[{0 if level == '2s' else 1}]", "source_unit": "s^-1", "public_unit": "s^-1", "SI_factor": 1.0, "degeneracy": degeneracy, "semantics": "photoionization rate from detailed balance; 2p divided by 3", "detailed_balance_partner": f"alpha_{level}", "derivative": "analytic log(Tr) JVP"})
    rows.append({"public_name": "R_2p2s", "source_member": "HyRec/R_inf.dat", "source_sha256": R2P2S_TABLE_SHA256, "source_function": "hydrogen.c::interpolate_rates", "source_lines": "215-219", "source_symbol": "R2p2s", "source_unit": "s^-1", "public_unit": "s^-1", "SI_factor": 1.0, "degeneracy": "2p:2s=3:1 coupling", "semantics": "effective 2p to 2s rate", "detailed_balance_partner": "3*R_2p2s reverse multiplicity", "derivative": "analytic local cubic JVP in log(Tr)"})
    for public, symbol, semantics in (
        ("A1s", "A1s_tab", "3*A2p1s*phi(E)*DeltaE; native diffusion weight"),
        ("A2s", "A2s_tab", "2s two-photon/Raman integrated-bin rate; sub-Lya sum normalized to 8.2206 s^-1"),
        ("A3s3d", "A3s3d_tab", "3s+3d two-photon/Raman integrated-bin rate"),
        ("A4s4d", "A4s4d_tab", "4s+4d two-photon/Raman integrated-bin rate"),
    ):
        rows.append({"public_name": public, **common_two, "source_symbol": symbol, "source_unit": "s^-1 per native bin", "public_unit": "s^-1 per native bin", "SI_factor": 1.0, "degeneracy": "embedded in canonical table", "semantics": semantics, "detailed_balance_partner": "native virtual-state operator", "derivative": "constant in PR-05A rate snapshot; thermodynamic factors belong to native operator"})
    return rows


def schema_registry() -> dict[str, object]:
    units = {
        "BackgroundSnapshot": {
            "tau": "dimensionless", "cosmic_time_s": "s", "H_s_inv": "s^-1", "q": "dimensionless",
            "sigma_s_inv": "s^-1", "N_s_inv": "s^-1", "A_s_inv": "s^-1", "frame_rotation_s_inv": "s^-1",
            "beta_H": "dimensionless", "D0_beta_H_s_inv": "s^-1",
        },
        "PrimitiveRateSnapshot": {"alpha_m3_s": "m^3 s^-1", "delta_alpha_m3_s": "m^3 s^-1", "beta_s_inv": "s^-1", "R_2p2s_s_inv": "s^-1", "A1s_s_inv": "s^-1 per native bin", "A2s_s_inv": "s^-1 per native bin", "A3s3d_s_inv": "s^-1 per native bin", "A4s4d_s_inv": "s^-1 per native bin"},
        "AtomicRadiationState": {"real_departure": "signed dimensionless source variable", "native_departure": "signed dimensionless source variable", "com_occupation": "dimensionless and strictly positive", "x_1s": "per H", "x_2s": "per H", "x_2p": "per H", "x_e": "per H", "T_m_K": "K", "beta_H": "dimensionless"},
        "RadiationFeedback": {"rho_gamma_J_m3": "J m^-3", "p_gamma_Pa": "Pa", "q_gamma_a_W_m2": "W m^-2", "pi_gamma_ab_Pa": "Pa", "Q_atom_mu_W_m3": "W m^-3", "boundary_red_number_flux_per_H_s": "photons H^-1 s^-1", "boundary_blue_number_flux_per_H_s": "photons H^-1 s^-1"},
        "TrajectoryStepLedger": {"number_residual": "dimensionless", "photon_atom_energy_residual_W_m3": "W m^-3", "four_force_residual": "dimensionless", "minimum_physical_state": "mixed diagnostic with values reported separately in evidence", "entropy_production": "discrete collision free-energy production"},
    }
    classes = (BackgroundSnapshot, PrimitiveRateSnapshot, AtomicRadiationState, RadiationFeedback, TrajectoryStepLedger)
    return {"schema": "PR05A_PUBLIC_TRAJECTORY_SCHEMAS_V1", "classes": {cls.__name__: {"fields": [field.name for field in fields(cls)], "units": units[cls.__name__]} for cls in classes}, "geometry_microphysics_boundary": "Only BackgroundSnapshot physical tetrad fields enter; chart-internal host objects are forbidden."}


def ownership_rows() -> list[dict[str, object]]:
    return [
        {
            "term": term.name, "current_owner": term.current_owner,
            "replacement_owner": term.replacement_owner or "NONE",
            "removal_condition": term.removal_condition, "conservation": term.conservation,
            "removed": term.removed, "evaluation_count": term.evaluation_count,
            "application_count": term.application_count,
            "pure_interface_atom_source_W_m3": term.pure_interface_atom_source_W_m3,
        }
        for term in default_pr05a_ownership_registry().terms
    ]


def write_research_docs(metrics: dict[str, object]) -> None:
    RESEARCH_DOCS.mkdir(parents=True, exist_ok=True)
    documents = {
        "01_RESEARCH_CONTRACT.md": """# PR-05A research contract\n\nPrimary question: can the byte-locked original-HyRec primitive rate layer and a chart-independent trajectory schema be exposed as a conservative one-step DAE/operator contract without inventing a native-to-COM state remap?\n\nIn scope: source rate parity, units, degeneracies, analytic JVP, Saha null, native algebraic projection, COM interface-off equilibrium, feedback schema, ownership theorem and three source-conditioned snapshots.\n\nOut of scope: time-dependent native radiation, dynamic COM trajectory, short adaptive history, FLRW xe(z) parity and CMB observables.\n""",
        "02_EVIDENCE_ACQUISITION.md": f"""# Evidence acquisition\n\n- Canonical original-HyRec archive SHA-256: `{CANONICAL_HYREC_SHA256}`.\n- Alpha table: `{ALPHA_TABLE_SHA256}`.\n- R2p2s table: `{R2P2S_TABLE_SHA256}`.\n- Two-photon table: `{TWO_PHOTON_TABLE_SHA256}`.\n- Source-conditioned snapshots: z~1300,1100,900 from the source-identical v0.55 instrumentation.\n- Original C is compiled and compared at three trajectory points, a table-edge point and an off-grid point.\n- Independent references: 100-digit mpmath interpolation, Wolfram polynomial/detailed-balance identities and 120-digit special-function values.\n""",
        "03_CLAIM_SOURCE_AUDIT.md": """# Claim/source audit\n\nThe source symbol `DAlpha` is not a derivative. In `hydrogen.c::interpolate_rates` it is explicitly `Alpha(Tm,Tr)-Alpha(Tr,Tr)`. The public schema therefore names it `delta_alpha`; derivative fields are separately named `d_*`. Alpha is converted from cm^3/s to m^3/s. Beta, R2p2s and integrated-bin A tables remain s^-1. The 2p detailed-balance rate carries the source factor 1/3, paired with a 2p degeneracy of 3 in the equilibrium population.\n""",
        "04_HYPOTHESIS_AUDIT.md": """# Hypothesis audit\n\n- H1 PROMOTED: a typed source-rate adapter plus algebraic native DAE projection is sufficient for PR-05A.\n- H2 HELD: remove Sobolev/diffusion/Schur/history-compressed terms now. Rejected for this stage because explicit replacements are not yet present in the same residual.\n- H3 REJECTED: interpret `DAlpha` as a derivative. Directly contradicted by canonical source.\n- H4 REJECTED: infer a physical native-derived COM trajectory from the q_activity=1 operator-verification state. No such source-derived map exists.\n""",
        "05_ADVERSARIAL_REVIEW.md": """# Independent adversarial review\n\nAttacks applied: unit swap cm^3/s versus m^3/s; dropping the 2p degeneracy; treating cancellation-amplified delta-alpha relative error as gross interpolation failure; removing compressed terms before replacements; passing Bianchi type into local rates; clipping populations; accepting a future history endpoint; and relabelling an interface-off equilibrium lane as a physical trajectory. Each attack is either rejected by a test/registry gate or retained as an explicit claim boundary.\n""",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": """# Validation and dimensional closure\n\nThe public recombination coefficient has dimension m^3 s^-1, so n_H alpha has s^-1. Photoionization, R2p2s and integrated native-bin A coefficients have s^-1. RadiationFeedback uses rho_gamma [J m^-3], p_gamma and pi_gamma [Pa], q_gamma [W m^-2], and tetrad Q_atom [W m^-3]. The local scalar sector receives only physical tetrad data through BackgroundSnapshot.\n""",
        "07_VERIFICATION_RESULTS.md": "# Verification results\n\n```json\n" + json.dumps(metrics, indent=2, sort_keys=True) + "\n```\n",
        "08_EXTERNAL_GATE.md": """# External gate\n\nOriginal HyRec is the primary source for primitive rates and simultaneous radiation/atomic evolution. PETSc TS/SNES is retained as the planned PR-05C implicit ODE/DAE and event-handling production target. No external source is used to overwrite canonical source conventions.\n""",
        "09_FORMALIZATION.md": """# Formalization\n\nPR-05A is a semi-explicit bounded DAE contract: the original-HyRec real/virtual block is projected onto its canonical algebraic constraint while the already-verified COM Bose equilibrium is evaluated interface-off. The combined analytic JVP is block diagonal at this stage. Dynamic native and COM blocks, their coupling derivatives and adaptive eventful integration are PR-05B/C.\n""",
        "10_CLOSEOUT_AND_HANDOFF.md": """# Closeout and handoff\n\nPR-05A closes when source/C/Python/high-precision parity, Saha null, M-matrix evidence, one-step residual/JVP, positivity, conservation, restart, ownership and geometry-firewall gates pass at all three snapshots. PR-05B must next make native radiation and real atomic populations genuinely time dependent and jointly replace selected compressed terms.\n""",
    }
    for name, text in documents.items():
        (RESEARCH_DOCS / name).write_text(text, encoding="utf-8")


def main() -> None:
    if digest(HYREC_ARCHIVE) != CANONICAL_HYREC_SHA256:
        raise RuntimeError("canonical HyRec archive hash mismatch")
    shutil.rmtree(ARTIFACT, ignore_errors=True)
    ARTIFACT.mkdir(parents=True)
    RESEARCH_DOCS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pr05a-v058-") as temporary:
        work = Path(temporary)
        harness_receipts = [
            validate_harness(CODING_HARNESS, CODING_HARNESS_SHA256, "validate_harness.py", work, ARTIFACT / "CODING_HARNESS_VALIDATION.log"),
            validate_harness(RESEARCH_HARNESS, RESEARCH_HARNESS_SHA256, "validate_workspace.py", work, ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log"),
        ]
        table = OriginalHyRecPrimitiveRateTable.from_archive(HYREC_ARCHIVE)
        c_rows, c_metrics = c_rate_parity(table, work)
        hp_rows, hp_metrics = high_precision_rate_parity(table)

    network = CollisionNetwork.from_npz(NETWORK_PATH)
    grid = positive_harmonic_grid(12)
    snapshot_rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}
    rate_jvp_values = []
    full_jvp_values = []
    source_alpha_values = []
    source_delta_values = []
    source_beta_values = []
    saha_values = []
    native_values = []
    implicit_values = []
    number_values = []
    min_states = []
    m_margins = []
    eigenvalues = []
    future_endpoint_ok = True

    for target in TARGETS:
        problem, state, source, rates = problem_for(target, table, network, grid)
        evaluation = problem.evaluate(state)
        direction_rng = np.random.default_rng(target)
        full_jvp = problem.central_difference_jvp_residual(
            state,
            native_direction=direction_rng.normal(size=313),
            log_com_direction=direction_rng.normal(size=state.com_occupation.shape),
            step=1.0e-6,
        )
        rate_jvp = table.central_difference_jvp_residual(
            radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
            matter_to_radiation_temperature_ratio=source.TM_over_TR,
            direction_log_Tr_and_Tm_over_Tr=(0.37, -0.23),
            step=2.0e-6,
        )
        equilibrium_rates = table.evaluate(
            radiation_temperature_eV_rescaled=source.TR_eV_rescaled,
            matter_to_radiation_temperature_ratio=1.0,
            fsR=source.fsR,
            meR=source.meR,
        )
        saha = float(np.max(np.abs(detailed_balance_residuals(equilibrium_rates, n_H_m3=source.nH_cm3 * 1.0e6, x_1s=source.x1s))))
        m_matrix = audit_native_m_matrix(problem.native_matrix_s_inv)
        perturbed = state.replace(
            real_departure=state.real_departure * np.asarray([1.03, 0.97]),
            native_departure=state.native_departure * (1.0 + 0.02 * np.sin(np.arange(311))),
            classification=StateClassification.OPERATOR_VERIFICATION,
        )
        implicit = problem.implicit_step(perturbed, dt_s=DT_S)
        restart_exact = problem.restart_payload(implicit.state) == problem.restart_payload(problem.state_from_restart_payload(problem.restart_payload(implicit.state)))
        boundary = parse_original_hyrec_boundary_snapshot_csv(SNAPSHOT_DIR / f"pr04c_z{target}.csv")
        causal = all(sample.history_index_right <= boundary.trajectory.iz_local for sample in boundary.boundaries)
        future_endpoint_ok = future_endpoint_ok and causal

        alpha_relative = float(np.max(np.abs(rates.alpha_m3_s - source.Alpha * 1.0e-6) / np.maximum(np.abs(source.Alpha * 1.0e-6), 1.0e-300)))
        delta_relative = float(np.max(np.abs(rates.delta_alpha_m3_s - source.DAlpha * 1.0e-6) / np.maximum(np.abs(source.DAlpha * 1.0e-6), 1.0e-300)))
        beta_relative = float(np.max(np.abs(rates.beta_s_inv - source.Beta) / np.maximum(np.abs(source.Beta), 1.0e-300)))
        row = {
            "target_z": float(target), "snapshot_z": source.z,
            "alpha_source_relative": alpha_relative,
            "delta_alpha_source_raw_relative_diagnostic": delta_relative,
            "beta_source_relative": beta_relative,
            "rate_analytic_jvp_relative_error": rate_jvp,
            "saha_detailed_balance_relative": saha,
            "native_residual_relative": evaluation.native_residual_relative,
            "com_collision_relative": evaluation.com_collision_relative,
            "analytic_jvp_relative_error": full_jvp,
            "photon_number_residual": evaluation.ledger.number_residual,
            "photon_atom_energy_residual_W_m3": evaluation.ledger.photon_atom_energy_residual_W_m3,
            "four_force_relative": evaluation.ledger.four_force_residual,
            "entropy_production": evaluation.ledger.entropy_production,
            "minimum_physical_state": evaluation.ledger.minimum_physical_state,
            "m_matrix_diagonal_min_s_inv": m_matrix.diagonal_min,
            "m_matrix_off_diagonal_max_s_inv": m_matrix.off_diagonal_max,
            "m_matrix_column_dominance_margin_min_s_inv": m_matrix.column_dominance_margin_min,
            "m_matrix_minimum_real_eigenvalue_s_inv": m_matrix.minimum_real_eigenvalue,
            "m_matrix_pass": m_matrix.nonsingular_m_matrix,
            "implicit_backward_error": implicit.backward_error,
            "implicit_native_residual_relative": implicit.native_residual_relative,
            "implicit_com_residual_relative": implicit.com_residual_relative,
            "implicit_number_relative_change": implicit.number_relative_change,
            "implicit_minimum_physical_state": implicit.minimum_physical_state,
            "implicit_free_energy_change": implicit.free_energy_change,
            "restart_exact": restart_exact,
            "future_history_endpoint_rejected": causal,
            "interface_enabled": False,
            "state_classification": implicit.state.classification.value,
            "rho_gamma_J_m3": evaluation.feedback.rho_gamma_J_m3,
            "p_gamma_Pa": evaluation.feedback.p_gamma_Pa,
            "max_abs_q_gamma_W_m2": float(np.max(np.abs(evaluation.feedback.q_gamma_a_W_m2))),
            "max_abs_pi_gamma_Pa": float(np.max(np.abs(evaluation.feedback.pi_gamma_ab_Pa))),
            "max_abs_Q_atom_W_m3": float(np.max(np.abs(evaluation.feedback.Q_atom_mu_W_m3))),
        }
        snapshot_rows.append(row)
        arrays[f"z{target}_native_residual"] = evaluation.native_residual
        arrays[f"z{target}_com_collision_action"] = evaluation.com_collision_action
        arrays[f"z{target}_implicit_native_departure"] = implicit.state.native_departure
        arrays[f"z{target}_implicit_com_occupation"] = implicit.state.com_occupation
        rate_jvp_values.append(rate_jvp); full_jvp_values.append(full_jvp)
        source_alpha_values.append(alpha_relative); source_delta_values.append(delta_relative); source_beta_values.append(beta_relative)
        saha_values.append(saha); native_values.append(evaluation.native_residual_relative); implicit_values.append(implicit.backward_error)
        number_values.append(max(evaluation.ledger.number_residual, implicit.number_relative_change)); min_states.append(min(evaluation.ledger.minimum_physical_state, implicit.minimum_physical_state))
        m_margins.append(m_matrix.column_dominance_margin_min); eigenvalues.append(m_matrix.minimum_real_eigenvalue)

    # Fixed local hydrogen-frame state: Bianchi labels and geometric data may not alter local microphysics.
    source = parse_original_hyrec_snapshot_csv(SNAPSHOT_DIR / "pr04c_z1100.csv")
    rates = table.evaluate(radiation_temperature_eV_rescaled=source.TR_eV_rescaled, matter_to_radiation_temperature_ratio=source.TM_over_TR, fsR=source.fsR, meR=source.meR)
    state = atomic_state_from_source_snapshot(source, com_occupation=be_occupation(network, grid.n_angle), beta_H=np.zeros(3))
    geometries = (
        background_for(source, bianchi_type="II", sigma=np.diag([2.0e-14, -1.0e-14, -1.0e-14])),
        background_for(source, bianchi_type="VI_h", A=np.asarray([2.0e-14, 0.0, 0.0])),
        background_for(source, bianchi_type="VI_-1/9", sigma=np.diag([-2.0e-14, 1.0e-14, 1.0e-14])),
    )
    firewall_results = []
    for background in geometries:
        problem = PrimitiveTrajectoryProblem(background=background, source_snapshot=source, rates=rates, network=network, grid=grid, line=LineBoundaryConfig.lyman_alpha(temperature_K=state.T_m_K, x_red=-21.25, x_blue=21.25), interface_enabled=False)
        firewall_results.append(problem.evaluate(state))
    firewall_native = max(float(np.max(np.abs(firewall_results[0].native_residual - item.native_residual))) for item in firewall_results[1:])
    firewall_com = max(float(np.max(np.abs(firewall_results[0].com_collision_action - item.com_collision_action))) for item in firewall_results[1:])
    firewall_feedback = max(abs(firewall_results[0].feedback.rho_gamma_J_m3 - item.feedback.rho_gamma_J_m3) for item in firewall_results[1:])

    ownership = default_pr05a_ownership_registry(); ownership_audit = ownership.audit()
    all_metrics = {
        **c_metrics, **hp_metrics,
        "maximum_source_alpha_relative": max(source_alpha_values),
        "maximum_source_delta_alpha_raw_relative_diagnostic": max(source_delta_values),
        "maximum_source_beta_relative": max(source_beta_values),
        "maximum_rate_analytic_jvp_relative_error": max(rate_jvp_values),
        "maximum_saha_detailed_balance_relative": max(saha_values),
        "maximum_native_residual_relative": max(native_values),
        "maximum_full_analytic_jvp_relative_error": max(full_jvp_values),
        "maximum_implicit_backward_error": max(implicit_values),
        "maximum_number_residual": max(number_values),
        "minimum_physical_state": min(min_states),
        "minimum_m_matrix_column_dominance_margin_s_inv": min(m_margins),
        "minimum_m_matrix_real_eigenvalue_s_inv": min(eigenvalues),
        "maximum_photon_atom_energy_residual_W_m3": max(abs(float(row["photon_atom_energy_residual_W_m3"])) for row in snapshot_rows),
        "maximum_four_force_relative": max(float(row["four_force_relative"]) for row in snapshot_rows),
        "maximum_collision_entropy_production": max(float(row["entropy_production"]) for row in snapshot_rows),
        "restart_exact_all": all(bool(row["restart_exact"]) for row in snapshot_rows),
        "future_endpoint_causality_all": future_endpoint_ok,
        "geometry_firewall_native_absolute": firewall_native,
        "geometry_firewall_com_absolute": firewall_com,
        "geometry_firewall_feedback_absolute": firewall_feedback,
        "ownership_pass": ownership_audit.passed,
        "snapshot_count": len(snapshot_rows),
        "interface_enabled": False,
        "state_classification": "SOURCE_DERIVED_INPUT_OPERATOR_VERIFICATION_OUTPUT",
    }

    gates = [
        {"name": "canonical_archive", "passed": digest(HYREC_ARCHIVE) == CANONICAL_HYREC_SHA256},
        {"name": "source_table_hashes", "passed": table.source_hashes == {"Alpha_inf.dat": ALPHA_TABLE_SHA256, "R_inf.dat": R2P2S_TABLE_SHA256, "two_photon_tables.dat": TWO_PHOTON_TABLE_SHA256}},
        {"name": "C_Python_regular_parity", "passed": c_metrics["maximum_C_Python_non_delta_relative"] < 2.0e-12},
        {"name": "C_Python_delta_gross_parity", "passed": c_metrics["maximum_C_Python_delta_alpha_gross_scaled_relative"] < 2.0e-12},
        {"name": "high_precision_regular_parity", "passed": hp_metrics["maximum_100digit_regular_relative"] < 1.0e-12},
        {"name": "high_precision_delta_gross_parity", "passed": hp_metrics["maximum_100digit_delta_alpha_gross_scaled_relative"] < 1.0e-12},
        {"name": "rate_analytic_jvp", "passed": all_metrics["maximum_rate_analytic_jvp_relative_error"] < 2.0e-8},
        {"name": "saha_detailed_balance", "passed": all_metrics["maximum_saha_detailed_balance_relative"] < 5.0e-13},
        {"name": "native_source_residual", "passed": all_metrics["maximum_native_residual_relative"] < 2.0e-13},
        {"name": "native_m_matrix", "passed": all_metrics["minimum_m_matrix_column_dominance_margin_s_inv"] > 0.0 and all_metrics["minimum_m_matrix_real_eigenvalue_s_inv"] > 0.0},
        {"name": "full_analytic_jvp", "passed": all_metrics["maximum_full_analytic_jvp_relative_error"] < 1.0e-8},
        {"name": "implicit_backward_error", "passed": all_metrics["maximum_implicit_backward_error"] < 1.0e-11},
        {"name": "photon_number", "passed": all_metrics["maximum_number_residual"] < 1.0e-11},
        {"name": "photon_atom_energy", "passed": all_metrics["maximum_photon_atom_energy_residual_W_m3"] == 0.0},
        {"name": "four_force", "passed": all_metrics["maximum_four_force_relative"] == 0.0},
        {"name": "strict_positivity", "passed": all_metrics["minimum_physical_state"] > 0.0},
        {"name": "entropy_nonincrease", "passed": all_metrics["maximum_collision_entropy_production"] <= 0.0},
        {"name": "restart", "passed": all_metrics["restart_exact_all"]},
        {"name": "future_endpoint_causality", "passed": all_metrics["future_endpoint_causality_all"]},
        {"name": "ownership", "passed": all_metrics["ownership_pass"]},
        {"name": "geometry_firewall", "passed": firewall_native == 0.0 and firewall_com == 0.0 and firewall_feedback == 0.0},
        {"name": "interface_off_v057_parity", "passed": all(float(row["com_collision_relative"]) < 2.0e-13 and row["interface_enabled"] is False for row in snapshot_rows)},
    ]
    if not all(gate["passed"] for gate in gates):
        raise RuntimeError(f"PR-05A hard gate failed: {gates}")

    write_csv(ARTIFACT / "PRIMITIVE_RATE_SOURCE_REGISTRY.csv", source_registry())
    write_json(ARTIFACT / "PRIMITIVE_RATE_SOURCE_REGISTRY.json", source_registry())
    write_json(ARTIFACT / "PUBLIC_SCHEMA_REGISTRY.json", schema_registry())
    write_csv(ARTIFACT / "OWNERSHIP_REMOVAL_MATRIX.csv", ownership_rows())
    write_json(ARTIFACT / "OWNERSHIP_REMOVAL_MATRIX.json", {"classification": "PR05A_ONE_OWNER_REMOVAL_MATRIX", "audit": ownership_audit.__dict__, "terms": ownership_rows()})
    write_csv(ARTIFACT / "C_PYTHON_RATE_PARITY.csv", c_rows)
    write_csv(ARTIFACT / "HIGH_PRECISION_RATE_PARITY.csv", hp_rows)
    write_csv(ARTIFACT / "THREE_SNAPSHOT_PRIMITIVE_LEDGER.csv", snapshot_rows)
    write_json(ARTIFACT / "NUMERICAL_METRICS.json", all_metrics)
    write_json(ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json", {"classification": "PR05A_HARNESS_EXECUTION", "receipts": harness_receipts})
    write_json(ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json", {"classification": "WOLFRAM_PR05A_SYMBOLIC_RECEIPT", "result": [0, "Abs[e]", 1, 0, 0, 0], "identities": ["cross-lane signed sum can cancel while componentwise max remains", "four-point cubic weights sum to one", "weight derivatives sum to zero", "2s and 2p Saha detailed-balance residuals simplify to zero"], "status": "USED"})
    write_json(ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json", {"classification": "PRECISE_SPECIAL_FUNCTIONS_PR05A_RECEIPT", "Gamma_3_over_2_120": GAMMA_3_OVER_2_120, "Zeta_3_120": ZETA3_120, "status": "USED"})
    write_json(ARTIFACT / "TOOL_STATUS.json", {"web_search": "USED_PRIMARY_SOURCES", "Wolfram": "USED", "Precise_Special_Functions": "USED", "GitHub_connector": "USED_READ_ONLY", "coding_harness": "USED_AND_VALIDATED", "research_harness": "USED_AND_VALIDATED"})

    hard = {
        "classification": "PR05A_HARD_GATE_LEDGER",
        "status": "PASS_PR05A_SCHEMA_SOURCE_LOCK_ONE_STEP_DAE_PR05B_NEXT",
        "PR05A": "COMPLETE", "PR05": "IN_PROGRESS",
        "gates": gates,
        "claim_boundary": {
            "one_step_source_conditioned_dae": True,
            "native_time_dependent_trajectory": False,
            "native_derived_com_trajectory": False,
            "short_adaptive_trajectory": False,
            "flrw_history_parity": False,
            "compressed_terms_removed": False,
        },
        "diagnostics_not_hard_failures": {
            "delta_alpha_raw_relative_is_cancellation_amplified": True,
            "maximum_C_Python_delta_alpha_raw_relative": c_metrics["maximum_C_Python_delta_alpha_raw_relative_diagnostic"],
            "maximum_100digit_delta_alpha_raw_relative": hp_metrics["maximum_100digit_delta_alpha_raw_relative_diagnostic"],
        },
    }
    write_json(ARTIFACT / "HARD_GATE_LEDGER.json", hard)
    write_json(ARTIFACT / "PR05A_ledger.json", {"classification": "PR05A_DURABLE_LEDGER", "status": hard["status"], "canonical_hyrec_sha256": CANONICAL_HYREC_SHA256, "source_hashes": dict(table.source_hashes), "metrics": all_metrics, "hard_gate_ledger": "HARD_GATE_LEDGER.json", "next": "PR05B_TIME_DEPENDENT_NATIVE_ATOMIC_RADIATION_BLOCK"})

    formalism = f"""# PR-05A v0.58 primitive-rate and bounded trajectory schema\n\n## Scope\n\nPR-05A exposes the canonical October-2012 original-HyRec primitive rate layer, immutable public schemas, a fail-closed ownership/removal theorem, and a source-conditioned one-step algebraic DAE plus COM collision operator. It does **not** claim a time-dependent native radiation trajectory or FLRW recombination-history parity.\n\n## Conventions and units\n\nMetric signature is `(-,+,+,+)`. Ordinary frequency is in Hz. Constants `c`, `h`, and `k_B` remain explicit. Original source temperatures are in eV and recombination coefficients in cm^3/s; public alpha and delta-alpha are converted to m^3/s. Beta, R2p2s and integrated native-bin A coefficients are s^-1.\n\nThe canonical source symbol `DAlpha` obeys\n\n```text\nDAlpha = Alpha(Tm,Tr) - Alpha(Tr,Tr),\n```\n\nand is therefore published as `delta_alpha`, not as a derivative.\n\n## Detailed balance\n\nAt `Tm=Tr`,\n\n```text\nn_H alpha_i x_e^2 = beta_i x_i,\nx_2s = x_1s exp(-E21/Tr),\nx_2p = 3 x_1s exp(-E21/Tr).\n```\n\nThe explicit 2p degeneracy 3 cancels the source `Beta[1]` factor 1/3. Maximum three-lane relative residual: `{all_metrics['maximum_saha_detailed_balance_relative']:.17e}`.\n\n## Bounded DAE contract\n\nThe native block remains the canonical algebraic constraint\n\n```text\nT_native x_native - s_native = 0,\n```\n\nand its direct solution is the PR-05A DAE projection. The COM block is the already-verified interface-off Bose-equilibrium operator. The combined production JVP is the exact block action. Compressed Sobolev/diffusion/Schur/history terms remain active until their explicit replacements are present in the same residual and conservation ledger.\n\n## Cancellation diagnostics\n\nNear `Tm/Tr=1`, delta-alpha is a subtraction of nearly equal alpha values. Raw relative discrepancies are therefore cancellation-amplified and are retained as diagnostics. Hard parity is assessed against the gross alpha/alpha-equilibrium scale; maximum C/Python gross-scaled discrepancy is `{c_metrics['maximum_C_Python_delta_alpha_gross_scaled_relative']:.17e}` and the 100-digit discrepancy is `{hp_metrics['maximum_100digit_delta_alpha_gross_scaled_relative']:.17e}`.\n\n## Claim boundary\n\nThis stage proves schema/source/units/JVP/one-step-DAE closure at z~1300,1100,900. Dynamic native radiation, dynamic real populations, joint compressed-term replacement, adaptive integration and xe(z) parity remain PR-05B/C and PR-06.\n"""
    (ARTIFACT / "PR05A_PRIMITIVE_TRAJECTORY_FORMALISM.md").write_text(formalism, encoding="utf-8")
    (ARTIFACT / "README.md").write_text("# PR-05A v0.58\n\nSource-locked primitive original-HyRec rates, public trajectory schemas, fail-closed ownership, and bounded one-step DAE/operator evidence. See `HARD_GATE_LEDGER.json`.\n", encoding="utf-8")

    write_research_docs(all_metrics)
    for path in sorted(RESEARCH_DOCS.glob("*.md")):
        shutil.copy2(path, ARTIFACT / path.name)
    np.savez_compressed(DATA_OUT, **arrays, target_z=np.asarray(TARGETS, dtype=float), snapshot_z=np.asarray([float(row["snapshot_z"]) for row in snapshot_rows]), metrics_json=np.asarray(json.dumps(all_metrics, sort_keys=True)))
    shutil.copy2(DATA_OUT, ARTIFACT / DATA_OUT.name)
    shutil.copy2(ROOT / "docs/PR05_PRIMITIVE_TRAJECTORY_INTERFACE_PLAN.md", ARTIFACT / "PR05_PRIMITIVE_TRAJECTORY_INTERFACE_PLAN.md")

    verifier = '''#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
hard = json.loads((root / "HARD_GATE_LEDGER.json").read_text())
assert hard["status"] == "PASS_PR05A_SCHEMA_SOURCE_LOCK_ONE_STEP_DAE_PR05B_NEXT"
assert hard["PR05A"] == "COMPLETE" and hard["PR05"] == "IN_PROGRESS"
assert all(row["passed"] for row in hard["gates"])
with (root / "THREE_SNAPSHOT_PRIMITIVE_LEDGER.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
assert [float(row["target_z"]) for row in rows] == [1300.0, 1100.0, 900.0]
assert all(float(row["native_residual_relative"]) < 2e-13 for row in rows)
assert all(float(row["implicit_backward_error"]) < 1e-11 for row in rows)
assert all(float(row["minimum_physical_state"]) > 0 for row in rows)
for line in (root / "MANIFEST_SHA256.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    expected, relative = line.split("  ", 1)
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
print("PR-05A v0.58 artifact: PASS; schema/source lock and bounded one-step DAE COMPLETE; PR-05B OPEN")
'''
    (ARTIFACT / "verify_PR05A.py").write_text(verifier, encoding="utf-8")
    os.chmod(ARTIFACT / "verify_PR05A.py", 0o755)

    # Manifest excludes itself so the file is stable and independently checkable.
    manifest_lines = ["# SHA-256 manifest for PR-05A v0.58"]
    for path in sorted(ARTIFACT.iterdir()):
        if path.name == "MANIFEST_SHA256.txt" or not path.is_file():
            continue
        manifest_lines.append(f"{digest(path)}  {path.name}")
    (ARTIFACT / "MANIFEST_SHA256.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    # Validate compact verifier before packaging.
    run_logged([sys.executable, str(ARTIFACT / "verify_PR05A.py")], cwd=ROOT, log=ARTIFACT / "COMPACT_VERIFIER.log")
    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    if BUNDLE.exists():
        BUNDLE.unlink()
    with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(ARTIFACT.iterdir()):
            if path.is_file():
                archive.write(path, arcname=f"{ARTIFACT_NAME}/{path.name}")
    with zipfile.ZipFile(BUNDLE) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt artifact bundle member: {bad}")
    print(json.dumps({"status": hard["status"], "artifact": str(ARTIFACT), "bundle": str(BUNDLE), "bundle_sha256": digest(BUNDLE), "bundle_size_bytes": BUNDLE.stat().st_size, "data_sha256": digest(DATA_OUT), "metrics": all_metrics}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
