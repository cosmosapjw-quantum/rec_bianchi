"""Independent array-level review of the completed eight-IVP pilot.

No RHS, Jacobian, solver, old suite, or analysis runner is called. Geometry and
atomic constructors provide their owned constants/scales only. Collision
coefficients and all reported energy/refinement quantities are reconstructed
from the retained arrays and the pinned source table.
"""
import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import json
import math
import time
import numpy as np
from scipy.integrate import simpson, cumulative_trapezoid
from numpy.polynomial.legendre import legvander

UNIT = Path(__file__).resolve().parents[2]
REPO = UNIT.parents[1]
THERMAL = UNIT.parent / "rec_thermal_moments_20261022"
OMITTED = UNIT.parent / "rec_thermal_omitted_budget_20261022"
DONOR = UNIT.parent / "rec_rei_hheli_sandbox_20261021"
sys.path.insert(0, str(DONOR / "code"))
from atomic_network import AtomicNetwork
from geometry import Geometry

RUNTIME = "c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac"
KB, C, EV, HP = 1.380649e-23, 299792458., 1.602176634e-19, 6.62607015e-34
K = 6.6524587051e-29 / (9.1093837139e-31 * C)
ARAD = 8*math.pi**5*KB**4/(15*HP**3*C**3)
SEEDS = ("s03_m03_r03", "s04_m04_r04")
BRANCHES = ("actual_hot", "planck_reference")
REQUIRED = {"accepted_solver_nodes.npz", "trajectory.npz", "accepted_diagnostics.npz", "dense_513.npz", "dense_1025.npz"}
CI = ((1,2,"HI"), (3,4,"HI"), (5,6,"HI"), (7,8,"HeI"), (8,9,"HeII"), (10,11,"HeI"), (11,12,"HeII"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_json(p):
    return json.loads(Path(p).read_text())


def read_npz(p):
    with np.load(p, allow_pickle=False) as a:
        return {k:a[k].copy() for k in a.files}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def error(a, b, floor=1e-300):
    a, b = np.asarray(a), np.asarray(b)
    return float(np.max(abs(a-b)/np.maximum(floor, np.maximum(abs(a),abs(b)))))


def close(a, b, message, tolerance=3e-12, floor=1e-300):
    value = error(a,b,floor)
    check(value < tolerance, message + f": relative/scaled error {value}")
    return value


def diagnostics(a):
    names = a["diagnostic_names"].tolist()
    check(len(names) == len(set(names)), "unique diagnostic names")
    return {name:a["diagnostics"][:,i] for i,name in enumerate(names)}


def direct_coefficients(T, source):
    result = {}
    for channel, p in source["CI"]["parameters"].items():
        lam = 2*source["threshold_K"][channel]/T
        result["CI_"+channel] = source["CI"]["cgs_to_SI"]*p["A"]*T**(-1.5)*np.exp(-lam/2)*lam**(-p["b"])/(1+(lam/p["c"])**p["d"])**p["e"]
    for channel, p in source["CE"]["parameters"].items():
        result["CE_"+channel] = source["CE"]["cgs_to_SI"]*p["A"]*T**p["temperature_power"]*np.exp(-.75*source["threshold_K"][channel]/T)/(1+np.sqrt(T/1e5))
    return result


def main():
    start = time.perf_counter()
    campaign, analysis = UNIT/"results/compton8", UNIT/"results/analysis_v1"
    lock, ar = read_json(campaign/"CAMPAIGN_LOCK.json"), read_json(analysis/"RESULT.json")
    check(lock["source_identity"] == ar["runtime_identity"] == RUNTIME, "frozen runtime identity")
    check(ar["status"] == "COMPLETE" and ar["cases"] == 8, "complete eight-case analysis")
    for path,h in lock["source_files"].items():
        check(sha(REPO/path) == h, "runtime source bytes: "+path)
    for path,h in ar["source_files"].items():
        check(sha(UNIT/path) == h, "analysis source bytes: "+path)
    for path,row in ar["outputs"].items():
        p=analysis/path
        check(p.stat().st_size == row["bytes"] and sha(p) == row["sha256"], "analysis output binding: "+path)
    overall, refinement = read_json(analysis/"SUMMARY.json"), read_json(campaign/"REFINEMENT.json")
    attempts = [read_json(p) for p in sorted((campaign/"execution").glob("attempt_*/FINISHED.json"))]
    check(len(attempts) == len(list((campaign/"execution").glob("attempt_*"))), "no unfinished campaign invocation")
    check(all(a["status"] == "COMPLETE" for a in attempts), "completed invocation status")
    wall = sum(a["wall_seconds"] for a in attempts)
    check(wall < 1200 and sum(a["new_integrations_completed"] for a in attempts) == 8, "persistent finite eight-IVP allocation")
    check(all(a["old_IVP_reruns"] == 0 for a in attempts), "no old IVP replay")
    close(overall["total_charged_execution_wall_seconds"], wall, "reported campaign charge")
    atomic = AtomicNetwork()
    table = read_json(OMITTED/"data/HG97_COLLISIONAL_SOURCE.json")
    field_angles = legvander(np.linspace(-1,1,129),8)
    report = dict(schema="rec.compton.independent.saved_results.v1", status="IN_PROGRESS", runtime_identity=RUNTIME,
                  analysis_identity=ar["source_identity"], cases={}, refinements={}, branch_resolution={},
                  campaign_wall_seconds=wall, campaign_new_IVPs=8, reviewer_new_ODE_runs=0, old_suite_reruns=0,
                  inputs={"CAMPAIGN_LOCK.json":sha(campaign/"CAMPAIGN_LOCK.json"), "REFINEMENT.json":sha(campaign/"REFINEMENT.json"),
                          "analysis_RESULT.json":sha(analysis/"RESULT.json"), "analysis_SUMMARY.json":sha(analysis/"SUMMARY.json")})
    all_states = {}
    for seed in SEEDS:
        cfg = read_json(DONOR/"results/pilot_v2/cases"/seed/"RESULT.json")["config"]
        geo = Geometry(cfg["Sigma_F"],cfg["matter_A"],cfg["radiation_A"])
        ucoef = geo.source.rhocrit_j_m3*geo.model.omega_gamma
        for branch in BRANCHES:
            for refined in (False,True):
                label = seed+"_"+branch+("_refined" if refined else "_nominal")
                folder = campaign/label
                receipt = read_json(folder/"RESULT.json")
                check(receipt["status"] == "COMPLETE" and receipt["source_identity"] == RUNTIME, "complete source-bound case "+label)
                check(receipt["label"] == label and receipt["specification"]["branch"] == branch and receipt["specification"]["refined"] == refined, "case configuration "+label)
                check(set(receipt["outputs"]) == REQUIRED and len(receipt["gates"]) == 64 and all(v is True for v in receipt["gates"].values()), "exact saved inventory/gates "+label)
                check(receipt["wall_seconds"] < 240, "case cap "+label)
                for path,row in receipt["outputs"].items():
                    p=folder/path
                    check(p.stat().st_size == row["bytes"] and sha(p) == row["sha256"], "case output binding "+label+":"+path)
                baseline = THERMAL/"results/thermal8"/(seed+"_mao2017_"+("refined" if refined else "nominal"))
                old = read_npz(baseline/"trajectory.npz")
                check(sha(baseline/"trajectory.npz") == read_json(baseline/"RESULT.json")["trajectory_sha256"], "old baseline by identity")
                current, dense, half, accepted, solver = [read_npz(folder/n) for n in ("trajectory.npz","dense_1025.npz","dense_513.npz","accepted_diagnostics.npz","accepted_solver_nodes.npz")]
                check(np.array_equal(current["x"],old["x"]) and np.array_equal(current["initial_state"],old["initial_state"]), "exact paired baseline grid/state")
                check(np.array_equal(solver["x"],accepted["x"]) and np.array_equal(solver["raw_state"],accepted["raw_state"]), "accepted-node preservation")
                check(np.array_equal(dense["x"][::2],half["x"]), "nested dense x")
                close(dense["raw_state"][::2],half["raw_state"],"nested dense states",floor=1.)
                set_errors={}
                energies={}
                for name,a in (("comparison_109",current),("accepted",accepted),("dense_513",half),("dense_1025",dense)):
                    d=diagnostics(a);raw=a["raw_state"];Y=raw[:,40:61]*atomic.scales;T=np.exp(raw[:,62]);x=a["x"]
                    check(np.isfinite(raw).all() and np.isfinite(a["diagnostics"]).all(),"finite retained states")
                    check(np.all(raw[:,[40,45,46]] == 0),"physical native n/T zero")
                    check(raw[:,40:61].min() >= -2e-8 and abs(Y@atomic.A-1).max() < 2e-8,"population/baryon bounds")
                    check(np.all((T>=100)&(T<=1e6)) and np.diff(raw[:,61]).min()>=-2e-10,"T/tau bounds")
                    for indices in atomic.isotope_groups.values():
                        check(abs(Y[:,indices].sum(axis=1)-atomic.initial_Y[list(indices)].sum()).max()/atomic.scales[indices[0]] < 2e-7,"isotope bound")
                    close(a["Y"],Y,"native abundance scaling");close(a["T_K"],T,"log-temperature mapping")
                    eta=Y@(1+atomic.q);ne=d["nb_m3"]*(Y@atomic.q)
                    close(d["ne_m3"],ne,"electron owner");close(d["gas_particles_per_baryon"],eta,"particle owner")
                    check(ne.min()>=0,"nonnegative electrons")
                    check(max(abs(raw[:,13]-1).max(),abs(raw[:,31]-1).max())<2e-9,"number monopoles")
                    for start_block in (4,13,22,31):
                        moments=raw[:,start_block:start_block+9]
                        check(((moments*(2*np.arange(9)+1))@field_angles.T/moments[:,[0]]).min()>-2e-7,"finite angular positivity")
                    check(abs(a["signed_observables"][:,3]-a["signed_observables"][:,1]-a["signed_observables"][:,2]).max()<2e-16,"signed tensor sum")
                    a_scale=np.exp(x)/21;U=ucoef*raw[:,4]/a_scale**4;Tr=2.7255/a_scale;Ur=ARAD*Tr**4
                    uv=np.array([.5*(1+math.tanh((7-(21*math.exp(-float(xx))-1))/.8)) for xx in x])
                    eps=atomic.photon_energy_eV*EV;Uv=uv*float(atomic.photon_flux_bins_base@eps)/C;Mv=uv*float(atomic.photon_flux_bins_base@(eps*eps))/C
                    Qh=-4*K*ne*KB*T*U;Qr=4*K*ne*KB*Ur*(Tr-T);Qv=K*ne*(Mv-4*KB*T*Uv);Qc=Qh if branch=="actual_hot" else Qr
                    power_error=max(close(d[k],v,"reconstructed power "+k) for k,v in (("compton_actual_hot_W_m3",Qh),("compton_planck_reference_W_m3",Qr),("compton_uv_W_m3",Qv),("compton_selected_W_m3",Qc)))
                    source=(d["photo_absorbed_W_m3"]-d["total_escape_W_m3"]+Qc+Qv)/(d["nb_m3"]*d["H_s"])
                    work=3*KB*T*eta;energy=1.5*KB*T*eta+Y@atomic.ionization_energy_J
                    close(d["gas_energy_J_per_baryon"],energy,"thermal plus binding store")
                    close(d["gas_energy_source_J_per_baryon_per_x"],source,"new source integrand",floor=1e-26)
                    close(d["work_J_per_baryon_per_x"],work,"expansion work")
                    flux=(abs(d["photo_absorbed_W_m3"])+abs(d["total_escape_W_m3"])+abs(Qc)+abs(Qv))/(d["nb_m3"]*d["H_s"])+abs(work)
                    net=float(simpson(source-work,x=x));throughput=float(simpson(flux,x=x));residual=abs(energy[-1]-energy[0]-net)/throughput
                    stored=receipt["energy_integrals"][name]
                    close(stored["integrated_net_J_per_baryon"],net,"integrated gas balance",floor=1e-25)
                    # This is already a dimensionless throughput-normalized
                    # residual. Near zero, absolute floating-point roundoff is
                    # the meaningful comparison; the 3e-4 admission stays below.
                    close(stored["residual_scaled"],residual,"energy residual",tolerance=2e-14,floor=1.)
                    check(d["transfer_ledger_residual_scaled"].max()<5e-12,"local ledger gate")
                    ratio=abs(Qc)/(d["H_s"]*U)
                    close(stored["backreaction_ratio_integral"],float(simpson(ratio,x=x)),"backreaction integral")
                    close(stored["max_backreaction_ratio"],float(ratio.max()),"backreaction maximum")
                    energies[name]=dict(net=net,throughput=throughput,residual=residual)
                    set_errors[name]=dict(points=len(x),max_power_relative_error=power_error,min_population=float(raw[:,40:61].min()),energy_residual=residual)
                check(energies["dense_1025"]["residual"]<3e-4,"dense gas energy criterion")
                grid_delta=abs(energies["dense_1025"]["net"]-energies["dense_513"]["net"])/energies["dense_1025"]["throughput"]
                close(receipt["energy_grid_delta_scaled"],grid_delta,"513-to-1025 diagnostic difference",tolerance=2e-9)
                summary=overall["cases"][label];d=diagnostics(dense)
                dT=current["T_K"][-1]-old["T_K"][-1]
                close(summary["temperature_end_K"],current["T_K"][-1],"temperature endpoint")
                close(summary["delta_temperature_end_K"],dT,"temperature baseline difference")
                close(summary["delta_tau_end"],current["raw_state"][-1,61]-old["raw_state"][-1,61],"tau baseline difference")
                for energy_name,field,sign in (("compton_selected","compton_selected_W_m3",1),("compton_uv","compton_uv_W_m3",1),("photo_primary","photo_primary_W_m3",1),("rr_kinetic","rr_cooling_W_m3",-1),("total_escape","total_escape_W_m3",-1)):
                    integral=float(simpson(sign*d[field]/(d["nb_m3"]*d["H_s"]*EV),x=dense["x"]))
                    close(summary["energy_eV_per_baryon"][energy_name],integral,"summary actual-path energy")
                collision_errors=[]
                for grid,a in (("comparison_109",current),("dense_513",half),("dense_1025",dense)):
                    c=read_npz(analysis/label/"collisions"/("collisions_"+grid+".npz"));dd=diagnostics(a)
                    for k in ("x","Y","T_K"):
                        check(np.array_equal(c[k],a[k]),"collision current-state input "+k)
                    coeff=direct_coefficients(a["T_K"],table)
                    coefficient_error=max(close(c["coefficients_SI"][:,j],coeff[n],"independent HG97 coefficient",tolerance=5e-12) for j,n in enumerate(c["coefficient_names"].tolist()))
                    Y=a["Y"];nb=dd["nb_m3"];ne=dd["ne_m3"];T=a["T_K"];H=dd["H_s"];eta=dd["gas_particles_per_baryon"]
                    binding=np.zeros(len(T));particle=np.zeros(len(T))
                    for lower,upper,channel in CI:
                        events=ne*coeff["CI_"+channel]*Y[:,lower]
                        particle+=events;binding+=nb*events*(atomic.ionization_energy_J[upper]-atomic.ionization_energy_J[lower])
                    ceH=nb*ne*Y[:,[1,3,5]].sum(axis=1)*coeff["CE_HI"]
                    ceHe=nb*ne*Y[:,[8,11]].sum(axis=1)*coeff["CE_HeII"]
                    q={n:c["Q_W_m3"][:,j] for j,n in enumerate(c["process_names"].tolist())}
                    f={n:c["fixed_path_logT_forcing_per_x"][:,j] for j,n in enumerate(c["forcing_names"].tolist())}
                    for n,v in (("ci_kinetic",-binding),("ci_binding",binding),("ce_HI",-ceH),("ce_HeII",-ceHe),("included_collision_total_gas",-ceH-ceHe)):
                        close(q[n],v,"collision power owner "+n,tolerance=5e-12)
                    ef=2/(3*KB*T*nb*H*eta)
                    close(f["ci_full"],-ef*binding-particle/(H*eta),"CI caloric particle term",tolerance=5e-12)
                    close(f["included_collision_total"],-ef*(binding+ceH+ceHe)-particle/(H*eta),"combined collision forcing",tolerance=5e-12)
                    valid=np.column_stack([(T>=table["CI"]["published_temperature_range_K"][0])&(T<=table["CI"]["published_temperature_range_K"][1])]*3+[(T>=table["CE"]["published_temperature_range_K"][0])&(T<=table["CE"]["published_temperature_range_K"][1])]*2)
                    check(np.array_equal(c["in_published_accuracy_domain"],valid) and np.array_equal(c["analytic_continuation"],~valid),"fit support masks")
                    check(np.array_equal(c["coefficient_underflow_to_zero"],c["coefficients_SI"]==0),"underflow distinguished from availability")
                    cs=summary["collisions"]["grids"][grid]
                    for n in ("ci_kinetic","ce_HI","ce_HeII","included_collision_total_gas"):
                        values=q[n]/(nb*H*EV);dx=np.diff(a["x"]);pieces=.5*(values[:-1]+values[1:])*dx
                        stored=cs["energy_eV_per_baryon"][n]
                        close(stored["trapezoid"],float(pieces.sum()),"collision trapezoid")
                        close(stored["simpson"],float(simpson(values,x=a["x"])),"collision Simpson")
                        domain=np.all(valid[:,:3],axis=1) if n=="ci_kinetic" else valid[:,3] if n=="ce_HI" else valid[:,4] if n=="ce_HeII" else np.all(valid[:,3:],axis=1)
                        supported=domain[:-1]&domain[1:]
                        check(stored["supported_intervals"]==int(supported.sum()),"supported interval count")
                        close(stored["supported_interval_contribution"],float(pieces[supported].sum()),"source-supported contribution",floor=1e-300)
                        close(stored["continuation_or_boundary_contribution"],float(pieces[~supported].sum()),"continuation contribution",floor=1e-300)
                    collision_errors.append(dict(grid=grid,coefficient_max_relative_error=coefficient_error))
                all_states[label]=current
                report["cases"][label]=dict(input_receipt_sha256=sha(folder/"RESULT.json"),retained_sets=set_errors,collision_checks=collision_errors,
                    endpoint_T_K=float(current["T_K"][-1]),baseline_endpoint_T_K=float(old["T_K"][-1]),delta_T_K=float(dT),
                    delta_T_percent=float(100*dT/old["T_K"][-1]),delta_tau=float(current["raw_state"][-1,61]-old["raw_state"][-1,61]),
                    peak_T_1025_K=float(dense["T_K"].max()),compton_eV_per_baryon=summary["energy_eV_per_baryon"]["compton_selected"],
                    max_backreaction_ratio=summary["max_backreaction_ratio"],backreaction_integral=summary["backreaction_ratio_integral"],
                    CI_energy_eV=summary["collisions"]["energy_eV_per_baryon"]["ci_kinetic"]["simpson"],
                    CE_HI_energy_eV=summary["collisions"]["energy_eV_per_baryon"]["ce_HI"]["simpson"],
                    energy_residual_1025=energies["dense_1025"]["residual"],energy_grid_delta=grid_delta)
        for branch in BRANCHES:
            a,b=(all_states[seed+"_"+branch+"_"+r] for r in ("nominal","refined"))
            raw=b["raw_state"]-a["raw_state"];signed=b["signed_observables"]-a["signed_observables"]
            metrics=dict(max_abs_delta_lnT=float(abs(raw[:,62]).max()),max_abs_delta_conditional_ion_fraction=float(abs(raw[:,40:61]).max()),max_abs_delta_tau=float(abs(raw[:,61]).max()),max_abs_delta_signed_six=float(abs(signed).max()),max_abs_delta_signed_stress_only=float(abs(signed[:,1:]).max()),max_abs_delta_signed_shear=float(abs(signed[:,0]).max()))
            check(metrics["max_abs_delta_lnT"]<3e-5 and metrics["max_abs_delta_conditional_ion_fraction"]<3e-5 and metrics["max_abs_delta_tau"]<3e-7 and metrics["max_abs_delta_signed_six"]<3e-7,"finite refinement criteria")
            for k,v in metrics.items():close(refinement["pairs"][seed+"_"+branch]["metrics"][k],v,"reported refinement")
            report["refinements"][seed+"_"+branch]=metrics
        ah,pr=(all_states[seed+"_"+branch+"_refined"] for branch in BRANCHES)
        delta=ah["raw_state"]-pr["raw_state"];signed=ah["signed_observables"]-pr["signed_observables"]
        diffs=dict(lnT=float(abs(delta[:,62]).max()),conditional_fraction=float(abs(delta[:,40:61]).max()),tau=float(abs(delta[:,61]).max()),signed_six=float(abs(signed).max()),signed_stress_only=float(abs(signed[:,1:]).max()))
        keys=dict(lnT="max_abs_delta_lnT",conditional_fraction="max_abs_delta_conditional_ion_fraction",tau="max_abs_delta_tau",signed_six="max_abs_delta_signed_six",signed_stress_only="max_abs_delta_signed_stress_only")
        rows={}
        for n,value in diffs.items():
            scale=sum(report["refinements"][seed+"_"+branch][keys[n]] for branch in BRANCHES)
            s=overall["branch_comparisons"][seed]["resolution"][n]
            close(s["branch_difference"],value,"branch comparison magnitude")
            close(s["sum_of_observed_refinement_changes"],scale,"branch finite resolution scale")
            check(s["exceeds_observed_refinement_changes"] == (value>scale),"empirical resolution flag")
            rows[n]=dict(branch_difference=value,observed_refinement_sum=scale,resolved_at_observed_refinement=value>scale)
        report["branch_resolution"][seed]=rows
    report.update(status="PASS_SCOPED_RESULTS",wall_seconds=time.perf_counter()-start,
                  limitations=["Saved arrays and finite retained-point admission were checked; internal solver trials and continuum positivity were not claimed.",
                               "Finite refinement differences are empirical evidence, not global error bounds.",
                               "CI/CE sources remain diagnostic and include labelled low-temperature analytic continuation.",
                               "The actual photon recoil/induced spectrum and dynamic radiation energy backreaction remain outside this pilot."])
    print(json.dumps(report,indent=2,allow_nan=False))


if __name__ == "__main__":
    main()
