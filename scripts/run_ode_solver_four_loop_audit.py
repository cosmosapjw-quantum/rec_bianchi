#!/usr/bin/env python3
"""Run the bounded ODE/DAE four-loop implementation audit.

The runner is intentionally local and fail-closed.  It records complete command
output, deterministic numerical probes, source custody, dependency identity,
the uncommitted diff identity, and changed-file hashes in one JSON document.
It does not publish, commit, reseal, or mutate durable stage artifacts.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = str(ROOT / "src")
if SOURCE_DIRECTORY not in sys.path:
    sys.path.insert(0, SOURCE_DIRECTORY)
DEFAULT_OUTPUT = ROOT / "docs/audit/ODE_SOLVER_FOUR_LOOP_RUN_DATA_20260823.json"
OUTPUT_RELATIVE = DEFAULT_OUTPUT.relative_to(ROOT).as_posix()
SOURCE_RECORDS = {
    "physics_specific": (
        Path("/tmp/rec_bianchi_physics_research_record.md"),
        "bbee0d8a3362848aa028d627bd93f84e92fcec7e4c429b8562392224469c15a0",
    ),
    "physics_seeded_harness": (
        Path("/tmp/rec_bianchi_physseed_research_record.md"),
        "36a55288fa60cea297c810d9e17b2a69642675d9a4a2cc99d32f03dca0b853ba",
    ),
    "independent_numerical": (
        Path("/tmp/rec_bianchi_independent_numerical_research.md"),
        "ca38de1658436a81806a9561fca5eb449e75d649f2cd57226944ae18e7571849",
    ),
    "algorithm_seeded_harness": (
        Path("/tmp/rec_bianchi_algoseed_coding_research_record.md"),
        "36a01fab6217e13b6a32d4150caf190d6f114db4531eb03bca6346694337a454",
    ),
    "foundational_inventory": (
        Path("/tmp/rec_bianchi_stiff_dae_research.md"),
        "52f6673d19d5faa473ee5f02e059bf6f95e96efa5a894c6083399fb1db3ea12b",
    ),
}
FIXED_ENVIRONMENT = {
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1",
    "TZ": "UTC",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def audit_environment() -> dict[str, str]:
    env = dict(os.environ)
    env.update(FIXED_ENVIRONMENT)
    source = str(ROOT / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = source if not existing else os.pathsep.join((source, existing))
    return env


def ensure_fixed_runner_environment() -> None:
    """Re-exec before probes if process-start controls are not exact.

    ``PYTHONHASHSEED`` and native thread-pool settings cannot be made reliable
    by mutating ``os.environ`` after interpreter/library startup.  The first
    invocation therefore performs no audit work and replaces itself with an
    exact-environment process when any fixed control differs.
    """

    observed = {name: os.environ.get(name) for name in FIXED_ENVIRONMENT}
    if observed == FIXED_ENVIRONMENT:
        return
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:]]
    os.execve(sys.executable, argv, audit_environment())


def _decode_timeout_stream(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


@dataclass(frozen=True)
class CommandReceipt:
    command_id: str
    argv: list[str]
    cwd: str
    required: bool
    started_at_utc: str
    duration_seconds: float
    exit_code: int | None
    timed_out: bool
    timeout_seconds: float
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return not self.timed_out and self.exit_code == 0


def run_command(
    command_id: str,
    argv: Sequence[str],
    *,
    required: bool,
    timeout_seconds: float,
) -> CommandReceipt:
    started_at = utc_now()
    start = time.perf_counter()
    try:
        result = subprocess.run(
            list(argv),
            cwd=ROOT,
            env=audit_environment(),
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
        exit_code: int | None = int(result.returncode)
        timed_out = False
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        timed_out = True
        stdout = _decode_timeout_stream(exc.stdout)
        stderr = _decode_timeout_stream(exc.stderr)
    return CommandReceipt(
        command_id=command_id,
        argv=list(argv),
        cwd=str(ROOT),
        required=required,
        started_at_utc=started_at,
        duration_seconds=time.perf_counter() - start,
        exit_code=exit_code,
        timed_out=timed_out,
        timeout_seconds=float(timeout_seconds),
        stdout=stdout,
        stderr=stderr,
    )


def git_text(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def changed_file_hashes(output_path: Path) -> dict[str, str]:
    tracked = git_text(
        "diff", "--name-only", "--diff-filter=ACMRTUXB", "HEAD", "--"
    ).splitlines()
    untracked = git_text("ls-files", "--others", "--exclude-standard").splitlines()
    excluded = {output_path.resolve()}
    hashes: dict[str, str] = {}
    for relative in sorted(set(tracked + untracked)):
        path = (ROOT / relative).resolve()
        if path in excluded or not path.is_file():
            continue
        hashes[relative] = sha256_file(path)
    return hashes


def dependency_identity() -> dict[str, object]:
    distributions: dict[str, str | None] = {}
    for name in ("numpy", "scipy", "mpmath", "pytest"):
        try:
            distributions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            distributions[name] = None

    numpy_configuration = ""
    try:
        import numpy as np

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            np.show_config()
        numpy_configuration = buffer.getvalue()
    except Exception as exc:  # pragma: no cover - audit environment failure path
        numpy_configuration = f"UNAVAILABLE: {type(exc).__name__}: {exc}"

    cpu_model = None
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                cpu_model = line.split(":", 1)[1].strip()
                break
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "python_compiler": platform.python_compiler(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_model": cpu_model,
        "distributions": distributions,
        "numpy_configuration": numpy_configuration,
        "fixed_environment_declared": dict(FIXED_ENVIRONMENT),
        "fixed_environment_observed": {
            name: os.environ.get(name) for name in FIXED_ENVIRONMENT
        },
        "fixed_environment_matches": all(
            os.environ.get(name) == value
            for name, value in FIXED_ENVIRONMENT.items()
        ),
    }


def source_record_identity() -> dict[str, object]:
    output: dict[str, object] = {}
    for record_id, (path, expected) in SOURCE_RECORDS.items():
        observed = sha256_file(path) if path.is_file() else None
        output[record_id] = {
            "path": str(path),
            "expected_sha256": expected,
            "observed_sha256": observed,
            "match": observed == expected,
        }
    return output


def probe_transfer_small_optical_depth() -> dict[str, object]:
    import mpmath as mp

    from full_bianchi_hyrec.trajectory.characteristic_angular import (
        constant_coefficient_transfer,
        constant_coefficient_transfer_jvp,
    )

    f_initial = 0.7
    emissivity = 1.3
    travel_time = 2.0
    rows: list[dict[str, float]] = []
    for opacity in (1.0e-6, 1.0e-8, 1.0e-10, 1.0e-20, 0.0):
        value = constant_coefficient_transfer(
            f_initial=f_initial,
            emissivity_s_inv=emissivity,
            opacity_s_inv=opacity,
            travel_time_s=travel_time,
        )
        jvp = constant_coefficient_transfer_jvp(
            f_initial=f_initial,
            emissivity_s_inv=emissivity,
            opacity_s_inv=opacity,
            travel_time_s=travel_time,
            d_opacity_s_inv=1.0,
        )
        with mp.workdps(100):
            f0_mp = mp.mpf(str(f_initial))
            emissivity_mp = mp.mpf(str(emissivity))
            time_mp = mp.mpf(str(travel_time))
            if opacity == 0.0:
                value_reference = f0_mp + emissivity_mp * time_mp
                jvp_reference = -time_mp * f0_mp - mp.mpf("0.5") * emissivity_mp * time_mp**2
            else:
                opacity_mp = mp.mpf(str(opacity))
                attenuation = mp.exp(-opacity_mp * time_mp)
                absorbed = -mp.expm1(-opacity_mp * time_mp)
                value_reference = attenuation * f0_mp + emissivity_mp * absorbed / opacity_mp
                jvp_reference = (
                    -time_mp * attenuation * f0_mp
                    + emissivity_mp
                    * (time_mp * attenuation * opacity_mp - absorbed)
                    / opacity_mp**2
                )
        value_reference_float = float(value_reference)
        jvp_reference_float = float(jvp_reference)
        rows.append(
            {
                "opacity_s_inv": opacity,
                "optical_depth": opacity * travel_time,
                "value": value,
                "value_reference_mpmath_100dps": value_reference_float,
                "value_relative_error": abs(value - value_reference_float)
                / abs(value_reference_float),
                "jvp": jvp,
                "jvp_reference_mpmath_100dps": jvp_reference_float,
                "jvp_relative_error": abs(jvp - jvp_reference_float)
                / abs(jvp_reference_float),
            }
        )
    maximum = max(row["jvp_relative_error"] for row in rows)

    tangents = {
        "d_f_initial": -0.2,
        "d_emissivity_s_inv": 0.4,
        "d_opacity_s_inv": 1.1,
        "d_travel_time_s": -0.3,
    }
    optical_depths = (
        0.0,
        1.0e-30,
        1.0e-24,
        1.0e-20,
        1.0e-16,
        1.0e-12,
        1.0e-10,
        1.0e-8,
        1.0e-6,
        1.0e-4,
        1.0e-3,
        0.01 - 1.0e-12,
        0.01,
        0.01 + 1.0e-12,
        0.1,
        1.0,
        10.0,
        100.0,
        1000.0,
    )
    sweep_rows: list[dict[str, float]] = []
    for optical_depth in optical_depths:
        opacity = optical_depth / travel_time
        value = constant_coefficient_transfer(
            f_initial=f_initial,
            emissivity_s_inv=emissivity,
            opacity_s_inv=opacity,
            travel_time_s=travel_time,
        )
        jvp = constant_coefficient_transfer_jvp(
            f_initial=f_initial,
            emissivity_s_inv=emissivity,
            opacity_s_inv=opacity,
            travel_time_s=travel_time,
            **tangents,
        )
        with mp.workdps(100):
            f0_mp = mp.mpf(str(f_initial))
            emissivity_mp = mp.mpf(str(emissivity))
            opacity_mp = mp.mpf(str(opacity))
            time_mp = mp.mpf(str(travel_time))
            attenuation = mp.exp(-opacity_mp * time_mp)
            if opacity == 0.0:
                source_factor = time_mp
                source_opacity_derivative = -mp.mpf("0.5") * time_mp**2
            else:
                absorbed = -mp.expm1(-opacity_mp * time_mp)
                source_factor = absorbed / opacity_mp
                source_opacity_derivative = (
                    time_mp * attenuation * opacity_mp - absorbed
                ) / opacity_mp**2
            value_reference = attenuation * f0_mp + emissivity_mp * source_factor
            opacity_partial = (
                -time_mp * attenuation * f0_mp
                + emissivity_mp * source_opacity_derivative
            )
            time_partial = attenuation * (
                emissivity_mp - opacity_mp * f0_mp
            )
            jvp_reference = (
                attenuation * mp.mpf(str(tangents["d_f_initial"]))
                + source_factor * mp.mpf(str(tangents["d_emissivity_s_inv"]))
                + opacity_partial * mp.mpf(str(tangents["d_opacity_s_inv"]))
                + time_partial * mp.mpf(str(tangents["d_travel_time_s"]))
            )
        value_reference_float = float(value_reference)
        jvp_reference_float = float(jvp_reference)
        sweep_rows.append(
            {
                "optical_depth": optical_depth,
                "opacity_s_inv": opacity,
                "value": value,
                "value_reference_mpmath_100dps": value_reference_float,
                "value_relative_error": abs(value - value_reference_float)
                / abs(value_reference_float),
                "full_direction_jvp": jvp,
                "full_direction_jvp_reference_mpmath_100dps": jvp_reference_float,
                "full_direction_jvp_relative_error": abs(jvp - jvp_reference_float)
                / max(abs(jvp_reference_float), 1.0e-300),
            }
        )
    maximum_sweep_value_error = max(
        row["value_relative_error"] for row in sweep_rows
    )
    maximum_sweep_jvp_error = max(
        row["full_direction_jvp_relative_error"] for row in sweep_rows
    )
    passed = (
        maximum <= 2.0e-14
        and maximum_sweep_value_error <= 2.0e-14
        and maximum_sweep_jvp_error <= 2.0e-14
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "maximum_jvp_relative_error": maximum,
        "maximum_sweep_primal_relative_error": maximum_sweep_value_error,
        "maximum_sweep_full_direction_jvp_relative_error": maximum_sweep_jvp_error,
        "acceptance_limit": 2.0e-14,
        "rows": rows,
        "full_direction_tangents": tangents,
        "full_direction_sweep_rows": sweep_rows,
    }


def probe_harmonic_grid_identity() -> dict[str, object]:
    import numpy as np

    from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid

    directions = np.asarray(
        [[1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, -1.0, 1.0]]
    ) / math.sqrt(3.0)
    weights = np.ones(4) / 4.0
    grid = HarmonicGrid.from_directions(directions, weights, ell_max=1)
    before = sha256_bytes(grid.directions.tobytes() + grid.synthesis.tobytes())
    directions[0] = np.asarray([1.0, 0.0, 0.0])
    weights[0] = 0.9
    after = sha256_bytes(grid.directions.tobytes() + grid.synthesis.tobytes())
    flag_reversal_rejected = False
    try:
        grid.directions.setflags(write=True)
    except ValueError:
        flag_reversal_rejected = True
    inconsistent_constructor_rejected = False
    try:
        HarmonicGrid(
            grid.directions,
            grid.weights,
            grid.ell_max,
            grid.lm,
            np.zeros_like(grid.synthesis),
            grid.analysis,
            grid.ell_of_mode,
            grid.gram_residual,
        )
    except ValueError:
        inconsistent_constructor_rejected = True
    epsilon = 1.0e-8
    near_rank_directions = np.asarray(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, epsilon],
        ]
    )
    near_rank_directions /= np.linalg.norm(near_rank_directions, axis=1)[:, None]
    near_rank_affine_condition = float(
        np.linalg.cond(
            np.column_stack((np.ones(len(near_rank_directions)), near_rank_directions))
        )
    )
    near_rank_grid_rejected = False
    try:
        HarmonicGrid.from_directions(
            near_rank_directions, np.ones(4), ell_max=1
        )
    except ValueError:
        near_rank_grid_rejected = True
    passed = (
        before == after
        and flag_reversal_rejected
        and inconsistent_constructor_rejected
        and near_rank_grid_rejected
        and math.isfinite(grid.gram_residual)
        and grid.gram_residual <= 1.0e-10
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "primitive_derived_sha256_before_caller_mutation": before,
        "primitive_derived_sha256_after_caller_mutation": after,
        "caller_alias_detached": before == after,
        "write_flag_reversal_rejected": flag_reversal_rejected,
        "inconsistent_raw_constructor_rejected": inconsistent_constructor_rejected,
        "near_rank_grid_rejected": near_rank_grid_rejected,
        "near_rank_grid_epsilon": epsilon,
        "near_rank_affine_basis_condition": near_rank_affine_condition,
        "gram_residual": grid.gram_residual,
        "gram_residual_acceptance_limit": 1.0e-10,
    }


def probe_causal_history_and_ptc() -> dict[str, object]:
    import numpy as np

    from full_bianchi_hyrec.trajectory.causal_history import (
        CharacteristicHistoryGrid,
        FutureHistoryEndpointError,
    )
    from full_bianchi_hyrec.trajectory.pseudotransient_continuation import (
        AcceptedContinuationState,
        ContinuationTransaction,
        PseudoTransientResult,
        solve_pseudotransient,
    )

    eta_start = -8.0
    dlna = 1.0e-3
    eta = eta_start + dlna * np.arange(8)
    grid = CharacteristicHistoryGrid(
        eta=eta,
        source_indices=np.arange(8),
        z_start=math.exp(-eta_start) - 1.0,
        dlna=dlna,
        energy_eV=np.linspace(5.0, 12.7, 311),
        source_hashes={"audit-probe": "0" * 64},
    )
    stencil = grid.locate(eta[4] + 0.75 * dlna)
    values = np.linspace(0.2, 0.9, 8)
    direction = np.linspace(-2.0, 3.0, 8)
    jvp = stencil.jvp(values, direction, delta_eta=0.2 * dlna)
    doubled = stencil.jvp(values, 2.0 * direction, delta_eta=0.4 * dlna)
    homogeneity_error = abs(doubled - 2.0 * jvp)
    one_slice_future_rejected = False
    try:
        grid.locate(eta_start, accepted_count=1)
    except FutureHistoryEndpointError:
        one_slice_future_rejected = True

    digest = lambda label: hashlib.sha256(label.encode("utf-8")).hexdigest()
    source_metadata: dict[str, object] = {"nested": {"values": [1, 2]}}
    parent = AcceptedContinuationState(
        values=np.asarray([2.0]),
        positive_mask=np.asarray([False]),
        accepted_history_count=7,
        history_sha256=digest("history"),
        background_sha256=digest("background"),
        network_sha256=digest("network"),
        interface_sha256=digest("interface"),
        branch_id="BII",
        metadata=source_metadata,
    )
    parent_sha_before = parent.sha256
    source_metadata["nested"]["values"].append(3)  # type: ignore[index,union-attr]
    metadata_source_detached = parent.sha256 == parent_sha_before
    metadata_mutation_rejected = False
    try:
        parent.metadata["forbidden"] = True  # type: ignore[index]
    except TypeError:
        metadata_mutation_rejected = True

    result = solve_pseudotransient(
        parent,
        residual=lambda state: state - 1.0,
        jacobian=lambda state: np.asarray([[1.0]]),
        mass_diagonal=np.asarray([1.0]),
    )
    signed_minima_are_none = bool(result.iterations) and all(
        item.minimum_positive_value is None for item in result.iterations
    )
    restart_sha = sha256_bytes(result.restart_bytes())

    fabricated = PseudoTransientResult(
        parent_sha256=parent.sha256,
        state_values=np.asarray([999.0]),
        converged=True,
        iterations=(),
        final_physical_residual=0.0,
        accepted_history_count=parent.accepted_history_count,
    )
    transaction = ContinuationTransaction(
        parent,
        fabricated,
        admission_metric=lambda state: abs(float(state[0] - 1.0)),
        maximum_admission_residual=1.0e-10,
    )
    fabricated_commit_rejected = False
    try:
        transaction.commit(history_sha256=digest("fabricated"))
    except RuntimeError:
        fabricated_commit_rejected = True

    toctou_result = PseudoTransientResult(
        parent_sha256=parent.sha256,
        state_values=np.asarray([1.0]),
        converged=True,
        iterations=(),
        final_physical_residual=0.0,
        accepted_history_count=parent.accepted_history_count,
    )

    def mutating_metric(candidate_state):
        object.__setattr__(toctou_result, "state_values", np.asarray([999.0]))
        return 0.0

    toctou_transaction = ContinuationTransaction(
        parent,
        toctou_result,
        admission_metric=mutating_metric,
        maximum_admission_residual=1.0e-10,
    )
    toctou_commit_rejected = False
    try:
        toctou_transaction.commit(history_sha256=digest("toctou"))
    except RuntimeError:
        toctou_commit_rejected = True

    passed = all(
        (
            homogeneity_error <= 2.0e-15,
            one_slice_future_rejected,
            metadata_source_detached,
            metadata_mutation_rejected,
            result.converged,
            signed_minima_are_none,
            fabricated_commit_rejected,
            toctou_commit_rejected,
        )
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "fixed_stencil_jvp": jvp,
        "fixed_stencil_doubled_jvp": doubled,
        "jvp_homogeneity_absolute_error": homogeneity_error,
        "one_slice_future_rejected": one_slice_future_rejected,
        "metadata_source_detached": metadata_source_detached,
        "metadata_mutation_rejected": metadata_mutation_rejected,
        "signed_only_ptc_converged": result.converged,
        "signed_only_minima_are_none": signed_minima_are_none,
        "signed_only_restart_sha256": restart_sha,
        "fabricated_commit_rejected": fabricated_commit_rejected,
        "mutating_metric_toctou_commit_rejected": toctou_commit_rejected,
        "mutating_metric_commit_count": toctou_transaction.commit_count,
    }


def probe_adaptive_macro_contracts() -> dict[str, object]:
    import numpy as np

    from full_bianchi_hyrec.trajectory.adaptive_macro import (
        AdaptiveBackwardEulerFailure,
        AdaptiveControllerTolerances,
        AdaptiveTrajectoryContext,
        AdaptiveTrialFailureKind,
        advance_canonical_macro_interval,
    )
    from full_bianchi_hyrec.trajectory.causal_history import (
        AcceptedRadiationHistory,
        CharacteristicHistoryGrid,
        HistoryAppendCandidate,
    )

    @dataclass(frozen=True)
    class Step:
        state_vector: object
        converged: bool
        backward_error: float
        algebraic_residual_relative: float
        minimum_physical_population: float

    dlna = 1.0e-3
    eta_start = -8.0
    eta = eta_start + dlna * np.arange(5)
    history = AcceptedRadiationHistory(
        grid=CharacteristicHistoryGrid(
            eta=eta,
            source_indices=np.arange(5),
            z_start=math.exp(-eta_start) - 1.0,
            dlna=dlna,
            energy_eV=np.linspace(5.0, 12.7, 311),
            source_hashes={"audit-adaptive": "1" * 64},
        ),
        outgoing_virtual=np.zeros((311, 5)),
        outgoing_lyman=np.zeros((3, 5)),
        average_virtual=np.zeros((311, 5)),
        completeness="SYNTHETIC_FULL",
    )

    def candidate(parent: AcceptedRadiationHistory) -> HistoryAppendCandidate:
        return HistoryAppendCandidate(
            accepted_index=parent.accepted_count,
            eta=parent.grid.eta[-1] + parent.grid.dlna,
            outgoing_virtual=np.zeros(311),
            outgoing_lyman=np.zeros(3),
            average_virtual=np.zeros(311),
            parent_sha256=parent.sha256,
        )

    def linear_step(state, width):
        old = np.asarray(state, dtype=float)
        updated = np.array(old, copy=True)
        updated[0] = old[0] / (1.0 + width)
        updated[1] = old[1] - 0.25 * width
        return Step(updated, True, 0.0, 0.0, float(updated[0]))

    fixed_context = AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.asarray([1.0, 0.25]),
        accepted_history=history,
        controller_step=dlna,
        tolerances=AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=dlna,
            maximum_step=dlna,
        ),
        background_label="audit-fine-endpoint",
    )
    fixed_updated, fixed_ledger = advance_canonical_macro_interval(
        fixed_context, stepper=linear_step, candidate_factory=candidate
    )
    coarse = 1.0 / (1.0 + dlna)
    fine = 1.0 / (1.0 + 0.5 * dlna) ** 2
    exact = math.exp(-dlna)
    returned = float(fixed_updated.state_vector[0])

    shared_buffer = np.empty(2, dtype=float)

    def reused_buffer_step(state, width):
        old = np.asarray(state, dtype=float)
        shared_buffer[0] = old[0] / (1.0 + width)
        shared_buffer[1] = old[1] - 0.25 * width
        return Step(shared_buffer, True, 0.0, 0.0, float(shared_buffer[0]))

    reused_updated, reused_ledger = advance_canonical_macro_interval(
        fixed_context, stepper=reused_buffer_step, candidate_factory=candidate
    )
    reused_error = reused_ledger.attempts[0].error_norm
    reused_returned = float(reused_updated.state_vector[0])

    calls: list[float] = []

    def failure_then_identity(state, width):
        calls.append(float(width))
        if len(calls) == 1:
            return AdaptiveBackwardEulerFailure(
                kind=AdaptiveTrialFailureKind.RETRY_LINEAR,
                message="audit injected linear failure",
                diagnostics=(("trial_width", float(width)),),
            )
        return Step(np.array(state, copy=True), True, 1.0e-13, 2.0e-13, 0.75)

    failure_context = AdaptiveTrajectoryContext(
        eta=history.grid.eta[-1],
        state_vector=np.asarray([1.0, 0.0]),
        accepted_history=history,
        controller_step=dlna,
        tolerances=AdaptiveControllerTolerances.scalar(
            size=2,
            absolute=1.0,
            relative=1.0,
            minimum_step=dlna / 128.0,
            maximum_step=dlna,
        ),
        background_label="audit-failure-contraction",
    )
    _failure_updated, failure_ledger = advance_canonical_macro_interval(
        failure_context,
        stepper=failure_then_identity,
        candidate_factory=candidate,
    )
    contraction = calls[1] / calls[0]
    first_attempt = failure_ledger.attempts[0]
    passed = all(
        (
            fixed_ledger.accepted_microsteps == 1,
            math.isclose(returned, fine, rel_tol=0.0, abs_tol=1.0e-15),
            reused_error is not None and reused_error > 0.0,
            math.isclose(reused_returned, fine, rel_tol=0.0, abs_tol=1.0e-15),
            abs(fine - exact) < abs(coarse - exact),
            math.isclose(contraction, 0.35, rel_tol=0.0, abs_tol=2.0e-15),
            first_attempt.failure_kind is AdaptiveTrialFailureKind.RETRY_LINEAR,
            first_attempt.error_norm is None,
            first_attempt.minimum_physical_population is None,
        )
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "step_width": dlna,
        "returned_endpoint": returned,
        "fine_endpoint": fine,
        "coarse_endpoint": coarse,
        "exact_endpoint": exact,
        "fine_absolute_error": abs(fine - exact),
        "coarse_absolute_error": abs(coarse - exact),
        "coarse_to_fine_error_ratio": abs(coarse - exact) / abs(fine - exact),
        "reused_stage_buffer_reported_error_norm": reused_error,
        "reused_stage_buffer_returned_endpoint": reused_returned,
        "reused_stage_buffer_snapshot_preserved": bool(
            reused_error is not None
            and reused_error > 0.0
            and math.isclose(reused_returned, fine, rel_tol=0.0, abs_tol=1.0e-15)
        ),
        "linear_failure_contraction": contraction,
        "expected_linear_failure_contraction": 0.35,
        "dependent_half_steps_short_circuited_before_retry": len(calls) >= 2,
        "first_attempt_failure_kind": first_attempt.failure_kind.value,
        "first_attempt_has_committable_state": False,
    }


def run_probe(name: str, function: Callable[[], dict[str, object]]) -> dict[str, object]:
    started = utc_now()
    start = time.perf_counter()
    try:
        evidence = function()
        exception = None
    except Exception as exc:  # pragma: no cover - fail-closed audit path
        evidence = {"status": "FAIL"}
        exception = {"type": type(exc).__name__, "message": str(exc)}
    return {
        "probe_id": name,
        "argv": [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:]],
        "cwd": str(ROOT),
        "fixed_environment_observed": {
            key: os.environ.get(key) for key in FIXED_ENVIRONMENT
        },
        "started_at_utc": started,
        "duration_seconds": time.perf_counter() - start,
        "evidence": evidence,
        "exception": exception,
    }


def command_plan(*, include_scientific: bool) -> list[tuple[str, list[str], bool, float]]:
    python = sys.executable
    focused = [
        "tests/trajectory/test_adaptive_canonical_macro.py",
        "tests/trajectory/test_causal_characteristic_history.py",
        "tests/trajectory/test_characteristic_angular_solver.py",
        "tests/trajectory/test_pseudotransient_continuation.py",
        "tests/recoil/test_nonlinear_bose_release.py",
        "tests/recoil/test_nonlinear_bose_runtime.py",
    ]
    plan = [
        (
            "focused_changed_surface_tests",
            [python, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", *focused],
            True,
            900.0,
        ),
        (
            "fast_repository_tests",
            [python, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-m", "not slow"],
            True,
            1800.0,
        ),
        ("verify_repo_quick", [python, "-B", "scripts/verify_repo.py", "--quick"], True, 600.0),
        ("verify_repo_all", [python, "-B", "scripts/verify_repo.py", "--all"], True, 2400.0),
        (
            "compileall_changed_code",
            [
                python,
                "-B",
                "-m",
                "compileall",
                "-q",
                "src/full_bianchi_hyrec",
                "scripts/run_ode_solver_four_loop_audit.py",
            ],
            True,
            600.0,
        ),
        ("import_contract", [python, "-B", "scripts/check_imports.py"], True, 600.0),
        ("git_diff_check", ["git", "diff", "--check"], True, 120.0),
        ("installed_distributions", [python, "-B", "-m", "pip", "freeze", "--all"], False, 600.0),
    ]
    if include_scientific:
        plan.append(
            (
                "verify_repo_scientific",
                [python, "-B", "scripts/verify_repo.py", "--scientific"],
                True,
                14400.0,
            )
        )
    return plan


def transcribed_preimplementation_evidence() -> list[dict[str, object]]:
    """Live receipts captured before the implementation diff existed.

    These rows are deliberately labelled transcriptions: they are historical
    evidence from this bounded session, not postimage reruns.
    """

    receipts = [
        {
            "receipt_id": "preedit_fast_baseline",
            "provenance": "transcribed_live_process_receipt",
            "cwd": str(ROOT),
            "argv": [
                "python",
                "-B",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "-m",
                "not slow",
            ],
            "exit_code": 0,
            "stdout_summary": "324 passed, 37 deselected in 22.72s",
        },
        {
            "receipt_id": "history_ptc_red",
            "provenance": "transcribed_live_process_receipt",
            "argv": [
                "python",
                "-B",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/trajectory/test_causal_characteristic_history.py",
                "tests/trajectory/test_pseudotransient_continuation.py",
            ],
            "exit_code": 1,
            "stdout_summary": "10 failed, 12 passed in 2.03s",
            "failure_meaning": "expected preimplementation counterexamples",
        },
        {
            "receipt_id": "history_ptc_green",
            "provenance": "transcribed_live_process_receipt",
            "argv": [
                "python",
                "-B",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/trajectory/test_causal_characteristic_history.py",
                "tests/trajectory/test_pseudotransient_continuation.py",
            ],
            "exit_code": 0,
            "stdout_summary": "22 passed in 2.34s",
        },
        {
            "receipt_id": "adaptive_counterexamples_red",
            "provenance": "transcribed_live_process_receipt",
            "argv": [
                "python",
                "-B",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/trajectory/test_adaptive_canonical_macro.py",
                "-k",
                "fine_endpoint or finite_typed or typed_failure or rejected_trial_diagnostics or event_landing",
            ],
            "exit_code": 1,
            "stdout_summary": "6 failed, 7 deselected in 0.74s",
            "failure_meaning": "expected preimplementation counterexamples",
        },
        {
            "receipt_id": "adaptive_counterexamples_green",
            "provenance": "transcribed_live_process_receipt",
            "argv": [
                "python",
                "-B",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/trajectory/test_adaptive_canonical_macro.py",
                "-k",
                "fine_endpoint or finite_typed or typed_failure or rejected_trial_diagnostics or event_landing",
            ],
            "exit_code": 0,
            "stdout_summary": "8 passed, 7 deselected in 0.60s",
        },
        {
            "receipt_id": "adaptive_affected_suite",
            "provenance": "transcribed_live_process_receipt",
            "argv": [
                "python",
                "-B",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/trajectory/test_adaptive_canonical_macro.py",
                "tests/trajectory/test_scalar_history_owner_swap.py",
                "tests/trajectory/test_source_identifiable_dae.py",
            ],
            "exit_code": 0,
            "stdout_summary": "31 passed in 4.56s",
        },
        {
            "receipt_id": "kernel_grid_preedit_baseline",
            "provenance": "transcribed_live_process_receipt",
            "exit_code": 0,
            "stdout_summary": "17 passed in 2.86s",
        },
        {
            "receipt_id": "kernel_grid_counterexamples_red",
            "provenance": "transcribed_live_process_receipt",
            "exit_code": 1,
            "stdout_summary": "33 failed, 18 passed in 2.83s",
            "failure_meaning": "expected preimplementation counterexamples",
        },
        {
            "receipt_id": "kernel_grid_test_oracle_correction",
            "provenance": "transcribed_live_process_receipt",
            "exit_code": 1,
            "stdout_summary": "1 failed, 50 passed",
            "failure_meaning": "test incorrectly required bitwise equality after legitimate weight normalization; production behavior was not weakened",
            "disposition": "test changed to a 1-ULP-scale numerical comparison",
        },
        {
            "receipt_id": "kernel_grid_final_focused",
            "provenance": "transcribed_live_process_receipt",
            "exit_code": 0,
            "stdout_summary": "51 passed in 2.63s",
        },
        {
            "receipt_id": "kernel_grid_related_regression",
            "provenance": "transcribed_live_process_receipt",
            "exit_code": 0,
            "stdout_summary": "205 passed in 99.88s",
        },
        {
            "receipt_id": "kernel_probe_environment_correction",
            "provenance": "transcribed_tool_failure_receipt",
            "failure": "first standalone mpmath probe omitted PYTHONPATH=src and raised ModuleNotFoundError",
            "disposition": "reran with the repository source path declared; this changed the execution environment rather than retrying an unchanged numerical failure",
        },
        {
            "receipt_id": "preedit_counterexample_metrics",
            "provenance": "transcribed_live_probe_receipt",
            "observations": {
                "adaptive": [
                    "coarse full state was committed instead of the fine endpoint",
                    "zero-LTE failure retried the same h",
                    "event inside h_min was overrun",
                    "rejected extrema contaminated accepted diagnostics",
                    "recoverable failure could not construct because Inf was forbidden",
                ],
                "events": "two and grazing roots were missed while the ODE solve reported success",
                "transfer_jvp_relative_error_by_opacity": {
                    "1e-6": 3.445e-6,
                    "1e-8": 0.105858,
                    "1e-10": 538.462,
                    "1e-20": 6.5e19,
                },
                "zero_distance_invalid_occupation_returned": -7.0,
                "causal_history_count_one_future_was_thermal": True,
                "causal_jvp_direction_switch_on_scaling": True,
                "fabricated_continuation_state_committed": [999.0],
                "signed_only_restart_minimum": "Infinity",
                "harmonic_grid_alias_and_stale_synthesis": True,
                "history_copy_lower_bound_bytes": 140231525000,
            },
        },
        {
            "receipt_id": "orchestration_retry",
            "provenance": "transcribed_tool_failure_receipt",
            "attempt": 1,
            "failure": "initial command selected the not-yet-created isolated worktree as cwd",
            "disposition": "same command retried once after creating and verifying the exact-head worktree",
            "retry_budget_used": 1,
        },
        {
            "receipt_id": "audit_runner_direct_probe_red",
            "provenance": "transcribed_live_process_receipt",
            "started_at_utc": "2026-08-23T09:34:02.040642Z",
            "duration_seconds": 73.46210460399743,
            "exit_code": 1,
            "status": "FAIL",
            "required_commands_pass": True,
            "failed_probe_count": 4,
            "failure": "runner process omitted the repository src directory from sys.path; all direct probes raised ModuleNotFoundError",
            "disposition": "insert the exact repository source directory before direct imports and rerun the changed audit-runner cell",
        },
        {
            "receipt_id": "repair_probe_helper_import_error",
            "provenance": "transcribed_tool_failure_receipt",
            "exit_code": 1,
            "failure": "an ad hoc importlib helper omitted sys.modules registration and dataclass decoration raised AttributeError",
            "disposition": "the helper path was abandoned without an unchanged retry; source py_compile/diff checks passed and authoritative probes run only in the audit runner",
        },
        {
            "receipt_id": "repair_closeout_first_integrated_fail",
            "provenance": "transcribed_live_process_receipt",
            "duration_seconds": 49.99548924798728,
            "status": "FAIL",
            "focused_result": "91 passed in 4.79s",
            "fast_result": "1 failed, 377 passed, 37 deselected in 20.90s",
            "verify_repo_all_result": "FAIL on the same test after internal fast run",
            "failure": "the 26-direction background fixture requested ell_max=4 although its 25-mode synthesis rank is 22, condition is 3.720941216207938e16, and analysis/synthesis identity residual is 68.95678676278546",
            "disposition": "kept the new fail-closed gate, asserted ell_max=4 rejection, and ran the direction-only characteristic test at the largest full-rank fixture basis ell_max=3",
        },
    ]
    for receipt in receipts:
        receipt["original_capture_class"] = receipt.pop("provenance")
        receipt["provenance"] = "TRANSCRIBED_SUMMARY_ONLY"
        receipt["raw_receipt_available"] = False
        receipt["limitation"] = (
            "No retained canonical raw stdout/stderr bundle exists; use only as "
            "a bounded historical summary, not as independently replayable evidence."
        )
    return receipts


def independent_review_receipt() -> dict[str, object]:
    """Preserve the sole reviewer verdict without overstating its raw custody."""

    return {
        "review_round": 1,
        "verdict": "REWORK",
        "scope": "external-audit handoff readiness only",
        "provenance": "TRANSCRIBED_INDEPENDENT_REVIEW_SUMMARY_ONLY",
        "raw_receipt_available": False,
        "reviewer_modified_files": False,
        "confirmed_before_repair": {
            "focused": "88 passed in 4.52s",
            "fast": "375 passed, 37 deselected in 33.31s",
            "issue_inventory": "56 unique; 8 LOCAL-VALIDATED, 8 PARTIAL, 40 OPEN",
            "git_diff_check": "PASS",
        },
        "fatal_findings": [
            {
                "id": "REVIEW-F1",
                "finding": "adaptive stage-output buffer alias produced false zero LTE",
                "observed_reported_error_norm": 0.0,
                "independent_scaled_full_fine_difference": 249500.68677753734,
            },
            {
                "id": "REVIEW-F2",
                "finding": "PTC admission callback mutation changed checked state 1 to committed state 999",
                "observed_checked_metric": 0.0,
                "observed_committed_value": 999.0,
            },
            {
                "id": "REVIEW-F3",
                "finding": "near-rank HarmonicGrid admitted an incoherent transform",
                "observed_gram_residual": 1.1404378348209572,
                "observed_synthesis_condition": 3695735321.5580006,
            },
            {
                "id": "REVIEW-F4",
                "finding": "pre-review JSON omitted the later report hash and did not bind direct probes to the declared fixed process environment",
            },
        ],
        "repair_policy": "one repair-closeout; no second review round",
    }


def main() -> int:
    ensure_fixed_runner_environment()
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--include-scientific", action="store_true")
    args = parser.parse_args()
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    started_at = utc_now()
    start = time.perf_counter()
    commands = [
        run_command(command_id, argv, required=required, timeout_seconds=timeout)
        for command_id, argv, required, timeout in command_plan(
            include_scientific=args.include_scientific
        )
    ]
    probes = [
        run_probe("adaptive_macro_contracts", probe_adaptive_macro_contracts),
        run_probe("stable_transfer_mpmath_oracle", probe_transfer_small_optical_depth),
        run_probe("harmonic_grid_identity", probe_harmonic_grid_identity),
        run_probe("causal_history_and_ptc_contracts", probe_causal_history_and_ptc),
    ]

    source_records = source_record_identity()
    environment = dependency_identity()
    required_commands_pass = all(item.passed for item in commands if item.required)
    probes_pass = all(item["evidence"].get("status") == "PASS" for item in probes)
    sources_match = all(item["match"] for item in source_records.values())
    runner_environment_matches = bool(environment["fixed_environment_matches"])
    overall = (
        "PASS"
        if required_commands_pass
        and probes_pass
        and sources_match
        and runner_environment_matches
        else "FAIL"
    )

    raw_diff = git_text("diff", "--binary", "HEAD", "--")
    payload: dict[str, object] = {
        "schema": "REC_BIANCHI_ODE_FOUR_LOOP_AUDIT_V1",
        "status": overall,
        "claim_tier": "LOCAL_IMPLEMENTATION_VALIDATION_ONLY",
        "generated_at_utc": utc_now(),
        "started_at_utc": started_at,
        "duration_seconds": time.perf_counter() - start,
        "repository": {
            "root": str(ROOT),
            "branch": git_text("branch", "--show-current").strip(),
            "head": git_text("rev-parse", "HEAD").strip(),
            "head_tree": git_text("rev-parse", "HEAD^{tree}").strip(),
            "status_porcelain": git_text("status", "--short"),
            "diff_sha256": sha256_bytes(raw_diff.encode("utf-8")),
            "changed_file_sha256": changed_file_hashes(output_path),
            "generated_artifact_excluded_from_own_hash": output_path.relative_to(ROOT).as_posix(),
        },
        "source_records": source_records,
        "environment": environment,
        "preimplementation_evidence": transcribed_preimplementation_evidence(),
        "independent_review": independent_review_receipt(),
        "commands": [
            {**asdict(item), "passed": item.passed}
            for item in commands
        ],
        "numerical_probes": probes,
        "acceptance": {
            "required_commands_pass": required_commands_pass,
            "numerical_probes_pass": probes_pass,
            "source_record_hashes_match": sources_match,
            "runner_process_environment_matches_declared": runner_environment_matches,
            "scientific_tier_requested": bool(args.include_scientific),
            "promotion_authority": False,
        },
        "explicit_nonclaims": [
            "No full E1C/native-COM residual was implemented or executed.",
            "No production or long cosmological trajectory was admitted.",
            "No certified complete multiple/grazing-event enumerator was implemented.",
            "No AP, grid-refinement, endpoint-accuracy, or scalability claim follows.",
            "No push, merge, commit, reseal, or durable-stage publication was performed.",
        ],
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(output_path)
    print(json.dumps({"status": overall, "output": str(output_path)}, sort_keys=True))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
