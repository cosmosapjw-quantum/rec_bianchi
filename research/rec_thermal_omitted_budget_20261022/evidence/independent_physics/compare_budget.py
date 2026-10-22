"""Compare published budget arrays to independent immutable-input algebra.

No imports from the new runtime; no ODE integration.
Run recompute_saved8.py first. This writes only this reviewer's receipt.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import numpy as np
from scipy.constants import sigma as SB
from scipy.integrate import cumulative_trapezoid

HERE=Path(__file__).resolve().parent
UNIT=HERE.parents[1]
ROOT=UNIT.parents[1]
DONOR=ROOT/"research/rec_rei_hheli_sandbox_20261021"
sys.path.insert(0,str(DONOR/"code"))
from atomic_network import AtomicNetwork
atomic=AtomicNetwork()
kb=1.380649e-23;c=299792458.;ev=1.602176634e-19;h=6.62607015e-34
ar=8*np.pi**5*kb**4/(15*h**3*c**3)
BUDGET=UNIT/"results/budget_v1"
summary=json.loads((BUDGET/"SUMMARY.json").read_text())
receipt=json.loads((BUDGET/"RESULT.json").read_text())
ind=json.loads((HERE/"INDEPENDENT_FIXED_PATH.json").read_text())
data=np.load(HERE/"independent_fixed_path.npz",allow_pickle=False)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(UNIT)),sha256=sha(p),bytes=p.stat().st_size)
def relative(a,b):
    a=np.asarray(a);b=np.asarray(b)
    if a.shape!=b.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise AssertionError("invalid comparison shape or nonfinite values")
    return float(np.max(np.abs(a-b)/np.maximum(np.maximum(np.abs(a),np.abs(b)),1e-300)))
def near(a,b,limit=1e-11):
    r=relative(a,b)
    if r>limit:raise AssertionError(("independent comparison failed",r,limit))
    return r

assert summary["source_identity"]=="88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c"
assert summary["status"]=="COMPLETE_SCOPED_FIXED_PATH_BUDGET" and receipt["status"]=="COMPLETE"
for name,expected in summary["source_files"].items():assert sha(UNIT/name)==expected
encoded=json.dumps(summary["source_files"],sort_keys=True).encode()
assert hashlib.sha256(encoded).hexdigest()==summary["source_identity"]
for name,row in receipt["files"].items():
    p=BUDGET/name
    assert sha(p)==row["sha256"] and p.stat().st_size==row["bytes"]
assert summary["new_ODE_integrations"]==0 and summary["old_IVP_reruns"]==0
cols={name:i for i,name in enumerate(ind["arrays_columns"])}
comparisons=[]
mapping={"CMB_hot":"compton_hot_cmb","Planck_reference":"compton_planck_reference",
         "UV_net":"compton_uv","CI_kinetic":"ci_kinetic","CI_binding":"ci_binding",
         "base_total_kinetic":"added_kinetic_primary","base_total_gas":"added_total_gas_primary",
         "old_primary":"photo_primary","old_RR_loss":"rr_kinetic","old_DR_loss":"dr_kinetic"}
for rec in ind["cases"]:
    case=rec["case_id"];s=summary["cases"][case]
    assert rec["input_sha256"]==s["input_trajectory_sha256"]
    with np.load(BUDGET/case/"budget.npz",allow_pickle=False) as b:
        x=b["x"];T=b["T_K"];Y=b["Y"];H=b["H_s"];nb=b["nb_m3"]
        eta=Y@(1+atomic.q);ne=nb*(Y@atomic.q)
        Q={str(n):b["Q_W_m3"][:,i] for i,n in enumerate(b["process_names"])}
        F={str(n):b["fixed_path_logT_forcing_per_x"][:,i] for i,n in enumerate(b["forcing_names"])}
        P=data[case+"__powers"]
        assert np.array_equal(x,data[case+"__x"]) and len(x)==109
        assert np.all(Y[:,[0,5,6]]==0)
        power_rel=max(near(P[:,cols[a]],Q[z]) for a,z in mapping.items())
        power_rel=max(power_rel,near(P[:,cols["CE_kinetic"]],Q["ce_HI"]+Q["ce_HeII"]))
        power_rel=max(power_rel,near(-3*kb*T*eta*nb*H,Q["adiabatic_work"]))
        coeff_rel=near(data[case+"__coefficients"],b["coefficients_SI"])
        dY_rel=near(data[case+"__dYdt"],b["ci_dY_dt"])
        particle_rel=near(data[case+"__particle_source"],b["ci_particle_source_per_baryon_s"])
        forcing_rel=near(data[case+"__forcing"],F["added_primary"])
        forcing_rel=max(forcing_rel,near(-b["ci_particle_source_per_baryon_s"]/(H*eta),F["ci_particle_only"]))
        forcing_rel=max(forcing_rel,near(F["ci_energy_only"]+F["ci_particle_only"],F["ci_full"]))
        assert np.all(Q["compton_hot_cmb"]<=0) and np.all(Q["compton_uv"]>=0)
        assert np.all(Q["ci_kinetic"]<=0) and np.all(Q["ce_HI"]<=0) and np.all(Q["ce_HeII"]<=0)
        valid=np.column_stack([(T>=1e4)&(T<=1e9)]*3+[(T>=5e3)&(T<=5e5)]*2)
        assert np.array_equal(valid,b["in_published_accuracy_domain"])
        assert np.all(~b["underflow_to_zero"])
        assert np.array_equal(b["ci_available_mask"],np.isin(np.arange(21),[1,3,5,7,8,10,11]))
        assert np.array_equal(b["ce_available_mask"],np.isin(np.arange(21),[1,3,5,8,11]))
        assert np.array_equal(b["ci_unavailable_mask"],np.isin(np.arange(21),[13,14,15,17,18,19]))
        assert np.array_equal(b["ce_unavailable_mask"],np.isin(np.arange(21),[7,10,13,14,15,17,18,19]))
        dY=b["ci_dY_dt"];ps=b["ci_particle_source_per_baryon_s"]
        bound=nb*(dY@atomic.ionization_energy_J)
        ci_balance=float(np.max(np.abs(Q["ci_kinetic"]+bound)/np.maximum(np.abs(Q["ci_kinetic"])+np.abs(bound),1e-300)))
        particle_balance=near(dY@atomic.q,ps,1e-13)
        mass_balance=float(np.max(np.abs(dY@atomic.A)/np.maximum(np.sum(np.abs(dY)*atomic.A,axis=1),1e-300)))
        isotope_balance=max(float(np.max(np.abs(dY[:,list(indices)].sum(axis=1))/np.maximum(np.abs(dY[:,list(indices)]).sum(axis=1),1e-300))) for indices in atomic.isotope_groups.values())
        assert max(ci_balance,particle_balance,mass_balance,isotope_balance)<=1e-13
        aa=np.exp(x)/21
        Ug=4*SB/c*2.7255**4*b["photon_energy_monopole"]/aa**4
        reference_moment_rel=near(ar*(2.7255/aa)**4,b["U_gamma_planck_reference_J_m3"])
        actual_moment_rel=near(Ug,b["U_gamma_actual_J_m3"])
        near(ne,b["ne_m3"]);near(eta,b["eta"])
        integral_rel=0.
        for label in ["109_trapezoid","109_Simpson","55_trapezoid"]:
            old=rec["energy_eV_per_baryon_"+label]
            key={"109_trapezoid":"trapezoid_109","109_Simpson":"simpson_109","55_trapezoid":"trapezoid_55"}[label]
            for a,z in mapping.items():integral_rel=max(integral_rel,near(old[a],s["energy_eV_per_baryon"][z][key]))
            integral_rel=max(integral_rel,near(old["CE_kinetic"],s["energy_eV_per_baryon"]["ce_HI"][key]+s["energy_eV_per_baryon"]["ce_HeII"][key]))
        integral_rel=max(integral_rel,near(rec["forcing_109_trapezoid"],s["fixed_path_logT_forcing"]["added_primary"]["trapezoid_109"]))
        near(rec["CI_continuation_and_boundary_eV_per_baryon"],s["energy_eV_per_baryon"]["ci_kinetic"]["continuation_or_boundary_contribution"])
        near(rec["CE_continuation_and_boundary_eV_per_baryon"],s["energy_eV_per_baryon"]["ce_HI"]["continuation_or_boundary_contribution"]+s["energy_eV_per_baryon"]["ce_HeII"]["continuation_or_boundary_contribution"])
        for group in ["energy_eV_per_baryon","fixed_path_logT_forcing"]:
            for values in s[group].values():
                near(values["supported_interval_contribution"]+values["continuation_or_boundary_contribution"],values["trapezoid_109"])
        qintegrand=b["Q_W_m3"]/(nb*H*ev)[:,None]
        near(qintegrand,b["energy_integrand_eV_baryon_per_x"])
        near(cumulative_trapezoid(qintegrand,x=x,axis=0,initial=0),b["energy_cumulative_eV_baryon"])
        comparisons.append(dict(case_id=case,budget_npz=ref(BUDGET/case/"budget.npz"),
             maximum_relative_power_difference=power_rel,
             maximum_relative_coefficient_difference=coeff_rel,
             maximum_relative_dY_difference=dY_rel,
             maximum_relative_particle_source_difference=particle_rel,
             maximum_relative_forcing_difference=forcing_rel,
             maximum_relative_integral_difference=integral_rel,
             CI_binding_balance_scaled=ci_balance,particle_balance_scaled=particle_balance,
             baryon_balance_scaled=mass_balance,isotope_balance_scaled=isotope_balance,
             actual_radiation_moment_relative_difference=actual_moment_rel,
             reference_radiation_moment_relative_difference=reference_moment_rel,
             CI_outside_source_domain_nodes=int((~valid[:,0]).sum()),
             CE_outside_source_domain_nodes=int((~valid[:,3]).sum()),
             exact_zero_neutron_tritium=True,all_scoped_checks_passed=True))
primary=[r for r in ind["cases"] if r["case_id"].endswith("_mao2017_nominal")]
def rng(key):return [min(r["energy_eV_per_baryon_109_trapezoid"][key] for r in primary),max(r["energy_eV_per_baryon_109_trapezoid"][key] for r in primary)]
review=dict(
    schema="rec.omitted.physics_review.v1",reviewed_utc=datetime.now(timezone.utc).isoformat(),
    status="PASS_SCOPED_IMPLEMENTATION_AND_FIXED_PATH_RESULTS",
    source_identity=summary["source_identity"],source_files=summary["source_files"],
    theory_identity=ref(UNIT/"THEORY_KO.md"),provenance_identity=ref(UNIT/"provenance/SOURCES.json"),
    authorship_disclosure="Reviewer authored THEORY_KO.md and SOURCES.json. Review is independent of the runtime implementation and reconstructs results from raw prior NPZ; it is not an independent review of own theory.",
    independent_method="Direct HG97 original formula evaluation and independent Compton moments; no new-runtime imports. Uses stored H,nb and rawY,T, independently reconstructs ne and eta.",
    source_inputs=[ref(BUDGET/"RESULT.json"),ref(BUDGET/"SUMMARY.json"),ref(BUDGET/"INPUTS.json")],
    corrected_before_first_postprocess=[
        dict(id="PM-OMIT-01",issue="A common-event CI balance is identically zero and is not an independent gradient check.",resolution="Driver uses nb I·dY minus binding and separately gates the charge/particle residual."),
        dict(id="PM-OMIT-02",issue="Stored Planck-reference energy moment used a slightly different radiation constant than its computed power.",resolution="Saved reference U now uses the same A_RAD*Tref^4. Actual U retains the inherited source normalization.")],
    open_blocking_findings=[],new_ODE_integrations=0,old_IVP_reruns=0,
    checked_saved_states=872,checked_trajectories=8,
    primary_109_trapezoid_ranges_eV_per_baryon={k:rng(k) for k in ["CMB_hot","Planck_reference","UV_net","CI_kinetic","CI_binding","CE_kinetic","base_total_kinetic","base_total_gas"]},
    primary_fixed_path_forcing_range=[min(r["forcing_109_trapezoid"] for r in primary),max(r["forcing_109_trapezoid"] for r in primary)],
    scientific_assessment="The identifiable actual-U thermal Compton term dominates the supplied omitted components and motivates Compton coupling work. The fixed-path result does not solve a corrected temperature or close the missing full photon spectrum.",
    limitations=[
        "First-order Thomson/nonrelativistic Compton; full CMB recoil/induced closure absent.",
        "The Planck curve is a separately assumed isotropic field, not an actual-spectrum reconstruction.",
        "HG source accuracy intervals and low-T analytic continuation remain distinct; no new empirical validation.",
        "HeI CE/metastables and Li CI/CE are unavailable; other missing processes are not bounded by this result.",
        "109-point trapezoid,55-point coarsening and109-point Simpson are retained-grid diagnostics, not continuous error bounds.",
        "Integrated forcing is not delta lnT, a solved thermal history, or a rigorous total omission bound.",
        "Budget interval starts at the restart nearz7.9637; inherited elapsed_Myr remains cumulative fromz20.",
        "No new geometry/stress/opacity response can be inferred without solving the changed coupled problem.",
        "Physical HOLD, production NOT_APPROVED, global convergence NOT_RUN, U5 CLOSED_HOLD_NOT_RESET and REI_activation=false remain."],
    case_comparisons=comparisons,
    independent_artifacts=[ref(HERE/n) for n in ["recompute_saved8.py","compare_budget.py","INDEPENDENT_FIXED_PATH.json","independent_fixed_path.npz"]],
)
out=UNIT/"evidence/PHYSICS_REVIEW.json"
out.write_text(json.dumps(review,indent=2)+"\n")
print(json.dumps(dict(status=review["status"],review_sha256=sha(out),
                     maximum_power_relative_difference=max(r["maximum_relative_power_difference"] for r in comparisons),
                     maximum_coefficient_relative_difference=max(r["maximum_relative_coefficient_difference"] for r in comparisons),
                     maximum_forcing_relative_difference=max(r["maximum_relative_forcing_difference"] for r in comparisons),
                     maximum_integral_relative_difference=max(r["maximum_relative_integral_difference"] for r in comparisons)),indent=2))
