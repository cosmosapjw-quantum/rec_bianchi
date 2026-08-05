from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import numpy as np
import pytest

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    DIFFUSION_START,
    DIFFUSION_STOP,
    NDIFF,
    ORIGINAL_HYREC_ARCHIVE_BYTES,
    ORIGINAL_HYREC_ARCHIVE_ENTRY_COUNT,
    ORIGINAL_HYREC_ARCHIVE_SHA256,
    audit_original_hyrec_archive,
    build_native_diffusion_network,
    central_difference_jvp_residual,
    inferred_log_cell_edges_eV,
    inferred_photon_mode_measure_m3,
    physical_number_map_residual,
    populate_original_hyrec_diffusion,
    read_two_photon_table,
    safe_extract_original_hyrec_archive,
    schur_reduce_line_centre,
)

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = (
    ROOT
    / "archive"
    / "inputs"
    / "original_hyrec_oct2012"
    / "HyRec_Oct2012.zip"
)
C3B1 = (
    ROOT
    / "archive"
    / "expanded"
    / "Full_Bianchi_HyRec_C3B1_native_sparse_block_v0_27"
)


def _extract_table(tmp_path: Path) -> Path:
    safe_extract_original_hyrec_archive(ARCHIVE, tmp_path)
    return tmp_path / "HyRec" / "two_photon_tables.dat"


def test_original_hyrec_archive_is_byte_locked_and_safe():
    audit = audit_original_hyrec_archive(ARCHIVE)
    assert audit.safe
    assert audit.sha256 == ORIGINAL_HYREC_ARCHIVE_SHA256
    assert audit.size_bytes == ORIGINAL_HYREC_ARCHIVE_BYTES
    assert audit.entry_count == ORIGINAL_HYREC_ARCHIVE_ENTRY_COUNT
    assert audit.file_count == 26
    assert audit.directory_count == 3
    assert audit.total_uncompressed_bytes == 1_002_107


def test_python_diffusion_reconstructs_pinned_native_registry(tmp_path):
    table = read_two_photon_table(_extract_table(tmp_path))
    rates = populate_original_hyrec_diffusion(table, temperature_K=3000.0)
    rows = list(csv.DictReader((C3B1 / "diffusion_detailed_balance.csv").open()))
    expected_up = np.asarray([float(row["Aup_s_inv"]) for row in rows])
    expected_down = np.asarray([float(row["Adn_s_inv"]) for row in rows])
    active = slice(DIFFUSION_START, DIFFUSION_STOP)
    assert np.array_equal(rates.energy_eV[active], table[active, 0])
    assert np.max(np.abs(rates.Aup_s_inv[active] - expected_up)) < 5e-13
    assert np.max(np.abs(rates.Adn_s_inv[active] - expected_down)) < 5e-13
    assert rates.A2p_up_s_inv == pytest.approx(3740.248028270316, rel=2e-15)
    assert rates.A2p_dn_s_inv == pytest.approx(3759.9654428934414, rel=2e-15)


def test_native_proxy_network_closes_balance_moments_schur_and_implicit(tmp_path):
    table = read_two_photon_table(_extract_table(tmp_path))
    rates = populate_original_hyrec_diffusion(table, temperature_K=3000.0)
    network = build_native_diffusion_network(rates)
    scale = np.max(np.abs(network.generator_s_inv))
    assert np.max(np.abs(network.generator_s_inv.sum(axis=0))) / scale < 2e-15
    null_scale = scale * np.max(network.equilibrium_proxy)
    assert np.max(
        np.abs(network.generator_s_inv @ network.equilibrium_proxy)
    ) / null_scale < 2e-15
    for order in range(5):
        exchange = network.proxy_moments_Hz[order] - (
            (-1) ** order
        ) * network.proxy_moments_Hz[order].T
        assert np.max(np.abs(exchange)) / np.max(
            np.abs(network.proxy_moments_Hz[order])
        ) < 4e-15
    assert np.all(network.proxy_moments_Hz[2] >= 0.0)
    assert np.all(network.proxy_moments_Hz[4] >= 0.0)

    reduced = schur_reduce_line_centre(network)
    qscale = np.max(np.abs(reduced.generator_s_inv))
    assert np.max(np.abs(reduced.generator_s_inv.sum(axis=0))) / qscale < 2e-15
    assert reduced.direct_bridge_red_to_blue_s_inv > 0.0
    assert reduced.direct_bridge_blue_to_red_s_inv > 0.0

    state = network.equilibrium_proxy * (
        1.0 + 0.09 * np.sin(np.arange(network.state_count))
    )
    direction = np.cos(np.arange(network.state_count) * 0.37)
    assert central_difference_jvp_residual(
        network.generator_s_inv, state, direction
    ) < 2e-9
    advanced = network.backward_euler(state, dt_s=1e-3)
    assert np.min(advanced) > 0.0
    assert np.sum(advanced) == pytest.approx(np.sum(state), rel=3e-14, abs=1e-40)


def test_native_proxy_is_not_silently_identified_with_physical_photon_measure(tmp_path):
    table = read_two_photon_table(_extract_table(tmp_path))
    rates = populate_original_hyrec_diffusion(table, temperature_K=3000.0)
    network = build_native_diffusion_network(rates)
    reduced = schur_reduce_line_centre(network)
    edges = inferred_log_cell_edges_eV(rates.energy_eV)
    modes = inferred_photon_mode_measure_m3(edges)
    assert edges.shape == (NDIFF + 1,)
    assert modes.shape == (NDIFF,)
    assert np.all(modes > 0.0)
    # Direct Aup/Adn substitution is not a physical finite-volume photon
    # generator: its conserved left measure is one, not the varying mode weight.
    residual = physical_number_map_residual(reduced, modes)
    assert residual > 1e-4
    assert residual < 2e-2


def test_pr04b1_durable_artifact_closes_bounded_stage():
    artifact = (
        ROOT
        / "archive"
        / "expanded"
        / "Full_Bianchi_HyRec_PR04B1_original_HyRec_native_map_v0_52"
    )
    ledger = json.loads((artifact / "PR04B1_ledger.json").read_text())
    assert ledger["status"] == (
        "PASS_PR04B1_ORIGINAL_HYREC_SOURCE_NATIVE_PROXY_MAP_PR04B2_OPEN"
    )
    assert all(ledger["hard_gate_status"].values())
    assert ledger["source_lock"]["archive"]["sha256"] == (
        ORIGINAL_HYREC_ARCHIVE_SHA256
    )
    assert ledger["decision"]["native_raw_rate_substitution"] == "FORBIDDEN"
    assert ledger["decision"]["physical_common_measure_parity"] == (
        "OPEN_FAIL_CLOSED"
    )
    with np.load(
        ROOT / "data" / "original_hyrec_native_v052.npz", allow_pickle=False
    ) as evidence:
        assert evidence["native_generator_sInv"].shape == (NDIFF + 1, NDIFF + 1)
        assert evidence["schur_generator_sInv"].shape == (NDIFF, NDIFF)
        assert np.all(evidence["inferred_photon_mode_measure_m3"] > 0.0)


@pytest.mark.slow
def test_original_c_diffusion_harness_matches_python(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc unavailable")
    safe_extract_original_hyrec_archive(ARCHIVE, tmp_path)
    source = tmp_path / "HyRec"
    harness = ROOT / "scripts" / "c_harness" / "original_hyrec_native_diffusion_harness.c"
    executable = tmp_path / "native_diffusion_harness"
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
    output = subprocess.run(
        [str(executable), "3000"],
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    scalar = {line.split(",")[0]: float(line.split(",")[1]) for line in output[:3]}
    rows = list(csv.DictReader(output[3:]))
    c_up = np.asarray([float(row["Aup_s_inv"]) for row in rows])
    c_down = np.asarray([float(row["Adn_s_inv"]) for row in rows])
    table = read_two_photon_table(source / "two_photon_tables.dat")
    rates = populate_original_hyrec_diffusion(table, 3000.0)
    active = slice(DIFFUSION_START, DIFFUSION_STOP)
    assert np.array_equal(c_up, rates.Aup_s_inv[active])
    assert np.array_equal(c_down, rates.Adn_s_inv[active])
    assert scalar["A2p_up_s_inv"] == pytest.approx(
        rates.A2p_up_s_inv, rel=2e-16
    )
    assert scalar["A2p_dn_s_inv"] == pytest.approx(
        rates.A2p_dn_s_inv, rel=2e-16
    )
