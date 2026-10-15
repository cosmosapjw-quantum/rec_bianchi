"""Prepare an opt-in typed REI boundary *comparison* candidate.

Do not mutate REI scenario, Rust launch bindings, checkpoints or native solver.
The generated packet is informational until separate authorization explicitly
selects a new reionization initial-state sensitivity experiment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from full_bianchi_hyrec.trajectory.rei_initial_boundary import REIConditionalIC


def make_candidate(*,scenario:Path,source_boundary:Path):
    ic=REIConditionalIC.from_scenario(scenario)
    source=json.loads(source_boundary.read_text())
    if source.get("schema")!="rec.rei.primordial_reference_boundary.v1":
        raise ValueError("unknown source bridge schema")
    if source["rei_scenario_sha256"]!=ic.scenario_sha256:
        raise ValueError("REI scenario has drifted; rederive the donor")
    if source.get("decision")!="REI_REFERENCE_COUNTERFACTUAL_NOT_ADOPTED":
        raise ValueError("upstream donor unexpectedly adopted")
    donor=source["hyrec_full_conditional_projection"]
    chem=source["helium_projected_species"]
    if not (0<=donor["electron_fraction_per_H"]<=1 and donor["temperature_K"]>0
            and chem["xHeII"]==0 and chem["xHeIII"]==0):
        raise ValueError("recombination donor is not a legal neutral-helium IC candidate")
    if abs(chem["xHII_candidate"]-donor["electron_fraction_per_H"])>1e-15:
        raise ValueError("donor electron/ionic projection violates chosen neutral He")
    return {
        "schema":"rei.conditional.primordial_donor_candidate.v1",
        "activation":"DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN",
        "adopted_into_original_REI_scenario":False,
        "source_rei_goal":"REI-AXBI-GOAL-20261014",
        "source_rei_scenario_sha256":ic.scenario_sha256,
        "source_rec_full_C_stdout_sha256":source["source_sha256"],
        "model":"ORIGINAL_HYREC_2012_FULL_H_HE_FLRW_Q0_CONDITIONAL",
        "clock":"zbar=20 reference slice; NOT proper time since z=20",
        "source_physics":"reference primordial recombination only; no astrophysical prehistory",
        "candidate_initial_gas":{
            "x_HII":chem["xHII_candidate"],
            "x_HeII":0.,
            "x_HeIII":0.,
            "Tgas_K":donor["temperature_K"],
            "electron_fraction_xe_per_H":donor["electron_fraction_per_H"],
        },
        "original_REI_gas_initial":{
            "x_HII":ic.x_HII,
            "x_HeII":ic.x_HeII,
            "x_HeIII":ic.x_HeIII,
            "Tgas_K":ic.Tgas_K,
        },
        "unchanged_initial_ionizing_photons":"EXACT_ZERO_CONDITIONAL_REI_ASTROPHYSICAL_SOURCE_ONSET",
        "scientific_state":"COMPARISON_PACKET_NOT_DERIVED_BIANCHI_PRIMORDIAL_HISTORY",
        "source_conversion":{
            "nH_source_vs_REI_fractional":source["normalization_mismatch"]["relative_nH_donor_minus_rei"],
            "fHe_REI":source["normalization_mismatch"]["fHe_REI"],
            "fHe_source":source["normalization_mismatch"]["fHe_HyRec"],
        },
        "requirements_before_USE":[
            "Create isolated REI sensitivity branch/run with fresh physical zbar20 initial point and identical MD14/BB50K source; do not resume baseline checkpoints",
            "Preserve exact original scenario unchanged and compare paired q0 and signed-q families only as conditional initial-value sensitivity",
            "Compute native gas species/charge/energy ledgers, BBN-style plots and milestone differences, and absolute solver error before any claim of observed or fitted effect",
            "Do not interpret q!=0 case as a physically evolved primordial anisotropic recombination history",
        ],
        "provenance_sha256":hashlib.sha256(source_boundary.read_bytes()).hexdigest(),
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--scenario",required=True,type=Path)
    ap.add_argument("--source",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    candidate=make_candidate(scenario=a.scenario,source_boundary=a.source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(candidate,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "output":str(a.output),
        "source_hyrec_sha":candidate["source_rec_full_C_stdout_sha256"],
        "activation":candidate["activation"],
        "candidate":candidate["candidate_initial_gas"],
    },indent=2))
