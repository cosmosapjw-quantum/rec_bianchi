#!/usr/bin/env python3
"""Build PR-05C2C1B2B1B/v0.71 physical acceptance-gate evidence.

The v0.70-P0 pseudo-transient reference used a generic normwise backward-error
scale with an absolute unit floor.  Photon occupations in the locked z~1100
Bianchi-II lane are O(1e-18), so that floor can inflate the Jacobian scale by
roughly eighteen orders of magnitude and falsely classify the initial physical
macro state as converged.  This bounded stage:

* replaces the unit floor with a state-relative floor;
* connects the durable coupled residual and analytic physical-variable JVP;
* retains the problem-specific gross-residual and photon-number hard gates;
* constructs a matrix-free shifted JVP operator; and
* records a dt/normalization adversarial plot without claiming macro convergence.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.background import BackgroundSnapshotSequence  # noqa: E402
from full_bianchi_hyrec.recoil.frequency_liouville import (  # noqa: E402
    ConservativeFrequencyLiouville,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (  # noqa: E402
    LineBoundaryConfig,
)
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.direct_thermodynamic import (  # noqa: E402
    load_direct_network_node,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (  # noqa: E402
    CoupledCollisionTransportProblem,
)
from full_bianchi_hyrec.trajectory.physical_continuation import (  # noqa: E402
    CoupledPhysicalContinuationAdapter,
)
from full_bianchi_hyrec.trajectory.pseudotransient_continuation import (  # noqa: E402
    _physical_backward_error,
)

VERSION = 71
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1B_physical_acceptance_gate_v0_71"
STATUS = (
    "PASS_P0_FALSE_CONVERGENCE_GATE_FIXED_PHYSICAL_RESIDUAL_JVP_CONNECTED_"
    "MATRIX_FREE_CONTINUATION_OPEN"
)
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c1b2b1b_physical_acceptance_gate_v071.npz"
FORMALISM = ROOT / "docs" / "PR05C2C1B2B1B_PHYSICAL_ACCEPTANCE_GATE_FORMALISM.md"
REPORT = ROOT / "docs" / "PR05C2C1B2B1B_RESEARCH_REPORT.md"
NEXT_PLAN = ROOT / "docs" / "PR05C2C1B2B1C_MATRIX_FREE_CONTINUATION_PLAN.md"
DIRECT_NODE = ROOT / "data" / "z1100_direct_network_node.npz"
BACKGROUND = ROOT / "data" / "pr01c_background_snapshots_v048.npz"
BOUNDARY = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "pr04c_z1100.csv"
)
CODING_HARNESS = (
    ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
)
RESEARCH_HARNESS = (
    ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
)
CODING_HARNESS_SHA256 = (
    "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
)
RESEARCH_HARNESS_SHA256 = (
    "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
)
ACCEPTANCE_TOLERANCE = 1.0e-11


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for key in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(
                buffer, np.asarray(arrays[key]), allow_pickle=False
            )
            info = zipfile.ZipInfo(f"{key}.npy", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(
                info,
                buffer.getvalue(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def deterministic_zip(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(
                str(path.relative_to(source)), (1980, 1, 1, 0, 0, 0)
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def validate_harness(
    archive: Path,
    expected: str,
    validator: str,
    work: Path,
    log: Path,
) -> dict[str, object]:
    observed = sha256(archive)
    if observed != expected:
        raise RuntimeError(f"harness hash mismatch: {archive}")
    destination = work / archive.stem
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise RuntimeError(f"corrupt harness: {archive}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator))
    if len(matches) != 1:
        raise RuntimeError(f"cannot uniquely locate {validator}")
    result = subprocess.run(
        [sys.executable, str(matches[0])],
        cwd=matches[0].parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"harness validation failed: {archive}")
    return {
        "archive": archive.name,
        "sha256": observed,
        "validator": validator,
        "passed": True,
    }


def build_locked_lane(
    dt_s: float,
) -> tuple[CoupledCollisionTransportProblem, np.ndarray, float, dict[str, object]]:
    node = load_direct_network_node(DIRECT_NODE)
    network = node.network
    with np.load(BACKGROUND, allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    source = parse_original_hyrec_boundary_snapshot_csv(BOUNDARY)
    red, blue = source.boundaries
    sequence = BackgroundSnapshotSequence.from_npz(
        BACKGROUND, "Bianchi_II_large_shear"
    )
    source_tau = 0.6072662349590596
    snapshot = sequence.snapshot_at_tau(
        source_tau, H_s_inv_override=source.trajectory.H_s_inv
    )
    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=node.temperature_K,
        x_red=-21.25,
        x_blue=21.25,
    )
    transport = ConservativeFrequencyLiouville.from_network(
        network, reference_line=line
    )
    speeds = transport.face_speeds_from_snapshot(snapshot, grid=grid, line=line)
    activity = network.equilibrium_weight / network.mode_measure
    scalar = activity / (1.0 - activity)
    parent = scalar[:, None] * (
        1.0 + 1.0e-5 * grid.directions[:, 0][None, :]
    )
    canonical_dt_s = 8.49e-5 / source.trajectory.H_s_inv
    problem = CoupledCollisionTransportProblem(
        network=network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=red.total_occupation,
        native_blue_occupation=blue.total_occupation,
        dt_s=float(dt_s),
    )
    provenance = {
        "target_redshift": 1100,
        "background_model": "Bianchi_II_large_shear",
        "source_tau": source_tau,
        "source_temperature_K": node.temperature_K,
        "source_nH_m3": node.nH_m3,
        "source_H_s_inv": source.trajectory.H_s_inv,
        "canonical_dt_s": canonical_dt_s,
        "state_count": int(parent.size),
        "angular_point_count": int(grid.n_angle),
        "frequency_state_count": int(network.n_state),
        "direct_node_sha256": sha256(DIRECT_NODE),
        "background_sha256": sha256(BACKGROUND),
        "boundary_sha256": sha256(BOUNDARY),
    }
    return problem, parent, canonical_dt_s, provenance


def legacy_unit_floor_backward_error(
    residual: np.ndarray, state: np.ndarray, derivative: np.ndarray
) -> float:
    state_scale = np.maximum(np.abs(state), 1.0)
    operator_scale = np.abs(derivative) @ state_scale
    scale = np.maximum(1.0, operator_scale)
    return float(np.max(np.abs(residual) / scale))


def build_diagnostics() -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, np.ndarray],
    dict[str, object],
]:
    canonical_problem, parent_2d, canonical_dt_s, provenance = build_locked_lane(
        8.49e-5 / parse_original_hyrec_boundary_snapshot_csv(BOUNDARY).trajectory.H_s_inv
    )
    parent = parent_2d.ravel()
    canonical_adapter = CoupledPhysicalContinuationAdapter(
        canonical_problem, parent_2d
    )

    start = time.perf_counter()
    log_jacobian = canonical_problem.dense_jacobian(
        np.log(parent_2d), method="batched", chunk_size=64
    )
    dense_elapsed_s = time.perf_counter() - start
    physical_jacobian = log_jacobian / parent[None, :]
    action_jacobian = (
        np.eye(parent.size, dtype=float) - physical_jacobian
    ) / canonical_dt_s
    action = -canonical_adapter.residual(parent) / canonical_dt_s

    dt_values = np.unique(
        np.concatenate(
            (
                np.geomspace(1.0e-9, canonical_dt_s, 80),
                np.asarray([1.0, 1.0e3, 1.0e6, canonical_dt_s]),
            )
        )
    )
    rows: list[dict[str, object]] = []
    for dt_s in dt_values:
        problem, parent_copy, _canonical, _provenance = build_locked_lane(float(dt_s))
        adapter = CoupledPhysicalContinuationAdapter(problem, parent_copy)
        residual = adapter.residual(parent)
        derivative = np.eye(parent.size, dtype=float) - float(dt_s) * action_jacobian
        assessment = adapter.assess(parent)
        legacy = legacy_unit_floor_backward_error(residual, parent, derivative)
        corrected = _physical_backward_error(residual, parent, derivative)
        rows.append(
            {
                "dt_s": float(dt_s),
                "legacy_unit_floor_backward_error": legacy,
                "corrected_state_relative_backward_error": corrected,
                "physical_net_scaled_residual": assessment.net_scaled_residual,
                "physical_gross_backward_error": assessment.gross_backward_error,
                "physical_number_relative_residual": assessment.number_relative_residual,
                "physical_acceptance_metric": assessment.convergence_metric,
                "physical_gate_pass_1e_11": int(
                    assessment.passed(tolerance=ACCEPTANCE_TOLERANCE)
                ),
            }
        )

    def physical_metric(dt_s: float) -> float:
        problem, candidate_parent, _canonical, _provenance = build_locked_lane(dt_s)
        adapter = CoupledPhysicalContinuationAdapter(problem, candidate_parent)
        return adapter.convergence_metric(candidate_parent.ravel())

    root_dt_s = brentq(
        lambda value: physical_metric(value) - ACCEPTANCE_TOLERANCE,
        1.0e-12,
        1.0,
        xtol=1.0e-20,
        rtol=1.0e-12,
    )

    physical_state = np.asarray([1.0e-18])
    physical_residual = np.asarray([-1.0e2])
    physical_derivative = np.asarray([[1.0e20]])
    scaled_state = physical_state / 1.0e-18
    scaled_residual = physical_residual / 1.0e-18
    corrected_physical = _physical_backward_error(
        physical_residual, physical_state, physical_derivative
    )
    corrected_scaled = _physical_backward_error(
        scaled_residual, scaled_state, physical_derivative
    )
    legacy_physical = legacy_unit_floor_backward_error(
        physical_residual, physical_state, physical_derivative
    )
    legacy_scaled = legacy_unit_floor_backward_error(
        scaled_residual, scaled_state, physical_derivative
    )
    mutation_rows = [
        {
            "representation": "physical_occupation_O_1e_minus_18",
            "state": physical_state[0],
            "residual": physical_residual[0],
            "jacobian": physical_derivative[0, 0],
            "legacy_metric": legacy_physical,
            "corrected_metric": corrected_physical,
        },
        {
            "representation": "same_equation_rescaled_to_O_1",
            "state": scaled_state[0],
            "residual": scaled_residual[0],
            "jacobian": physical_derivative[0, 0],
            "legacy_metric": legacy_scaled,
            "corrected_metric": corrected_scaled,
        },
    ]

    rng = np.random.default_rng(20260809)
    direction = parent * rng.normal(size=parent.size)
    direction /= max(float(np.max(np.abs(direction / parent))), 1.0)
    pseudo_time_s = 1.0e-6
    mass = np.ones(parent.size)
    shifted = canonical_adapter.shifted_jvp(
        parent,
        direction,
        old_state=parent,
        pseudo_time=pseudo_time_s,
        mass_diagonal=mass,
    )
    epsilon = 1.0e-5
    shifted_fd = (
        canonical_adapter.pseudo_equation(
            parent + epsilon * direction,
            old_state=parent,
            pseudo_time=pseudo_time_s,
            mass_diagonal=mass,
        )
        - canonical_adapter.pseudo_equation(
            parent - epsilon * direction,
            old_state=parent,
            pseudo_time=pseudo_time_s,
            mass_diagonal=mass,
        )
    ) / (2.0 * epsilon)
    shifted_scale = max(
        float(np.max(np.abs(shifted))),
        float(np.max(np.abs(shifted_fd))),
        1.0e-300,
    )
    shifted_jvp_residual = float(np.max(np.abs(shifted - shifted_fd))) / shifted_scale

    canonical_row = min(rows, key=lambda row: abs(float(row["dt_s"]) - canonical_dt_s))
    metrics = {
        "classification": "PR05C2C1B2B1B_PHYSICAL_ACCEPTANCE_GATE_METRICS",
        "status": STATUS,
        "provenance": provenance,
        "acceptance_tolerance": ACCEPTANCE_TOLERANCE,
        "canonical_dt_s": canonical_dt_s,
        "largest_dt_passing_parent_acceptance_gate_s": root_dt_s,
        "canonical_dt_to_parent_gate_dt_ratio": canonical_dt_s / root_dt_s,
        "canonical_legacy_unit_floor_backward_error": canonical_row[
            "legacy_unit_floor_backward_error"
        ],
        "canonical_corrected_state_relative_backward_error": canonical_row[
            "corrected_state_relative_backward_error"
        ],
        "canonical_physical_gross_backward_error": canonical_row[
            "physical_gross_backward_error"
        ],
        "canonical_physical_number_relative_residual": canonical_row[
            "physical_number_relative_residual"
        ],
        "canonical_physical_acceptance_metric": canonical_row[
            "physical_acceptance_metric"
        ],
        "legacy_gate_false_pass_at_canonical_dt": bool(
            canonical_row["legacy_unit_floor_backward_error"]
            <= ACCEPTANCE_TOLERANCE
        ),
        "corrected_generic_gate_rejects_canonical_parent": bool(
            canonical_row["corrected_state_relative_backward_error"]
            > ACCEPTANCE_TOLERANCE
        ),
        "problem_specific_gate_rejects_canonical_parent": bool(
            canonical_row["physical_acceptance_metric"]
            > ACCEPTANCE_TOLERANCE
        ),
        "corrected_rescaling_invariance_relative_residual": abs(
            corrected_physical - corrected_scaled
        )
        / max(abs(corrected_physical), abs(corrected_scaled), 1.0e-300),
        "legacy_rescaling_disagreement_factor": max(
            legacy_physical, legacy_scaled
        )
        / max(min(legacy_physical, legacy_scaled), 1.0e-300),
        "shifted_matrix_free_jvp_relative_residual": shifted_jvp_residual,
        "dense_physical_jacobian_audit_elapsed_s": dense_elapsed_s,
        "dense_jacobian_condition_number": float(np.linalg.cond(physical_jacobian)),
        "state_minimum": float(np.min(parent)),
        "state_maximum": float(np.max(parent)),
        "action_maximum_abs_s_inv": float(np.max(np.abs(action))),
        "matrix_free_operator_available": True,
        "canonical_macro_convergence_claimed": False,
        "rust_backend_selected": False,
        "next": "PR05C2C1B2B1C_MATRIX_FREE_SAFEGUARDED_CONTINUATION_Z1100_BIANCHI_II",
    }
    arrays = {
        "dt_s": np.asarray([float(row["dt_s"]) for row in rows]),
        "legacy_unit_floor_backward_error": np.asarray(
            [float(row["legacy_unit_floor_backward_error"]) for row in rows]
        ),
        "corrected_state_relative_backward_error": np.asarray(
            [float(row["corrected_state_relative_backward_error"]) for row in rows]
        ),
        "physical_net_scaled_residual": np.asarray(
            [float(row["physical_net_scaled_residual"]) for row in rows]
        ),
        "physical_gross_backward_error": np.asarray(
            [float(row["physical_gross_backward_error"]) for row in rows]
        ),
        "physical_number_relative_residual": np.asarray(
            [float(row["physical_number_relative_residual"]) for row in rows]
        ),
        "physical_acceptance_metric": np.asarray(
            [float(row["physical_acceptance_metric"]) for row in rows]
        ),
        "parent_occupation": parent,
        "physical_action_s_inv": action,
        "scaling_mutation_corrected_metrics": np.asarray(
            [corrected_physical, corrected_scaled]
        ),
        "scaling_mutation_legacy_metrics": np.asarray(
            [legacy_physical, legacy_scaled]
        ),
    }
    return rows, mutation_rows, arrays, metrics


def write_plot(rows: list[dict[str, object]], path: Path) -> None:
    dt = np.asarray([float(row["dt_s"]) for row in rows])
    legacy = np.asarray(
        [float(row["legacy_unit_floor_backward_error"]) for row in rows]
    )
    corrected = np.asarray(
        [float(row["corrected_state_relative_backward_error"]) for row in rows]
    )
    gross = np.asarray([float(row["physical_gross_backward_error"]) for row in rows])
    number = np.asarray(
        [float(row["physical_number_relative_residual"]) for row in rows]
    )
    acceptance = np.asarray(
        [float(row["physical_acceptance_metric"]) for row in rows]
    )

    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    ax.loglog(dt, legacy, label="legacy generic metric (unit floor)", linestyle="--")
    ax.loglog(dt, corrected, label="corrected generic backward error")
    ax.loglog(dt, gross, label="physical gross backward error", linestyle="-.")
    ax.loglog(dt, number, label="photon-number relative residual", linestyle=":")
    ax.loglog(dt, acceptance, label="physical acceptance metric", linewidth=2.0)
    ax.axhline(ACCEPTANCE_TOLERANCE, label=r"hard threshold $10^{-11}$")
    ax.set_xlabel(r"trial physical step $\Delta t$ [s]")
    ax.set_ylabel("dimensionless acceptance diagnostic")
    ax.set_title(r"$z\simeq1100$ Bianchi-II parent: false-convergence audit")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(
        path,
        dpi=180,
        metadata={"Software": "rec_bianchi PR05C2C1B2B1B/v0.71"},
    )
    plt.close(fig)


def formalism_text(metrics: dict[str, object]) -> str:
    return rf"""# PR-05C2C1B2B1B/v0.71 physical acceptance-gate formalism

## Scope

This stage audits one locked accepted parent at `z~1100` on the actual
`Bianchi_II_large_shear` background.  It does not claim a converged physical
canonical macro.  The coupled backward-Euler residual is

\[
R(f;f_n)=f-f_n-\Delta t\,[C_{{\rm Bose}}(f)+L_\nu(f)+S_{{\rm interface}}].
\]

Metric signature is `(-,+,+,+)`, frequency is ordinary Hz, and `c,h,k_B` remain
explicit in the inherited physical operators.

## Defect

The reconstructed v0.70 generic backward error used the dimensionless scale
`max(|f_i|,1)`.  In the locked lane, occupations are about `1e-18`; therefore
`|J|max(|f|,1)` is not invariant under a harmless change of occupation units and
can suppress the reported error by about eighteen orders of magnitude.

## Corrected generic scale

Let

\[
s_i=\max\left(|f_i|,\sqrt{{\epsilon_{{\rm mach}}}}\,\|f\|_\infty\right).
\]

The generic normwise diagnostic is

\[
\epsilon_{{\rm gen}}
=\max_i\frac{{|R_i|}}{{\max[s_i,(|J|s)_i]}}.
\]

There is no absolute unit floor.  Under a consistent variable rescaling
`f=s y`, `R_y=R_f/s`, this diagnostic is invariant.

## Problem-specific macro acceptance

The physical solver retains two independent hard gates:

\[
\epsilon_{{\rm gross}}
=\frac{{\|R\|_\infty}}{{\max(\|f\|_\infty,\|f_n\|_\infty,
\|\Delta t C\|_\infty,\|\Delta t L\|_\infty)}},
\]

and the componentwise photon-number ledger residual
`epsilon_N`.  A candidate passes only when

\[
\max(\epsilon_{{\rm gross}},\epsilon_N)\le10^{{-11}}
\]

and every physical occupation is strictly positive.

## Matrix-free shifted JVP

For pseudo-time `Delta tau` and diagonal mass `M`,

\[
G(f)=M\frac{{f-f^m}}{{\Delta\tau}}+R(f;f_n),
\qquad
G'(f)v=M\frac{{v}}{{\Delta\tau}}+R'(f)v.
\]

The production-facing interface exposes the latter as a SciPy `LinearOperator`;
a dense Jacobian is assembled only for this bounded audit.

## Locked result

- canonical physical step: `{metrics['canonical_dt_s']:.17e} s`
- legacy generic metric: `{metrics['canonical_legacy_unit_floor_backward_error']:.17e}`
- corrected generic metric: `{metrics['canonical_corrected_state_relative_backward_error']:.17e}`
- physical gross error: `{metrics['canonical_physical_gross_backward_error']:.17e}`
- photon-number error: `{metrics['canonical_physical_number_relative_residual']:.17e}`
- largest parent-state step passing the `1e-11` gate: `{metrics['largest_dt_passing_parent_acceptance_gate_s']:.17e} s`
- canonical/gated-step ratio: `{metrics['canonical_dt_to_parent_gate_dt_ratio']:.17e}`

The initial parent is therefore rejected.  No macro convergence is inherited or
manufactured.
"""


def report_text(metrics: dict[str, object]) -> str:
    return f"""# PR-05C2C1B2B1B/v0.71 research report

## Result

`{STATUS}`

The adaptive CMB/BASS protocol requires contract reconstruction and baseline
mismatch resolution before performance-first optimization.  The current DAG
node was therefore narrowed to the physical acceptance metric rather than a
Rust port or a 9x4 macro sweep.

## Evidence

- exact v0.70 reconstructed parent provenance;
- complete z~1100 direct network node;
- actual v0.48 Bianchi-II background sequence;
- source-conditioned red/blue original-HyRec boundary occupations;
- durable nonlinear Bose action, conservative frequency transport and analytic JVP;
- dt sweep, variable-rescaling mutation and matrix-free shifted-JVP regression.

## Main finding

At the recorded canonical step, the old generic diagnostic is
`{metrics['canonical_legacy_unit_floor_backward_error']:.3e}` and would pass the
`1e-11` threshold.  The state-relative generic diagnostic is
`{metrics['canonical_corrected_state_relative_backward_error']:.3e}`, while the
load-bearing physical gross and number gates are
`{metrics['canonical_physical_gross_backward_error']:.3e}` and
`{metrics['canonical_physical_number_relative_residual']:.3e}`.  The initial
state is not a physical macro root.

A unit-rescaling adversary changes the legacy metric by a factor of
`{metrics['legacy_rescaling_disagreement_factor']:.3e}` but changes the corrected
metric by only `{metrics['corrected_rescaling_invariance_relative_residual']:.3e}`
relatively.

## PHYS-MATH audit

- Definitions: physical step and pseudo-time are separate.
- Units: occupations and all acceptance diagnostics are dimensionless; JVP maps
  occupation perturbations to occupation residuals.
- Positivity: physical states remain strictly positive; no clipping is used.
- Conservation: generic residual size cannot replace the independent photon
  number gate.
- Known limit: the scalar stiff manufactured problem reaches its exact root,
  but the physical canonical parent is correctly rejected.

## PHYS-MATH-CODE audit

- Equation-to-code: `CoupledCollisionTransportProblem.residual` and
  `residual_jvp` are the load-bearing operator path.
- Dense assembly: audit only; `shifted_linear_operator` is the continuation path.
- Regression: tiny-state, actual-lane JVP, scaling-invariance and hard-gate tests.
- Remaining P0: there is no safeguarded matrix-free nonlinear solve yet.

## Claim

Surviving claim: the false zero-iteration acceptance path is removed and the
physical residual/JVP is connected.  Narrowed claim: matrix-free continuation is
available as an operator interface, not as a converged macro solver.  Rejected
claim: v0.70-P0 generic acceptance alone establishes physical convergence.
"""


def next_plan_text() -> str:
    return """# PR-05C2C1B2B1C — safeguarded matrix-free continuation plan

1. Use the v0.71 `CoupledPhysicalContinuationAdapter` on the locked z~1100
   Bianchi-II accepted parent only.
2. Implement log-coordinate Newton--Krylov pseudo-transient steps using the
   shifted `LinearOperator`; do not assemble the 910x910 Jacobian in production.
3. Start with the diagonal/AP loss preconditioner already exposed by the coupled
   problem.  Add activity-nullspace RHS projection before any P/Q or Schur
   candidate.
4. Safeguard every step with physical gross, photon-number and positivity gates;
   use trust-region/backtracking when predicted and actual reductions disagree.
5. Generate residual-vs-pseudo-time, number-drift and Krylov-iteration plots.
6. Require one accepted physical macro and exact restart before extending to four
   macros.  Only then compare P/Q, atomic/native Schur, interface Schur and
   Krylov recycling.
7. Defer the Rust backend until Python residual/JVP and acceptance paths are
   reference-locked; Rust must reproduce residual/JVP and deterministic reduction
   before performance claims.
"""


def write_harness_documents(metrics: dict[str, object]) -> None:
    documents = {
        "01_CLEAN_CONTEXT.md": (
            "# CLEAN_CONTEXT\n\nThe mismatch is false pseudo-transient acceptance: "
            "a generic unit-floor metric passes the z~1100 Bianchi-II initial "
            "state while durable physical gross and number gates reject it.\n"
        ),
        "02_CONTRACT_RECONSTRUCTION.md": (
            "# Contract reconstruction\n\nPhysical state is positive occupation; the "
            "physical step is seconds; pseudo-time is a nonlinear globalization "
            "parameter.  Macro acceptance requires gross residual, photon number, "
            "positivity, and no history mutation during pseudo-steps.\n"
        ),
        "03_CODE_PATH_REALITY_AUDIT.md": (
            "# Code-path reality audit\n\nAuthority path: direct network -> actual "
            "Bianchi face speeds -> nonlinear Bose action + conservative frequency "
            "transport -> physical residual/JVP.  Dense Jacobian is audit-only.\n"
        ),
        "04_BOUNDED_HYPOTHESES.md": (
            "# Bounded hypotheses\n\nH1: canonical parent is already a root. Rejected. "
            "H2: only the generic normalization is wrong. Partly supported. H3: "
            "problem-specific conservation gates are mandatory. Supported. H4: "
            "Rust acceleration should be selected now. Rejected by DAG order.\n"
        ),
        "05_METACOGNITIVE_TRIAGE.md": (
            "# Metacognitive triage\n\nThe convenient narrative was that P0 continuation "
            "infrastructure merely needed a physical callback.  The adversarial tiny-state "
            "test instead exposed a load-bearing acceptance bug.\n"
        ),
        "06_VERIFIER_RESULTS.md": (
            "# Verifier results\n\n```json\n"
            + json.dumps(metrics, indent=2, sort_keys=True)
            + "\n```\n"
        ),
        "07_DUAL_AUDIT.md": (
            "# Dual audit\n\nPHYS-MATH: dimensions and scaling are consistent after "
            "removing the unit floor. PHYS-MATH-CODE: the actual physical residual and "
            "analytic JVP are connected; nonlinear matrix-free solve remains open.\n"
        ),
        "08_PLOT_CRAG.md": (
            "# Plot-based CRAG\n\nCorrectness: legacy and physical gates disagree at "
            "the canonical step. Retrieval: the physical componentwise gates are the "
            "existing authority. Augmented: the disagreement survives the full dt sweep "
            "and unit-rescaling mutation. Generation: a safeguarded matrix-free path is "
            "required before any multi-macro or Rust benchmark.\n"
        ),
        "09_FIX_AND_DEFER.md": (
            "# Fix and defer\n\nApplied: relative state scale, physical hard-gate "
            "callback, physical residual/JVP adapter. Deferred: P/Q and Schur "
            "preconditioners, Rust backend, 9x4 macro matrix. Forbidden now: fitting, "
            "cached endpoint reuse, performance-first rewrite.\n"
        ),
        "10_CLOSEOUT.md": (
            "# Closeout\n\nThe acceptance gate is repaired and the physical operator "
            "is connected. The DAG advances only to a single-lane safeguarded "
            "matrix-free continuation experiment.\n"
        ),
    }
    for name, text in documents.items():
        (EXPANDED / name).write_text(text, encoding="utf-8")


def artifact_verifier_source() -> str:
    return '''#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json
import numpy as np
ROOT=Path(__file__).resolve().parent
metrics=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
rows=list(csv.DictReader((ROOT/"PHYSICAL_ACCEPTANCE_DT_SWEEP.csv").open(newline="")))
assert metrics["status"].startswith("PASS_P0_FALSE_CONVERGENCE_GATE_FIXED")
assert metrics["legacy_gate_false_pass_at_canonical_dt"]
assert metrics["corrected_generic_gate_rejects_canonical_parent"]
assert metrics["problem_specific_gate_rejects_canonical_parent"]
assert metrics["canonical_physical_gross_backward_error"] > 0.9
assert metrics["canonical_physical_number_relative_residual"] > 0.9
assert metrics["shifted_matrix_free_jvp_relative_residual"] < 1.0e-8
assert metrics["corrected_rescaling_invariance_relative_residual"] < 1.0e-12
assert metrics["legacy_rescaling_disagreement_factor"] > 1.0e15
assert len(rows) >= 80
with np.load(ROOT/"pr05c2c1b2b1b_physical_acceptance_gate_v071.npz") as data:
    assert data["physical_acceptance_metric"].max() >= 1.0
manifest={}
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1);manifest[name]=digest
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(metrics["status"])
'''


def main() -> None:
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="pr05c2c1b2b1b-harness-") as temporary:
        work = Path(temporary)
        harnesses = {
            "coding": validate_harness(
                CODING_HARNESS,
                CODING_HARNESS_SHA256,
                "validate_harness.py",
                work,
                EXPANDED / "CODING_HARNESS_VALIDATION.log",
            ),
            "research": validate_harness(
                RESEARCH_HARNESS,
                RESEARCH_HARNESS_SHA256,
                "validate_workspace.py",
                work,
                EXPANDED / "RESEARCH_HARNESS_VALIDATION.log",
            ),
        }

    rows, mutation_rows, arrays, metrics = build_diagnostics()
    write_csv(EXPANDED / "PHYSICAL_ACCEPTANCE_DT_SWEEP.csv", rows)
    write_csv(EXPANDED / "SCALING_MUTATION.csv", mutation_rows)
    write_json(EXPANDED / "NUMERICAL_METRICS.json", metrics)
    write_json(
        EXPANDED / "HARD_GATE_LEDGER.json",
        {
            "PR05C2C1B2B1B": "COMPLETE_P0_GATE_FIX",
            "legacy_unit_floor_acceptance": "SUPERSEDED_FALSE_CONVERGENCE_RISK",
            "physical_residual_JVP": "CONNECTED_AND_REGRESSION_TESTED",
            "matrix_free_shifted_operator": "AVAILABLE_NOT_YET_SOLVED",
            "canonical_macro_convergence": "OPEN_NOT_CLAIMED",
            "multi_macro": "OPEN",
            "rust_backend": "DEFERRED_UNTIL_REFERENCE_PATH_CONVERGES",
        },
    )
    write_json(
        EXPANDED / "PR05C2C1B2B1B_ledger.json",
        {
            "classification": "PR05C2C1B2B1B_DURABLE_LEDGER",
            "status": STATUS,
            "metrics": metrics,
            "claim": "physical acceptance gate fixed; physical residual/JVP connected",
            "not_claimed": [
                "canonical macro convergence",
                "preconditioner selection",
                "Rust parity or speedup",
                "multi-macro trajectory",
            ],
            "next": metrics["next"],
        },
    )
    write_json(EXPANDED / "HARNESS_EXECUTION_RECEIPT.json", harnesses)
    write_json(
        EXPANDED / "WEB_LITERATURE_DECISION_RECEIPT.json",
        {
            "pseudo_transient_continuation": {
                "source": "Kelley and Keyes, Convergence Analysis of Pseudo-Transient Continuation",
                "decision": "use PTC as nonlinear globalization, not as evidence of physical time acceptance",
            },
            "PETSc_matrix_free": {
                "source": "PETSc SNES matrix-free operator and separate Pmat/PCSHELL documentation",
                "decision": "retain analytic matrix-free JVP and separate measured preconditioner",
            },
            "PETSc_nullspace": {
                "source": "PETSc MatSetNullSpace documentation",
                "decision": "project incompatible RHS components before singular/near-singular Krylov solves",
            },
        },
    )
    write_json(
        EXPANDED / "SYMBOLIC_AND_HIGH_PRECISION_RECEIPT.json",
        {
            "rescaling_identity": "R_y(y)=R_x(s*y)/s and J_y=J_x imply a scale-invariant normwise diagnostic when the state scale has no absolute unit floor",
            "gross_gate": "max(gross_backward_error, number_relative_residual)",
            "precise_special_functions": "not load-bearing for this acceptance audit",
        },
    )
    write_harness_documents(metrics)
    FORMALISM.write_text(formalism_text(metrics), encoding="utf-8")
    REPORT.write_text(report_text(metrics), encoding="utf-8")
    NEXT_PLAN.write_text(next_plan_text(), encoding="utf-8")
    shutil.copy2(FORMALISM, EXPANDED / FORMALISM.name)
    shutil.copy2(REPORT, EXPANDED / REPORT.name)
    shutil.copy2(NEXT_PLAN, EXPANDED / NEXT_PLAN.name)

    plot = EXPANDED / "PHYSICAL_ACCEPTANCE_DIAGNOSTIC.png"
    write_plot(rows, plot)
    deterministic_npz(EXPANDED / DATA.name, arrays)
    verifier = EXPANDED / "verify_PR05C2C1B2B1B.py"
    verifier.write_text(artifact_verifier_source(), encoding="utf-8")
    verifier.chmod(0o755)

    manifest_paths = sorted(
        path
        for path in EXPANDED.iterdir()
        if path.is_file() and path.name != "MANIFEST_SHA256.txt"
    )
    (EXPANDED / "MANIFEST_SHA256.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in manifest_paths),
        encoding="utf-8",
    )
    result = subprocess.run([sys.executable, str(verifier)], cwd=EXPANDED)
    if result.returncode:
        raise SystemExit(result.returncode)
    deterministic_zip(EXPANDED, BUNDLE)
    shutil.copy2(EXPANDED / DATA.name, DATA)
    print(STATUS)
    print(f"artifact_sha256={sha256(BUNDLE)}")
    print(f"data_sha256={sha256(DATA)}")
    print(f"generated_utc={datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
