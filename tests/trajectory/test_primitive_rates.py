from __future__ import annotations

import math
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.primitive_rates import (
    ALPHA_TABLE_SHA256,
    R2P2S_TABLE_SHA256,
    TWO_PHOTON_TABLE_SHA256,
    OriginalHyRecPrimitiveRateTable,
    detailed_balance_residuals,
)


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
HARNESS = ROOT / "scripts/c_harness/original_hyrec_primitive_rates_harness.c"
TR_EV = 0.25882399309326415
TM_OVER_TR = 0.9999895025729527


def test_primitive_rate_tables_are_byte_locked_and_source_semantics_are_explicit():
    table = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    assert table.source_hashes["Alpha_inf.dat"] == ALPHA_TABLE_SHA256
    assert table.source_hashes["R_inf.dat"] == R2P2S_TABLE_SHA256
    assert table.source_hashes["two_photon_tables.dat"] == TWO_PHOTON_TABLE_SHA256
    assert table.log_alpha.shape == (2, 40, 100)
    assert table.log_R2p2s.shape == (100,)
    assert table.two_photon_rates_s_inv.shape == (4, 311)
    assert table.delta_alpha_semantics == "alpha(Tm,Tr)-alpha(Tr,Tr); not a derivative"
    assert np.sum(table.two_photon_rates_s_inv[1, :140]) == pytest.approx(
        8.2206, rel=3e-15, abs=1e-15
    )


def test_python_adapter_matches_locked_original_c_reference_at_z1100():
    rates = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE).evaluate(
        radiation_temperature_eV_rescaled=TR_EV,
        matter_to_radiation_temperature_ratio=TM_OVER_TR,
    )
    expected = np.asarray(
        [
            2.09937585386526381e-13,
            5.52180134217451934e-13,
            1.60346327119637110e-18,
            5.24383993731017171e-18,
            1.64709560121260836e2,
            1.44406694000861734e2,
            7.77675164480855415e2,
        ]
    )
    observed_cgs = np.asarray(
        [
            rates.alpha_m3_s[0] * 1.0e6,
            rates.alpha_m3_s[1] * 1.0e6,
            rates.delta_alpha_m3_s[0] * 1.0e6,
            rates.delta_alpha_m3_s[1] * 1.0e6,
            rates.beta_s_inv[0],
            rates.beta_s_inv[1],
            rates.R_2p2s_s_inv,
        ]
    )
    assert np.max(np.abs(observed_cgs - expected) / np.maximum(np.abs(expected), 1e-300)) < 5e-13
    assert rates.delta_alpha_m3_s[0] == pytest.approx(
        rates.alpha_m3_s[0] - rates.alpha_equilibrium_m3_s[0], rel=2e-13
    )


def test_analytic_rate_jvp_matches_centered_difference():
    table = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    direction = np.asarray([0.37, -0.23])
    residual = table.central_difference_jvp_residual(
        radiation_temperature_eV_rescaled=0.17,
        matter_to_radiation_temperature_ratio=0.81,
        direction_log_Tr_and_Tm_over_Tr=direction,
        step=2.0e-6,
    )
    assert residual < 2.0e-8


def test_saha_detailed_balance_null_is_dimensionally_closed():
    table = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    rates = table.evaluate(
        radiation_temperature_eV_rescaled=0.2,
        matter_to_radiation_temperature_ratio=1.0,
    )
    residual = detailed_balance_residuals(
        rates,
        n_H_m3=2.4e8,
        x_1s=0.7,
    )
    assert residual.shape == (2,)
    assert np.max(np.abs(residual)) < 5.0e-13


@pytest.mark.slow
def test_original_c_interpolate_rates_matches_python_at_knot_and_off_grid(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc unavailable")
    table = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    source = table.extract_source_tree(tmp_path)
    executable = tmp_path / "primitive_rates_harness"
    subprocess.run(
        [
            "gcc",
            "-std=c11",
            "-D_DEFAULT_SOURCE",
            "-O2",
            "-I",
            str(source),
            str(HARNESS),
            str(source / "hydrogen.c"),
            str(source / "hyrectools.c"),
            "-lm",
            "-o",
            str(executable),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    points = [(TR_EV, TM_OVER_TR), (0.04, 0.1), (0.173, 0.736)]
    for Tr, ratio in points:
        output = subprocess.run(
            [str(executable), f"{Tr:.17g}", f"{ratio:.17g}", "1", "1"],
            cwd=source,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()
        c_values = np.asarray([float(value) for value in output])
        py = table.evaluate(
            radiation_temperature_eV_rescaled=Tr,
            matter_to_radiation_temperature_ratio=ratio,
        )
        py_values = np.concatenate(
            (
                py.alpha_m3_s * 1.0e6,
                py.delta_alpha_m3_s * 1.0e6,
                py.beta_s_inv,
                [py.R_2p2s_s_inv],
            )
        )
        relative = np.abs(py_values - c_values) / np.maximum(np.abs(c_values), 1.0e-300)
        assert np.max(relative) < 2.0e-12
