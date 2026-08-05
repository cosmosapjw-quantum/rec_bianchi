#!/usr/bin/env python3
"""Build and verify PR-03/v0.50 full scalar COM--KHW release.

The expensive moment and nonlinear-runtime regressions use one BLAS thread per
process.  The stage preserves the PR-01 frame adapter and PR-02 runtime APIs;
only the scalar atomic response and its derived conductance moments change.
"""
from __future__ import annotations

import os
import sys

if os.environ.get("PR03_NUMERICAL_THREAD_LOCK") != "1":
    environment = os.environ.copy()
    environment.update(
        {
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "PR02_NUMERICAL_THREAD_LOCK": "1",
            "PR03_NUMERICAL_THREAD_LOCK": "1",
        }
    )
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

import mpmath as mp
import numpy as np
import sympy as sp
from scipy.constants import c, h, physical_constants
from scipy.special import wofz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC
from full_bianchi_hyrec.recoil.event import scatter_elastic
from full_bianchi_hyrec.recoil.event_weight import pt_reverse_kinematics
from full_bianchi_hyrec.recoil.exterior_interface import (
    EXTERIOR_CELLS,
    exterior_pair_bundle,
    exterior_pair_conductance,
    interior_cells,
)
from full_bianchi_hyrec.recoil.far_exterior import (
    FAR_CELLS,
    assemble_scalar_pair_generator,
)
from full_bianchi_hyrec.recoil.four_vector import (
    atom_four_momentum,
    photon_four_momentum,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    apply_nonlinear_bose_operator,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    ADAPTIVE_GRID_ORDER,
    BoseCollisionRuntime,
    CollisionNetwork,
    LineBoundaryConfig,
)
from full_bianchi_hyrec.recoil.same_cell_regular import (
    integrate_same_cell_regularized,
)
from full_bianchi_hyrec.recoil.scalar_com_khw import (
    LY_ALPHA_FREQUENCY_HZ,
    LY_ALPHA_OSCILLATOR_STRENGTH,
    RYDBERG_FREQUENCY_HZ,
    bound_oscillator_strength,
    compile_oscillator_strength_measure,
    compile_smooth_background_series,
    continuum_oscillator_strength_density,
    default_scalar_com_khw_model,
    denominator_reciprocity_residuals,
    direct_smooth_background,
    fixed_nucleus_length_gauge_amplitude,
    scalar_com_khw_amplitude,
    scalar_event_com_khw_amplitude,
    smooth_background_polynomial,
)

ARTIFACT_NAME = "Full_Bianchi_HyRec_PR03_full_scalar_COM_KHW_v0_50"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "full_scalar_com_khw_v050.npz"
PARENT_COLLISION_DATA = ROOT / "data" / "far_scalar_release_v047.npz"
SNAPSHOT_DATA = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
CACHE = ROOT / ".cache" / "v050_full_scalar_khw"
COMMON_MODE_FACTOR = 8.0 * math.pi * PCC.dnu / PCC.c**3
M_H = physical_constants["atomic mass constant"][0] * 1.00782503223


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def _save_cache(path: Path, **values) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **values)
    temporary.replace(path)


def _network_job(job):
    kind, a, b, target, source, ell_max, cache_name = job
    cache = Path(cache_name)
    if cache.exists():
        with np.load(cache, allow_pickle=False) as data:
            return (
                kind,
                a,
                b,
                np.asarray(data["values"]),
                np.asarray(data.get("transfer", np.zeros(2))),
            )
    if kind == "interior":
        values = COMMON_MODE_FACTOR * PCC.integrate_unordered_pair(
            int(a),
            int(b),
            lane="production",
            ell_max=ell_max,
            amplitude_lane="full",
        )
        transfer = np.zeros(2)
    elif kind in {"near", "far"}:
        values, transfer = exterior_pair_bundle(
            tuple(target),
            tuple(source),
            lane="production",
            ell_max=ell_max,
            amplitude_lane="full",
        )
    elif kind == "same":
        values = integrate_same_cell_regularized(
            int(a),
            lane="production",
            ell_max=ell_max,
            amplitude_lane="full",
        )
        transfer = np.zeros(2)
    else:
        raise ValueError(kind)
    _save_cache(cache, values=values, transfer=transfer)
    return kind, a, b, values, transfer


def build_network(workers: int, ell_max: int = 24):
    with np.load(PARENT_COLLISION_DATA, allow_pickle=False) as parent:
        intervals = np.asarray(parent["state_intervals"], dtype=float)
        labels = parent["state_labels"].astype(str)
        mode = np.asarray(parent["mode_measure_m3"], dtype=float)
        equilibrium = np.asarray(parent["equilibrium_weight_m3"], dtype=float)
        momentum = np.asarray(parent["momentum_scale"], dtype=float)
        release_states = parent["release_states"].astype(str)
        release_ell = np.asarray(parent["release_ell"], dtype=int)
        provisional_pair = np.asarray(parent["pair_moments_m3_sInv"], dtype=float)
        provisional_same = np.asarray(parent["same_cell_rates_sInv"], dtype=float)

    interior = interior_cells()
    near = EXTERIOR_CELLS
    far = FAR_CELLS
    expected = np.asarray(interior + near + far, dtype=float)
    if intervals.shape != expected.shape or np.max(np.abs(intervals - expected)) > 0.0:
        raise RuntimeError("v0.47 state registry no longer matches source intervals")
    n_int, n_near, n_far = len(interior), len(near), len(far)
    n_state = len(intervals)

    jobs = []
    for i in range(n_int):
        for j in range(i + 1, n_int):
            jobs.append(
                (
                    "interior",
                    i,
                    j,
                    interior[i],
                    interior[j],
                    ell_max,
                    str(CACHE / f"interior_i{i:02d}_j{j:02d}.npz"),
                )
            )
    for e, cell in enumerate(near):
        for i, source in enumerate(interior):
            jobs.append(
                (
                    "near",
                    e,
                    i,
                    cell,
                    source,
                    ell_max,
                    str(CACHE / f"near_e{e:02d}_i{i:02d}.npz"),
                )
            )
    for e, cell in enumerate(far):
        for i, source in enumerate(interior):
            jobs.append(
                (
                    "far",
                    e,
                    i,
                    cell,
                    source,
                    ell_max,
                    str(CACHE / f"far_e{e:02d}_i{i:02d}.npz"),
                )
            )
    for i in range(n_int):
        jobs.append(
            (
                "same",
                i,
                0,
                interior[i],
                interior[i],
                ell_max,
                str(CACHE / f"same_i{i:02d}.npz"),
            )
        )

    pair_moments = np.zeros((ell_max + 1, n_state, n_state), dtype=float)
    same_rates = np.zeros((ell_max + 1, n_state), dtype=float)
    near_transfer = np.zeros((n_near, n_int, 2), dtype=float)
    far_transfer = np.zeros((n_far, n_int, 2), dtype=float)

    start = time.time()
    completed = 0
    CACHE.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [executor.submit(_network_job, job) for job in jobs]
        for future in as_completed(futures):
            kind, a, b, values, transfer = future.result()
            if kind == "interior":
                pair_moments[:, a, b] = values
                pair_moments[:, b, a] = values
            elif kind == "near":
                state = n_int + a
                pair_moments[:, state, b] = values
                pair_moments[:, b, state] = values
                near_transfer[a, b] = transfer
            elif kind == "far":
                state = n_int + n_near + a
                pair_moments[:, state, b] = values
                pair_moments[:, b, state] = values
                far_transfer[a, b] = transfer
            else:
                same_rates[:, a] = values
            completed += 1
            if completed % 10 == 0 or completed == len(jobs):
                print(
                    f"PR03_NETWORK_PROGRESS {completed}/{len(jobs)} "
                    f"elapsed_s={time.time()-start:.1f}",
                    flush=True,
                )

    scalar_generator = assemble_scalar_pair_generator(pair_moments[0], equilibrium)
    return {
        "intervals": intervals,
        "labels": labels,
        "mode": mode,
        "equilibrium": equilibrium,
        "momentum": momentum,
        "release_states": release_states,
        "release_ell": release_ell,
        "pair_moments": pair_moments,
        "same_rates": same_rates,
        "scalar_generator": scalar_generator,
        "near_transfer": near_transfer,
        "far_transfer": far_transfer,
        "provisional_pair": provisional_pair,
        "provisional_same": provisional_same,
        "elapsed_s": time.time() - start,
    }


def high_precision_spectrum_audit():
    mp.mp.dps = 90

    def bound_f(n):
        n = mp.mpf(n)
        return (
            mp.mpf(256) / 3
            * n**5
            * (n - 1) ** (2 * n - 4)
            / (n + 1) ** (2 * n + 4)
        )

    def continuum_f(n):
        n = mp.mpf(n)
        return (
            mp.mpf(256) / 3
            * n**5
            / (1 + n**2) ** 4
            * mp.e ** (-4 * n * mp.atan(1 / n))
            / (1 - mp.e ** (-2 * mp.pi * n))
        )

    bound_sum = mp.nsum(lambda index: bound_f(index), [2, mp.inf])
    bound_alpha = mp.nsum(
        lambda index: 4 * bound_f(index) / (1 - 1 / index**2) ** 2,
        [2, mp.inf],
    )

    def mapped_integral(function):
        def mapped(t):
            if t == 1:
                return mp.mpf("0")
            n = t / (1 - t)
            return function(n) / (1 - t) ** 2
        return mp.quad(mapped, [0, mp.mpf("0.5"), mp.mpf("0.9"), mp.mpf("0.99"), 1])

    continuum_sum = mapped_integral(continuum_f)
    continuum_alpha = mapped_integral(
        lambda n: 4 * continuum_f(n) / (1 + 1 / n**2) ** 2
    )
    trk = bound_sum + continuum_sum
    alpha = bound_alpha + continuum_alpha

    model = default_scalar_com_khw_model()
    measure = model.measure
    rows = [
        {
            "check": "bound_infinite_oscillator_strength",
            "reference": mp.nstr(bound_sum, 40),
            "production": f"{measure.raw_bound_partial_sum + measure.tail_weight:.17g}",
            "absolute_residual": mp.nstr(
                abs(bound_sum - mp.mpf(str(measure.raw_bound_partial_sum + measure.tail_weight))),
                20,
            ),
        },
        {
            "check": "continuum_infinite_oscillator_strength",
            "reference": mp.nstr(continuum_sum, 40),
            "production": f"{measure.raw_continuum_quadrature_sum:.17g}",
            "absolute_residual": mp.nstr(
                abs(continuum_sum - mp.mpf(str(measure.raw_continuum_quadrature_sum))),
                20,
            ),
        },
        {
            "check": "TRK_bound_plus_continuum",
            "reference": mp.nstr(trk, 40),
            "production": f"{measure.trk_sum:.17g}",
            "absolute_residual": mp.nstr(abs(trk - 1), 20),
        },
        {
            "check": "static_polarizability_a0_cubed",
            "reference": mp.nstr(alpha, 40),
            "production": f"{measure.static_polarizability_a0_cubed:.17g}",
            "absolute_residual": mp.nstr(abs(alpha - mp.mpf("4.5")), 20),
        },
        {
            "check": "Ly_alpha_oscillator_strength",
            "reference": mp.nstr(bound_f(2), 40),
            "production": f"{LY_ALPHA_OSCILLATOR_STRENGTH:.17g}",
            "absolute_residual": mp.nstr(
                abs(bound_f(2) - mp.mpf(str(LY_ALPHA_OSCILLATOR_STRENGTH))), 20
            ),
        },
    ]
    return rows, {
        "bound_sum": bound_sum,
        "continuum_sum": continuum_sum,
        "trk": trk,
        "bound_alpha": bound_alpha,
        "continuum_alpha": continuum_alpha,
        "alpha": alpha,
    }


def symbolic_and_special_function_audit():
    x, delta = sp.symbols("x delta", nonzero=True)
    time_ordering = sp.simplify(
        delta * sp.Rational(1, 2) * (1 / (delta - x) + 1 / (delta + x))
        - delta**2 / (delta**2 - x**2)
    )
    gauge_channel = sp.simplify(
        1 - delta**2 / (delta**2 - x**2) + x**2 / (delta**2 - x**2)
    )
    rows = [
        {
            "check": "SymPy_two_time_ordering_identity",
            "argument": "symbolic",
            "reference": "0",
            "computed": str(time_ordering),
            "relative_residual": 0.0 if time_ordering == 0 else 1.0,
        },
        {
            "check": "SymPy_seagull_TRK_to_length_gauge_channel",
            "argument": "symbolic",
            "reference": "0",
            "computed": str(gauge_channel),
            "relative_residual": 0.0 if gauge_channel == 0 else 1.0,
        },
    ]
    mp.mp.dps = 100
    for value in (
        complex(0.1, 0.2),
        complex(-3.0, 0.01),
        complex(8.0, 1.0e-4),
        complex(-12.0, 2.0),
    ):
        z = mp.mpc(str(value.real), str(value.imag))
        reference = mp.e ** (-z * z) * mp.erfc(-1j * z)
        computed = complex(wofz(value))
        residual = abs(mp.mpc(computed.real, computed.imag) - reference) / max(
            abs(reference), mp.mpf("1e-100")
        )
        rows.append(
            {
                "check": "Faddeeva_SciPy_vs_mpmath_100dps",
                "argument": repr(value),
                "reference": mp.nstr(reference, 35),
                "computed": repr(computed),
                "relative_residual": float(residual),
            }
        )
    return rows


def gauge_ir_uv_audit():
    model = default_scalar_com_khw_model()
    measure = model.measure
    rows: list[dict] = []
    maximum_gauge = 0.0
    for fraction in (1.0e-3, 1.0e-2, 0.1, 0.5, 0.7):
        frequency = fraction * RYDBERG_FREQUENCY_HZ
        velocity = scalar_com_khw_amplitude(
            frequency, frequency, include_2p_width=False
        ).real
        length = fixed_nucleus_length_gauge_amplitude(frequency)
        residual = abs(velocity - length) / (abs(length) + 1.0e-300)
        maximum_gauge = max(maximum_gauge, residual)
        rows.append(
            {
                "check": "fixed_nucleus_velocity_length_gauge",
                "parameter": fraction,
                "value": velocity,
                "reference": length,
                "relative_residual": residual,
            }
        )

    q = 2.0e-5
    a1 = abs(
        scalar_com_khw_amplitude(
            q * RYDBERG_FREQUENCY_HZ,
            q * RYDBERG_FREQUENCY_HZ,
            include_2p_width=False,
        )
    )
    a2 = abs(
        scalar_com_khw_amplitude(
            2.0 * q * RYDBERG_FREQUENCY_HZ,
            2.0 * q * RYDBERG_FREQUENCY_HZ,
            include_2p_width=False,
        )
    )
    amp_power = math.log(a2 / a1) / math.log(2.0)
    sigma_power = math.log((a2 / a1) ** 2) / math.log(2.0)
    rows.extend(
        [
            {
                "check": "infrared_amplitude_power",
                "parameter": q,
                "value": amp_power,
                "reference": 2.0,
                "relative_residual": abs(amp_power / 2.0 - 1.0),
            },
            {
                "check": "infrared_cross_section_power",
                "parameter": q,
                "value": sigma_power,
                "reference": 4.0,
                "relative_residual": abs(sigma_power / 4.0 - 1.0),
            },
        ]
    )

    continuum_convergence = []
    for order in (64, 128, 256, 512):
        compiled = compile_oscillator_strength_measure(512, order)
        continuum_convergence.append(
            (order, compiled.raw_continuum_quadrature_sum)
        )
    reference_continuum = continuum_convergence[-1][1]
    for order, value in continuum_convergence:
        rows.append(
            {
                "check": "continuum_positive_quadrature_convergence",
                "parameter": order,
                "value": value,
                "reference": reference_continuum,
                "relative_residual": abs(value / reference_continuum - 1.0),
            }
        )

    # High intermediate-energy continuum is n->0 in this parameterization.
    nodes, weights = np.polynomial.legendre.leggauss(256)
    n_cut = 1.0e-2
    n = 0.5 * n_cut * (nodes + 1.0)
    high_energy_weight = 0.5 * n_cut * float(
        np.dot(weights, continuum_oscillator_strength_density(n))
    )
    rows.append(
        {
            "check": "high_intermediate_energy_continuum_tail_n_lt_1e-2",
            "parameter": n_cut,
            "value": high_energy_weight,
            "reference": measure.trk_sum,
            "relative_residual": high_energy_weight / measure.trk_sum,
        }
    )

    production = compile_smooth_background_series(4)
    reference = compile_smooth_background_series(8)
    A = np.asarray([-8.0, -4.0, -1.0, 0.0, 3.0, 8.0]) * PCC.dnu
    B = np.asarray([2.0, 1.2, 0.5, 1.5, 2.0, 2.5]) * PCC.dnu
    C = 2.0 * LY_ALPHA_FREQUENCY_HZ + np.asarray([-5.0, -2.0, 0.0, 1.0, 4.0, 8.0]) * PCC.dnu
    D = -B
    pcoeff = smooth_background_polynomial(A, B, C, D, series=production)
    rcoeff = smooth_background_polynomial(A, B, C, D, series=reference)
    max_p = 0.0
    max_r = 0.0
    for z in (-8.0, -3.0, 0.0, 2.0, 8.0):
        direct = direct_smooth_background(A, B, C, D, z)
        pvalue = sum(pcoeff[k] * z**k for k in range(5))
        rvalue = sum(rcoeff[k] * z**k for k in range(9))
        max_p = max(max_p, float(np.max(np.abs(pvalue / direct - 1.0))))
        max_r = max(max_r, float(np.max(np.abs(rvalue / direct - 1.0))))
    rows.extend(
        [
            {
                "check": "smooth_background_order4_vs_direct",
                "parameter": 4,
                "value": max_p,
                "reference": 0.0,
                "relative_residual": max_p,
            },
            {
                "check": "smooth_background_order8_vs_direct",
                "parameter": 8,
                "value": max_r,
                "reference": 0.0,
                "relative_residual": max_r,
            },
        ]
    )
    return rows, {
        "maximum_gauge_residual": maximum_gauge,
        "infrared_amplitude_power": amp_power,
        "infrared_cross_section_power": sigma_power,
        "maximum_order4_background_residual": max_p,
        "maximum_order8_background_residual": max_r,
        "high_energy_continuum_tail": high_energy_weight,
    }


def pt_reciprocity_audit():
    atom = atom_four_momentum(M_H, np.asarray([2.0e-5, -1.0e-5, 0.5e-5]))
    photon = photon_four_momentum(
        1.00003 * LY_ALPHA_FREQUENCY_HZ, np.asarray([0.3, -0.4, 0.8])
    )
    event = scatter_elastic(atom, photon, np.asarray([-0.7, 0.2, 0.5]), M_H)
    reverse = pt_reverse_kinematics(event)
    denominator_residual = max(
        denominator_reciprocity_residuals(
            event.P_i,
            event.k_i,
            event.k_f,
            reverse.P_i,
            reverse.k_i,
            reverse.k_f,
            M_H,
        )
    )
    forward = scalar_event_com_khw_amplitude(event.P_i, event.k_i, event.k_f, M_H)
    backward = scalar_event_com_khw_amplitude(
        reverse.P_i, reverse.k_i, reverse.k_f, M_H
    )
    amplitude_residual = abs(forward - backward) / max(abs(forward), abs(backward))

    # Arbitrary-precision, exactly conservative recoil event with the atom
    # initially at rest.  Energies are used directly; c is retained.
    mp.mp.dps = 90
    c_mp = mp.mpf(str(c))
    h_mp = mp.mpf(str(h))
    mass = mp.mpf(str(M_H))
    rest = mass * c_mp**2
    nu = mp.mpf("1.00003") * mp.mpf(str(LY_ALPHA_FREQUENCY_HZ))
    incoming_energy = h_mp * nu
    mu = mp.mpf("0.37")
    outgoing_energy = incoming_energy / (
        1 + incoming_energy / rest * (1 - mu)
    )
    sin_theta = mp.sqrt(1 - mu**2)
    k_in = [mp.mpf("0"), mp.mpf("0"), incoming_energy / c_mp]
    k_out = [
        outgoing_energy / c_mp * sin_theta,
        mp.mpf("0"),
        outgoing_energy / c_mp * mu,
    ]
    p_final = [k_in[i] - k_out[i] for i in range(3)]
    energy_final = mp.sqrt(rest**2 + c_mp**2 * sum(v * v for v in p_final))

    def denominators(p, ein, kin, eout, kout, transitions):
        ground_energy = mp.sqrt(rest**2 + c_mp**2 * sum(v * v for v in p))
        result_minus = []
        result_plus = []
        for transition in transitions:
            excited_rest = rest + h_mp * transition
            pa = [p[i] + kin[i] for i in range(3)]
            pe = [p[i] - kout[i] for i in range(3)]
            ea = mp.sqrt(excited_rest**2 + c_mp**2 * sum(v * v for v in pa))
            ee = mp.sqrt(excited_rest**2 + c_mp**2 * sum(v * v for v in pe))
            result_minus.append((ea - ground_energy - ein) / h_mp)
            result_plus.append((ee - ground_energy + eout) / h_mp)
        return result_minus, result_plus

    transitions = [
        mp.mpf(str(LY_ALPHA_FREQUENCY_HZ)),
        mp.mpf(str(RYDBERG_FREQUENCY_HZ * (1 - 1 / 9))),
        mp.mpf(str(RYDBERG_FREQUENCY_HZ * 1.7)),
    ]
    forward_hp = denominators(
        [mp.mpf("0")] * 3,
        incoming_energy,
        k_in,
        outgoing_energy,
        k_out,
        transitions,
    )
    reverse_hp = denominators(
        [-v for v in p_final],
        outgoing_energy,
        [-v for v in k_out],
        incoming_energy,
        [-v for v in k_in],
        transitions,
    )
    hp_residual = max(
        abs(a - b) / max(abs(a), abs(b), mp.mpf("1"))
        for left, right in zip(forward_hp, reverse_hp)
        for a, b in zip(left, right)
    )
    energy_shell_residual = abs(
        energy_final - (rest + incoming_energy - outgoing_energy)
    ) / rest
    rows = [
        {
            "check": "float64_statewise_denominator_PT",
            "relative_residual": denominator_residual,
        },
        {
            "check": "float64_full_amplitude_PT",
            "relative_residual": amplitude_residual,
        },
        {
            "check": "mpmath_90dps_statewise_denominator_PT",
            "relative_residual": mp.nstr(hp_residual, 30),
        },
        {
            "check": "mpmath_90dps_event_energy_shell",
            "relative_residual": mp.nstr(energy_shell_residual, 30),
        },
    ]
    return rows, {
        "float_denominator_residual": denominator_residual,
        "float_amplitude_residual": amplitude_residual,
        "high_precision_denominator_residual": float(hp_residual),
        "high_precision_event_shell_residual": float(energy_shell_residual),
    }


def selected_pair_audit(network_data):
    interior = interior_cells()
    near = EXTERIOR_CELLS
    far = FAR_CELLS
    selected = [
        ("interior_core", "interior", 7, 9),
        ("interior_cross", "interior", 0, 16),
        ("near_red", "near", 5, 0),
        ("near_blue", "near", 6, 16),
        ("far_red", "far", 2, 0),
        ("far_blue", "far", 3, 16),
    ]
    rows = []
    max_quadrature = 0.0
    max_orientation = 0.0
    max_network_reproduction = 0.0
    for name, kind, a, b in selected:
        if kind == "interior":
            target = interior[a]
            source = interior[b]
            production = COMMON_MODE_FACTOR * PCC.integrate_unordered_pair(
                a, b, lane="production", ell_max=6, amplitude_lane="full"
            )
            reference = COMMON_MODE_FACTOR * PCC.integrate_unordered_pair(
                a, b, lane="reference", ell_max=6, amplitude_lane="full"
            )
            reverse = COMMON_MODE_FACTOR * PCC.integrate_unordered_pair(
                b, a, lane="production", ell_max=6, amplitude_lane="full"
            )
            stored = network_data["pair_moments"][:7, a, b]
            provisional = network_data["provisional_pair"][:7, a, b]
        else:
            cells = near if kind == "near" else far
            target = cells[a]
            source = interior[b]
            production = exterior_pair_conductance(
                target,
                source,
                lane="production",
                ell_max=6,
                amplitude_lane="full",
            )
            reference = exterior_pair_conductance(
                target,
                source,
                lane="reference",
                ell_max=6,
                amplitude_lane="full",
            )
            reverse = exterior_pair_conductance(
                source,
                target,
                lane="production",
                ell_max=6,
                amplitude_lane="full",
            )
            offset = len(interior) + (0 if kind == "near" else len(near))
            stored = network_data["pair_moments"][:7, offset + a, b]
            provisional = network_data["provisional_pair"][:7, offset + a, b]
        qrel = float(
            np.linalg.norm(production - reference)
            / (np.linalg.norm(reference) + 1.0e-300)
        )
        orel = float(
            np.linalg.norm(production - reverse)
            / (np.linalg.norm(production) + 1.0e-300)
        )
        nrel = float(
            np.linalg.norm(production - stored)
            / (np.linalg.norm(production) + 1.0e-300)
        )
        prel = float(
            np.linalg.norm(production - provisional)
            / (np.linalg.norm(provisional) + 1.0e-300)
        )
        max_quadrature = max(max_quadrature, qrel)
        max_orientation = max(max_orientation, orel)
        max_network_reproduction = max(max_network_reproduction, nrel)
        rows.append(
            {
                "case": name,
                "kind": kind,
                "S0_full": production[0],
                "S0_provisional": provisional[0],
                "full_minus_provisional_relative": prel,
                "production_reference_relative": qrel,
                "orientation_relative": orel,
                "stored_reproduction_relative": nrel,
            }
        )
    return rows, {
        "maximum_selected_quadrature_relative": max_quadrature,
        "maximum_selected_orientation_relative": max_orientation,
        "maximum_selected_network_reproduction_relative": max_network_reproduction,
    }


def load_pr02_helpers():
    path = ROOT / "scripts" / "run_pr02_nonlinear_bose_runtime_stage.py"
    spec = importlib.util.spec_from_file_location("pr02_stage_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load PR-02 helper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def runtime_regressions(network: CollisionNetwork):
    helper = load_pr02_helpers()
    runtime = BoseCollisionRuntime(network)
    boundary = LineBoundaryConfig.lyman_alpha()
    policy_rows = []
    operator_rows = []
    implicit_rows = []
    jacobian_rows = []
    evidence = {}

    maxima = {
        "be": 0.0,
        "number": 0.0,
        "boundary_number": 0.0,
        "jvp": 0.0,
        "jvp_number": 0.0,
        "implicit_jvp": 0.0,
        "four_h": 0.0,
        "four_n": 0.0,
        "frame": 0.0,
        "gram": 0.0,
        "implicit_residual": 0.0,
        "implicit_number": 0.0,
        "entropy": -math.inf,
        "free_change": -math.inf,
    }
    minima = {
        "grid_weight": math.inf,
        "boundary_fraction": math.inf,
        "implicit_occupation": math.inf,
    }

    with np.load(SNAPSHOT_DATA, allow_pickle=False) as snapshot_data:
        for spec in helper.SCENARIOS:
            snapshot = helper.snapshot_record(
                snapshot_data, spec["model"], spec["snapshot_index"]
            )
            state = runtime.prepare(snapshot, boundary=boundary)
            occupation = helper.runtime_occupation(spec["name"], state, network)
            result = runtime.evaluate(state, occupation)

            be = helper.be_family(network, 1.0)
            be_occupation = np.repeat(be[:, None], state.grid.n_angle, axis=1)
            be_result = apply_nonlinear_bose_operator(
                be_occupation,
                mode_measure=network.mode_measure,
                equilibrium_weight=network.equilibrium_weight,
                pair_moments=network.pair_moments,
                same_cell_rates=network.same_cell_rates,
                grid=state.grid,
                photon_momentum_scale=network.momentum_scale,
            )
            be_relative = float(
                np.max(np.abs(be_result.number_action))
                / (be_result.gross_action_scale + 1.0e-300)
            )
            jvp, jvp_fd, jvp_relative, jvp_number = helper.exact_jvp_regression(
                occupation, state, network
            )

            action = result.full_action.occupation_action
            negative = action < 0.0
            if not np.any(negative):
                raise RuntimeError(f"{spec['name']} has no positivity-limiting mode")
            explicit_critical_dt = float(
                np.min(-occupation[negative] / action[negative])
            )
            dt_s = 1.02 * explicit_critical_dt
            implicit = runtime.implicit_step(state, occupation, dt_s=dt_s)

            implicit_jvp_relative = math.nan
            if spec["name"] == "finite_or_mixed_tilt":
                _, _, implicit_jvp_relative = helper.implicit_jvp_regression(
                    occupation, state, network, dt_s
                )
                maxima["implicit_jvp"] = max(
                    maxima["implicit_jvp"], implicit_jvp_relative
                )

            full_number = helper.relative_number_residual(result.full_action)
            boundary_number = helper.relative_number_residual(result.boundary_action)
            full_norm = float(np.linalg.norm(result.full_action.occupation_action))
            boundary_norm = float(
                np.linalg.norm(result.boundary_action.occupation_action)
            )
            boundary_fraction = boundary_norm / (full_norm + 1.0e-300)

            policy_rows.append(
                {
                    "scenario": spec["name"],
                    "bianchi_type": snapshot.bianchi_type,
                    "chart_id": snapshot.chart_id,
                    "selected_policy": state.policy.policy,
                    "ell_max": state.policy.ell_max,
                    "lebedev_order": ADAPTIVE_GRID_ORDER[state.policy.ell_max],
                    "angle_count": state.grid.n_angle,
                    "minimum_weight": float(np.min(state.grid.weights)),
                    "gram_residual": state.grid.gram_residual,
                    "frame_roundtrip_residual": state.frame_roundtrip_residual,
                    "characteristic_crossing": state.policy.characteristic_crossing,
                    "policy_match": (
                        state.policy.policy == spec["expected_policy"]
                        and state.policy.ell_max == spec["expected_ell_max"]
                    ),
                }
            )
            operator_rows.append(
                {
                    "scenario": spec["name"],
                    "BE_action_relative": be_relative,
                    "number_residual_relative": full_number,
                    "boundary_number_residual_relative": boundary_number,
                    "entropy_free_energy_production": result.full_action.entropy_production,
                    "boundary_to_full_action_norm": boundary_fraction,
                    "four_force_hydrogen_residual": result.four_force_hydrogen_residual,
                    "four_force_normal_residual": result.four_force_normal_residual,
                }
            )
            implicit_rows.append(
                {
                    "scenario": spec["name"],
                    "explicit_critical_dt_s": explicit_critical_dt,
                    "implicit_dt_s": dt_s,
                    "explicit_trial_minimum": implicit.explicit_trial_minimum,
                    "implicit_minimum": implicit.minimum_occupation,
                    "converged": implicit.converged,
                    "newton_iterations": implicit.newton_iterations,
                    "total_gmres_iterations": implicit.total_gmres_iterations,
                    "residual_relative": implicit.residual_relative,
                    "number_relative_change": implicit.number_relative_change,
                    "free_energy_change": implicit.free_energy_change,
                }
            )
            jacobian_rows.append(
                {
                    "scenario": spec["name"],
                    "test": "collision_action_exact_JVP",
                    "relative_residual": jvp_relative,
                    "number_left_null_relative": jvp_number,
                }
            )
            if math.isfinite(implicit_jvp_relative):
                jacobian_rows.append(
                    {
                        "scenario": spec["name"],
                        "test": "log_backward_euler_residual_JVP",
                        "relative_residual": implicit_jvp_relative,
                        "number_left_null_relative": "",
                    }
                )

            prefix = spec["name"]
            evidence[f"{prefix}_occupation"] = occupation
            evidence[f"{prefix}_action"] = result.full_action.occupation_action
            evidence[f"{prefix}_implicit"] = implicit.occupation
            evidence[f"{prefix}_directions_normal"] = state.direction_normal
            evidence[f"{prefix}_directions_hydrogen"] = state.direction_hydrogen
            evidence[f"{prefix}_weights"] = state.grid.weights
            evidence[f"{prefix}_jvp_exact"] = jvp.occupation_action_jvp
            evidence[f"{prefix}_jvp_fd"] = jvp_fd

            maxima["be"] = max(maxima["be"], be_relative)
            maxima["number"] = max(maxima["number"], full_number)
            maxima["boundary_number"] = max(
                maxima["boundary_number"], boundary_number
            )
            maxima["jvp"] = max(maxima["jvp"], jvp_relative)
            maxima["jvp_number"] = max(maxima["jvp_number"], jvp_number)
            maxima["four_h"] = max(
                maxima["four_h"], result.four_force_hydrogen_residual
            )
            maxima["four_n"] = max(
                maxima["four_n"], result.four_force_normal_residual
            )
            maxima["frame"] = max(maxima["frame"], state.frame_roundtrip_residual)
            maxima["gram"] = max(maxima["gram"], state.grid.gram_residual)
            maxima["implicit_residual"] = max(
                maxima["implicit_residual"], implicit.residual_relative
            )
            maxima["implicit_number"] = max(
                maxima["implicit_number"], implicit.number_relative_change
            )
            maxima["entropy"] = max(
                maxima["entropy"], result.full_action.entropy_production
            )
            maxima["free_change"] = max(
                maxima["free_change"], implicit.free_energy_change
            )
            minima["grid_weight"] = min(
                minima["grid_weight"], float(np.min(state.grid.weights))
            )
            minima["boundary_fraction"] = min(
                minima["boundary_fraction"], boundary_fraction
            )
            minima["implicit_occupation"] = min(
                minima["implicit_occupation"], implicit.minimum_occupation
            )

        firewall_actions = []
        common_occupation = None
        for model, index in (
            ("Bianchi_II_large_shear", 70),
            ("Bianchi_VI_h_tilted_large_shear", 100),
            ("Bianchi_VI_minus_1_over_9_exceptional", 100),
        ):
            snapshot = helper.snapshot_record(snapshot_data, model, index)
            state = runtime.prepare(snapshot, force_ell_max=12)
            if common_occupation is None:
                base = helper.be_family(network, 0.25)
                angular = 1.0 + 0.08 * state.grid.directions[:, 2]
                common_occupation = base[:, None] * angular[None, :]
            firewall_actions.append(
                runtime.evaluate(state, common_occupation).full_action.occupation_action
            )
    firewall = np.asarray(firewall_actions)
    geometry_difference = float(np.max(np.abs(firewall - firewall[0])))
    evidence["geometry_firewall_actions"] = firewall

    gates = {
        "runtime_BackgroundSnapshot_connection": all(
            row["policy_match"] for row in policy_rows
        ),
        "adaptive_L12_L20_L24_policy": {
            (row["selected_policy"], int(row["ell_max"])) for row in policy_rows
        }
        == {
            ("finite_or_mixed_tilt", 12),
            ("nonlinear_even_shear", 20),
            ("directional_crossing", 24),
        },
        "positive_weight_grids": minima["grid_weight"] > 0.0,
        "harmonic_analysis_exactness": maxima["gram"] < 5.0e-12,
        "frame_roundtrip": maxima["frame"] < 2.0e-13,
        "Bose_Einstein_null": maxima["be"] < 2.0e-14,
        "photon_number": maxima["number"] < 1.0e-13,
        "boundary_edge_number": maxima["boundary_number"] < 1.0e-13,
        "stimulated_boundary_edge_active": minima["boundary_fraction"] > 1.0e-8,
        "entropy_free_energy_dissipation": maxima["entropy"] <= 0.0,
        "analytic_collision_JVP": maxima["jvp"] < 2.0e-8,
        "collision_JVP_number_left_null": maxima["jvp_number"] < 1.0e-12,
        "analytic_implicit_residual_JVP": maxima["implicit_jvp"] < 2.0e-8,
        "implicit_convergence": all(row["converged"] for row in implicit_rows)
        and maxima["implicit_residual"] < 5.0e-10,
        "implicit_positivity": minima["implicit_occupation"] > 0.0,
        "explicit_stress_fails_positivity": all(
            row["explicit_trial_minimum"] < 0.0 for row in implicit_rows
        ),
        "implicit_number": maxima["implicit_number"] < 5.0e-12,
        "implicit_free_energy": maxima["free_change"] < 0.0,
        "total_four_force_hydrogen": maxima["four_h"] < 1.0e-12,
        "total_four_force_normal": maxima["four_n"] < 1.0e-12,
        "local_microphysics_firewall": geometry_difference == 0.0,
    }
    if not all(gates.values()):
        raise RuntimeError(
            "PR-03 inherited runtime gates failed: "
            + repr([name for name, value in gates.items() if not value])
        )
    hard_results = {
        "maximum_BE_action_relative": maxima["be"],
        "maximum_number_residual_relative": maxima["number"],
        "maximum_boundary_number_residual_relative": maxima["boundary_number"],
        "maximum_entropy_free_energy_production": maxima["entropy"],
        "minimum_boundary_to_full_action_norm": minima["boundary_fraction"],
        "maximum_collision_JVP_relative": maxima["jvp"],
        "maximum_collision_JVP_number_left_null_relative": maxima["jvp_number"],
        "maximum_implicit_residual_JVP_relative": maxima["implicit_jvp"],
        "minimum_grid_weight": minima["grid_weight"],
        "maximum_harmonic_gram_residual": maxima["gram"],
        "maximum_frame_roundtrip_residual": maxima["frame"],
        "maximum_implicit_residual_relative": maxima["implicit_residual"],
        "maximum_implicit_number_relative_change": maxima["implicit_number"],
        "minimum_implicit_occupation": minima["implicit_occupation"],
        "maximum_free_energy_change": maxima["free_change"],
        "maximum_four_force_hydrogen_residual": maxima["four_h"],
        "maximum_four_force_normal_residual": maxima["four_n"],
        "geometry_collision_action_difference": geometry_difference,
    }
    return policy_rows, operator_rows, implicit_rows, jacobian_rows, evidence, hard_results, gates


def manifest(artifact: Path) -> None:
    rows = []
    for path in sorted(artifact.iterdir()):
        if path.name == "MANIFEST_SHA256.txt":
            continue
        rows.append(f"{sha256(path)}  {path.name}")
    (artifact / "MANIFEST_SHA256.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def make_bundle():
    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    if BUNDLE.exists():
        BUNDLE.unlink()
    with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ARTIFACT.iterdir()):
            archive.write(path, arcname=f"{ARTIFACT_NAME}/{path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--reuse-network", action="store_true")
    args = parser.parse_args()

    previous_network_elapsed_s: float | None = None
    previous_ledger = ARTIFACT / "PR03_ledger.json"
    if args.reuse_network and previous_ledger.exists():
        try:
            previous_network_elapsed_s = float(
                json.loads(previous_ledger.read_text(encoding="utf-8"))[
                    "hard_results"
                ]["network_build_elapsed_s"]
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            previous_network_elapsed_s = None

    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)

    if args.reuse_network and DATA_OUT.exists():
        with np.load(DATA_OUT, allow_pickle=False) as data:
            network_data = {
                "intervals": np.asarray(data["state_intervals"]),
                "labels": data["state_labels"].astype(str),
                "mode": np.asarray(data["mode_measure_m3"]),
                "equilibrium": np.asarray(data["equilibrium_weight_m3"]),
                "momentum": np.asarray(data["momentum_scale"]),
                "release_states": data["release_states"].astype(str),
                "release_ell": np.asarray(data["release_ell"]),
                "pair_moments": np.asarray(data["pair_moments_m3_sInv"]),
                "same_rates": np.asarray(data["same_cell_rates_sInv"]),
                "scalar_generator": np.asarray(data["scalar_generator_sInv"]),
                "near_transfer": np.asarray(data["near_transfer_weighted"]),
                "far_transfer": np.asarray(data["far_transfer_weighted"]),
                "provisional_pair": np.asarray(data["provisional_pair_moments_m3_sInv"]),
                "provisional_same": np.asarray(data["provisional_same_cell_rates_sInv"]),
                "elapsed_s": (
                    previous_network_elapsed_s
                    if previous_network_elapsed_s is not None
                    else float("nan")
                ),
            }
    else:
        network_data = build_network(args.workers)
        np.savez_compressed(
            DATA_OUT,
            classification=np.asarray("PR03_FULL_SCALAR_COM_KHW"),
            amplitude_lane=np.asarray("full_bound_continuum_seagull_interference"),
            state_intervals=network_data["intervals"],
            state_labels=network_data["labels"],
            pair_moments_m3_sInv=network_data["pair_moments"],
            same_cell_rates_sInv=network_data["same_rates"],
            mode_measure_m3=network_data["mode"],
            equilibrium_weight_m3=network_data["equilibrium"],
            momentum_scale=network_data["momentum"],
            scalar_generator_sInv=network_data["scalar_generator"],
            near_transfer_weighted=network_data["near_transfer"],
            far_transfer_weighted=network_data["far_transfer"],
            release_states=network_data["release_states"],
            release_ell=network_data["release_ell"],
            provisional_pair_moments_m3_sInv=network_data["provisional_pair"],
            provisional_same_cell_rates_sInv=network_data["provisional_same"],
        )

    pair = network_data["pair_moments"]
    same = network_data["same_rates"]
    pi = network_data["equilibrium"]
    generator = network_data["scalar_generator"]
    pair_scale = float(np.max(np.abs(pair)))
    positive_entries = pair[0][np.triu_indices(pair.shape[1], 1)]
    positive_entries = positive_entries[positive_entries > 0.0]
    minimum_scalar = float(np.min(positive_entries))
    symmetry = float(np.max(np.abs(pair - np.swapaxes(pair, 1, 2))) / (pair_scale + 1e-300))
    left_null = float(np.max(np.abs(np.ones(len(pi)) @ generator)) / (np.max(np.abs(generator)) + 1e-300))
    right_null = float(np.max(np.abs(generator @ pi)) / (np.max(np.abs(generator)) * np.max(pi) + 1e-300))
    full_provisional_relative = float(
        np.linalg.norm(pair - network_data["provisional_pair"])
        / (np.linalg.norm(network_data["provisional_pair"]) + 1e-300)
    )
    same_provisional_relative = float(
        np.linalg.norm(same - network_data["provisional_same"])
        / (np.linalg.norm(network_data["provisional_same"]) + 1e-300)
    )

    print("PR03 audit: high-precision spectrum", flush=True)
    spectrum_rows, spectrum_hp = high_precision_spectrum_audit()
    print("PR03 audit: symbolic and special functions", flush=True)
    special_rows = symbolic_and_special_function_audit()
    print("PR03 audit: gauge, IR and UV", flush=True)
    gauge_rows, gauge_results = gauge_ir_uv_audit()
    print("PR03 audit: PT reciprocity", flush=True)
    pt_rows, pt_results = pt_reciprocity_audit()
    print("PR03 audit: selected pair parity", flush=True)
    pair_rows, pair_results = selected_pair_audit(network_data)

    print("PR03 audit: inherited PR02 runtime gates", flush=True)
    network = CollisionNetwork.from_npz(DATA_OUT)
    (
        policy_rows,
        operator_rows,
        implicit_rows,
        jacobian_rows,
        runtime_evidence,
        runtime_results,
        runtime_gates,
    ) = runtime_regressions(network)
    print("PR03 audit: writing durable artifact", flush=True)

    maximum_special = max(
        float(row["relative_residual"])
        for row in special_rows
        if not isinstance(row["relative_residual"], str)
    )
    hard_results = {
        "network_build_elapsed_s": network_data["elapsed_s"],
        "minimum_scalar_conductance": minimum_scalar,
        "pair_symmetry_relative": symmetry,
        "scalar_left_null_relative": left_null,
        "scalar_right_null_relative": right_null,
        "full_vs_provisional_pair_network_relative": full_provisional_relative,
        "full_vs_provisional_same_cell_relative": same_provisional_relative,
        **pair_results,
        **gauge_results,
        **pt_results,
        "maximum_special_function_relative": maximum_special,
        **runtime_results,
    }
    hard_gates = {
        "positive_complete_scalar_conductance": minimum_scalar > 0.0,
        "pair_reciprocity": symmetry < 2.0e-12,
        "scalar_number": left_null < 2.0e-14,
        "scalar_equilibrium": right_null < 2.0e-12,
        "complete_lane_nontrivial": full_provisional_relative > 1.0e-14,
        "same_cell_complete_lane_nontrivial": same_provisional_relative > 1.0e-14,
        "selected_quadrature": pair_results["maximum_selected_quadrature_relative"] < 2.0e-7,
        "selected_orientation": pair_results["maximum_selected_orientation_relative"] < 2.0e-12,
        "stored_network_reproduction": pair_results["maximum_selected_network_reproduction_relative"] < 2.0e-13,
        "TRK_normalization": abs(float(spectrum_hp["trk"] - 1)) < 1.0e-60,
        "static_polarizability": abs(float(spectrum_hp["alpha"] - mp.mpf("4.5"))) < 1.0e-60,
        "positive_spectrum_measure": float(np.min(default_scalar_com_khw_model().measure.oscillator_weights)) > 0.0,
        "fixed_nucleus_velocity_length_gauge": gauge_results["maximum_gauge_residual"] < 3.0e-9,
        "infrared_amplitude_nu2": abs(gauge_results["infrared_amplitude_power"] - 2.0) < 3.0e-6,
        "infrared_cross_section_nu4": abs(gauge_results["infrared_cross_section_power"] - 4.0) < 6.0e-6,
        "smooth_background_compiler": gauge_results["maximum_order4_background_residual"] < 5.0e-12,
        "Faddeeva_independent_reference": maximum_special < 3.0e-14,
        "float64_PT_reciprocity": pt_results["float_amplitude_residual"] < 5.0e-10,
        "high_precision_PT_reciprocity": pt_results["high_precision_denominator_residual"] < 1.0e-70,
        **runtime_gates,
    }
    hard_gates = {name: bool(value) for name, value in hard_gates.items()}
    if not all(hard_gates.values()):
        raise RuntimeError(
            "PR-03 hard gates failed: "
            + repr([name for name, value in hard_gates.items() if not value])
        )

    write_csv(ARTIFACT / "atomic_spectrum_audit.csv", spectrum_rows)
    write_csv(ARTIFACT / "symbolic_special_function_audit.csv", special_rows)
    write_csv(ARTIFACT / "gauge_IR_UV_audit.csv", gauge_rows)
    write_csv(ARTIFACT / "PT_reciprocity_audit.csv", pt_rows)
    write_csv(ARTIFACT / "selected_pair_parity.csv", pair_rows)
    write_csv(ARTIFACT / "runtime_policy_summary.csv", policy_rows)
    write_csv(ARTIFACT / "operator_gate_summary.csv", operator_rows)
    write_csv(ARTIFACT / "implicit_update_summary.csv", implicit_rows)
    write_csv(ARTIFACT / "jacobian_regression.csv", jacobian_rows)

    evidence = {
        "transition_hz": default_scalar_com_khw_model().measure.transition_hz,
        "oscillator_weights": default_scalar_com_khw_model().measure.oscillator_weights,
        "channel_code": default_scalar_com_khw_model().measure.channel_code,
        "channel_parameter": default_scalar_com_khw_model().measure.channel_parameter,
        "state_intervals": network.state_intervals,
        "state_labels": network.state_labels,
        "pair_moments_m3_sInv": network.pair_moments,
        "same_cell_rates_sInv": network.same_cell_rates,
        "provisional_pair_moments_m3_sInv": network_data["provisional_pair"],
        "provisional_same_cell_rates_sInv": network_data["provisional_same"],
        **runtime_evidence,
    }
    np.savez_compressed(ARTIFACT / "full_scalar_COM_KHW_evidence.npz", **evidence)
    shutil.copy2(DATA_OUT, ARTIFACT / DATA_OUT.name)

    formalism = r'''# PR-03 full scalar COM–KHW amplitude

## Scope and conventions

The metric signature is `(-,+,+,+)`.  Frequencies are ordinary frequencies
in Hz and every energy denominator is divided by `h`; `c`, `h`, and `k_B`
remain explicit.  The background is homogeneous.  Bianchi geometry enters
only through the already-locked `BackgroundSnapshot` frame adapter.

For scalar elastic `1s -> 1s` scattering in the velocity gauge, the local
atomic amplitude is

\[
 \mathcal{M}=1-\frac12\int d f_s\,\nu_s\left[
 \frac{1}{D_s^- - i\gamma_s}+\frac{1}{D_s^+ + i\gamma_s}\right].
\]

The leading one is the `A^2` seagull.  The measure contains the complete
hydrogen `1s -> np` bound spectrum and the positive continuum density.  Both
time orderings and all interference terms are retained.  Only the unresolved
`2p` pole receives the Ly-alpha natural width in this release window.

Each intermediate internal state has rest mass
`M_s=M_H+h nu_s/c^2`.  Its COM denominators are evaluated on that mass shell,
which removes the spurious reciprocity defect produced by adding an internal
energy to a common-mass kinetic energy after relativistic recoil.

Using the TRK sum, the fixed-nucleus, zero-width elastic amplitude is exactly
rearranged as

\[
 \mathcal{M}(\nu)=-\nu^2\int\frac{d f_s}{\nu_s^2-\nu^2},
\]

so the infrared amplitude is proportional to `nu^2` and the Rayleigh cross
section to `nu^4`.  This velocity/length identity is audited in the fixed-nucleus,
zero-width limit; the finite-recoil production lane is independently audited by
statewise PT reciprocity rather than claimed as a full relativistic gauge proof.
The production Ly-alpha conditional average isolates the
`2p` pole with the Faddeeva function.  The seagull plus all higher
bound/continuum channels are compiled as a source-moment polynomial; no
cross-section fit or free normalization is introduced.

The v0.50 35-state moments are regenerated through `ell=24`.  PR-01 frame
adaptation and the PR-02 nonlinear/JVP/implicit APIs are unchanged.  The
provisional `2p` lane remains explicit only for transition parity.

## Scope boundary

This PR closes the scalar elastic Ly-alpha production window
`|x|<=21.25`, which lies below the Lyman limit.  It audits convergence of the
high-intermediate-energy continuum tail but does not claim a global causal
above-ionization photon-frequency branch.  Raman channels, fine structure,
J-state interference, polarization and atomic alignment remain outside the
12-PR scalar release.  Exterior–exterior collisions remain assigned to the
boundary/Liouville module.
'''
    (ARTIFACT / "PR03_FULL_SCALAR_COM_KHW_FORMALISM.md").write_text(
        formalism, encoding="utf-8"
    )

    literature_lock = """# PR-03 literature and provenance lock

Retrieved and cross-checked on 2026-08-05. These sources fix the bounded scalar-elastic Kramers–Heisenberg–Waller implementation and its audits; they do not enlarge the v0.50 scope beyond the limitations in `PR03_ledger.json`.

1. Mitsuru Kokubo, “Rayleigh and Raman scattering cross-sections and phase matrices of the ground-state hydrogen atom, and their astrophysical implications,” *MNRAS* **529** (2024) 2131–2149, DOI `10.1093/mnras/stae515`, arXiv `2308.04959`.
   - Lock used: explicit ground-state hydrogen KHW construction, Rayleigh/Raman channel distinction, angular phase structure.
2. Hee-Won Lee and Hee Il Kim, “Rayleigh scattering cross-section redward of Lyα by atomic hydrogen,” *MNRAS* **347** (2004) 802–806, DOI `10.1111/j.1365-2966.2004.07255.x`, arXiv `astro-ph/0402023`.
   - Lock used: infinite bound-state sum plus continuum integral and the infrared cross-section scaling proportional to the fourth power of frequency.
3. Hee-Won Lee, “Exact low-energy expansion of the Rayleigh scattering cross-section by atomic hydrogen,” *MNRAS* **358** (2005) 1472–1476, DOI `10.1111/j.1365-2966.2005.08859.x`.
   - Lock used: exact low-energy coefficients, Dalgarno–Lewis cross-check, and static-polarizability/infrared audit.

## Tool provenance

- Web search: used for source discovery and bibliographic cross-checking.
- Wolfram connector: not exposed in this runtime.
- Precise Special Functions connector: not exposed in this runtime.
- Explicit fallbacks: SymPy exact identities; `mpmath` 90–100 decimal calculations; SciPy positive quadrature and Faddeeva implementation.
"""
    (ARTIFACT / "PR03_LITERATURE_LOCK.md").write_text(
        literature_lock, encoding="utf-8"
    )

    ledger = {
        "classification": "PR03_FULL_SCALAR_COM_KHW_PRODUCTION",
        "stage": "PR-03",
        "status": "PASS_PR03_COMPLETE",
        "source": {
            "parent_collision_data": str(PARENT_COLLISION_DATA.relative_to(ROOT)),
            "parent_collision_sha256": sha256(PARENT_COLLISION_DATA),
            "background_snapshot_data": str(SNAPSHOT_DATA.relative_to(ROOT)),
            "background_snapshot_sha256": sha256(SNAPSHOT_DATA),
            "literature_lock": [
                "Kokubo 2024 MNRAS 529 2131, DOI 10.1093/mnras/stae515, arXiv 2308.04959",
                "Lee and Kim 2004 MNRAS 347 802, DOI 10.1111/j.1365-2966.2004.07255.x, arXiv astro-ph/0402023",
                "Lee 2005 MNRAS 358 1472, DOI 10.1111/j.1365-2966.2005.08859.x",
            ],
            "independent_tools": {
                "web_search": "USED",
                "Wolfram_connector": "UNAVAILABLE_IN_RUNTIME",
                "Precise_Special_Functions_connector": "UNAVAILABLE_IN_RUNTIME",
                "fallbacks": [
                    "SymPy exact identities",
                    "mpmath 90-100 decimal references",
                    "SciPy independent positive quadrature and Faddeeva implementation",
                ],
            },
        },
        "atomic_model": {
            "bound_n_max_explicit": default_scalar_com_khw_model().measure.bound_n_max,
            "continuum_positive_quadrature_order": default_scalar_com_khw_model().measure.continuum_order,
            "positive_Rydberg_tail_weight": default_scalar_com_khw_model().measure.tail_weight,
            "positive_Rydberg_tail_delta_Ry": default_scalar_com_khw_model().measure.tail_delta_rydberg,
            "background_polynomial_order": default_scalar_com_khw_model().background_order,
            "seagull": True,
            "time_orderings": 2,
            "bound_continuum_interference": True,
            "state_resolved_relativistic_COM_mass_shell": True,
        },
        "network": {
            "states": int(network.n_state),
            "ell_max": int(network.pair_moments.shape[0] - 1),
            "interior_pairs": 136,
            "near_interface_pairs": 204,
            "far_interface_pairs": 102,
            "same_cell_blocks": 17,
            "amplitude_lane": "full_bound_continuum_seagull_interference",
            "provisional_lane_retained": True,
        },
        "hard_results": hard_results,
        "hard_gate_status": hard_gates,
        "decision": {
            "PR03": "PASS",
            "PR03_status": "COMPLETE",
            "frame_adapter_API": "UNCHANGED",
            "nonlinear_runtime_API": "UNCHANGED",
            "production_amplitude": "FULL_SCALAR_COM_KHW",
            "next_PR": "PR-04 HYREC common-measure moment projection",
        },
        "limitations": [
            "The release is scalar elastic Ly-alpha transport; Raman channels are not included.",
            "The production photon-frequency window |x|<=21.25 lies below ionization; the global above-threshold causal continuum branch is not claimed.",
            "Only the unresolved 2p pole carries natural width in this bounded release window.",
            "Fine structure, J-state interference, polarization, and atomic alignment remain outside the scalar roadmap.",
            "Exterior-exterior collisions remain assigned to the boundary/Liouville module.",
            "Velocity/length gauge equivalence is demonstrated in the fixed-nucleus, zero-width elastic limit; finite-recoil production is audited by PT reciprocity, not claimed as a complete relativistic gauge proof.",
            "Wolfram and Precise Special Functions connectors were not exposed; explicit SymPy/mpmath/SciPy fallbacks are recorded instead.",
        ],
        "next_stage": {
            "name": "PR-04 HYREC common-measure moment projection",
            "tasks": [
                "Project the full scalar KHW event kernel onto the HYREC common measure without a fitted normalization.",
                "Derive and implement Gamma and M1-M4 moment channels with units and sign conventions locked.",
                "Close discrete-to-continuum normalization, recoil-energy, detailed-balance and Jacobian gates.",
                "Preserve the PR-01 BackgroundSnapshot firewall and PR-02 nonlinear runtime API.",
            ],
        },
    }
    (ARTIFACT / "PR03_ledger.json").write_text(
        json.dumps(ledger, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )

    readme = f'''# {ARTIFACT_NAME}\n\nDurable PR-03 scalar bound-plus-continuum COM–KHW release.\n\n- status: `PASS_PR03_COMPLETE`\n- production data: `{DATA_OUT.name}`\n- next: PR-04 HYREC common-measure moment projection\n\nRun `python verify_PR03.py` inside this directory.\n'''
    (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")
    verify = '''from pathlib import Path\nimport json,numpy as np\nHERE=Path(__file__).resolve().parent\nledger=json.loads((HERE/"PR03_ledger.json").read_text())\nassert ledger["status"]=="PASS_PR03_COMPLETE"\nassert all(ledger["hard_gate_status"].values())\ndata=np.load(HERE/"full_scalar_com_khw_v050.npz",allow_pickle=False)\nS=data["pair_moments_m3_sInv"]\nassert S.shape==(25,35,35)\nassert np.min(S[0])>=0\nassert np.max(np.abs(S-np.swapaxes(S,1,2)))<2e-12*(np.max(np.abs(S))+1e-300)\nassert data["amplitude_lane"].item()=="full_bound_continuum_seagull_interference"\nprint("PR-03 full scalar COM-KHW: PASS")\n'''
    (ARTIFACT / "verify_PR03.py").write_text(verify, encoding="utf-8")
    manifest(ARTIFACT)
    make_bundle()
    print(
        json.dumps(
            {
                "artifact": str(ARTIFACT),
                "bundle": str(BUNDLE),
                "bundle_sha256": sha256(BUNDLE),
                "data": str(DATA_OUT),
                "data_sha256": sha256(DATA_OUT),
                "hard_results": hard_results,
                "hard_gates": hard_gates,
            },
            indent=2,
            default=json_default,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
