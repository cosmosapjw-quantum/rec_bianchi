from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import tempfile
import zipfile
import hashlib
import os
import shutil
import subprocess
import sys

import numpy as np
import pytest
from scipy.constants import h

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    H_PLANCK_EV_S,
    ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
    ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
    safe_extract_original_hyrec_archive,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    OriginalHyRecBoundarySample,
    boundary_sample_reconstruction_residuals,
    parse_original_hyrec_boundary_snapshot_csv,
)


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
INSTRUMENTER = ROOT / "scripts/c_harness/instrument_original_hyrec_pr04c.py"


def _load_instrumenter():
    specification = importlib.util.spec_from_file_location("instrument_pr04c", INSTRUMENTER)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load PR04C instrumenter")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_instrumenter_adds_three_guarded_targets_to_canonical_source() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        source = archive.read("HyRec/hydrogen.c").decode("utf-8")
    instrumented = _load_instrumenter().instrument_hydrogen_source(source)
    assert instrumented.count("#ifdef PR04C_DIAGNOSTICS") >= 5
    assert "1300." in instrumented
    assert "1100." in instrumented
    assert "900." in instrumented
    assert "PR04C_DIAGNOSTIC_DIR" in instrumented
    assert source in instrumented or len(instrumented) > len(source)


def test_boundary_sample_reconstructs_number_and_energy_fluxes() -> None:
    energy_eV = 10.2
    fsR = 1.0
    meR = 1.0
    frequency_Hz = energy_eV / H_PLANCK_EV_S
    H_s_inv = 5.0e-14
    mode = 3.0e13
    y0 = 2.0e-13
    y1 = 4.0e-13
    fraction = 0.25
    distortion = (1.0 - fraction) * y0 + fraction * y1
    blackbody = 1.0e-17
    total = blackbody + distortion
    sample = OriginalHyRecBoundarySample(
        side="blue",
        interface_x=21.25,
        doppler_width_eV=1.0e-4,
        interface_energy_eV=energy_eV,
        interface_frequency_Hz=frequency_Hz,
        source_index=2,
        source_energy_eV=10.2002,
        lna_query=-7.0,
        history_index_left=10,
        history_index_right=11,
        interpolation_fraction=fraction,
        history_value_left=y0,
        history_value_right=y1,
        distortion_occupation=distortion,
        blackbody_occupation=blackbody,
        total_occupation=total,
        mode_factor_per_H=mode,
        distortion_number_flux_per_H_s=H_s_inv * mode * distortion,
        reference_number_flux_per_H_s=H_s_inv * mode * blackbody,
        total_number_flux_per_H_s=H_s_inv * mode * total,
        distortion_photon_energy_flux_W_per_H=h * frequency_Hz * H_s_inv * mode * distortion,
        reference_photon_energy_flux_W_per_H=h * frequency_Hz * H_s_inv * mode * blackbody,
        total_photon_energy_flux_W_per_H=h * frequency_Hz * H_s_inv * mode * total,
    )
    residuals = boundary_sample_reconstruction_residuals(
        sample,
        H_s_inv=H_s_inv,
        nH_cm3=250.0,
        TR_eV_rescaled=0.25,
        fsR=fsR,
        meR=meR,
        energy_grid_eV=np.asarray([10.1, 10.15, 10.2002, 10.3]),
        check_blackbody=False,
        check_mode_factor=False,
    )
    assert max(residuals.values()) < 1.0e-14
    assert sample.total_number_flux_per_H_s > 0.0
    assert sample.total_photon_energy_flux_W_per_H > 0.0


def test_boundary_sample_rejects_nonminimal_source_or_bad_fraction() -> None:
    base = dict(
        side="red",
        interface_x=-21.25,
        doppler_width_eV=1.0e-4,
        interface_energy_eV=10.2,
        interface_frequency_Hz=10.2 / H_PLANCK_EV_S,
        source_index=2,
        source_energy_eV=10.3,
        lna_query=-7.0,
        history_index_left=10,
        history_index_right=11,
        interpolation_fraction=0.5,
        history_value_left=1.0e-13,
        history_value_right=2.0e-13,
        distortion_occupation=1.5e-13,
        blackbody_occupation=1.0e-17,
        total_occupation=1.5001e-13,
        mode_factor_per_H=3.0e13,
        distortion_number_flux_per_H_s=2.25e-13,
        reference_number_flux_per_H_s=1.5e-17,
        total_number_flux_per_H_s=2.25015e-13,
        distortion_photon_energy_flux_W_per_H=h * (10.2 / H_PLANCK_EV_S) * 2.25e-13,
        reference_photon_energy_flux_W_per_H=h * (10.2 / H_PLANCK_EV_S) * 1.5e-17,
        total_photon_energy_flux_W_per_H=h * (10.2 / H_PLANCK_EV_S) * 2.25015e-13,
    )
    bad_fraction = dict(base)
    bad_fraction["interpolation_fraction"] = 1.2
    with pytest.raises(ValueError, match="fraction"):
        OriginalHyRecBoundarySample(**bad_fraction)

    sample = OriginalHyRecBoundarySample(**base)
    with pytest.raises(ValueError, match="minimal"):
        boundary_sample_reconstruction_residuals(
            sample,
            H_s_inv=5.0e-14,
            nH_cm3=250.0,
            TR_eV_rescaled=0.25,
            fsR=1.0,
            meR=1.0,
            energy_grid_eV=np.asarray([10.1, 10.21, 10.3]),
            check_blackbody=False,
            check_mode_factor=False,
        )



def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.slow
def test_guarded_pr04c_build_emits_three_source_identical_boundary_snapshots(
    tmp_path, binary_hash_is_meaningful
):
    if shutil.which("gcc") is None:
        pytest.skip("gcc unavailable")
    safe_extract_original_hyrec_archive(ARCHIVE, tmp_path)
    source = tmp_path / "HyRec"

    def compile_binary(name: str, diagnostics: bool) -> Path:
        executable = tmp_path / name
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
            command.append("-DPR04C_DIAGNOSTICS")
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
        subprocess.run(command, cwd=source, check=True, capture_output=True)
        return executable

    def execute(executable: Path, output: Path, diagnostic_dir: Path | None = None) -> None:
        environment = os.environ.copy()
        if diagnostic_dir is not None:
            environment["PR04C_DIAGNOSTIC_DIR"] = str(diagnostic_dir)
        with (source / "input.dat").open("rb") as stdin, output.open("wb") as stdout:
            subprocess.run(
                [str(executable)],
                cwd=source,
                env=environment,
                stdin=stdin,
                stdout=stdout,
                stderr=subprocess.DEVNULL,
                check=True,
            )

    canonical = compile_binary("canonical", diagnostics=False)
    canonical_output = tmp_path / "canonical.out"
    execute(canonical, canonical_output)
    # The numerical output is the scientific guarantee and is portable.
    assert _sha256(canonical_output) == ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256
    # The binary hash only means something on the toolchain that pinned it.
    if binary_hash_is_meaningful:
        assert _sha256(canonical) == ORIGINAL_HYREC_PORTABLE_BINARY_SHA256

    subprocess.run(
        [sys.executable, str(INSTRUMENTER), str(source / "hydrogen.c")],
        cwd=ROOT,
        check=True,
    )
    guard_off = compile_binary("guard_off", diagnostics=False)
    guard_off_output = tmp_path / "guard_off.out"
    execute(guard_off, guard_off_output)
    assert _sha256(guard_off) == _sha256(canonical)
    assert _sha256(guard_off_output) == _sha256(canonical_output)

    diagnostic_dir = tmp_path / "snapshots"
    diagnostic_dir.mkdir()
    guard_on = compile_binary("guard_on", diagnostics=True)
    guard_on_output = tmp_path / "guard_on.out"
    execute(guard_on, guard_on_output, diagnostic_dir)
    assert _sha256(guard_on_output) == _sha256(canonical_output)

    current_endpoint_uses = 0
    for target in (1300, 1100, 900):
        snapshot = parse_original_hyrec_boundary_snapshot_csv(
            diagnostic_dir / f"pr04c_z{target}.csv"
        )
        assert snapshot.trajectory.target_z == float(target)
        assert abs(snapshot.trajectory.z - target) < 0.08
        assert tuple(sample.side for sample in snapshot.boundaries) == ("red", "blue")
        for sample in snapshot.boundaries:
            assert sample.history_index_right <= snapshot.trajectory.iz_local
            current_endpoint_uses += int(
                sample.history_index_right == snapshot.trajectory.iz_local
            )
            residuals = boundary_sample_reconstruction_residuals(
                sample,
                H_s_inv=snapshot.trajectory.H_s_inv,
                nH_cm3=snapshot.trajectory.nH_cm3,
                TR_eV_rescaled=snapshot.trajectory.TR_eV_rescaled,
                fsR=snapshot.trajectory.fsR,
                meR=snapshot.trajectory.meR,
                energy_grid_eV=snapshot.trajectory.energy_eV,
            )
            assert max(residuals.values()) < 3.0e-13
            assert sample.total_occupation > 0.0
            assert sample.total_number_flux_per_H_s > 0.0

    # At least one exact interface lies less than one DLNA below its least
    # higher native source.  After the current source step has been solved,
    # source-identical diagnostic interpolation therefore legitimately uses
    # the newly available current endpoint rather than declaring a false
    # history-range failure.
    assert current_endpoint_uses >= 1
