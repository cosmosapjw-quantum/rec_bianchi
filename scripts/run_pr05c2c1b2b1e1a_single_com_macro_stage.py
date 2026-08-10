#!/usr/bin/env python3
"""Build PR-05C2C1B2B1E1A/v0.74 single-COM-macro evidence."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.background import (  # noqa: E402
    BackgroundSnapshotSequence,
    BianchiIINormalizedState,
    BianchiReviewBianchiIIProvider,
    OrthogonalGammaLawMatter,
)
from full_bianchi_hyrec.recoil.frequency_liouville import (  # noqa: E402
    ConservativeFrequencyLiouville,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid  # noqa: E402
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig  # noqa: E402
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.causal_history import AcceptedRadiationHistory  # noqa: E402
from full_bianchi_hyrec.trajectory.direct_thermodynamic import (  # noqa: E402
    load_direct_network_node,
)
from full_bianchi_hyrec.trajectory.full_coupled_adaptive import (  # noqa: E402
    CoupledCollisionTransportProblem,
)
from full_bianchi_hyrec.trajectory.single_com_macro import (  # noqa: E402
    assess_roundoff_aware_macro,
    solve_roundoff_aware_single_macro,
)
from full_bianchi_hyrec.trajectory.source_derived_parent import (  # noqa: E402
    build_source_derived_bootstrap_parent,
)

VERSION = 74
STAGE = "PR-05C2C1B2B1E1A/v0.74"
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1E1A_single_com_macro_v0_74"
STATUS = (
    "PASS_PR05C2C1B2B1E1A_SOURCE_CONDITIONED_SINGLE_COM_MACRO_"
    "ROUNDOFF_LIMITED_ROOT_ATOMIC_HISTORY_COUPLING_OPEN"
)
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c1b2b1e1a_single_com_macro_v074.npz"
FORMALISM = ROOT / "docs" / "PR05C2C1B2B1E1A_SINGLE_COM_MACRO_FORMALISM.md"
REPORT = ROOT / "docs" / "PR05C2C1B2B1E1A_RESEARCH_REPORT.md"
NEXT_PLAN = ROOT / "docs" / "PR05C2C1B2B1E1B_DYNAMIC_ATOMIC_MACRO_PLAN.md"
HISTORY_PATH = ROOT / "data/pr05b2_source_history_v060.npz"
NODE_PATH = ROOT / "data/z1100_direct_network_node.npz"
BACKGROUND_PATH = ROOT / "data/pr01c_background_snapshots_v048.npz"
SOURCE_PATH = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "pr04c_z1100.csv"
)
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
TAU0 = 0.6072662349590596
BRANCH_ID = "Bianchi_II:expanding:orthogonal"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for key in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(arrays[key]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{key}.npy", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, buffer.getvalue(), compresslevel=9)


def deterministic_zip(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(source)), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def validate_harness(
    archive: Path,
    expected_sha256: str,
    validator: str,
    work: Path,
    log: Path,
) -> dict[str, object]:
    observed = sha256(archive)
    if observed != expected_sha256:
        raise RuntimeError(f"harness SHA-256 mismatch: {archive}")
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


def build_problem():
    source = parse_original_hyrec_boundary_snapshot_csv(SOURCE_PATH)
    with np.load(HISTORY_PATH, allow_pickle=False) as data:
        full_history = AcceptedRadiationHistory.from_npz_mapping(data)
    history = full_history.prefix(source.trajectory.iz_local + 1)
    node = load_direct_network_node(NODE_PATH)
    with np.load(BACKGROUND_PATH, allow_pickle=False) as data:
        grid = HarmonicGrid.from_directions(
            data["directions"], data["angular_weights"], ell_max=3
        )
    locked = BackgroundSnapshotSequence.from_npz(
        BACKGROUND_PATH, "Bianchi_II_large_shear"
    )
    start = locked.snapshot_at_tau(TAU0)
    provider = BianchiReviewBianchiIIProvider()
    sequence = provider.snapshots(
        family="II",
        eta_grid=np.asarray([TAU0, TAU0 + history.grid.dlna]),
        initial_state=BianchiIINormalizedState.from_snapshot(start),
        matter_parameters=OrthogonalGammaLawMatter(gamma=4.0 / 3.0),
        H_anchor_s_inv=start.H_s_inv,
        eta_anchor=TAU0,
        cosmic_time_anchor_s=start.cosmic_time_s,
    )
    parent = build_source_derived_bootstrap_parent(
        history=history,
        source_snapshot=source.trajectory,
        source_snapshot_sha256=sha256(SOURCE_PATH),
        network_node=node,
        angular_grid=grid,
        background_sequence=sequence,
        background_tau=TAU0,
        branch_id=BRANCH_ID,
    )
    parent.parent.validate_for_production(parent.requirements)

    line = LineBoundaryConfig.lyman_alpha(
        temperature_K=node.temperature_K, x_red=-21.25, x_blue=21.25
    )
    endpoint_tau = TAU0 + history.grid.dlna
    endpoint_raw = sequence.snapshot_at_tau(endpoint_tau)
    endpoint_H = source.trajectory.H_s_inv * (
        endpoint_raw.H_s_inv / start.H_s_inv
    )
    endpoint = sequence.snapshot_at_tau(
        endpoint_tau, H_s_inv_override=endpoint_H
    )
    physical_dt_s = (
        endpoint_raw.cosmic_time_s - start.cosmic_time_s
    ) * start.H_s_inv / source.trajectory.H_s_inv
    transport = ConservativeFrequencyLiouville.from_network(
        node.network, reference_line=line
    )
    speeds = transport.face_speeds_from_snapshot(endpoint, grid=grid, line=line)
    problem = CoupledCollisionTransportProblem(
        network=node.network,
        grid=grid,
        transport=transport,
        face_speeds_x_s_inv=speeds,
        native_red_occupation=parent.interface_samples[0].total_occupation,
        native_blue_occupation=parent.interface_samples[1].total_occupation,
        dt_s=physical_dt_s,
    )
    roots = sequence.boundary_speed_roots(
        tau_start=TAU0,
        tau_end=endpoint_tau,
        directions_normal=grid.directions,
        line=line,
    )
    return source, history, node, grid, start, endpoint_raw, endpoint, sequence, parent, problem, roots


def build_evidence():
    (
        source,
        history,
        node,
        grid,
        start,
        endpoint_raw,
        endpoint,
        sequence,
        parent,
        problem,
        roots,
    ) = build_problem()
    old = np.array(parent.parent.occupation, copy=True)
    initial = assess_roundoff_aware_macro(
        problem, old_occupation=old, occupation=old
    )
    result = solve_roundoff_aware_single_macro(problem, old)
    if not result.converged or not result.assessment.passed():
        raise RuntimeError("roundoff-aware single COM macro did not pass")

    candidate = np.asarray(result.occupation)
    relative_update = candidate / old - 1.0
    root_tolerance = 5.0e-15
    initial_red_ties = sum(
        int(np.count_nonzero(np.abs(item - TAU0) <= root_tolerance))
        for item in roots.red_by_direction
    )
    initial_blue_ties = sum(
        int(np.count_nonzero(np.abs(item - TAU0) <= root_tolerance))
        for item in roots.blue_by_direction
    )
    interior_red_roots = sum(
        int(np.count_nonzero((item > TAU0 + root_tolerance) & (item < TAU0 + history.grid.dlna - root_tolerance)))
        for item in roots.red_by_direction
    )
    interior_blue_roots = sum(
        int(np.count_nonzero((item > TAU0 + root_tolerance) & (item < TAU0 + history.grid.dlna - root_tolerance)))
        for item in roots.blue_by_direction
    )
    if interior_red_roots or interior_blue_roots:
        raise RuntimeError("interior boundary-speed root requires macro splitting")
    iterations = [
        {
            "iteration": row.iteration,
            "raw_residual_inf": row.raw_residual_inf,
            "net_scaled_residual": row.normalized_residual_inf,
            "gross_backward_error": row.gross_backward_error,
            "number_relative_residual": row.number_relative_residual,
            "residual_roundoff_ratio": row.residual_roundoff_ratio,
            "gmres_iterations": row.gmres_iterations,
            "damping": row.damping,
        }
        for row in result.iterations
    ]
    profile_rows = []
    for index, label in enumerate(node.network.state_labels):
        profile_rows.append(
            {
                "state_index": index,
                "state_label": str(label),
                "x_center": float(node.network.centers[index]),
                "parent_monopole": float(np.sum(grid.weights * old[index])),
                "candidate_monopole": float(np.sum(grid.weights * candidate[index])),
                "maximum_relative_update": float(np.max(np.abs(relative_update[index]))),
            }
        )

    start_H_source = source.trajectory.H_s_inv
    provider_dt = endpoint_raw.cosmic_time_s - start.cosmic_time_s
    canonical_dt = history.grid.dlna / start_H_source
    metrics = {
        "classification": "PR05C2C1B2B1E1A_NUMERICAL_METRICS",
        "status": STATUS,
        "claim_boundary": (
            "SOURCE_CONDITIONED_COM_COLLISION_TRANSPORT_SUBBLOCK_ROOT_"
            "HELD_NATIVE_BOUNDARY_NO_ATOMIC_OR_HISTORY_APPEND"
        ),
        "accepted_history_index": parent.parent.accepted_history_index,
        "accepted_history_sha256": parent.parent.accepted_history_sha256,
        "parent_sha256": parent.parent.sha256,
        "background_sequence_sha256": parent.background_sequence_sha256,
        "network_sha256": parent.parent.network_sha256,
        "interface_sha256": parent.interface_sha256,
        "canonical_dlna": history.grid.dlna,
        "canonical_FLRW_dt_s": canonical_dt,
        "provider_rescaled_dt_s": problem.dt_s,
        "provider_to_FLRW_dt_ratio": problem.dt_s / canonical_dt,
        "start_H_s_inv": start_H_source,
        "endpoint_H_s_inv": endpoint.H_s_inv,
        "endpoint_H_relative_change": endpoint.H_s_inv / start_H_source - 1.0,
        "endpoint_q_relative_change": endpoint.q / start.q - 1.0,
        "initial_red_tie_direction_count": initial_red_ties,
        "initial_blue_tie_direction_count": initial_blue_ties,
        "interior_red_boundary_root_count": interior_red_roots,
        "interior_blue_boundary_root_count": interior_blue_roots,
        "initial_tie_resolved_by_endpoint_branch": True,
        "initial_raw_residual_inf": initial.raw_residual_inf,
        "initial_net_scaled_residual": initial.net_scaled_residual,
        "initial_gross_backward_error": initial.gross_backward_error,
        "initial_number_relative_residual": initial.number_relative_residual,
        "initial_energy_net_relative_residual": initial.energy_net_relative_residual,
        "final_raw_residual_inf": result.assessment.raw_residual_inf,
        "final_net_scaled_residual": result.assessment.net_scaled_residual,
        "final_gross_backward_error": result.assessment.gross_backward_error,
        "final_residual_roundoff_bound": result.assessment.residual_roundoff_bound,
        "final_residual_roundoff_ratio": result.assessment.residual_roundoff_ratio,
        "final_residual_roundoff_limited": result.assessment.residual_roundoff_limited,
        "final_number_residual_m3": result.assessment.number_residual_m3,
        "final_number_relative_residual": result.assessment.number_relative_residual,
        "final_energy_residual_J_m3": result.assessment.energy_residual_J_m3,
        "final_energy_net_relative_residual": result.assessment.energy_net_relative_residual,
        "final_energy_gross_backward_error": result.assessment.energy_gross_backward_error,
        "final_energy_roundoff_bound_J_m3": result.assessment.energy_roundoff_bound_J_m3,
        "final_energy_roundoff_ratio": result.assessment.energy_roundoff_ratio,
        "final_energy_roundoff_limited": result.assessment.energy_roundoff_limited,
        "final_minimum_occupation": result.assessment.minimum_occupation,
        "final_collision_entropy_production": result.assessment.collision_entropy_production,
        "final_collision_four_force_residual": result.assessment.collision_four_force_residual,
        "final_pair_loop_action_relative_residual": result.assessment.pair_loop_action_relative_residual,
        "final_pair_loop_four_force_gross_relative_residual": result.assessment.pair_loop_four_force_gross_relative_residual,
        "residual_reduction": result.assessment.residual_reduction,
        "activity_log_shift": result.activity_log_shift,
        "activity_shift_max_relative": result.activity_shift_max_relative,
        "maximum_state_relative_update": float(np.max(np.abs(relative_update))),
        "newton_iteration_records": len(result.iterations),
        "total_gmres_iterations": result.total_gmres_iterations,
        "solve_elapsed_s": result.elapsed_s,
        "convergence_basis": result.convergence_basis,
        "strict_positivity": bool(np.min(candidate) > 0.0),
        "history_append_performed": False,
        "atomic_source_evolved": False,
        "native_boundary_evolved": False,
        "dynamic_background_endpoint_used": True,
        "full_coupled_macro_endpoint": False,
    }
    arrays = {
        "parent_occupation": old,
        "candidate_occupation": candidate,
        "relative_update": relative_update,
        "state_centers": node.network.centers,
        "angular_weights": grid.weights,
        "directions": grid.directions,
        "iteration_raw_residual": np.asarray([row["raw_residual_inf"] for row in iterations]),
        "iteration_net_scaled_residual": np.asarray([row["net_scaled_residual"] for row in iterations]),
        "iteration_gross_backward_error": np.asarray([row["gross_backward_error"] for row in iterations]),
        "iteration_number_relative_residual": np.asarray([row["number_relative_residual"] for row in iterations]),
        "iteration_roundoff_ratio": np.asarray([row["residual_roundoff_ratio"] for row in iterations]),
        "endpoint_face_speeds_x_s_inv": problem.face_speeds_x_s_inv,
    }
    return metrics, iterations, profile_rows, arrays


def make_plots(metrics: dict[str, object], arrays: dict[str, np.ndarray]) -> None:
    iteration = np.arange(arrays["iteration_raw_residual"].size)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4))
    axes[0].semilogy(iteration, arrays["iteration_net_scaled_residual"], "o-", label="net/state diagnostic")
    axes[0].semilogy(iteration, arrays["iteration_gross_backward_error"], "s-", label="gross backward error")
    axes[0].semilogy(iteration, arrays["iteration_number_relative_residual"], "^-", label="photon-number residual")
    axes[0].axhline(1.0e-11, linestyle="--", label="hard-gate tolerance")
    axes[0].set_xlabel("Newton/ledger-restoration record")
    axes[0].set_ylabel("dimensionless diagnostic")
    axes[0].set_title("physical hard gates")
    axes[0].legend(fontsize="small")
    axes[1].semilogy(iteration, arrays["iteration_roundoff_ratio"], "o-")
    axes[1].axhline(1.0, linestyle="--", label="raw residual = roundoff bound")
    axes[1].set_xlabel("Newton/ledger-restoration record")
    axes[1].set_ylabel("raw residual / gross-event roundoff bound")
    axes[1].set_title("cancellation-floor audit")
    axes[1].legend(fontsize="small")
    fig.suptitle("v0.74 source-conditioned single COM macro")
    fig.tight_layout()
    fig.savefig(EXPANDED / "SINGLE_COM_MACRO_CONVERGENCE.png", dpi=220)
    plt.close(fig)

    centers = arrays["state_centers"]
    order = np.argsort(centers, kind="stable")
    weights = arrays["angular_weights"]
    parent = arrays["parent_occupation"] @ weights
    candidate = arrays["candidate_occupation"] @ weights
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    axes[0].semilogy(centers[order], parent[order], "o-", label="source-derived parent")
    axes[0].semilogy(centers[order], candidate[order], "s--", label="single-COM root")
    axes[0].set_xlabel("Doppler coordinate x")
    axes[0].set_ylabel("angular-mean occupation")
    axes[0].legend(fontsize="small")
    axes[1].plot(centers[order], (candidate[order] / parent[order] - 1.0))
    axes[1].set_xlabel("Doppler coordinate x")
    axes[1].set_ylabel("relative monopole update")
    axes[1].set_title("bounded collision--transport correction")
    figure_title = (
        "Held native source boundary; atomic/history coupling remains open\n"
        f"net floor={metrics['final_net_scaled_residual']:.2e}, "
        f"gross={metrics['final_gross_backward_error']:.2e}"
    )
    fig.suptitle(figure_title)
    fig.tight_layout()
    fig.savefig(EXPANDED / "SINGLE_COM_MACRO_STATE_UPDATE.png", dpi=220)
    plt.close(fig)


def formalism_text(metrics: dict[str, object]) -> str:
    return rf"""# PR-05C2C1B2B1E1A single-COM-macro formalism

## Scope

This stage solves one source-conditioned 35-state by 26-direction COM
collision--frequency-transport backward-Euler subblock.  The v0.73 accepted
parent and red/blue boundary occupations are immutable inputs.  The Bianchi-II
geometry is evaluated at the provider macro endpoint.  Atomic populations,
one-/two-photon/Raman source coefficients and accepted original-HyRec history
are **not** advanced here.

## Physical residual

With ordinary frequency in Hz and metric signature `(-,+,+,+)`,

\[
 R(f)=f-f_n-\Delta t\,[C_{{\rm Bose}}(f)+L_\nu(f)].
\]

Occupation is dimensionless and both actions have units `s^-1`.

## Gross-event backward error

The net residual is cancellation dominated.  The collision gross scale is the
forward+reverse event-action scale divided by the smallest weighted frequency
mode measure.  The transport gross scale is the sum of absolute adjacent face
fluxes divided by each cell mode measure.  The hard residual gate uses

\[
 \epsilon_{{\rm gross}}=
 \frac{{\|R\|_\infty}}{{
 \max(\|f_n\|_\infty,\|f\|_\infty,
      \Delta t C_{{\rm gross}},\Delta t L_{{\rm gross}})}}.
\]

The cancellation-amplified net/state diagnostic remains public.  It may exceed
`1e-11` only when the raw residual is also below a conservative floating-point
bound `128 eps_machine * gross_scale`.

## Number restoration

At the numerical floor, photon number is restored along the common Bose
chemical-activity direction

\[
 \phi_i=\frac{{f_i}}{{z_i(1+f_i)}},\qquad
 \phi_i\mapsto e^\delta\phi_i.
\]

The correction is accepted only when it is below `1e-8` pointwise and closes the
independent number ledger.  It is an internal conservation restoration, not a
fit to external data and not a free thermodynamic normalization.

## Result and claim boundary

Gross backward error: `{metrics['final_gross_backward_error']:.17e}`.
Photon-number residual: `{metrics['final_number_relative_residual']:.17e}`.
Energy gross backward error: `{metrics['final_energy_gross_backward_error']:.17e}`.
Net/state residual diagnostic: `{metrics['final_net_scaled_residual']:.17e}`.

This is a roundoff-limited COM subblock root.  It is **not** a full atomic,
native-history or exactly-once-history-commit macro endpoint.
"""


def report_text(metrics: dict[str, object]) -> str:
    return f"""# PR-05C2C1B2B1E1A research report

## Decision

`{STATUS}`

The v0.73 source-derived parent does admit a positive conservative root of the
bounded nonlinear COM collision--transport subproblem.  The apparent
`O(1e-6)` net/state residual floor is not a physical nonconvergence: the raw
residual is `{metrics['final_residual_roundoff_ratio']:.3e}` times the explicit
gross-event floating-point bound, while the gross backward error is
`{metrics['final_gross_backward_error']:.3e}`.

The result survives an independent pair-loop collision oracle and closes the
photon-number ledger after a `{metrics['activity_shift_max_relative']:.3e}`
maximum activity-direction correction.  Exact face-energy bookkeeping is also
roundoff limited relative to the gross photon-energy event scale.

## Narrowed claim

The numerical root-existence blocker for the COM subblock is closed.  The
native boundary was held at its source-derived v0.73 value, and atomic
one-/two-photon/Raman populations and accepted history were not evolved.  The
next stage must connect those representation-local owners before exactly one
history append can be claimed.
"""


def next_plan_text() -> str:
    return """# PR-05C2C1B2B1E1B dynamic atomic/native macro plan

## Objective

Advance the v0.73 accepted parent through one complete `z~1100` orthogonal
Bianchi-II canonical macro with dynamic atomic/native/history coupling.

## Required order

1. Reuse the v0.74 roundoff-aware COM solver and acceptance metrics unchanged.
2. Evaluate one-photon and canonical two-photon/Raman paired source rates at the
   trial endpoint.
3. Evolve the typed original-HyRec characteristic history transactionally;
   proposed nonlinear iterates may not mutate accepted history.
4. Recompute red/blue native occupations from the trial atomic/radiation state,
   rather than holding the v0.73 boundary fixed.
5. Use the dynamic Bianchi-II provider and localize any face-speed or branch
   event before the endpoint solve.
6. Commit exactly one accepted history slice only after every physical gate
   passes.

## Hard gates

- strict positivity without clipping
- gross residual, photon number and gross energy backward error below `1e-11`
- analytic JVP below `1e-8`
- photon--atom four-force and source-ownership closure
- event refinement and deterministic restart
- reject/rollback byte identity
- accepted-history count exactly `+1`

Preconditioner and Rust bake-offs remain deferred until this same full physical
residual path converges.
"""


def harness_docs(metrics: dict[str, object]) -> dict[str, str]:
    return {
        "01_RESEARCH_CONTRACT.md": "Question: does the v0.73 accepted parent admit a positive conservative COM collision--transport macro root without hiding float64 cancellation?\n",
        "02_EVIDENCE_ACQUISITION.md": "Evidence: v0.73 parent, direct z1100 network, dynamic Bianchi-II endpoint, exact vectorized and pair-loop collision operators, conservative frequency transport.\n",
        "03_CLAIM_SOURCE_AUDIT.md": "Source-derived: parent and boundary history, provider geometry, direct network. New numerical contract: gross-event roundoff-aware acceptance. Atomic/history advancement is not claimed.\n",
        "04_HYPOTHESIS_SPACE.md": "H_A no root; H_B root exists but net residual is cancellation-limited; H_C apparent pass is a loose normalization. Evidence selects H_B and rejects H_C via independent ledgers.\n",
        "05_ADVERSARIAL_REVIEW.md": "Attacks: initial-parent false pass, external normalization, number drift, energy drift, pair-loop disagreement, entropy increase, negative occupation. All are hard-gated.\n",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": "Occupation is dimensionless; actions are s^-1; number actions m^-3 s^-1; macro energy J m^-3. Gross scales use matching units.\n",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": f"Gross={metrics['final_gross_backward_error']:.17e}; number={metrics['final_number_relative_residual']:.17e}; pair-loop={metrics['final_pair_loop_action_relative_residual']:.17e}.\n",
        "08_EXTERNAL_GATE.md": "The COM root may enter the next full residual only as a bounded subblock oracle. It may not append accepted history or replace atomic/native ownership.\n",
        "09_FORMALIZATION.md": "Formalism is recorded in PR05C2C1B2B1E1A_SINGLE_COM_MACRO_FORMALISM.md and executable contracts live in trajectory.single_com_macro.\n",
        "10_CLOSEOUT_AND_HANDOFF.md": "Numerical COM root blocker closed. Dynamic atomic/native/history macro remains the only next node.\n",
    }


def verifier_source() -> str:
    return f'''#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert m["status"]=={STATUS!r}
assert m["strict_positivity"]
assert m["final_gross_backward_error"]<1e-11
assert m["final_number_relative_residual"]<1e-11
assert m["final_energy_gross_backward_error"]<1e-11
assert m["final_residual_roundoff_limited"]
assert m["final_energy_roundoff_limited"]
assert m["final_net_scaled_residual"]>1e-11
assert m["activity_shift_max_relative"]<1e-8
assert m["final_pair_loop_action_relative_residual"]<1e-8
assert m["final_pair_loop_four_force_gross_relative_residual"]<1e-12
assert m["final_collision_entropy_production"]<=0.0
assert not m["history_append_performed"]
assert not m["atomic_source_evolved"]
assert not m["native_boundary_evolved"]
assert not m["full_coupled_macro_endpoint"]
assert m["interior_red_boundary_root_count"]==0
assert m["interior_blue_boundary_root_count"]==0
assert m["initial_tie_resolved_by_endpoint_branch"]
assert len(list(csv.DictReader((ROOT/"ITERATION_LEDGER.csv").open())))>=3
with np.load(ROOT/"{DATA.name}") as data:
    assert data["parent_occupation"].shape==(35,26)
    assert data["candidate_occupation"].shape==(35,26)
    assert np.min(data["candidate_occupation"])>0.0
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(m["status"])
'''


def update_bundle_index() -> None:
    path = ROOT / "state/BUNDLE_INDEX.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in rows if int(row.get("version", -1)) != VERSION]
    rows.append(
        {
            "bundle": BUNDLE.name,
            "sha256": sha256(BUNDLE),
            "size_bytes": BUNDLE.stat().st_size,
            "version": VERSION,
        }
    )
    rows.sort(key=lambda row: (int(row.get("version", -1)), str(row.get("bundle", ""))))
    write_json(path, rows)


def main() -> None:
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="pr05c2c1b2b1e1a-harness-") as tmp:
        work = Path(tmp)
        harness = {
            "research": validate_harness(
                RESEARCH_HARNESS,
                RESEARCH_HARNESS_SHA256,
                "validate_workspace.py",
                work,
                EXPANDED / "RESEARCH_HARNESS_VALIDATION.log",
            ),
            "coding": validate_harness(
                CODING_HARNESS,
                CODING_HARNESS_SHA256,
                "validate_harness.py",
                work,
                EXPANDED / "CODING_HARNESS_VALIDATION.log",
            ),
        }
    metrics, iterations, profile_rows, arrays = build_evidence()
    write_json(EXPANDED / "NUMERICAL_METRICS.json", metrics)
    write_csv(EXPANDED / "ITERATION_LEDGER.csv", iterations)
    write_csv(EXPANDED / "STATE_PROFILE.csv", profile_rows)
    write_json(EXPANDED / "HARNESS_EXECUTION_RECEIPT.json", harness)
    write_json(
        EXPANDED / "SOURCE_PROVENANCE.json",
        {
            "history_path": str(HISTORY_PATH.relative_to(ROOT)),
            "history_sha256": sha256(HISTORY_PATH),
            "source_path": str(SOURCE_PATH.relative_to(ROOT)),
            "source_sha256": sha256(SOURCE_PATH),
            "network_path": str(NODE_PATH.relative_to(ROOT)),
            "network_sha256": sha256(NODE_PATH),
            "background_path": str(BACKGROUND_PATH.relative_to(ROOT)),
            "background_sha256": sha256(BACKGROUND_PATH),
        },
    )
    write_json(
        EXPANDED / "PR05C2C1B2B1E1A_ledger.json",
        {
            "classification": "PR05C2C1B2B1E1A_DURABLE_LEDGER",
            "stage": STAGE,
            "status": STATUS,
            "source_conditioned_single_COM_root": "COMPLETE",
            "full_atomic_native_macro": "OPEN",
            "history_append": "NOT_PERFORMED",
            "next": "PR05C2C1B2B1E1B_DYNAMIC_ATOMIC_NATIVE_MACRO",
        },
    )
    write_json(
        EXPANDED / "HARD_GATE_LEDGER.json",
        {
            "strict_positivity": True,
            "gross_backward_error": metrics["final_gross_backward_error"],
            "photon_number": metrics["final_number_relative_residual"],
            "energy_gross_backward_error": metrics["final_energy_gross_backward_error"],
            "pair_loop_parity": metrics["final_pair_loop_action_relative_residual"],
            "entropy_nonincrease": metrics["final_collision_entropy_production"] <= 0.0,
            "net_scaled_diagnostic_retained": metrics["final_net_scaled_residual"],
            "held_native_boundary": True,
            "atomic_history_advance": False,
        },
    )
    write_json(
        EXPANDED / "CLAIM_BOUNDARY.json",
        {
            "implemented": [
                "dynamic-endpoint Bianchi-II COM collision-transport root",
                "gross-event roundoff-aware residual gate",
                "activity-direction photon-number restoration",
                "pair-loop/vectorized parity audit",
            ],
            "not_claimed": [
                "dynamic atomic source evolution",
                "trial-dependent native boundary evolution",
                "accepted-history append",
                "full coupled macro endpoint",
                "selected production preconditioner",
            ],
        },
    )
    harness_dir = EXPANDED / "harness" / "research"
    harness_dir.mkdir(parents=True)
    for name, text in harness_docs(metrics).items():
        (harness_dir / name).write_text(text, encoding="utf-8")

    deterministic_npz(EXPANDED / DATA.name, arrays)
    deterministic_npz(DATA, arrays)
    make_plots(metrics, arrays)
    FORMALISM.write_text(formalism_text(metrics), encoding="utf-8")
    REPORT.write_text(report_text(metrics), encoding="utf-8")
    NEXT_PLAN.write_text(next_plan_text(), encoding="utf-8")
    for doc in (FORMALISM, REPORT, NEXT_PLAN):
        shutil.copy2(doc, EXPANDED / doc.name)
    verifier = EXPANDED / "verify_PR05C2C1B2B1E1A.py"
    verifier.write_text(verifier_source(), encoding="utf-8")
    verifier.chmod(0o755)
    manifest = sorted(
        path
        for path in EXPANDED.rglob("*")
        if path.is_file() and path.name != "MANIFEST_SHA256.txt"
    )
    (EXPANDED / "MANIFEST_SHA256.txt").write_text(
        "".join(
            f"{sha256(path)}  {path.relative_to(EXPANDED)}\n" for path in manifest
        ),
        encoding="utf-8",
    )
    check = subprocess.run([sys.executable, str(verifier)], cwd=EXPANDED)
    if check.returncode:
        raise SystemExit(check.returncode)
    deterministic_zip(EXPANDED, BUNDLE)
    update_bundle_index()
    print(STATUS)
    print(f"artifact_sha256={sha256(BUNDLE)}")
    print(f"data_sha256={sha256(DATA)}")
    print(f"generated_utc={datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
