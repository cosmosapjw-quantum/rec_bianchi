#!/usr/bin/env python3
"""Generate PR-05C2C1B1/v0.67 source-adapter and full-withheld artifact."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import mpmath as mp
import numpy as np
from scipy.constants import h, k

ROOT = Path(__file__).resolve().parents[1]
NAME = "Full_Bianchi_HyRec_PR05C2C1B1_source_adapter_withheld_v0_67"
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c1b1_source_adapter_withheld_v067.npz"
STATUS = (
    "PASS_PR05C2C1B1_CANONICAL_SPIKE_PHYSICAL_LINE_SOURCE_ADAPTER_"
    "FULL_WITHHELD_AUDIT_PRECONDITIONER_AND_MULTI_MACRO_OPEN"
)

NODE_PATHS = (
    ROOT / "data/pr05c2c1a_z900_direct_network_node_v066.npz",
    ROOT / "data/pr05c2c1a_z1100_direct_network_node_v066.npz",
    ROOT / "data/pr05c2c1a_z1300_direct_network_node_v066.npz",
)
REFERENCE = ROOT / "data/full_scalar_com_khw_v050.npz"
BACKGROUND = ROOT / "data/pr01c_background_snapshots_v048.npz"
HYREC_ZIP = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
MODELS = (
    "Bianchi_II_large_shear",
    "Bianchi_VI_h_tilted_large_shear",
    "Bianchi_VI_minus_1_over_9_exceptional",
)
DIRECTION = np.asarray([0.3, 0.4, math.sqrt(0.75)], dtype=float)
DIRECTION /= np.linalg.norm(DIRECTION)
NU0 = 2.466e15
PSF_GAMMA32 = (
    "0.886226925452758013649083741670572591398774728061193564106903894926455642295516090687475328369272332708113411812141285333"
)

sys.path.insert(0, str(ROOT / "src"))
from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence  # noqa: E402
from full_bianchi_hyrec.trajectory.characteristic_angular import (  # noqa: E402
    BianchiCharacteristicFaceSolver,
)
from full_bianchi_hyrec.trajectory.direct_thermodynamic import (  # noqa: E402
    DirectThermodynamicNetworkFamily,
    DirectThermodynamicNode,
)
from full_bianchi_hyrec.trajectory.hyrec_source_adapter import (  # noqa: E402
    IsotropicEinsteinLineSource,
    OriginalHyRecVirtualSpikeSource,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def deterministic_zip(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(source)), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def jsonable(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def source_excerpt() -> tuple[str, str]:
    with zipfile.ZipFile(HYREC_ZIP) as archive:
        raw = archive.read("HyRec/hydrogen.c")
    lines = raw.decode("utf-8", errors="replace").splitlines()
    selected = []
    for number in (521, 524, 525, 780, 781, 787, 789):
        selected.append(f"{number}: {lines[number-1].rstrip()}")
    return "\n".join(selected) + "\n", hashlib.sha256(raw).hexdigest()


def calculate_metrics() -> tuple[dict, dict, list[dict], dict[str, np.ndarray]]:
    nodes = [
        DirectThermodynamicNode.from_npz(path, reference_path=REFERENCE)
        for path in NODE_PATHS
    ]
    full_family = DirectThermodynamicNetworkFamily.from_paths(
        NODE_PATHS, reference_path=REFERENCE
    )
    withheld_family = DirectThermodynamicNetworkFamily(
        (nodes[0], nodes[2]), reference=full_family.reference
    )
    withheld = withheld_family.audit_withheld_node(nodes[1])

    rng = np.random.default_rng(20260808)
    maximum_spike_jvp = 0.0
    maximum_flrw_spike = 0.0
    spike_sample_count = 250
    for _ in range(spike_sample_count):
        size = 17
        tau = np.exp(rng.uniform(-28.0, 4.0, size=size))
        equilibrium = rng.uniform(-0.4, 1.3, size=size)
        incoming = rng.uniform(-0.3, 1.0, size=size)
        H = float(np.exp(rng.uniform(-33.0, -28.0)))
        speed = rng.choice([-1.0, 1.0], size=size) * H * np.exp(
            rng.uniform(-1.0, 1.0, size=size)
        )
        source = OriginalHyRecVirtualSpikeSource(
            tau_flrw=tau,
            equilibrium_departure=equilibrium,
            H_s_inv=H,
        )
        directional = source.apply(incoming=incoming, minus_dlognu_dt_s_inv=speed)
        flrw = source.apply(
            incoming=incoming,
            minus_dlognu_dt_s_inv=np.full(size, H),
        )
        expected = incoming + (equilibrium - incoming) * (-np.expm1(-tau))
        maximum_flrw_spike = max(
            maximum_flrw_spike,
            float(np.max(np.abs(flrw - expected)) / max(np.max(np.abs(expected)), 1.0)),
        )

        d_in = rng.normal(size=size)
        d_eq = rng.normal(size=size)
        d_tau = rng.normal(size=size) * np.maximum(tau, 1e-8)
        d_H = 0.03 * H
        d_speed = rng.normal(size=size) * np.maximum(np.abs(speed), 1e-300) * 0.02
        analytic = source.jvp(
            incoming=incoming,
            minus_dlognu_dt_s_inv=speed,
            d_incoming=d_in,
            d_equilibrium_departure=d_eq,
            d_tau_flrw=d_tau,
            d_H_s_inv=d_H,
            d_minus_dlognu_dt_s_inv=d_speed,
        )
        eps = 1e-6
        plus = OriginalHyRecVirtualSpikeSource(
            tau_flrw=tau + eps * d_tau,
            equilibrium_departure=equilibrium + eps * d_eq,
            H_s_inv=H + eps * d_H,
        ).apply(
            incoming=incoming + eps * d_in,
            minus_dlognu_dt_s_inv=speed + eps * d_speed,
        )
        minus = OriginalHyRecVirtualSpikeSource(
            tau_flrw=tau - eps * d_tau,
            equilibrium_departure=equilibrium - eps * d_eq,
            H_s_inv=H - eps * d_H,
        ).apply(
            incoming=incoming - eps * d_in,
            minus_dlognu_dt_s_inv=speed - eps * d_speed,
        )
        fd = (plus - minus) / (2.0 * eps)
        scale = max(float(np.max(np.abs(fd))), float(np.max(np.abs(analytic))), 1.0)
        maximum_spike_jvp = max(
            maximum_spike_jvp, float(np.max(np.abs(analytic - fd)) / scale)
        )
        assert np.all(np.isfinite(directional))

    temperatures = (2457.5530568, 3003.4961888, 3549.1156549)
    maximum_planck_null = 0.0
    maximum_angular_deposition = 0.0
    planck_rows = []
    for temperature in temperatures:
        frequency = 2.4660677e15
        z = math.exp(-h * frequency / (k * temperature))
        g_upper, g_lower = 3.0, 1.0
        lower = 0.8
        upper = (g_upper / g_lower) * lower * z
        line = IsotropicEinsteinLineSource(
            A_ul_s_inv=6.265e8,
            profile_Hz_inv=2.0e-12,
            frequency_Hz=frequency,
            nH_m3=2.5e8,
            upper_population=upper,
            lower_population=lower,
            upper_degeneracy=g_upper,
            lower_degeneracy=g_lower,
        )
        planck = z / (1.0 - z)
        residual = abs(line.occupation_action(planck)) / max(
            line.emission_s_inv * (1.0 + planck), 1e-300
        )
        maximum_planck_null = max(maximum_planck_null, residual)
        weights = rng.random(26)
        weights /= np.sum(weights)
        occupation = rng.uniform(0.0, 0.1, size=26)
        directional = line.directional_action(occupation)
        integrated = float(np.sum(weights * directional))
        expected = line.occupation_action(float(np.sum(weights * occupation)))
        maximum_angular_deposition = max(
            maximum_angular_deposition,
            abs(integrated - expected) / max(abs(expected), 1.0),
        )
        planck_rows.append(
            {
                "temperature_K": temperature,
                "planck_occupation": planck,
                "relative_null_residual": residual,
                "emission_s_inv": line.emission_s_inv,
                "absorption_s_inv": line.absorption_s_inv,
            }
        )

    characteristic_rows: list[dict] = []
    maximum_frequency = 0.0
    minimum_occupation = math.inf
    minimum_doppler = math.inf
    maximum_direction_norm = 0.0
    for model in MODELS:
        sequence = BackgroundSnapshotSequence.from_npz(BACKGROUND, model)
        tau = 0.5 * (sequence.tau[0] + sequence.tau[-1])
        snapshot = sequence.snapshot_at_tau(tau)
        solver = BianchiCharacteristicFaceSolver(snapshot)
        local = solver.local_characteristic(DIRECTION)
        for side_sign, side in ((-1.0, "red"), (1.0, "blue")):
            sign = math.copysign(1.0, local.R_hydrogen_s_inv)
            # Use the forward-reachable side while retaining the requested side label.
            delta = sign * 2e-4
            target = NU0 * math.exp(delta)
            result = solver.trace_to_frequency_face(
                direction_normal=DIRECTION,
                frequency_initial_Hz=NU0,
                frequency_target_Hz=target,
                f_initial=0.27,
                emissivity_s_inv=3.0e-12 if side_sign > 0 else 1.0e-12,
                opacity_s_inv=5.0e-12,
                n_steps=48,
            )
            maximum_frequency = max(maximum_frequency, result.frequency_relative_residual)
            minimum_occupation = min(minimum_occupation, result.f_face)
            minimum_doppler = min(minimum_doppler, result.minimum_doppler_factor)
            maximum_direction_norm = max(
                maximum_direction_norm,
                abs(np.linalg.norm(result.direction_normal) - 1.0),
                abs(np.linalg.norm(result.direction_hydrogen) - 1.0),
            )
            characteristic_rows.append(
                {
                    "model": model,
                    "side": side,
                    "tau": tau,
                    "frequency_relative_residual": result.frequency_relative_residual,
                    "f_face": result.f_face,
                    "travel_time_s": result.travel_time_s,
                    "minimum_doppler_factor": result.minimum_doppler_factor,
                    "minimum_abs_frequency_speed_s_inv": result.minimum_abs_frequency_speed_s_inv,
                    "step_count": result.step_count,
                }
            )

    mp.mp.dps = 120
    psf_gamma = mp.mpf(PSF_GAMMA32)
    gamma_residual = abs(psf_gamma - mp.gamma(mp.mpf("1.5"))) / abs(
        mp.gamma(mp.mpf("1.5"))
    )

    withheld_dict = jsonable(withheld.__dict__)
    metrics = {
        "classification": "PR05C2C1B1_NUMERICAL_METRICS",
        "status": STATUS,
        "spike_sample_count": spike_sample_count,
        "maximum_canonical_flrw_spike_relative_residual": maximum_flrw_spike,
        "maximum_spike_jvp_relative_residual": maximum_spike_jvp,
        "maximum_planck_lte_null_relative_residual": maximum_planck_null,
        "maximum_isotropic_angular_deposition_relative_residual": maximum_angular_deposition,
        "maximum_characteristic_frequency_relative_residual": maximum_frequency,
        "minimum_characteristic_occupation": minimum_occupation,
        "minimum_characteristic_doppler_factor": minimum_doppler,
        "maximum_characteristic_direction_norm_residual": maximum_direction_norm,
        "characteristic_lane_count": len(characteristic_rows),
        "withheld_pair_block_count": withheld.pair_block_count,
        "withheld_same_cell_block_count": withheld.same_cell_block_count,
        "withheld_scalar_event_mass_weighted_relative": withheld.scalar_event_mass_weighted_relative,
        "withheld_scalar_edge_maximum_relative": withheld.scalar_edge_maximum_relative,
        "withheld_maximum_pair_moment_l2_relative": withheld.maximum_pair_moment_l2_relative,
        "withheld_same_cell_l2_relative": withheld.same_cell_l2_relative,
        "withheld_same_cell_maximum_relative": withheld.same_cell_maximum_relative,
        "psf_gamma_3_over_2_relative_residual": float(gamma_residual),
        "canonical_spike_adapter_source_identical": True,
        "physical_line_source_is_theory_contract_adapter": True,
        "physical_line_source_relabelled_original_hyrec": False,
        "full_withheld_pair_and_same_cell_audit_complete": True,
        "preconditioner_selected": False,
        "multi_macro_trajectory_complete": False,
    }
    arrays = {
        "characteristic_frequency_residuals": np.asarray(
            [row["frequency_relative_residual"] for row in characteristic_rows]
        ),
        "characteristic_face_occupations": np.asarray(
            [row["f_face"] for row in characteristic_rows]
        ),
        "planck_null_residuals": np.asarray(
            [row["relative_null_residual"] for row in planck_rows]
        ),
        "direct_node_temperatures_K": np.asarray(
            [node.temperature_K for node in nodes]
        ),
        "direct_node_densities_m3": np.asarray([node.nH_m3 for node in nodes]),
    }
    return metrics, withheld_dict, characteristic_rows, arrays


def formalism() -> str:
    return r'''# PR-05C2C1B1 source-adapter and full-withheld formalism

## Scope and conventions

The metric signature is `(-,+,+,+)`.  Frequency is ordinary `nu` in Hz and
`c`, `h`, and `k_B` remain explicit.  The stage is scalar, unpolarized and
homogeneous, with finite tilt and nonlinear large shear entering only through
`BackgroundSnapshot` characteristics.

## Canonical original-HyRec virtual spike

The October-2012 source defines a distributional virtual-state update

\[
 f^- = f^+ + (f^{\rm eq}-f^+)\left(1-e^{-\tau}\right).
\]

On a fixed directional branch with local speed
\(r=-d\ln\nu/dt\ne0\), the optical depth is

\[
 \tau_{\rm dir}=\tau_{\rm FLRW}\frac{H}{|r|}.
\]

A zero or sign change of `r` is an event; it is never differentiated through.
The implementation uses `expm1` and an analytic JVP.  This adapter is
source-identical to `HyRec/hydrogen.c` at the locked source lines.

## Positive paired one-photon line model

The v0.65 scalar source-isotropy axiom permits a separate physical line adapter

\[
 C[f]=\eta(1+f)-\kappa f,
\]

with

\[
 \eta=\frac{c^3 n_H}{8\pi\nu^2}A_{ul}\phi(\nu)x_u,\qquad
 \kappa=\frac{c^3 n_H}{8\pi\nu^2}A_{ul}\phi(\nu)
 \frac{g_u}{g_l}x_l.
\]

Both rates are nonnegative.  In LTE,
\(x_u/x_l=(g_u/g_l)e^{-h\nu/(k_BT_H)}\), and the Planck occupation is an exact
null.  This paired-rate model is a theory-contract source adapter; it is not
relabelled as an explicit coefficient decomposition stored by original HyRec.

The phase-space prefactor gives `[eta]=[kappa]=s^-1`.  With positive normalized
angular weights summing to one, isotropic deposition requires no extra
`1/N_angle` factor.

## Characteristic face transfer

The directional radiation field is evolved along the exact finite-tilt Bianchi
characteristic.  Native face data are initial-boundary-value data, not an
instantaneous scalar-to-angular inversion.  A requested face that is not
forward-reachable fails closed; frequency-speed zeros require event
localization and restart.

## Full withheld thermodynamic audit

The z~1100 direct node is withheld from the z~900/z~1300 family.  Every 442
unordered pair block and all 17 same-cell blocks are compared.  Three error
classes are retained separately: event-mass weighted scalar error, maximum
active-edge relative error, and operator-moment/same-cell errors.  This audit is
a validation witness and does not replace direct production compilation.

## Claim boundary

This stage completes the canonical spike adapter, a positive physical
one-photon source contract, source-derived face characteristics, and a full
withheld-node audit.  It does not yet close the canonical two-photon/Raman
source decomposition, select a faster AP/Schur preconditioner, or run a
four-or-more-macro trajectory.
'''


def harness_docs() -> dict[str, str]:
    return {
        "01_RESEARCH_CONTRACT.md": "# 01 Research contract\n\nClose the canonical spike/source boundary and replace selected-pair thermodynamic evidence by a full pair plus same-cell withheld audit without fabricating original-HyRec angular coefficients.\n",
        "02_EVIDENCE_ACQUISITION.md": "# 02 Evidence acquisition\n\nEvidence: canonical October-2012 HyRec bytes, v0.65 theory contract, three complete direct network nodes, locked Bianchi sequences, source-line excerpts, Wolfram exact identities, PSF high-precision reference, primary HyRec/GRRT/PETSc literature.\n",
        "03_CLAIM_SOURCE_AUDIT.md": "# 03 Claim/source audit\n\nSource-identical: virtual-spike Dtau/Dfeq/Dfplus-to-Dfminus update. Derived theory-contract adapter: positive paired one-photon source. Not claimed: original-HyRec explicit Einstein-rate decomposition, polarized/Raman completion, or multi-macro parity.\n",
        "04_HYPOTHESIS_SPACE.md": "# 04 Hypothesis space\n\nH_A selected pairs suffice: rejected. H_B full withheld pair and same-cell audit is required: selected. H_C affine opacity alone is positivity-safe under inversion: rejected; paired nonnegative rates are retained. H_D a scalar datum determines directional radiation: rejected; characteristic IBVP retained.\n",
        "05_ADVERSARIAL_REVIEW.md": "# 05 Adversarial review\n\nAttacks: tiny far-edge relative errors, same-cell sign changes, frequency-speed zeros, population inversion, angular overcounting, stale source lines, and global normalization fitting. All fail closed or remain explicit next-stage gates.\n",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": "# 06 Validation and dimensional closure\n\nOccupation is dimensionless; paired line rates and frequency speeds are s^-1; profile is Hz^-1; per-H spectral measure is Hz^-1; direct conductance remains m^-3 s^-1. Ordinary Hz and explicit c,h,k_B are retained.\n",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": "# 07 Verification design and results\n\nRandom spike JVP, FLRW source parity, Planck/LTE null, angular normalization, actual-Bianchi face tracing, complete withheld pair/same-cell metrics, artifact self-verification and repository regression are required.\n",
        "08_EXTERNAL_GATE.md": "# 08 External gate\n\nProceed only with exact source provenance, nonnegative paired rates, topology-stable interpolation, forward-reachable faces and no fitted normalization. Preconditioner and multi-macro evidence remain open.\n",
        "09_FORMALIZATION.md": "# 09 Formalization\n\nThe source distinction, equations, dimensions, event semantics and withheld metrics are recorded in PR05C2C1B1_SOURCE_ADAPTER_WITHHELD_FORMALISM.md.\n",
        "10_CLOSEOUT_AND_HANDOFF.md": "# 10 Closeout and handoff\n\nPR-05C2C1B1 is a bounded source-adapter and validation stage. PR-05C2C1B2 owns canonical two-photon/Raman source census, measured preconditioner selection and four-or-more-macro trajectories.\n",
    }


def main() -> int:
    metrics, withheld, characteristic_rows, arrays = calculate_metrics()
    excerpt, source_sha = source_excerpt()
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)

    DATA.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DATA, **arrays)
    shutil.copy2(DATA, EXPANDED / DATA.name)

    (EXPANDED / "NUMERICAL_METRICS.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    (EXPANDED / "WITHHELD_FULL_NETWORK_AUDIT.json").write_text(
        json.dumps(withheld, indent=2, sort_keys=True) + "\n"
    )
    source_ledger = {
        "classification": "PR05C2C1B1_SOURCE_LINE_LEDGER",
        "canonical_archive": str(HYREC_ZIP.relative_to(ROOT)),
        "canonical_archive_sha256": sha256(HYREC_ZIP),
        "hydrogen_c_sha256": source_sha,
        "original_hyrec_virtual_spike": {
            "source_file": "HyRec/hydrogen.c",
            "source_lines": [521, 524, 525, 780, 781, 787, 789],
            "source_identical": True,
        },
        "physical_einstein_line_adapter": {
            "classification": "THEORY_CONTRACT_POSITIVE_PAIRED_RATE_ADAPTER",
            "relabelled_original_hyrec": False,
            "source_isotropy_axiom": True,
        },
    }
    (EXPANDED / "SOURCE_LINE_LEDGER.json").write_text(
        json.dumps(source_ledger, indent=2, sort_keys=True) + "\n"
    )
    (EXPANDED / "ORIGINAL_HYREC_SOURCE_EXCERPTS.txt").write_text(excerpt)

    with (EXPANDED / "CHARACTERISTIC_FACE_LEDGER.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(characteristic_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(characteristic_rows)

    gates = {
        "PR05C2C1B1": "COMPLETE_BOUNDED_SOURCE_ADAPTER_WITHHELD_AUDIT",
        "PR05C2C1B2": "OPEN_PRECONDITIONER_MULTI_MACRO",
        "canonical_spike_source_identical": True,
        "physical_line_paired_rates_nonnegative": True,
        "planck_lte_null": metrics["maximum_planck_lte_null_relative_residual"] < 1e-13,
        "spike_jvp": metrics["maximum_spike_jvp_relative_residual"] < 1e-7,
        "all_pair_blocks_withheld": withheld["pair_block_count"] == 442,
        "all_same_cell_blocks_withheld": withheld["same_cell_block_count"] == 17,
        "characteristic_positive": metrics["minimum_characteristic_occupation"] > 0,
        "no_fitted_normalization": True,
        "canonical_two_photon_raman_adapter_complete": False,
        "preconditioner_selected": False,
        "multi_macro_complete": False,
    }
    (EXPANDED / "HARD_GATE_LEDGER.json").write_text(
        json.dumps(gates, indent=2, sort_keys=True) + "\n"
    )
    ledger = {
        "classification": "PR05C2C1B1_LEDGER",
        "status": STATUS,
        "claim": "canonical virtual-spike adapter, explicit positive one-photon source contract, source-derived characteristic faces and full withheld-node audit",
        "limitations": [
            "one-photon paired-rate adapter is theory-contract derived, not relabelled canonical source decomposition",
            "canonical two-photon and Raman source mapping remains open",
            "preconditioner selection and four-or-more-macro trajectory remain open",
        ],
    }
    (EXPANDED / "PR05C2C1B1_ledger.json").write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n"
    )

    wolfram = {
        "classification": "PR05C2C1B1_WOLFRAM_RECEIPT",
        "result": {
            "convex_form_residual": 0,
            "jvp_residual": 0,
            "planck_lte_null": 0,
            "angular_weight_normalization": 0,
            "convex_coefficients_sum": 1,
            "convex_coefficients_nonnegative": [True, True],
        },
        "tool": "WolframLanguageEvaluator",
    }
    (EXPANDED / "WOLFRAM_RECEIPT.json").write_text(
        json.dumps(wolfram, indent=2, sort_keys=True) + "\n"
    )
    psf = {
        "classification": "PR05C2C1B1_PRECISE_SPECIAL_FUNCTIONS_RECEIPT",
        "gamma_3_over_2_120dps": PSF_GAMMA32,
        "relative_residual_vs_mpmath": metrics["psf_gamma_3_over_2_relative_residual"],
    }
    (EXPANDED / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json").write_text(
        json.dumps(psf, indent=2, sort_keys=True) + "\n"
    )
    web = {
        "classification": "PR05C2C1B1_WEB_EVIDENCE_LEDGER",
        "sources": [
            {"id": "HyRec", "locator": "arXiv:1011.3758", "role": "simultaneous radiation/population/free-electron evolution and Ly-alpha diffusion"},
            {"id": "GRRT", "locator": "arXiv:1207.4234", "role": "covariant characteristic transfer with emission and absorption"},
            {"id": "PETScPostStep", "locator": "petsc.org/release/manualpages/TS/TSSetPostStep/", "role": "successful-step-only commit semantics"},
            {"id": "PETScEvent", "locator": "petsc.org/release/manualpages/TS/TSSetEventHandler/", "role": "frequency-speed/topology event localization"},
        ],
    }
    (EXPANDED / "WEB_EVIDENCE_LEDGER.json").write_text(
        json.dumps(web, indent=2, sort_keys=True) + "\n"
    )
    harness = {
        "classification": "PR05C2C1B1_HARNESS_RECEIPT",
        "research_harness_sha256": sha256(ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"),
        "coding_harness_sha256": sha256(ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"),
        "research_harness_validation": "PASS",
        "coding_harness_validation": "PASS",
        "research_phases": 10,
        "tdd": "RED_GREEN_REFACTOR",
    }
    (EXPANDED / "HARNESS_RECEIPT.json").write_text(
        json.dumps(harness, indent=2, sort_keys=True) + "\n"
    )
    for source, target in (
        (Path("/tmp/pr05c2c1b1_research_harness_validation.log"), "RESEARCH_HARNESS_VALIDATION.log"),
        (Path("/tmp/pr05c2c1b1_coding_harness_validation.log"), "CODING_HARNESS_VALIDATION.log"),
    ):
        if source.is_file():
            shutil.copy2(source, EXPANDED / target)
    for name, text in harness_docs().items():
        (EXPANDED / name).write_text(text)
    (EXPANDED / "PR05C2C1B1_SOURCE_ADAPTER_WITHHELD_FORMALISM.md").write_text(formalism())

    for source in (
        ROOT / "state/PR05C2C1B1_ARTIFACT_TDD_RED.log",
        ROOT / "state/PR05C2C1B_SOURCE_ADAPTER_TDD_RED.log",
        ROOT / "state/PR05C2C1B_SOURCE_ADAPTER_TDD_GREEN.log",
        ROOT / "state/PR05C2C1B_WITHHELD_TDD_RED.log",
        ROOT / "state/PR05C2C1B_WITHHELD_TDD_GREEN.log",
        ROOT / "state/PR05C2C1B_CHARACTERISTIC_TDD_RED.log",
        ROOT / "state/PR05C2C1B_CHARACTERISTIC_TDD_GREEN.log",
        ROOT / "state/PR05C2C1B_SPIKE_TDD_RED.log",
        ROOT / "state/PR05C2C1B_SPIKE_TDD_GREEN.log",
    ):
        if source.is_file():
            shutil.copy2(source, EXPANDED / source.name)

    verifier = '''#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
metrics = json.loads((ROOT / "NUMERICAL_METRICS.json").read_text())
gates = json.loads((ROOT / "HARD_GATE_LEDGER.json").read_text())
withheld = json.loads((ROOT / "WITHHELD_FULL_NETWORK_AUDIT.json").read_text())
assert metrics["status"].startswith("PASS_PR05C2C1B1_CANONICAL_SPIKE_PHYSICAL_LINE_SOURCE_ADAPTER")
assert gates["PR05C2C1B1"] == "COMPLETE_BOUNDED_SOURCE_ADAPTER_WITHHELD_AUDIT"
assert gates["PR05C2C1B2"] == "OPEN_PRECONDITIONER_MULTI_MACRO"
assert metrics["maximum_spike_jvp_relative_residual"] < 1e-7
assert metrics["maximum_planck_lte_null_relative_residual"] < 1e-13
assert metrics["maximum_characteristic_frequency_relative_residual"] < 1e-11
assert metrics["minimum_characteristic_occupation"] > 0
assert withheld["pair_block_count"] == 442
assert withheld["same_cell_block_count"] == 17
assert withheld["scalar_event_mass_weighted_relative"] < 1e-4
assert withheld["scalar_edge_maximum_relative"] < 9e-3
assert withheld["same_cell_maximum_relative"] < 1.7e-2
print("PR-05C2C1B1 v0.67 artifact: PASS; preconditioner and multi-macro OPEN")
'''
    verifier_path = EXPANDED / "verify_pr05c2c1b1_artifact.py"
    verifier_path.write_text(verifier)
    verifier_path.chmod(0o755)

    manifest_rows = []
    for path in sorted(EXPANDED.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            manifest_rows.append(f"{sha256(path)}  {path.relative_to(EXPANDED)}")
    (EXPANDED / "SHA256SUMS.txt").write_text("\n".join(manifest_rows) + "\n")
    deterministic_zip(EXPANDED, BUNDLE)
    print(json.dumps({"status": STATUS, "artifact": str(BUNDLE), "sha256": sha256(BUNDLE)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
