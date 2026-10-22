"""Extract report numbers from completed receipts and arrays; no model or ODE."""
import hashlib
import json
from pathlib import Path
import numpy as np

UNIT = Path(__file__).resolve().parents[1]
ANALYSIS = UNIT / "results/analysis_v1"
CAMPAIGN = UNIT / "results/compton8"
EV_J = 1.602176634e-19


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ANALYSIS / "SUMMARY.json"
    summary = json.loads(source.read_text())
    cases = summary["cases"]
    receipts = {label: json.loads((CAMPAIGN / label / "RESULT.json").read_text()) for label in cases}
    primary = {}
    for label, row in cases.items():
        if not row["refined"]:
            continue
        with np.load(ANALYSIS / label / "comparison_and_source_data.npz", allow_pickle=False) as a:
            delta = a["raw_delta_from_baseline"][:, 40:61]
            point, species = np.unravel_index(np.argmax(abs(delta)), delta.shape)
            peak_index = int(np.argmax(a["dense_T_K"]))
            detail = dict(max_fraction_difference=float(delta[point, species]),
                          at_z=float(a["z"][point]), species_index=int(species),
                          peak_temperature_z=float(a["dense_z"][peak_index]))
        with np.load(ANALYSIS / label / "collisions/collisions_dense_1025.npz", allow_pickle=False) as a:
            detail["species"] = str(a["species_names"][species])
        fields = (
            "temperature_end_K", "baseline_temperature_end_K", "delta_temperature_end_K",
            "delta_temperature_end_percent", "peak_temperature_109_K", "peak_temperature_1025_K",
            "max_abs_delta_lnT_109", "max_abs_delta_conditional_fraction_109",
            "max_abs_delta_signed_six_109", "max_abs_delta_signed_stress_only_109",
            "tau_end", "delta_tau_end", "delta_tau_end_percent_of_cumulative",
            "delta_tau_end_percent_of_restart_increment", "electron_density_end_m3",
            "delta_electron_density_end_m3", "elapsed_Myr_start", "elapsed_Myr_end",
            "energy_eV_per_baryon", "source_owner_decomposition_eV_per_baryon",
            "gas_integral_residual_scaled", "gas_integral_513_1025_delta_scaled",
            "max_backreaction_ratio", "backreaction_ratio_integral", "max_trace_energy_fraction",
        )
        primary[label] = {key: row[key] for key in fields}
        primary[label]["ionic_detail"] = detail
        c = row["collisions"]
        primary[label]["collision_energy"] = {key: c["energy_eV_per_baryon"][key]
                                                for key in ("ci_kinetic", "ci_binding", "ce_HI", "ce_HeII")}
        primary[label]["collision_forcing"] = c["fixed_path_logT_forcing"]["included_collision_total"]
        primary[label]["collision_domain"] = c["grids"]["dense_1025"]["source_support"]
        primary[label]["compton_over_primary_heat_percent"] = (
            -100 * row["energy_eV_per_baryon"]["compton_selected"] /
            row["energy_eV_per_baryon"]["photo_primary"])
        e = receipts[label]["energy_integrals"]["dense_1025"]
        primary[label]["gas_delta_energy_eV_baryon"] = e["delta_energy_J_per_baryon"] / EV_J
        primary[label]["gas_integrated_net_eV_baryon"] = e["integrated_net_J_per_baryon"] / EV_J
        primary[label]["gas_absolute_throughput_eV_baryon"] = e["throughput_J_per_baryon"] / EV_J

    rs = list(receipts.values())
    admission = [grid["metrics"] for r in rs for grid in r["admission"].values()]
    totals = dict(
        distinct_new_IVPs=summary["new_coupled_IVPs"], old_IVP_reruns=summary["old_IVP_reruns"],
        all_case_gates_pass=all(all(r["gates"].values()) for r in rs),
        per_case_gates=[len(r["gates"]) for r in rs],
        charged_execution_wall_seconds=summary["total_charged_execution_wall_seconds"],
        case_wall_sum_seconds=sum(r["wall_seconds"] for r in rs),
        integration_wall_sum_seconds=sum(r["integration_wall_seconds"] for r in rs),
        diagnostics_persistence_wall_sum_seconds=sum(r["diagnostics_and_persistence_wall_seconds"] for r in rs),
        own_cpu_sum_seconds=sum(r["own_cpu_seconds"] for r in rs),
        case_wall_min_seconds=min(r["wall_seconds"] for r in rs),
        case_wall_max_seconds=max(r["wall_seconds"] for r in rs),
        peak_RSS_KiB=max(r["process_peak_RSS_KiB"] for r in rs),
        accepted_nodes=sum(r["accepted_nodes"] for r in rs),
        retained_diagnostic_rows=sum(m["samples"] for m in admission),
        diagnostic_sets_per_case=4,
        energy_residual_max=max(r["energy_integrals"]["dense_1025"]["residual_scaled"] for r in rs),
        energy_grid_delta_max=max(r["energy_grid_delta_scaled"] for r in rs),
        source_energy_residual_max=max(m["max_source_energy_residual"] for m in admission),
        transfer_ledger_residual_max=max(m["max_transfer_ledger_residual"] for m in admission),
        einstein_residual_max=max(m["max_einstein_constraint"] for m in admission),
        tensor_sum_residual_max=max(m["max_tensor_sum_residual"] for m in admission),
        scaled_population_min=min(m["min_scaled_population"] for m in admission),
        baryon_residual_max=max(m["max_baryon_error"] for m in admission),
        isotope_residual_max=max(max(m["isotope_errors"].values()) for m in admission),
        min_finite_angular_weight=min(m["min_finite_angular_weight"] for m in admission),
    )
    metrics = list(summary["refinement"]["pairs"].values())
    facts = dict(
        status="EXTRACTED_FROM_COMPLETED_IMMUTABLE_RESULTS",
        runtime_identity=summary["runtime_identity"], analysis_identity=summary["source_identity"],
        inputs={str(source.relative_to(UNIT)): digest(source),
                "results/analysis_v1/RESULT.json": digest(ANALYSIS / "RESULT.json"),
                "results/compton8/REFINEMENT.json": digest(CAMPAIGN / "REFINEMENT.json")},
        generator_sha256=digest(Path(__file__)), primary=primary, totals=totals,
        refinement_maxima={key: max(row["metrics"][key] for row in metrics)
                           for key in metrics[0]["metrics"]},
        branch_comparisons=summary["branch_comparisons"],
        notes=["Maxima over explicitly saved physical sample sets, not the continuum.",
               "Timing categories are actual receipts; no unmeasured speedup is claimed.",
               "CI/CE budgets are diagnostics on the new paths, not applied exchanges."],
    )
    with (UNIT / "evidence/REPORT_FACTS.json").open("x") as stream:
        json.dump(facts, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(totals=totals, refinement_maxima=facts["refinement_maxima"],
                         ionic_details={k:v["ionic_detail"] for k,v in primary.items()}), indent=2))


if __name__ == "__main__":
    main()
