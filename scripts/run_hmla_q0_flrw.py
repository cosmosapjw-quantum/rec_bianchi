#!/usr/bin/env python3
"""Execute truly independently integrated REC HMLA2s2p H-only+Tm FLRW histories.

Compares an actual local ODE solution (not a copy/interpolation of upstream
ionization) with the exactly SHA-locked original HyRec2012 FULL output, and
reports physical-model error separately from within-model numerical refinement.
"""
from __future__ import annotations

import argparse,csv,hashlib,json,time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from full_bianchi_hyrec.trajectory.hmla_flrw import integrate_hmla_hydrogen
from verify_hmla_native_rhs import source,COSMOPARAMS

FULL_SHA="e772c8cdd19e20618a1f71c2104e542fbb7de287ecc8ee1c7ae06697af8bf906"
C_EMLA_SHA="75d4bd873fa45b941a58a2977c5f8206002fedead134499d2a16a976b49d38d6"


def run(full_path:Path,outdir:Path,*,nsteps:int=201,c_emla_path:Path|None=None):
    if outdir.exists() and any(outdir.iterdir()):
        raise ValueError("refusing overwrite of scientific results")
    if hashlib.sha256(full_path.read_bytes()).hexdigest()!=FULL_SHA:
        raise ValueError("wrong original HyRec2012 FULL source/history identity")
    outdir.mkdir(parents=True,exist_ok=True)
    model=source()
    reference=np.loadtxt(full_path,dtype=float)
    zref=reference[:,0][::-1]
    xref=reference[:,1][::-1]
    Tref=(reference[:,2]*COSMOPARAMS["tcmb0_K"]*(1.+reference[:,0]))[::-1]
    emla=None
    if c_emla_path is not None:
        if hashlib.sha256(c_emla_path.read_bytes()).hexdigest()!=C_EMLA_SHA:
            raise ValueError("original source C EMLA2s2p mode-switch SHA does not match")
        emla=np.loadtxt(c_emla_path,dtype=float)
        if emla.shape!=(8001,3) or not np.array_equal(emla[:,0],reference[:,0]):
            raise ValueError("original EMLA C and FULL sources use mismatched grid")
    if len(reference)!=8001 or not np.all(np.diff(zref)>0):
        raise ValueError("original 2012 reference not valid native history")
    records=[]
    histories=[]
    for name,rtol,atol in (
       ("coarse",3e-6,2e-8),
       ("baseline",2e-7,2e-9),
       ("tight",2e-9,2e-11),
    ):
        began=time.perf_counter()
        hist=integrate_hmla_hydrogen(
            model,z_initial=1600.,z_final=600.,points=nsteps,
            rtol=rtol,atol=atol,method="BDF",
        )
        secs=time.perf_counter()-began
        xfull=np.interp(hist.z,zref,xref)
        Tfull=np.interp(hist.z,zref,Tref)
        relx=hist.x_HII/xfull-1
        relT=hist.Tm_K/Tfull-1
        idx=int(np.argmax(np.abs(relx)))
        rec={
          "name":name,"rtol":rtol,"atol_x":atol,
          "wall_s":secs,
          "initial_ionization_source":"analytic first-order hydrogen post-Saha, own source Jacobian; no reference injection",
          "z_start":float(hist.z[0]),"z_end":float(hist.z[-1]),
          "x_end":float(hist.x_HII[-1]),"Tm_end_K":float(hist.Tm_K[-1]),
          "max_rel_deviation_vs_original_FULL_xe":float(abs(relx[idx])),
          "signed_deviation_at_max":float(relx[idx]),
          "redshift_of_max":float(hist.z[idx]),
          "max_rel_matter_T_deviation_vs_original_FULL":
             float(np.max(np.abs(relT))),
        }
        if emla is not None:
            xeC=np.interp(hist.z,emla[:,0][::-1],emla[:,1][::-1])
            c_rel=np.abs(hist.x_HII/xeC-1)
            rec["C_EMLA2s2p_hydrogen_relative_difference_max"]=float(np.max(c_rel))
            rec["C_EMLA2s2p_hydrogen_difference_max_redshift"]=float(hist.z[int(np.argmax(c_rel))])
        histories.append(hist)
        records.append(rec)
        print("RUN",json.dumps(rec),flush=True)
    tight=histories[-1]
    numerical={
        "coarse_to_tight_max_absolute_x_HII":
          float(np.max(abs(histories[0].x_HII-tight.x_HII))),
        "coarse_to_tight_max_rel_x_HII":
          float(np.max(abs(histories[0].x_HII/tight.x_HII-1))),
        "baseline_to_tight_max_absolute_x_HII":
          float(np.max(abs(histories[1].x_HII-tight.x_HII))),
        "baseline_to_tight_max_rel_x_HII":
          float(np.max(abs(histories[1].x_HII/tight.x_HII-1))),
        "baseline_to_tight_max_rel_Tm":
          float(np.max(abs(histories[1].Tm_K/tight.Tm_K-1))),
        "numerical_model_difference_ratio":
          float(np.max(abs(histories[1].x_HII/tight.x_HII-1)) /
                max(records[-1]["max_rel_deviation_vs_original_FULL_xe"],1e-30)),
    }
    if numerical["baseline_to_tight_max_rel_x_HII"]>2e-3:
        raise AssertionError("HMLA scientific integration has unacceptably large within-model solver error")
    rows=[]
    for i,z in enumerate(tight.z):
        rows.append({
            "z":float(z),
            "rec_native_q0_HMLA_HII":float(tight.x_HII[i]),
            "hyrec2012_full_xe":float(np.interp(z,zref,xref)),
            "rec_native_q0_Tm_K":float(tight.Tm_K[i]),
            "hyrec2012_full_Tm_K":float(np.interp(z,zref,Tref)),
            "difference_xHII_minus_full_xe":float(tight.x_HII[i]-np.interp(z,zref,xref)),
            "C_original_EMLA_xe":(
              float(np.interp(z,emla[:,0][::-1],emla[:,1][::-1]))
              if emla is not None else float("nan")
            ),
        })
    with (outdir/"REC_HMLA_Q0_TRAJECTORY.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    report={
       "schema":"rec.hmla2s2p.flrw_hydrogen_only.self_integrated.v1",
       "status":"ACTUAL_REC_PYTHON_SELF_INTEGRATED_PARTIAL_MODEL",
       "is_not":"original HyRec FULL, coupled helium reionization, full Bianchi transfer",
       "source_original_HyRec2012_archive_sha256":
         hashlib.sha256(Path(model.table.archive_path).read_bytes()).hexdigest(),
       "reference_HyRec_FULL_output_sha256":FULL_SHA,
       "original_C_EMLA2s2p_mode_switched_output_sha256":(C_EMLA_SHA if emla is not None else None),
       "source_mode_switch_in_reference":"#define MODEL FULL -> #define MODEL EMLA2s2p, original other C files unchanged",
       "cosmology":COSMOPARAMS,
       "source_helium":"neutral helium heat capacity included; ionic He fractions not evolved",
       "time_coordinate":"eta=ln a, dTm/deta=-2Tm+GammaC/H*(Tr-Tm)",
       "HMLA_mechanism":"original 2012 alpha2s alpha2p Dalpha beta2s beta2p R2p2s; C-factor; Ly-alpha Sobolev; no time-dependent line diffusion",
       "initial_conditions":"analytic first-order hydrogen post-Saha x_HII at z1600 (from own source Jacobian) and original-source Compton steady-state Tm; reference output NEVER used as IC",
       "runs":records,
       "numerical_convergence":numerical,
       "reference_comparison_qualifier":"Original FULL xe includes helium, ours equals xHII only; only partially comparable where helium neutral",
       "next_physics":"Full helium dynamics, Ly-alpha/nonthermal photon diffusion and source-owning coupling; no automatic science admission",
    }
    (outdir/"RUN_RESULTS.json").write_text(json.dumps(report,indent=2)+"\n")
    fig,ax=plt.subplots(figsize=(8.5,5.4))
    ax.semilogy(tight.z,tight.x_HII,label="REC new q=0, independent HMLA2s2p hydrogen ODE")
    use=(zref>=600)&(zref<=1600)
    ax.semilogy(zref[use],xref[use],label="Original HyRec FULL (includes He)",linestyle="--")
    if emla is not None:
        ax.semilogy(emla[:,0][::-1],emla[:,1][::-1],
                    label="Original C HyRec EMLA2s2p switch, includes He",linestyle=":")
    ax.invert_xaxis()
    ax.set_xlabel("Redshift z")
    ax.set_ylabel("Ionized hydrogen / H or xe / H")
    ax.set_title("Real REC H-only trajectory vs original HyRec FULL reference")
    ax.legend()
    ax.grid(True,which="both",alpha=.23)
    fig.tight_layout();fig.savefig(outdir/"REC_Q0_HMLA_XE_COMPARISON.png",dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.5,5.4))
    xfull=np.interp(tight.z,zref,xref)
    ax.plot(tight.z,100.*(tight.x_HII/xfull-1.))
    ax.invert_xaxis();ax.axhline(0,color="black",linewidth=.8)
    ax.set_xlabel("Redshift z");ax.set_ylabel("100 × [x_HII(REC) / xe(FULL) - 1] [%]")
    ax.set_title("Difference in physical source model, not code implementation residual")
    ax.grid(True,alpha=.22)
    fig.tight_layout();fig.savefig(outdir/"REC_Q0_HMLA_REL_DIFFERENCE.png",dpi=180)
    plt.close(fig)
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original-full",type=Path,required=True)
    parser.add_argument("--outdir",type=Path,required=True)
    parser.add_argument("--points",type=int,default=201)
    parser.add_argument("--c-emla",type=Path,default=None)
    a=parser.parse_args()
    run(a.original_full.resolve(),a.outdir.resolve(),nsteps=a.points,
        c_emla_path=(a.c_emla.resolve() if a.c_emla is not None else None))


if __name__=="__main__":
    main()
