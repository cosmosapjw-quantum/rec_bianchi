#!/usr/bin/env python3
"""Reference-to-reference recombination comparison with exact source/output SHA.

The three independent *upstream binaries* must have already run with the
identical massless-Neff=3 FLRW inputs produced in the isolated research runner.
This script does NOT compute a REC_BIANCHI xe(z) history or claim it reproduces
the reference when the local full trajectory has not run.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

from full_bianchi_hyrec.trajectory.recombination_reference import (
    RecombinationReferenceKind,PrimordialReferenceHistory,
    compare_primordial_references,original_hyrec_atomic_table_supported_redshift,
)

PHYSICAL_COSMOLOGY_KEYS=(
    "h","Omega_b","Omega_cb","T0_K","Y_He_mass_fraction","N_eff_massless",
    "neutrino_mass_eV","Omega_r_h2","Omega_de_h2",
    "Omega_b_h2","Omega_cb_h2",
)
SOURCE_IDS={
    "HyRec_2012_FULL":"48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27",
    "HyRec2_2020":"09e8243d0e08edd3603a94dfbc445ae06cafe139",
    "RECFAST_1.7":"b34efc0f409050a980be5deca7d016a01bd13631",
}


def read_native_references(evidence_root:Path):
    contract=json.loads((evidence_root/"COSMOLOGY.json").read_text())
    source=json.loads((evidence_root/"REFERENCE_EXECUTION.json").read_text())
    physics={k:contract[k] for k in PHYSICAL_COSMOLOGY_KEYS}
    physics_digest=hashlib.sha256(
        json.dumps(physics,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()
    if abs(physics["N_eff_massless"]-3)>1e-14 or physics["neutrino_mass_eV"]!=0:
        raise ValueError("massless neutrino fixed FLRW comparison lane requires Neff=3.0")
    result={}
    for label,k in (("HyRec_2012_FULL",RecombinationReferenceKind.HYREC_2012),
                    ("HyRec2_2020",RecombinationReferenceKind.HYREC2_2020),
                    ("RECFAST_1.7",RecombinationReferenceKind.RECFAST_17)):
        record=source[label]
        path=evidence_root/record["output_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record["output_sha256"]:
            raise ValueError("upstream reference output has changed: SHA256 mismatch")
        if SOURCE_IDS[label]!=contract[{
            "HyRec_2012_FULL":"source_2012",
            "HyRec2_2020":"source_hyrec2",
            "RECFAST_1.7":"source_recfast"
        }[label]] and label!="HyRec_2012_FULL":
            raise ValueError("source code identity changed unexpectedly")
        history=PrimordialReferenceHistory.from_native_output(
            path,kind=k,
            y_he_mass=contract["Y_He_mass_fraction"],
            cmb_temperature_K=contract["T0_K"],
            source_identity=SOURCE_IDS[label],
            cosmology_sha256=physics_digest,
            input_sha256=record["stdin_sha256"],
        )
        result[label]=history
    return contract,physics_digest,result


def run(evidence_root:Path, outdir:Path):
    if outdir.exists() and any(outdir.iterdir()):
        raise ValueError("output directory is not empty; preserve prior evidence")
    outdir.mkdir(parents=True,exist_ok=True)
    contract,cosmo,ref=read_native_references(evidence_root)
    parent=ref["HyRec_2012_FULL"]
    h2=ref["HyRec2_2020"]
    fast=ref["RECFAST_1.7"]
    windows=[("hydrogen",600,1600),("helium",1600,3000),
             ("post_recombination_no_reionization",20,200)]
    comparisons={}
    for title,lo,hi in windows:
        for candidate in (h2,fast):
            key=f"{title}::{candidate.kind.value}"
            comparisons[key]=compare_primordial_references(
                parent,candidate,z_min=lo,z_max=hi,step=10
            )
    z=np.array([20,100,300,600,800,1000,1100,1300,1500,1600,1800,2000,2500,3000],dtype=float)
    table=[]
    for zz in z:
        row={"z":int(zz)}
        for title,history in ref.items():
            row["xe_"+title]=float(history.evaluate([zz])[0])
            if history.matter_temperature_K is not None:
                row["Tm_K_"+title]=float(history.evaluate([zz],property="T_m_K")[0])
        table.append(row)
    csvname=outdir/"REFERENCE_SAMPLES.csv"
    with csvname.open("w",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=list(table[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(table)

    valid=original_hyrec_atomic_table_supported_redshift(
        cmb_temperature_K=contract["T0_K"]
    )
    verdict={
      "schema":"rec.primordial_recombination.reference_codes.v1",
      "comparison_type":"THREE_EXECUTED_UPSTREAM_REFERENCES_NOT_REC_NATIVE_XE_HISTORY",
      "source_locked_flrw_cosmology":{k:contract[k] for k in PHYSICAL_COSMOLOGY_KEYS},
      "cosmology_canonical_sha256":cosmo,
      "upstream_sources":{label:{
           "kind":h.kind.value,
           "source_identity":h.source_identity,
           "output_sha256":h.output_sha256,
           "input_sha256":h.input_sha256,
           "rows":len(h.redshift),
           "redshift_min":float(h.redshift[-1]),
           "redshift_max":float(h.redshift[0]),
           "temperature_units":"Kelvin" if h.matter_temperature_K is not None else "NOT_AVAILABLE_IN_RECFAST_SOURCE",
       } for label,h in ref.items()},
      "electron_fraction_definition":"xe=n_e/n_H (may exceed 1 due to HeII, HeIII)",
      "T_m_conversion_original_HyRec2012":"T_m[K]=third_output*(1+z)*T_CMB0[K]",
      "tr_original_HyRec_atomic_table_valid_redshift_for_T0":valid,
      "flrw_history_reference_code_intercomparisons":comparisons,
      "native_REC_Bianchi_or_flrw_full_xe_history":"NOT_COMPUTED_NOT_COMPARED",
      "current_REC_atomic_table_native_parity":"SEPARATE_NATIVE_C_COMPARISON_EXPECTED",
      "reionization_history_for_z_4_to_20":"NOT_PROVIDED_BY_ANY_OF_THE_ABOVE_REFERENCE_RUNS",
      "scientific_admission":"REFERENCE_BENCHMARKS_PREPARED_ONLY",
      "difference_interpretation":"RECFAST 1.7 has different effective 3-level atomic approximations, not a byte-identical HyRec source. Do not require exact xe agreement.",
      "reference_sample_csv_sha256":hashlib.sha256(csvname.read_bytes()).hexdigest(),
    }
    p=outdir/"REFERENCE_INTERCOMPARISON.json"
    p.write_text(json.dumps(verdict,indent=2)+"\n")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8.5,5.6))
    for label,h in ref.items():
        use=(h.redshift>=20)&(h.redshift<=3000)
        ax.semilogy(h.redshift[use],h.xe_per_hydrogen[use],
             label=label.replace("_"," "))
    ax.set_xlim(3000,0)
    ax.set_ylim(1e-4,2.)
    ax.set_ylabel("Free electrons / hydrogen nucleus")
    ax.set_xlabel("Redshift z")
    ax.set_title("Matched-parameter reference recombination histories (NO REC full history)")
    ax.legend()
    ax.grid(True,alpha=.2,which="both")
    fig.tight_layout();fig.savefig(outdir/"REFERENCE_XE_CURVES.png",dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.5,5.6))
    for label,h in ref.items():
        if h.matter_temperature_K is None:continue
        zrange=(h.redshift>=20)&(h.redshift<=2000)
        ax.loglog(1+h.redshift[zrange],h.matter_temperature_K[zrange],
                  label=label)
    ax.set_xlabel("1 + z")
    ax.set_ylabel("Matter temperature Tm [K]")
    ax.set_title("Original HyRec / HyRec-2 thermal history (RECFAST Tm unavailable)")
    ax.grid(True,alpha=.2,which="both")
    ax.legend()
    fig.tight_layout();fig.savefig(outdir/"REFERENCE_TM_CURVES.png",dpi=170);plt.close(fig)
    print(json.dumps({
      "normalized_reference_domain":[round(x,2) for x in valid],
      "comparisons":{k:(v["maximum_abs_relative_xe_difference"],v["redshift_at_max"])
                     for k,v in comparisons.items()},
      "samples":len(table),"physical_production_claim":False,
    },indent=2))
    return verdict

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--evidence-root",type=Path,required=True)
    cli.add_argument("--outdir",type=Path,required=True)
    a=cli.parse_args()
    run(a.evidence_root,a.outdir)

if __name__=="__main__":
    main()
