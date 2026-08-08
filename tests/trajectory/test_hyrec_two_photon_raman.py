from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
from scipy.constants import h, k

from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
    A2S_THRESHOLD_EV,
    A3S3D_THRESHOLD_EV,
    A4S4D_THRESHOLD_EV,
    CanonicalTwoPhotonRamanCoupling,
    OriginalHyRecTwoPhotonRamanTable,
    PhysicalTwoPhotonRamanBin,
    TWO_PHOTON_TABLE_SHA256,
)


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def test_canonical_table_is_byte_locked_normalized_and_process_classified():
    table = OriginalHyRecTwoPhotonRamanTable.from_archive(ARCHIVE)
    assert table.source_hashes["two_photon_tables.dat"] == TWO_PHOTON_TABLE_SHA256
    assert table.energy_eV.shape == (311,)
    assert table.integrated_rates_s_inv.shape == (4, 311)
    assert np.sum(table.A2s_s_inv[:140]) == pytest.approx(8.2206, rel=3e-15)
    assert np.all(table.energy_eV[:140] < A2S_THRESHOLD_EV)
    assert np.all(table.energy_eV[140:] > A2S_THRESHOLD_EV)
    assert np.all(table.energy_eV[:271] < A3S3D_THRESHOLD_EV)
    assert np.all(table.energy_eV[271:] > A3S3D_THRESHOLD_EV)
    assert np.all(table.energy_eV < A4S4D_THRESHOLD_EV)
    assert table.process_kind("2s", 139) == "two_photon"
    assert table.process_kind("2s", 140) == "raman"
    assert table.process_kind("3s3d", 270) == "two_photon"
    assert table.process_kind("3s3d", 271) == "raman"
    assert table.process_kind("4s4d", 310) == "two_photon"
    assert set((270, 278, 290, 299, 308, 472, 477)).issubset(table.source_lines)


def test_canonical_coupling_reproduces_source_formula_and_detailed_balance():
    table = OriginalHyRecTwoPhotonRamanTable.from_archive(ARCHIVE)
    temperature_eV = 0.25882399309326415
    coupling = table.evaluate_canonical_coupling(
        radiation_temperature_eV=temperature_eV,
        fsR=1.0,
        meR=1.0,
    )
    indices = np.asarray([0, 139, 140, 270, 271, 310])
    energy = table.energy_eV[indices]
    scale = 1.0

    expected_2s_real_to_virtual = (
        scale
        * table.A2s_s_inv[indices]
        / np.abs(np.expm1((energy - A2S_THRESHOLD_EV) / temperature_eV))
    )
    expected_2s_virtual_to_real = expected_2s_real_to_virtual * np.exp(
        (energy - A2S_THRESHOLD_EV) / temperature_eV
    )
    expected_2p_real_to_virtual = (
        math.exp(-(A3S3D_THRESHOLD_EV - A2S_THRESHOLD_EV) / temperature_eV)
        * table.A3s3d_s_inv[indices]
        / (3.0 * np.abs(np.expm1((energy - A3S3D_THRESHOLD_EV) / temperature_eV)))
        + math.exp(-(A4S4D_THRESHOLD_EV - A2S_THRESHOLD_EV) / temperature_eV)
        * table.A4s4d_s_inv[indices]
        / (3.0 * np.abs(np.expm1((energy - A4S4D_THRESHOLD_EV) / temperature_eV)))
    )
    expected_2p_virtual_to_real = expected_2p_real_to_virtual * 3.0 * np.exp(
        (energy - A2S_THRESHOLD_EV) / temperature_eV
    )

    assert np.allclose(
        coupling.real_to_virtual_s_inv[0, indices],
        expected_2s_real_to_virtual,
        rtol=3e-15,
    )
    assert np.allclose(
        coupling.virtual_to_real_s_inv[0, indices],
        expected_2s_virtual_to_real,
        rtol=3e-15,
    )
    assert np.allclose(
        coupling.real_to_virtual_s_inv[1, indices],
        expected_2p_real_to_virtual,
        rtol=4e-15,
    )
    assert np.allclose(
        coupling.virtual_to_real_s_inv[1, indices],
        expected_2p_virtual_to_real,
        rtol=4e-15,
    )
    assert np.array_equal(
        coupling.Tvr_offdiag_s_inv, -coupling.real_to_virtual_s_inv
    )
    assert np.array_equal(
        coupling.Trv_offdiag_s_inv, -coupling.virtual_to_real_s_inv
    )
    assert np.allclose(
        coupling.virtual_to_real_s_inv[0],
        coupling.real_to_virtual_s_inv[0]
        * np.exp((table.energy_eV - A2S_THRESHOLD_EV) / temperature_eV),
        rtol=4e-15,
        atol=0.0,
    )
    assert np.allclose(
        coupling.virtual_to_real_s_inv[1],
        coupling.real_to_virtual_s_inv[1]
        * 3.0
        * np.exp((table.energy_eV - A2S_THRESHOLD_EV) / temperature_eV),
        rtol=4e-15,
        atol=0.0,
    )


def test_canonical_coupling_analytic_temperature_jvp_matches_centered_difference():
    table = OriginalHyRecTwoPhotonRamanTable.from_archive(ARCHIVE)
    temperature = 0.173
    coupling = table.evaluate_canonical_coupling(
        radiation_temperature_eV=temperature,
        fsR=1.02,
        meR=0.98,
    )
    direction_log_temperature = 0.37
    direction_log_fsR = -0.11
    direction_log_meR = 0.23
    analytic = coupling.jvp(
        d_log_radiation_temperature=direction_log_temperature,
        d_log_fsR=direction_log_fsR,
        d_log_meR=direction_log_meR,
    )
    # A moderately sized log-parameter step avoids subtractive roundoff in the
    # smallest far-wing coefficients while retaining the centered-difference
    # truncation regime.
    eps = 3.0e-5
    plus = table.evaluate_canonical_coupling(
        radiation_temperature_eV=temperature * math.exp(eps * direction_log_temperature),
        fsR=1.02 * math.exp(eps * direction_log_fsR),
        meR=0.98 * math.exp(eps * direction_log_meR),
    ).coefficient_vector_s_inv
    minus = table.evaluate_canonical_coupling(
        radiation_temperature_eV=temperature * math.exp(-eps * direction_log_temperature),
        fsR=1.02 * math.exp(-eps * direction_log_fsR),
        meR=0.98 * math.exp(-eps * direction_log_meR),
    ).coefficient_vector_s_inv
    finite_difference = (plus - minus) / (2.0 * eps)
    scale = np.maximum(np.maximum(np.abs(analytic), np.abs(finite_difference)), 1e-250)
    assert np.max(np.abs(analytic - finite_difference) / scale) < 5e-8


def _planck(frequency_Hz: float, temperature_K: float) -> float:
    z = math.exp(-h * frequency_Hz / (k * temperature_K))
    return z / (1.0 - z)


@pytest.mark.parametrize("process", ["two_photon", "raman"])
def test_physical_two_photon_raman_paired_action_has_lte_planck_null(process):
    temperature = 3000.0
    transition_frequency = 2.6e15
    companion_frequency = 0.7e15
    if process == "two_photon":
        tracked_frequency = transition_frequency - companion_frequency
    else:
        tracked_frequency = transition_frequency + companion_frequency
    degeneracy_ratio = 3.0
    ground_population = 0.76
    upper_population = degeneracy_ratio * ground_population * math.exp(
        -h * transition_frequency / (k * temperature)
    )
    source = PhysicalTwoPhotonRamanBin(
        process=process,
        integrated_rate_s_inv=0.013,
        transition_frequency_Hz=transition_frequency,
        companion_frequency_Hz=companion_frequency,
        tracked_frequency_Hz=tracked_frequency,
        upper_population=upper_population,
        ground_population=ground_population,
        upper_to_ground_degeneracy_ratio=degeneracy_ratio,
    )
    companion = _planck(companion_frequency, temperature)
    tracked = _planck(tracked_frequency, temperature)
    forward, reverse = source.paired_rates(
        companion_occupation=companion,
        tracked_occupation=tracked,
    )
    assert forward >= 0.0
    assert reverse >= 0.0
    assert abs(forward - reverse) / max(forward, reverse, 1e-300) < 8e-15
    assert abs(source.net_action(companion, tracked)) / max(forward, reverse) < 8e-15


def test_physical_two_photon_raman_jvp_matches_centered_difference():
    source = PhysicalTwoPhotonRamanBin(
        process="raman",
        integrated_rate_s_inv=0.027,
        transition_frequency_Hz=2.4e15,
        companion_frequency_Hz=0.35e15,
        tracked_frequency_Hz=2.75e15,
        upper_population=0.012,
        ground_population=0.81,
        upper_to_ground_degeneracy_ratio=3.0,
    )
    companion = 0.031
    tracked = 0.006
    direction = dict(
        d_integrated_rate_s_inv=-0.004,
        d_upper_population=0.003,
        d_ground_population=-0.02,
        d_companion_occupation=0.017,
        d_tracked_occupation=-0.002,
    )
    analytic = source.jvp(
        companion_occupation=companion,
        tracked_occupation=tracked,
        **direction,
    )
    eps = 1e-6
    def shifted(sign: float) -> float:
        shifted_source = PhysicalTwoPhotonRamanBin(
            process="raman",
            integrated_rate_s_inv=source.integrated_rate_s_inv
            + sign * eps * direction["d_integrated_rate_s_inv"],
            transition_frequency_Hz=source.transition_frequency_Hz,
            companion_frequency_Hz=source.companion_frequency_Hz,
            tracked_frequency_Hz=source.tracked_frequency_Hz,
            upper_population=source.upper_population
            + sign * eps * direction["d_upper_population"],
            ground_population=source.ground_population
            + sign * eps * direction["d_ground_population"],
            upper_to_ground_degeneracy_ratio=source.upper_to_ground_degeneracy_ratio,
        )
        return shifted_source.net_action(
            companion + sign * eps * direction["d_companion_occupation"],
            tracked + sign * eps * direction["d_tracked_occupation"],
        )
    finite_difference = (shifted(1.0) - shifted(-1.0)) / (2.0 * eps)
    assert analytic == pytest.approx(finite_difference, rel=2e-9, abs=1e-12)

@pytest.mark.slow
def test_canonical_coupling_matches_original_c_source_for_all_virtual_bins(tmp_path):
    import shutil
    import subprocess

    from full_bianchi_hyrec.trajectory.primitive_rates import (
        OriginalHyRecPrimitiveRateTable,
    )

    if shutil.which("gcc") is None:
        pytest.skip("gcc unavailable")
    source = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE).extract_source_tree(
        tmp_path
    )
    harness = ROOT / "scripts/c_harness/original_hyrec_two_photon_raman_harness.c"
    executable = tmp_path / "original_hyrec_two_photon_raman_harness"
    subprocess.run(
        [
            "gcc",
            "-std=c11",
            "-D_DEFAULT_SOURCE",
            "-O2",
            "-I",
            str(source),
            str(harness),
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
    temperature = 0.25882399309326415
    fsR = 1.013
    meR = 0.987
    output = subprocess.run(
        [str(executable), f"{temperature:.17g}", f"{fsR:.17g}", f"{meR:.17g}"],
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    c_values = np.loadtxt(output.splitlines())
    coupling = OriginalHyRecTwoPhotonRamanTable.from_archive(
        ARCHIVE
    ).evaluate_canonical_coupling(
        radiation_temperature_eV=temperature,
        fsR=fsR,
        meR=meR,
    )
    assert c_values.shape == (311, 6)
    assert np.array_equal(c_values[:, 0].astype(int), np.arange(311))
    assert np.allclose(c_values[:, 1], coupling.real_to_virtual_s_inv[0], rtol=2e-13)
    assert np.allclose(c_values[:, 2], coupling.virtual_to_real_s_inv[0], rtol=2e-13)
    assert np.allclose(c_values[:, 3], coupling.real_to_virtual_s_inv[1], rtol=2e-13)
    assert np.allclose(c_values[:, 4], coupling.virtual_to_real_s_inv[1], rtol=2e-13)
    assert np.allclose(c_values[:, 5], coupling.Trr_diagonal_addition_s_inv.sum(), rtol=2e-13)
