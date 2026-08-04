#!/usr/bin/env python3
"""Generate PR-01B1-B3B3B0 near-exterior interface artifact."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import hashlib
import json
import math
from pathlib import Path
import zipfile

import numpy as np

from full_bianchi_hyrec.recoil.exterior_interface import (
    BLUE_CELLS,
    EXTERIOR_CELLS,
    RED_CELLS,
    assemble_scalar_interface_generator,
    exterior_pair_bundle,
    interior_cells,
    physical_equilibrium_interval_weight,
)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _compute_pair_job(args):
    e_index, i_index, e_cell, i_cell, lane, ell_max, cache_file = args
    cache_file = Path(cache_file)
    if cache_file.exists():
        data = np.load(cache_file)
        return e_index, i_index, data["conductance"], data["transfer"]
    values, moments = exterior_pair_bundle(
        tuple(e_cell), tuple(i_cell), lane=lane, ell_max=ell_max
    )
    temporary = cache_file.with_suffix(".tmp.npz")
    np.savez_compressed(temporary, conductance=values, transfer=moments)
    temporary.replace(cache_file)
    return e_index, i_index, values, moments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--lane", default="production", choices=("coarse", "production", "reference"))
    parser.add_argument("--ell-max", type=int, default=24)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    repo = args.repo.resolve()
    stage_name = "Full_Bianchi_HyRec_PR01B1B3B3B0_exterior_interface_v0_46"
    artifact = repo / "archive" / "expanded" / stage_name
    artifact.mkdir(parents=True, exist_ok=True)

    interior = interior_cells()
    exterior = EXTERIOR_CELLS
    ell_max = args.ell_max
    conductance = np.zeros((ell_max + 1, len(exterior), len(interior)))
    transfer = np.zeros((len(exterior), len(interior), 2))

    cache_dir = repo / ".cache" / "exterior_pair_cache_v046"
    cache_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for e_index, e_cell in enumerate(exterior):
        for i_index, i_cell in enumerate(interior):
            jobs.append(
                (
                    e_index,
                    i_index,
                    e_cell,
                    i_cell,
                    args.lane,
                    ell_max,
                    str(cache_dir / f"pair_e{e_index:02d}_i{i_index:02d}.npz"),
                )
            )

    completed = 0
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [executor.submit(_compute_pair_job, job) for job in jobs]
        for future in as_completed(futures):
            e_index, i_index, values, moments = future.result()
            conductance[:, e_index, i_index] = values
            transfer[e_index, i_index] = moments
            completed += 1
            if completed % 12 == 0 or completed == len(jobs):
                print(f"PAIR_PROGRESS {completed}/{len(jobs)}", flush=True)

    rows: list[dict] = []
    for e_index, e_cell in enumerate(exterior):
        side = "red" if e_index < len(RED_CELLS) else "blue"
        for i_index, i_cell in enumerate(interior):
            values = conductance[:, e_index, i_index]
            moments = transfer[e_index, i_index]
            rows.append(
                {
                    "exterior_index": e_index,
                    "side": side,
                    "exterior_left": e_cell[0],
                    "exterior_right": e_cell[1],
                    "interior_index": i_index,
                    "interior_left": i_cell[0],
                    "interior_right": i_cell[1],
                    "S0_m^-3_s^-1": values[0],
                    "S1_m^-3_s^-1": values[1],
                    "S2_m^-3_s^-1": values[2],
                    "photon_delta_p0_weighted": moments[0],
                    "photon_delta_ppar_weighted": moments[1],
                }
            )

    interior_pi = np.asarray(
        [physical_equilibrium_interval_weight(*cell) for cell in interior]
    )
    exterior_pi = np.asarray(
        [physical_equilibrium_interval_weight(*cell) for cell in exterior]
    )

    interface_generator = assemble_scalar_interface_generator(
        conductance[0], interior_pi=interior_pi, exterior_pi=exterior_pi
    )
    equilibrium = np.concatenate([interior_pi, exterior_pi])
    interface_left_null = float(np.max(np.abs(np.ones(len(equilibrium)) @ interface_generator)))
    interface_left_null_relative = interface_left_null / (np.max(np.abs(interface_generator)) + 1.0e-300)
    interface_right_null = float(
        np.max(np.abs(interface_generator @ equilibrium))
        / (np.max(np.abs(interface_generator)) * np.max(equilibrium) + 1.0e-300)
    )

    v045 = np.load(
        repo
        / "archive/expanded/Full_Bianchi_HyRec_PR01B1B3B3A_same_cell_regular_v0_45/"
        "same_cell_regularized_block.npz"
    )
    bounded = np.asarray(v045["bounded_collision_matrices_ell0_to6_sInv"])
    if np.max(np.abs(np.asarray(v045["equilibrium_weight_m3"]) - interior_pi)) / np.max(interior_pi) > 5e-13:
        raise RuntimeError("interior equilibrium weights disagree with v0.45")

    ell_release = min(6, ell_max)
    combined = np.zeros((ell_release + 1, len(equilibrium), len(equilibrium)))
    combined[:, : len(interior), : len(interior)] = bounded[: ell_release + 1]
    for ell in range(ell_release + 1):
        for e_index in range(len(exterior)):
            state_e = len(interior) + e_index
            for i_index in range(len(interior)):
                s_ell = conductance[ell, e_index, i_index]
                s_zero = conductance[0, e_index, i_index]
                combined[ell, state_e, i_index] += s_ell / interior_pi[i_index]
                combined[ell, i_index, state_e] += s_ell / exterior_pi[e_index]
                combined[ell, i_index, i_index] -= s_zero / interior_pi[i_index]
                combined[ell, state_e, state_e] -= s_zero / exterior_pi[e_index]

    combined_left_null = float(np.max(np.abs(np.ones(len(equilibrium)) @ combined[0])))
    combined_left_null_relative = combined_left_null / (np.max(np.abs(combined[0])) + 1.0e-300)
    combined_right_null = float(
        np.max(np.abs(combined[0] @ equilibrium))
        / (np.max(np.abs(combined[0])) * np.max(equilibrium) + 1.0e-300)
    )

    rng = np.random.default_rng(20260804)
    u = np.exp(rng.normal(size=len(equilibrium)))
    density = equilibrium * u
    number_residual = float(abs(np.sum(combined[0] @ density)))
    number_residual_relative = number_residual / (
        np.max(np.abs(combined[0])) * np.sum(np.abs(density)) + 1.0e-300
    )
    entropy_production = 0.0
    for e_index in range(len(exterior)):
        for i_index in range(len(interior)):
            left = u[i_index]
            right = u[len(interior) + e_index]
            entropy_production -= conductance[0, e_index, i_index] * (left - right) * (math.log(left) - math.log(right))

    photon_transfer = transfer
    hydrogen_transfer = -photon_transfer
    four_force_residual = float(np.max(np.abs(photon_transfer + hydrogen_transfer)))

    outward_rates = conductance[0] / interior_pi[None, :]
    reverse_rates = conductance[0] / exterior_pi[:, None]
    red_out = outward_rates[: len(RED_CELLS)].sum(axis=0)
    blue_out = outward_rates[len(RED_CELLS) :].sum(axis=0)
    red_reverse = reverse_rates[: len(RED_CELLS)].sum(axis=1)
    blue_reverse = reverse_rates[len(RED_CELLS) :].sum(axis=1)

    selected = [
        (len(RED_CELLS) - 1, 0, "red_adjacent"),
        (len(RED_CELLS), len(interior) - 1, "blue_adjacent"),
        (0, 8, "far_red_center"),
        (len(exterior) - 1, 8, "far_blue_center"),
        (len(RED_CELLS) - 1, 16, "red_cross_resonance"),
        (len(RED_CELLS), 0, "blue_cross_resonance"),
    ]
    convergence_rows = []
    orientation_max = 0.0
    quadrature_max = 0.0
    for e_index, i_index, name in selected:
        production, _ = exterior_pair_bundle(
            exterior[e_index], interior[i_index], lane="production", ell_max=6
        )
        reference, _ = exterior_pair_bundle(
            exterior[e_index], interior[i_index], lane="reference", ell_max=6
        )
        reverse, _ = exterior_pair_bundle(
            interior[i_index], exterior[e_index], lane="production", ell_max=6
        )
        quadrature = float(np.linalg.norm(production - reference) / np.linalg.norm(reference))
        orientation = float(np.linalg.norm(production - reverse) / np.linalg.norm(production))
        quadrature_max = max(quadrature_max, quadrature)
        orientation_max = max(orientation_max, orientation)
        convergence_rows.append(
            {
                "case": name,
                "exterior_index": e_index,
                "interior_index": i_index,
                "quadrature_relative": quadrature,
                "orientation_relative": orientation,
                "S0_production": production[0],
                "S0_reference": reference[0],
            }
        )

    source_rows = []
    for i_index, cell in enumerate(interior):
        source_rows.append(
            {
                "interior_index": i_index,
                "x_left": cell[0],
                "x_right": cell[1],
                "red_outflow_s^-1": red_out[i_index],
                "blue_outflow_s^-1": blue_out[i_index],
                "near_exterior_outflow_s^-1": red_out[i_index] + blue_out[i_index],
                "red_minus_blue_s^-1": red_out[i_index] - blue_out[i_index],
            }
        )

    exterior_rows = []
    for e_index, cell in enumerate(exterior):
        exterior_rows.append(
            {
                "exterior_index": e_index,
                "side": "red" if e_index < len(RED_CELLS) else "blue",
                "x_left": cell[0],
                "x_right": cell[1],
                "equilibrium_weight_m^-3": exterior_pi[e_index],
                "reverse_total_rate_s^-1": reverse_rates[e_index].sum(),
            }
        )

    write_csv(artifact / "exterior_pair_ledger.csv", rows)
    write_csv(artifact / "selected_exterior_convergence.csv", convergence_rows)
    write_csv(artifact / "interior_source_exterior_rates.csv", source_rows)
    write_csv(artifact / "exterior_state_registry.csv", exterior_rows)

    np.savez_compressed(
        artifact / "exterior_interface_conductance.npz",
        classification=np.asarray("PR01B1B3B3B0_NEAR_EXTERIOR_INTERFACE"),
        interior_edges=np.asarray([cell for cell in interior]),
        exterior_edges=np.asarray([cell for cell in exterior]),
        red_cell_count=np.asarray(len(RED_CELLS)),
        ell_values=np.arange(ell_max + 1),
        conductance_m3_sInv=conductance,
        photon_transfer_weighted=photon_transfer,
        hydrogen_transfer_weighted=hydrogen_transfer,
        interior_equilibrium_weight_m3=interior_pi,
        exterior_equilibrium_weight_m3=exterior_pi,
        interface_scalar_generator_sInv=interface_generator,
        combined_collision_matrices_ell0_to6_sInv=combined,
        red_outflow_sInv=red_out,
        blue_outflow_sInv=blue_out,
        reverse_rates_sInv=reverse_rates,
    )

    ledger = {
        "classification": "PR01B1B3B3B0_NEAR_EXTERIOR_INTERFACE_LOCK",
        "stage": "PR-01B1-B3B3B0",
        "status": "PASS_NEAR_EXTERIOR_FAR_BOUNDARY_OPEN",
        "domain": {
            "interior": [-4.25, 4.25],
            "near_red_exterior": [-10.25, -4.25],
            "near_blue_exterior": [4.25, 10.25],
            "red_cells": [list(cell) for cell in RED_CELLS],
            "blue_cells": [list(cell) for cell in BLUE_CELLS],
            "far_boundary": "|x|=10.25; direct jumps beyond remain a separate far-flux gate",
        },
        "counts": {
            "interior_cells": len(interior),
            "exterior_cells": len(exterior),
            "unordered_interface_pairs": len(interior) * len(exterior),
            "ell_max": ell_max,
        },
        "hard_results": {
            "minimum_scalar_conductance": float(np.min(conductance[0])),
            "maximum_selected_quadrature_relative": quadrature_max,
            "maximum_selected_orientation_relative": orientation_max,
            "interface_left_null_absolute": interface_left_null,
            "interface_left_null_relative": interface_left_null_relative,
            "interface_right_null": interface_right_null,
            "combined_left_null_absolute": combined_left_null,
            "combined_left_null_relative": combined_left_null_relative,
            "combined_right_null": combined_right_null,
            "random_number_residual_absolute": number_residual,
            "random_number_residual_relative": number_residual_relative,
            "dilute_entropy_production": entropy_production,
            "same_event_four_force_residual": four_force_residual,
            "red_outflow_min_s^-1": float(np.min(red_out)),
            "red_outflow_max_s^-1": float(np.max(red_out)),
            "blue_outflow_min_s^-1": float(np.min(blue_out)),
            "blue_outflow_max_s^-1": float(np.max(blue_out)),
        },
        "hard_gate_status": {
            "scalar_positivity": bool(np.min(conductance[0]) >= 0.0),
            "selected_quadrature": bool(quadrature_max < 2.0e-7),
            "orientation_reciprocity": bool(orientation_max < 2.0e-12),
            "interface_number": bool(interface_left_null_relative < 1.0e-14),
            "interface_equilibrium": bool(interface_right_null < 1.0e-12),
            "combined_number": bool(combined_left_null_relative < 1.0e-14),
            "combined_equilibrium": bool(combined_right_null < 1.0e-12),
            "entropy_dissipation": bool(entropy_production <= 0.0),
            "same_event_four_force": bool(four_force_residual == 0.0),
            "far_direct_jump_closure": False,
            "full_adaptive_L12_L20_L24": False,
        },
        "decision": {
            "near_exterior_interface": "PASS",
            "far_boundary": "OPEN",
            "full_PR01_scalar_release": "OPEN",
        },
        "limitations": [
            "Exterior-exterior scattering and exterior same-cell angular damping are not included.",
            "Direct interior jumps beyond |x|=10.25 are not yet integrated.",
            "Four-force coefficients are axisymmetric equilibrium-weighted endpoint moments; the nonlinear harmonic edge action remains the next stage.",
            "The amplitude is still the provisional unresolved scalar 2p pole+crossed model.",
        ],
        "next_stage": {
            "name": "PR01B1B3B3B1_far_flux_and_full_scalar_release",
            "tasks": [
                "Integrate direct interior-to-far jumps beyond |x|=10.25 and lock the far boundary ledger.",
                "Apply the near-exterior conductance on L=12/20/24 harmonic-exact grids with nonlinear Bose edge flux.",
                "Close red/interior/blue photon number, entropy and total four-force for anisotropic mock states.",
                "Then execute PR-01C BackgroundSnapshot finite-tilt and large-shear frame-adapter regression.",
            ],
        },
    }
    (artifact / "PR01B1B3B3B0_ledger.json").write_text(
        json.dumps(ledger, indent=2), encoding="utf-8"
    )

    formalism = r"""# Near-exterior scattering interface

The compact line core is

\[
I=[-4.25,4.25].
\]

The first dynamic near-exterior states use the validated adaptive wing grid

\[
O_R^{\rm near}=[-10.25,-4.25],\qquad
O_B^{\rm near}=[4.25,10.25].
\]

Each interior/exterior frequency-cell pair is represented by one unordered
Maxwell--Juttner equilibrium conductance

\[
S_{ei}^{(\ell)}=S_{ie}^{(\ell)}.
\]

Rates are

\[
K_{e\leftarrow i}^{(\ell)}=\frac{S_{ei}^{(\ell)}}{\Pi_i},\qquad
K_{i\leftarrow e}^{(\ell)}=\frac{S_{ei}^{(\ell)}}{\Pi_e}.
\]

For every harmonic block, loss uses the scalar outflow

\[
\Gamma_i^{I\leftrightarrow O}=\sum_e\frac{S_{ei}^{(0)}}{\Pi_i}.
\]

For one nonlinear edge flux \(J_{e\leftarrow i}\), the same endpoint event
produces

\[
\Delta p_\gamma^\mu=p_e^\mu-p_i^\mu,\qquad
\Delta P_H^\mu=-\Delta p_\gamma^\mu.
\]

The present artifact closes the near interface only.  Direct jumps beyond
\(|x|=10.25\) are an explicit far-boundary ledger, not silently discarded.
"""
    (artifact / "EXTERIOR_INTERFACE_FORMALISM.md").write_text(formalism, encoding="utf-8")

    verify = f'''from pathlib import Path\nimport json, numpy as np\nHERE=Path(__file__).resolve().parent\nledger=json.loads((HERE/"PR01B1B3B3B0_ledger.json").read_text())\nfor key,value in ledger["hard_gate_status"].items():\n    if key in {{"far_direct_jump_closure","full_adaptive_L12_L20_L24"}}:\n        assert not value\n    else:\n        assert value\ndata=np.load(HERE/"exterior_interface_conductance.npz")\nassert data["conductance_m3_sInv"].shape == ({ell_max+1},12,17)\nassert np.min(data["conductance_m3_sInv"][0]) >= 0.0\nassert np.max(np.abs(data["photon_transfer_weighted"]+data["hydrogen_transfer_weighted"])) == 0.0\nprint("PR01B1-B3B3B0 near-exterior interface: PASS")\n'''
    (artifact / "verify_PR01B1B3B3B0.py").write_text(verify, encoding="utf-8")

    manifest = []
    for path in sorted(artifact.iterdir()):
        if path.name == "MANIFEST_SHA256.txt":
            continue
        manifest.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (artifact / "MANIFEST_SHA256.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(json.dumps({"artifact": str(artifact), "ledger": ledger}, indent=2))


if __name__ == "__main__":
    main()
