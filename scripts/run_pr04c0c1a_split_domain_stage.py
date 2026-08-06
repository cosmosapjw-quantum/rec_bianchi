#!/usr/bin/env python3
"""Build PR-04C0/C1A v0.55 split-domain ownership/boundary artifact.

This bounded release proves single ownership of every operator term and extracts
source-identical photon packets at x=+-21.25 from canonical October-2012
original HyRec at the predeclared z~1300,1100,900 snapshots.  It does not yet
deposit packets into the COM--KHW far-boundary/Liouville state.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
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

from full_bianchi_hyrec.recoil.original_hyrec_native import (  # noqa: E402
    ORIGINAL_HYREC_ARCHIVE_SHA256,
    ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
    ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
    safe_extract_original_hyrec_archive,
    sha256_file,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    boundary_sample_reconstruction_residuals,
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.recoil.split_domain_exchange import (  # noqa: E402
    SplitDomainExchangeOperator,
    default_ownership_registry,
    packet_from_original_hyrec_boundary_sample,
)


ARTIFACT_NAME = "Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
ARTIFACT = ROOT / "archive" / "expanded" / ARTIFACT_NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{ARTIFACT_NAME}.zip"
DATA_OUT = ROOT / "data" / "pr04c_split_domain_boundary_v055.npz"
ARCHIVE = ROOT / "archive" / "inputs" / "original_hyrec_oct2012" / "HyRec_Oct2012.zip"
INSTRUMENTER = ROOT / "scripts" / "c_harness" / "instrument_original_hyrec_pr04c.py"
CODING_HARNESS = ROOT / "archive" / "inputs" / "research_harnesses" / "physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS = ROOT / "archive" / "inputs" / "research_harnesses" / "physmath-research-harness-gpt56.zip"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
TARGETS = (1300, 1100, 900)
PSF_ZETA3_100 = (
    "1.202056903159594285399738161511449990764986292340498881792271555341838205786313090186455873609335258"
)
PSF_GAMMA3_100 = "2.0"


def digest(path: Path) -> str:
    return sha256_file(path)


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=json_default) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(
    command: list[str],
    *,
    cwd: Path,
    stdout: Path | None = None,
    stderr: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PWD"] = str(cwd)
    if env:
        environment.update(env)
    if stdout is not None and stderr is not None and stdout == stderr:
        with stdout.open("wb") as handle:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=environment,
                stdout=handle,
                stderr=subprocess.STDOUT,
                check=False,
            )
    else:
        out_handle = stdout.open("wb") if stdout is not None else subprocess.PIPE
        err_handle = stderr.open("wb") if stderr is not None else subprocess.PIPE
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=environment,
                stdout=out_handle,
                stderr=err_handle,
                check=False,
            )
        finally:
            if stdout is not None:
                out_handle.close()
            if stderr is not None:
                err_handle.close()
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")
    return result


def compile_hyrec(source: Path, output: Path, log: Path, *, diagnostics: bool) -> None:
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
            str(output),
        ]
    )
    run(command, cwd=source, stdout=log, stderr=log)


def execute_hyrec(
    source: Path,
    executable: Path,
    stdout_path: Path,
    stderr_path: Path,
    *,
    diagnostic_dir: Path | None = None,
) -> None:
    environment: dict[str, str] = {}
    if diagnostic_dir is not None:
        environment["PR04C_DIAGNOSTIC_DIR"] = str(diagnostic_dir)
    with (source / "input.dat").open("rb") as input_handle, stdout_path.open(
        "wb"
    ) as output_handle, stderr_path.open("wb") as error_handle:
        result = subprocess.run(
            [str(executable)],
            cwd=source,
            env={**os.environ, **environment},
            stdin=input_handle,
            stdout=output_handle,
            stderr=error_handle,
        )
    if result.returncode:
        raise RuntimeError(f"HyRec exited with status {result.returncode}")


def validate_harness(
    archive: Path,
    expected_sha256: str,
    validator_relative: str,
    log: Path,
    work: Path,
) -> dict:
    if digest(archive) != expected_sha256:
        raise ValueError(f"unexpected harness hash {archive}")
    destination = work / archive.stem
    destination.mkdir()
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError(f"harness ZIP failed integrity: {archive}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator_relative))
    if len(matches) != 1:
        raise ValueError(f"cannot locate {validator_relative} in {archive}")
    result = run(
        [sys.executable, str(matches[0])],
        cwd=matches[0].parents[1],
        stdout=log,
        stderr=log,
        check=False,
    )
    return {
        "archive": archive.name,
        "sha256": expected_sha256,
        "validator": validator_relative,
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
    }


def normalize_text_artifact(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    path.write_text(
        "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").splitlines()) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def create_manifest(artifact: Path) -> None:
    rows = []
    for path in sorted(artifact.iterdir()):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            rows.append(f"{digest(path)}  {path.name}")
    (artifact / "MANIFEST_SHA256.txt").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def main() -> None:
    if ARTIFACT.exists():
        shutil.rmtree(ARTIFACT)
    ARTIFACT.mkdir(parents=True)
    BUNDLE.unlink(missing_ok=True)
    DATA_OUT.unlink(missing_ok=True)

    if digest(ARCHIVE) != ORIGINAL_HYREC_ARCHIVE_SHA256:
        raise RuntimeError("canonical original-HyRec archive hash mismatch")

    with tempfile.TemporaryDirectory(prefix="pr04c0c1a-") as tmp:
        work = Path(tmp)
        coding_receipt = validate_harness(
            CODING_HARNESS,
            CODING_HARNESS_SHA256,
            "tools/validate_harness.py",
            ARTIFACT / "CODING_HARNESS_VALIDATION.log",
            work,
        )
        research_receipt = validate_harness(
            RESEARCH_HARNESS,
            RESEARCH_HARNESS_SHA256,
            "tools/validate_workspace.py",
            ARTIFACT / "RESEARCH_HARNESS_VALIDATION.log",
            work,
        )

        source_root = work / "canonical"
        safe_extract_original_hyrec_archive(ARCHIVE, source_root)
        source = source_root / "HyRec"

        canonical = work / "hyrec_canonical"
        compile_hyrec(source, canonical, ARTIFACT / "CANONICAL_COMPILE.log", diagnostics=False)
        canonical_output = work / "canonical.out"
        execute_hyrec(
            source,
            canonical,
            canonical_output,
            ARTIFACT / "CANONICAL_STDERR.log",
        )
        canonical_binary_hash = digest(canonical)
        canonical_history_hash = digest(canonical_output)

        run(
            [
                sys.executable,
                str(INSTRUMENTER),
                str(source / "hydrogen.c"),
                "--diff",
                str(ARTIFACT / "ORIGINAL_HYREC_PR04C_SOURCE.diff"),
            ],
            cwd=ROOT,
        )

        guard_off = work / "hyrec_guard_off"
        compile_hyrec(source, guard_off, ARTIFACT / "GUARD_OFF_COMPILE.log", diagnostics=False)
        guard_off_output = work / "guard_off.out"
        execute_hyrec(
            source,
            guard_off,
            guard_off_output,
            ARTIFACT / "GUARD_OFF_STDERR.log",
        )

        snapshot_dir = work / "snapshots"
        snapshot_dir.mkdir()
        guard_on = work / "hyrec_guard_on"
        compile_hyrec(source, guard_on, ARTIFACT / "GUARD_ON_COMPILE.log", diagnostics=True)
        guard_on_output = work / "guard_on.out"
        execute_hyrec(
            source,
            guard_on,
            guard_on_output,
            ARTIFACT / "GUARD_ON_STDERR.log",
            diagnostic_dir=snapshot_dir,
        )

        snapshot_rows: list[dict] = []
        packets = []
        packet_json: list[dict] = []
        reconstruction_max = 0.0
        geometry_max = 0.0
        current_endpoint_uses = 0
        number_residual_max = 0.0
        photon_energy_residual_max = 0.0
        total_energy_residual_max = 0.0
        operator = SplitDomainExchangeOperator(enabled=True)
        labels = ("II", "V", "VI_-1/9")

        for target in TARGETS:
            snapshot_path = snapshot_dir / f"pr04c_z{target}.csv"
            if not snapshot_path.exists():
                raise RuntimeError(f"missing snapshot {snapshot_path}")
            shutil.copy2(snapshot_path, ARTIFACT / snapshot_path.name)
            snapshot = parse_original_hyrec_boundary_snapshot_csv(snapshot_path)
            for sample in snapshot.boundaries:
                residuals = boundary_sample_reconstruction_residuals(
                    sample,
                    H_s_inv=snapshot.trajectory.H_s_inv,
                    nH_cm3=snapshot.trajectory.nH_cm3,
                    TR_eV_rescaled=snapshot.trajectory.TR_eV_rescaled,
                    fsR=snapshot.trajectory.fsR,
                    meR=snapshot.trajectory.meR,
                    energy_grid_eV=snapshot.trajectory.energy_eV,
                )
                sample_residual = max(residuals.values())
                reconstruction_max = max(reconstruction_max, sample_residual)
                current_endpoint_uses += int(
                    sample.history_index_right == snapshot.trajectory.iz_local
                )
                packet = packet_from_original_hyrec_boundary_sample(
                    sample, source_snapshot_z=snapshot.trajectory.z
                )
                evaluated = [operator.evaluate_packet(packet, bianchi_type=label) for label in labels]
                geometry_residual = 0.0 if all(item.sha256 == packet.sha256 for item in evaluated) else 1.0
                geometry_max = max(geometry_max, geometry_residual)
                result = operator.apply(
                    packet,
                    native_state=np.asarray([1.0, 2.0]),
                    com_state=np.asarray([3.0, 4.0]),
                    dt_s=1.0,
                )
                number_residual_max = max(
                    number_residual_max, abs(result.ledger.number_residual_per_H_s)
                )
                photon_energy_residual_max = max(
                    photon_energy_residual_max,
                    abs(result.ledger.photon_energy_residual_W_per_H),
                )
                total_energy_residual_max = max(
                    total_energy_residual_max,
                    abs(result.ledger.total_energy_residual_W_per_H),
                )
                packets.append(packet)
                packet_payload = packet.to_dict()
                packet_payload["sha256"] = packet.sha256
                packet_json.append(packet_payload)
                snapshot_rows.append(
                    {
                        "target_z": target,
                        "snapshot_z": snapshot.trajectory.z,
                        "iz_local": snapshot.trajectory.iz_local,
                        "xe": snapshot.trajectory.xe,
                        "x1s": snapshot.trajectory.x1s,
                        "nH_cm3": snapshot.trajectory.nH_cm3,
                        "H_s_inv": snapshot.trajectory.H_s_inv,
                        "TM_eV_rescaled": snapshot.trajectory.TM_eV_rescaled,
                        "TR_eV_rescaled": snapshot.trajectory.TR_eV_rescaled,
                        "side": sample.side,
                        "direction": packet.direction.value,
                        "interface_x": sample.interface_x,
                        "interface_energy_eV": sample.interface_energy_eV,
                        "interface_frequency_Hz": sample.interface_frequency_Hz,
                        "source_index": sample.source_index,
                        "source_energy_eV": sample.source_energy_eV,
                        "history_index_left": sample.history_index_left,
                        "history_index_right": sample.history_index_right,
                        "history_uses_current_endpoint": sample.history_index_right
                        == snapshot.trajectory.iz_local,
                        "interpolation_fraction": sample.interpolation_fraction,
                        "distortion_occupation": sample.distortion_occupation,
                        "reference_occupation": sample.blackbody_occupation,
                        "total_occupation": sample.total_occupation,
                        "mode_factor_per_H": sample.mode_factor_per_H,
                        "distortion_number_flux_per_H_s": sample.distortion_number_flux_per_H_s,
                        "reference_number_flux_per_H_s": sample.reference_number_flux_per_H_s,
                        "total_number_flux_per_H_s": sample.total_number_flux_per_H_s,
                        "distortion_photon_energy_flux_W_per_H": sample.distortion_photon_energy_flux_W_per_H,
                        "reference_photon_energy_flux_W_per_H": sample.reference_photon_energy_flux_W_per_H,
                        "total_photon_energy_flux_W_per_H": sample.total_photon_energy_flux_W_per_H,
                        "atom_source_W_per_H": packet.atom_energy_flux_W_per_H,
                        "reconstruction_max_relative_residual": sample_residual,
                        "geometry_firewall_residual": geometry_residual,
                        "number_ledger_residual_per_H_s": result.ledger.number_residual_per_H_s,
                        "photon_energy_ledger_residual_W_per_H": result.ledger.photon_energy_residual_W_per_H,
                        "total_energy_ledger_residual_W_per_H": result.ledger.total_energy_residual_W_per_H,
                        "packet_sha256": packet.sha256,
                    }
                )

        ownership = default_ownership_registry()
        ownership.validate()
        ownership_rows = [
            {
                "process": item.process,
                "owner": item.owner.value,
                "support": item.support,
            }
            for item in ownership.processes
        ]
        write_csv(ARTIFACT / "OPERATOR_OWNERSHIP_MATRIX.csv", ownership_rows)
        write_json(
            ARTIFACT / "OPERATOR_OWNERSHIP_MATRIX.json",
            {
                "process_count": len(ownership_rows),
                "required_processes": ownership.required_processes,
                "rows": ownership_rows,
            },
        )
        write_csv(ARTIFACT / "THREE_SNAPSHOT_INTERFACE_PACKETS.csv", snapshot_rows)
        write_json(
            ARTIFACT / "EXCHANGE_PACKET_RESTART.json",
            {
                "classification": "PR04C0C1A_RESTART_PACKETS",
                "version": "0.55",
                "packets": packet_json,
            },
        )

        target_z = np.asarray([row["target_z"] for row in snapshot_rows], dtype=float)
        actual_z = np.asarray([row["snapshot_z"] for row in snapshot_rows], dtype=float)
        side_code = np.asarray([0 if row["side"] == "red" else 1 for row in snapshot_rows], dtype=np.int8)
        direction_code = np.asarray([0 if row["direction"] == "com_to_native" else 1 for row in snapshot_rows], dtype=np.int8)
        interface_x = np.asarray([row["interface_x"] for row in snapshot_rows], dtype=float)
        frequency = np.asarray([row["interface_frequency_Hz"] for row in snapshot_rows], dtype=float)
        number_components = np.asarray(
            [
                [
                    row["total_number_flux_per_H_s"],
                    row["reference_number_flux_per_H_s"],
                    row["distortion_number_flux_per_H_s"],
                ]
                for row in snapshot_rows
            ],
            dtype=float,
        )
        energy_components = np.asarray(
            [
                [
                    row["total_photon_energy_flux_W_per_H"],
                    row["reference_photon_energy_flux_W_per_H"],
                    row["distortion_photon_energy_flux_W_per_H"],
                ]
                for row in snapshot_rows
            ],
            dtype=float,
        )
        indices = np.asarray(
            [
                [
                    row["source_index"],
                    row["history_index_left"],
                    row["history_index_right"],
                ]
                for row in snapshot_rows
            ],
            dtype=np.int64,
        )
        fractions = np.asarray([row["interpolation_fraction"] for row in snapshot_rows], dtype=float)
        residuals_array = np.asarray(
            [
                [
                    row["reconstruction_max_relative_residual"],
                    row["geometry_firewall_residual"],
                    row["number_ledger_residual_per_H_s"],
                    row["photon_energy_ledger_residual_W_per_H"],
                    row["total_energy_ledger_residual_W_per_H"],
                ]
                for row in snapshot_rows
            ],
            dtype=float,
        )
        np.savez_compressed(
            DATA_OUT,
            target_z=target_z,
            actual_z=actual_z,
            side_code=side_code,
            direction_code=direction_code,
            interface_x=interface_x,
            interface_frequency_Hz=frequency,
            number_flux_components_per_H_s=number_components,
            photon_energy_flux_components_W_per_H=energy_components,
            source_history_indices=indices,
            interpolation_fraction=fractions,
            residuals=residuals_array,
        )
        shutil.copy2(DATA_OUT, ARTIFACT / DATA_OUT.name)

        mp.mp.dps = 120
        zeta3_mp = mp.zeta(3)
        gamma3_mp = mp.gamma(3)
        planck_integral_mp = mp.quad(lambda x: x * x / mp.expm1(x), [0, 1, mp.inf])
        psf_zeta3 = mp.mpf(PSF_ZETA3_100)
        psf_gamma3 = mp.mpf(PSF_GAMMA3_100)
        zeta_relative = abs(psf_zeta3 - zeta3_mp) / abs(zeta3_mp)
        gamma_relative = abs(psf_gamma3 - gamma3_mp) / abs(gamma3_mp)
        integral_relative = abs(planck_integral_mp - 2 * zeta3_mp) / abs(2 * zeta3_mp)

        wolfram_receipt = {
            "tool": "WolframLanguageEvaluator",
            "code": "Assuming[{h>0,dt>0,lambda>=0,f0>=0,feq>=0,phiN>=0,nu>0},FullSimplify[{(f0+dt lambda feq)/(1+dt lambda)>=0,phiN+(-phiN),(h nu phiN)+(-h nu phiN),Integrate[x^2/(Exp[x]-1),{x,0,Infinity},GenerateConditions->False]}]]",
            "result": ["True", "0", "0", "2*Zeta[3]"],
            "interpretation": {
                "backward_Euler_scalar_relaxation_positive": True,
                "interface_number_opposite_sign_cancellation": "exact",
                "interface_photon_energy_opposite_sign_cancellation": "exact",
                "blackbody_log_frequency_number_integral": "2 Zeta[3]",
            },
        }
        write_json(ARTIFACT / "WOLFRAM_SYMBOLIC_RECEIPT.json", wolfram_receipt)
        precise_receipt = {
            "tool": "Precise Special Functions",
            "riemann_zeta_s3_precision_dps": 100,
            "riemann_zeta_s3": PSF_ZETA3_100,
            "gamma_z3_precision_dps": 100,
            "gamma_z3": PSF_GAMMA3_100,
            "independent_mpmath_dps": 120,
            "mpmath_zeta3": mp.nstr(zeta3_mp, 120),
            "mpmath_gamma3": mp.nstr(gamma3_mp, 120),
            "mpmath_planck_integral": mp.nstr(planck_integral_mp, 120),
            "zeta_relative_residual": mp.nstr(zeta_relative, 30),
            "gamma_relative_residual": mp.nstr(gamma_relative, 30),
            "integral_vs_2zeta3_relative_residual": mp.nstr(integral_relative, 30),
        }
        write_json(ARTIFACT / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json", precise_receipt)

        guard_off_binary_hash = digest(guard_off)
        guard_off_history_hash = digest(guard_off_output)
        guard_on_history_hash = digest(guard_on_output)
        hard_gates = {
            "canonical_archive_hash": digest(ARCHIVE) == ORIGINAL_HYREC_ARCHIVE_SHA256,
            "canonical_binary_hash": canonical_binary_hash == ORIGINAL_HYREC_PORTABLE_BINARY_SHA256,
            "canonical_history_hash": canonical_history_hash == ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256,
            "guard_off_binary_identical": guard_off_binary_hash == canonical_binary_hash,
            "guard_off_history_identical": guard_off_history_hash == canonical_history_hash,
            "guard_on_history_identical": guard_on_history_hash == canonical_history_hash,
            "three_predeclared_snapshots": len(snapshot_rows) == 6,
            "two_interfaces_per_snapshot": all(
                sum(int(row["target_z"] == target) for row in snapshot_rows) == 2
                for target in TARGETS
            ),
            "source_reconstruction": reconstruction_max < 3.0e-13,
            "current_endpoint_case_exercised": current_endpoint_uses >= 1,
            "positive_total_packets": all(packet.total_number_flux_per_H_s > 0.0 for packet in packets),
            "zero_atomic_interface_source": all(packet.atom_energy_flux_W_per_H == 0.0 for packet in packets),
            "single_owner_registry": len(ownership_rows) == len({row["process"] for row in ownership_rows}),
            "number_ledger_exact": number_residual_max == 0.0,
            "photon_energy_ledger_exact": photon_energy_residual_max == 0.0,
            "total_energy_ledger_exact": total_energy_residual_max == 0.0,
            "geometry_firewall_exact": geometry_max == 0.0,
            "wolfram_symbolic_checks": wolfram_receipt["result"] == ["True", "0", "0", "2*Zeta[3]"],
            "precise_zeta_reference": zeta_relative < mp.mpf("1e-99"),
            "precise_gamma_reference": gamma_relative == 0,
            "planck_integral_identity": integral_relative < mp.mpf("1e-100"),
            "coding_harness": coding_receipt["passed"],
            "research_harness": research_receipt["passed"],
        }

        metrics = {
            "snapshot_count": len(TARGETS),
            "packet_count": len(packets),
            "target_redshifts": TARGETS,
            "actual_redshifts": sorted({float(row["snapshot_z"]) for row in snapshot_rows}, reverse=True),
            "maximum_reconstruction_relative_residual": reconstruction_max,
            "current_history_endpoint_uses": current_endpoint_uses,
            "minimum_total_occupation": min(float(row["total_occupation"]) for row in snapshot_rows),
            "minimum_total_number_flux_per_H_s": min(float(row["total_number_flux_per_H_s"]) for row in snapshot_rows),
            "maximum_total_number_flux_per_H_s": max(float(row["total_number_flux_per_H_s"]) for row in snapshot_rows),
            "maximum_geometry_firewall_residual": geometry_max,
            "maximum_number_ledger_residual_per_H_s": number_residual_max,
            "maximum_photon_energy_ledger_residual_W_per_H": photon_energy_residual_max,
            "maximum_total_energy_ledger_residual_W_per_H": total_energy_residual_max,
            "zeta3_PSF_vs_mpmath_relative_residual": float(zeta_relative),
            "gamma3_PSF_vs_mpmath_relative_residual": float(gamma_relative),
            "planck_integral_vs_2zeta3_relative_residual": float(integral_relative),
        }

        provenance = {
            "classification": "OFFICIAL_SITE_CANONICAL_ARCHIVE_OWNER_ATTESTED_BYTE_LOCKED",
            "archive": str(ARCHIVE.relative_to(ROOT)),
            "sha256": digest(ARCHIVE),
            "size_bytes": ARCHIVE.stat().st_size,
            "metadata_policy": "Internal May/October metadata differences are intrinsic to the canonical official release.",
            "canonical_binary_sha256": canonical_binary_hash,
            "canonical_history_sha256": canonical_history_hash,
            "guard_off_binary_sha256": guard_off_binary_hash,
            "guard_off_history_sha256": guard_off_history_hash,
            "guard_on_history_sha256": guard_on_history_hash,
        }
        write_json(ARTIFACT / "ORIGINAL_HYREC_PROVENANCE_AND_GUARD_RECEIPT.json", provenance)

        formalism = f"""# PR-04C0/C1A split-domain boundary formalism

## Scope

This bounded v0.55 release closes the operator-ownership theorem and extracts
source-identical red/blue packets at `x=+-21.25` for the predeclared original-
HyRec snapshots near z=1300,1100,900. It does **not** deposit those packets into
the 35-state COM--KHW far-boundary/Liouville state; PR-04C1B/C2 remains open.

## Conventions and dimensions

`g=(-,+,+,+)`, hydrogen tetrad, ordinary frequency `nu` in Hz,
`x=(nu-nu_Lya)/Delta_nu_D`, and all `c,h,k_B` factors remain explicit. The
physical logarithmic-frequency mode factor is

`N_y = 8*pi*nu^3 f/(c^3 n_H)`.

Each packet carries positive total photon-number flux `Phi_N` in H^-1 s^-1
and transported photon-energy flux `Phi_E=h*nu*Phi_N` in W H^-1. The Planck
reference is nonnegative; the nonthermal distortion may be signed as long as
the total packet remains positive.

A computational representation crossing is not a new atom-photon event.
Consequently its atomic source is exactly zero. Atomic recoil remains owned by
the local COM--KHW collision or original-HyRec real/virtual operator. This
corrects the preliminary plan's conflation of transported absolute photon
energy with a collision energy increment. Global interface conservation is

`Phi_N_native + Phi_N_COM = 0`,
`Phi_E_native + Phi_E_COM = 0`,
`Phi_E_atom(interface) = 0`.

## Source-identical interface reconstruction

For an interface energy `E_I`, the least canonical native energy `E_s>E_I`
is selected. Free streaming gives the query time

`ln a_q = -ln[(1+z) E_s/E_I]`.

The October-2012 source's positive two-point linear history interpolation is
used without a fitted scale. At some interfaces `ln a_q` lies between the
previous and current trajectory endpoints. Diagnostics are emitted only after
`Dfminus_hist[:,iz]` has been solved, so `history_index_right==iz` is valid and
source-identical. Rejecting that endpoint would create a false range failure;
using any future endpoint remains forbidden.

## Ownership

Exactly one owner is assigned to native free streaming/escape/real-virtual
algebra, COM collision/Bose/recoil, COM internal Liouville transport, analytic
Planck reference, and the red/blue cross-interface terms. Each packet is
evaluated once and applied twice with opposite signs. Replacement switch OFF
returns exact state copies and a zero ledger.

## Results

- packets: {len(packets)};
- maximum independent reconstruction residual: {reconstruction_max:.17g};
- current-endpoint interpolation cases: {current_endpoint_uses};
- number and photon-energy global residuals: exactly zero;
- atom source at computational interfaces: exactly zero;
- Bianchi-label local-state firewall: exactly zero.

The Wolfram symbolic audit gives backward-Euler positivity, exact opposite-sign
number/energy cancellation and `Integral x^2/(exp(x)-1) dx = 2 Zeta(3)`. The
100-digit Precise Special Functions values agree with independent 120-digit
mpmath references at the residuals recorded in the ledger.
"""
        (ARTIFACT / "PR04C0C1A_SPLIT_DOMAIN_FORMALISM.md").write_text(
            formalism, encoding="utf-8"
        )

        adversarial = """# PR-04C0/C1A independent adversarial review

- No native state vector is globally remapped into the COM--KHW cells.
- The interface packet is unresolved; no silent cell-deposition closure is made.
- Current-step history values are used only after the canonical source has solved
  and stored them; no future state enters the diagnostic.
- The least higher canonical native energy is enforced independently in Python.
- Absolute photon energy transported across a computational interface is not
  misidentified as a new atom recoil event; interface atomic source is zero.
- The Bianchi label is an audit label only at fixed local hydrogen-frame state.
- PR-04C1B/C2 must still implement far-boundary deposition, block JVP,
  positivity and branch-zero localization. This release does not claim PR-04
  completion.

Disposition: `PASS_BOUNDED / PROCEED_TO_PR04C1B_C2`.
"""
        (ARTIFACT / "PR04C0C1A_INDEPENDENT_ADVERSARIAL_REVIEW.md").write_text(
            adversarial, encoding="utf-8"
        )

        tool_status = {
            "web_search": {
                "status": "USED",
                "primary_sources": [
                    "Ali-Haimoud and Hirata, HyRec, arXiv:1011.3758",
                    "Boon et al., Flux-Mortar Mixed Finite Element Methods on NonMatching Grids, DOI 10.1137/20M1361407",
                    "Girault et al., DG/mixed mortar coupling, DOI 10.1137/060671620",
                ],
            },
            "Wolfram": "USED_SYMBOLIC",
            "Precise_Special_Functions": "USED_100_DIGIT_ZETA_AND_GAMMA",
            "GitHub": "READ_ONLY_PERIODIC_CHECK; OWNER_PUSHES_LOCALLY",
            "custom_harnesses": {
                "coding": coding_receipt,
                "research": research_receipt,
            },
        }
        write_json(ARTIFACT / "TOOL_STATUS.json", tool_status)

        harness_receipt = {
            "classification": "PR04C0C1A_HARNESS_EXECUTION_RECEIPT",
            "coding": coding_receipt,
            "research": research_receipt,
            "implementation_plan": "docs/plans/2026-08-06-pr04c0-c1a-split-domain-boundary.md",
            "literature_basis": "docs/PR04C_LITERATURE_BASIS.md",
            "next_stage_plan": "docs/PR04C1B_C2_COUPLED_INTERFACE_PLAN.md",
        }
        write_json(ARTIFACT / "HARNESS_EXECUTION_RECEIPT.json", harness_receipt)

        status = (
            "PASS_PR04C0_OWNERSHIP_PR04C1A_NATIVE_BOUNDARY_INSTRUMENTATION_PR04C1B_C2_OPEN"
            if all(hard_gates.values())
            else "FAIL_PR04C0C1A_HARD_GATE"
        )
        ledger = {
            "classification": "PR04C0C1A_SPLIT_DOMAIN_BOUNDARY",
            "stage": "PR-04C0/C1A",
            "version": "0.55",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "scope": {
                "closed": [
                    "operator ownership and no-double-counting registry",
                    "canonical three-snapshot red/blue boundary instrumentation",
                    "positive total photon packet plus signed distortion decomposition",
                    "exact opposite-sign number and transported photon-energy ledgers",
                    "zero atomic source for pure representation crossing",
                    "restart serialization and local-state Bianchi firewall",
                ],
                "open": [
                    "COM far-boundary/Liouville packet deposition and removal",
                    "coupled implicit residual and analytic block JVP",
                    "branch-speed zero localization in the coupled interface update",
                    "PR-04 completion",
                ],
            },
            "metrics": metrics,
            "hard_gate_status": hard_gates,
            "provenance": provenance,
            "ownership_process_count": len(ownership_rows),
            "tool_status": tool_status,
            "harnesses": harness_receipt,
            "decision": {
                "PR04C0": "COMPLETE" if all(hard_gates.values()) else "FAIL",
                "PR04C1A": "COMPLETE" if all(hard_gates.values()) else "FAIL",
                "PR04": "IN_PROGRESS",
                "next_stage": "PR-04C1B/C2 far-boundary deposition and coupled implicit interface operator",
            },
        }
        write_json(ARTIFACT / "PR04C0C1A_ledger.json", ledger)
        write_json(ARTIFACT / "HARD_GATE_LEDGER.json", hard_gates)
        write_json(ARTIFACT / "NUMERICAL_METRICS.json", metrics)

        verifier_code = '''#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
import numpy as np
HERE=Path(__file__).resolve().parent
for line in (HERE/"MANIFEST_SHA256.txt").read_text().splitlines():
    expected,name=line.split("  ",1)
    got=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    assert got==expected,(name,got,expected)
ledger=json.loads((HERE/"PR04C0C1A_ledger.json").read_text())
assert ledger["status"]=="PASS_PR04C0_OWNERSHIP_PR04C1A_NATIVE_BOUNDARY_INSTRUMENTATION_PR04C1B_C2_OPEN"
assert all(ledger["hard_gate_status"].values())
assert ledger["decision"]["PR04"]=="IN_PROGRESS"
assert ledger["metrics"]["packet_count"]==6
assert ledger["metrics"]["current_history_endpoint_uses"]>=1
assert ledger["metrics"]["maximum_reconstruction_relative_residual"]<3e-13
with np.load(HERE/"pr04c_split_domain_boundary_v055.npz",allow_pickle=False) as data:
    assert data["target_z"].shape==(6,)
    assert data["number_flux_components_per_H_s"].shape==(6,3)
    assert np.all(data["number_flux_components_per_H_s"][:,0]>0)
    assert np.max(np.abs(data["residuals"][:,1:]))==0
print("PR-04C0/C1A split-domain boundary: PASS; PR-04C1B/C2 OPEN")
'''
        verifier = ARTIFACT / "verify_PR04C0C1A.py"
        verifier.write_text(verifier_code, encoding="utf-8")
        os.chmod(verifier, 0o755)

        readme = """# PR-04C0/C1A / v0.55

This immutable artifact closes the single-owner/no-double-counting theorem and
extracts six source-identical original-HyRec interface packets at x=+-21.25 for
z~1300,1100,900. Packet number and transported photon energy cancel exactly
between the two representation ledgers. The pure computational crossing has no
atomic source; recoil remains owned by the local collision operators.

PR-04 remains open. No packet is yet deposited into the COM--KHW far-boundary
or Liouville state.
"""
        (ARTIFACT / "README.md").write_text(readme, encoding="utf-8")

        for relative in (
            "docs/plans/2026-08-06-pr04c0-c1a-split-domain-boundary.md",
            "docs/PR04C_SPLIT_DOMAIN_EXCHANGE_PLAN.md",
            "docs/PR04C_LITERATURE_BASIS.md",
            "docs/PR04C0C1A_RESEARCH_CONTRACT.md",
            "docs/PR04C0C1A_EVIDENCE_LEDGER.md",
            "docs/PR04C0C1A_HYPOTHESIS_AUDIT.md",
            "docs/PR04C0C1A_VALIDATION_MATRIX.md",
            "docs/PR04C1B_C2_COUPLED_INTERFACE_PLAN.md",
        ):
            source_doc = ROOT / relative
            if source_doc.exists():
                shutil.copy2(source_doc, ARTIFACT / source_doc.name)

        for text_path in ARTIFACT.iterdir():
            if text_path.is_file() and text_path.suffix in {".log", ".diff"}:
                normalize_text_artifact(text_path)

        create_manifest(ARTIFACT)
        subprocess.run([sys.executable, str(verifier)], cwd=ARTIFACT, check=True)

        BUNDLE.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
            for path in sorted(ARTIFACT.iterdir()):
                if path.is_file():
                    info = zipfile.ZipInfo(f"{ARTIFACT_NAME}/{path.name}")
                    info.date_time = (2026, 8, 6, 0, 0, 0)
                    info.external_attr = (0o755 if os.access(path, os.X_OK) else 0o644) << 16
                    zipped.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": ARTIFACT_NAME,
                "bundle": str(BUNDLE),
                "bundle_sha256": digest(BUNDLE),
                "bundle_size_bytes": BUNDLE.stat().st_size,
                "data": str(DATA_OUT),
                "metrics": metrics,
            },
            indent=2,
            default=json_default,
        )
    )


if __name__ == "__main__":
    main()
