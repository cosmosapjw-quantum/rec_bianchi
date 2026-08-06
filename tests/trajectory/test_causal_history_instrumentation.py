from __future__ import annotations

import csv
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
)


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
INSTRUMENTER = ROOT / "scripts/c_harness/instrument_original_hyrec_pr05b2.py"


def _load_instrumenter():
    specification = importlib.util.spec_from_file_location(
        "instrument_pr05b2", INSTRUMENTER
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load PR-05B2 instrumenter")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_pr05b2_instrumenter_is_guarded_and_deterministic() -> None:
    with zipfile.ZipFile(ARCHIVE) as archive:
        source = archive.read("HyRec/hydrogen.c").decode("utf-8")
    first = _load_instrumenter().instrument_hydrogen_source(source)
    second = _load_instrumenter().instrument_hydrogen_source(source)
    assert first == second
    assert "#ifdef PR05B2_DIAGNOSTICS" in first
    assert "pr05b2_Dfminus_hist.f64" in first
    assert "pr05b2_Dfminus_Ly_hist.f64" in first
    assert "pr05b2_Dfnu_hist.f64" in first
    assert "accepted_count" in first


@pytest.mark.slow
def test_pr05b2_guard_off_is_source_identical_and_guard_on_dumps_complete_history(
    tmp_path: Path,
) -> None:
    if shutil.which("gcc") is None:
        pytest.skip("gcc unavailable")
    with zipfile.ZipFile(ARCHIVE) as archive:
        archive.extractall(tmp_path)
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
        subprocess.run(command, cwd=source, check=True, capture_output=True)
        return executable

    def execute(
        executable: Path,
        output: Path,
        diagnostic_dir: Path | None = None,
    ) -> None:
        environment = os.environ.copy()
        if diagnostic_dir is not None:
            environment["PR05B2_DIAGNOSTIC_DIR"] = str(diagnostic_dir)
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
    assert _sha256(canonical_output) == ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256

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

    diagnostic_dir = tmp_path / "diagnostics"
    diagnostic_dir.mkdir()
    guard_on = compile_binary("guard_on", diagnostics=True)
    guard_on_output = tmp_path / "guard_on.out"
    execute(guard_on, guard_on_output, diagnostic_dir)
    assert _sha256(guard_on_output) == _sha256(canonical_output)

    metadata: dict[str, str] = {}
    with (diagnostic_dir / "pr05b2_history_meta.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        for key, value in csv.reader(handle):
            metadata[key] = value
    assert metadata["schema"] == "PR05B2_SOURCE_HISTORY_RAW_V1"
    count = int(metadata["accepted_count"])
    assert count == int(metadata["iz_current"]) + 1
    assert int(metadata["nvirt"]) == 311
    assert int(metadata["nlyman"]) == 3
    assert (diagnostic_dir / "pr05b2_energy_eV.f64").stat().st_size == 311 * 8
    assert (diagnostic_dir / "pr05b2_Dfminus_hist.f64").stat().st_size == 311 * count * 8
    assert (diagnostic_dir / "pr05b2_Dfminus_Ly_hist.f64").stat().st_size == 3 * count * 8
    assert (diagnostic_dir / "pr05b2_Dfnu_hist.f64").stat().st_size == 311 * count * 8
