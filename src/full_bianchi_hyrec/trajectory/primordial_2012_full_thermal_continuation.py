"""Bounded source-native H+Tm FULL continuation to the original RT switch.

This begins at the preserved U5 accepted STOP, never restarts primordial
evolution, and stops before original history.c's EMLA branch.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA, causal_incoming_from_accepted_histories
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, populate_original_full_atomic,
    complete_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

START_J=8368
END_J=10972
START_GLOBAL_IZ=26591
END_GLOBAL_IZ=29195
EXTRA_ACCEPTED=END_J-START_J
SAMPLE_J=(8368,8369,8624,8880,9136,9392,9648,9904,10160,10416,
          10672,10928,10970,10971)
U5_STOP_NPZ_SHA256="09e702caf0bc0ce0edb1ce629477669c55e59c7fff34cd7298d759613719528f"
U5_STOP_JSON_SHA256="9fac62e0ae2edebb6f5ff42b0c73a7b1d4b5293cb5ac9bdd40971c9f7a5ee50d"
U5_ORIGINAL_VERIFICATION_SHA256="9453a59c6c2a19c4c3053e9b194e49cca30d736b7fee0849676f4329a41787a8"
U5_SCOPED_AUDIT_SHA256="1ee372333f3fc628a8dfa64c6bbf6b7e2fcad00f8e47a9bc798fa262bb9f6722"
FIELDS={"global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha",
        "hydrogen_rhs_dln_a","virtual_out","average_virtual","lyman_out",
        "matrix_residual","thermal_rhs_dln_a","thermal_prev_after","thermal_prev2_after"}


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def require_scoped_admission(path: Path) -> dict:
    """Fail closed until a fresh independent reviewer admits this exact U5 node."""
    receipt=json.loads(Path(path).read_text())
    if (receipt.get("decision")!="SCOPED_PASS" or
            receipt.get("reviewed_audit_sha256")!=U5_SCOPED_AUDIT_SHA256 or
            receipt.get("reviewed_u5_stop_sha256")!=U5_STOP_NPZ_SHA256 or
            receipt.get("original_verification_status")!="FAIL" or
            receipt.get("original_average_gate")!="HOLD_ORIGINAL_TOLERANCE_NOT_MET"):
        raise ValueError("U5_SCOPED_ADMISSION_MISSING_OR_MISMATCH")
    return receipt


def load_admitted_u5_stop(npz:Path,sidecar:Path,verification:Path,audit:Path,
                          admission:Path) -> tuple[dict[str,np.ndarray],dict]:
    for path,want in ((npz,U5_STOP_NPZ_SHA256),(sidecar,U5_STOP_JSON_SHA256),
                      (verification,U5_ORIGINAL_VERIFICATION_SHA256),
                      (audit,U5_SCOPED_AUDIT_SHA256)):
        if sha256(path)!=want: raise ValueError(f"U5_PINNED_INPUT_SHA_MISMATCH:{Path(path).name}")
    meta=json.loads(Path(sidecar).read_text())
    original=json.loads(Path(verification).read_text())
    scoped=json.loads(Path(audit).read_text())
    if (meta.get("phase")!="STOP" or meta.get("accepted_extra")!=7364 or
            meta.get("event_j")!=8366 or meta.get("branch_steps_after_event")!=2 or
            meta.get("npz_sha256")!=U5_STOP_NPZ_SHA256 or
            original.get("status")!="FAIL" or
            "row=2218 channel=average bin=8" not in original.get("first_failure",{}).get("message","") or
            scoped.get("state_causal_thermal_gate")!="PASS" or
            scoped.get("original_average_gate")!="HOLD_ORIGINAL_TOLERANCE_NOT_MET"):
        raise ValueError("U5_REVIEWED_SEMANTICS_MISMATCH")
    receipt=require_scoped_admission(admission)
    with np.load(npz,allow_pickle=False) as handle:
        if set(handle.files)!=FIELDS: raise ValueError("U5_STOP_FIELD_SET_MISMATCH")
        a={k:np.array(handle[k],copy=True) for k in handle.files}
    if (a["global_iz"].shape!=(START_J+1,) or
            a["virtual_out"].shape!=(NVIRT,START_J) or
            a["average_virtual"].shape!=(NVIRT,START_J) or
            a["lyman_out"].shape!=(3,START_J) or
            a["hydrogen_rhs_dln_a"].shape!=(START_J,) or
            a["thermal_rhs_dln_a"].shape!=(START_J,) or
            int(a["global_iz"][-1])!=START_GLOBAL_IZ or
            float(a["xHeII"][-1])!=0. or bool(a["post_saha"][-1]) or
            not np.all(np.isfinite(a["virtual_out"])) or
            not np.all(np.isfinite(a["lyman_out"]))):
        raise ValueError("U5_STOP_BOUNDARY_OR_CAUSAL_HISTORY_MISMATCH")
    if not all(math.isfinite(float(meta[key])) for key in ("thermal_prev","thermal_prev2")):
        raise ValueError("U5_THERMAL_MEMORY_MISSING")
    return a,{"thermal_prev":float(meta["thermal_prev"]),
              "thermal_prev2":float(meta["thermal_prev2"]),
              "admission_sha256":sha256(admission),"admission":receipt}


def continue_full_thermal_to_rt(checkpoint:dict[str,np.ndarray],boundary:dict,
                                c:HyRec2012Cosmology,source,*,
                                common_input_oracle:Callable,
                                checkpoint_callback:Callable[[dict],None]|None=None,
                                max_extra_accepted:int=EXTRA_ACCEPTED) -> dict:
    """Accept source-owned coupled H+Tm steps only, ending at RT input."""
    if not (1<=max_extra_accepted<=EXTRA_ACCEPTED): raise ValueError("U6_ACCEPTED_CAP_INVALID")
    if not callable(common_input_oracle) or not callable(getattr(common_input_oracle,"thermal_rhs",None)):
        raise ValueError("U6_COMMON_INPUT_C_ORACLE_REQUIRED")
    table=_canonical_twophoton_table(source.table.archive_path)
    ncap=START_J+max_extra_accepted
    node_names=("global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")
    nodes={k:np.empty(ncap+1,dtype=checkpoint[k].dtype) for k in node_names}
    for k in node_names: nodes[k][:START_J+1]=checkpoint[k]
    vout=np.full((NVIRT,ncap),np.nan); avgout=np.full((NVIRT,ncap),np.nan)
    lyout=np.full((3,ncap),np.nan)
    rhs=np.full(ncap,np.nan); trhs=np.full(ncap,np.nan); residual=np.full(ncap,np.nan)
    tprev_after=np.full(ncap,np.nan); tprev2_after=np.full(ncap,np.nan)
    for dst,key in ((vout,"virtual_out"),(avgout,"average_virtual"),(lyout,"lyman_out")):
        dst[:,:START_J]=checkpoint[key]
    rhs[:START_J]=checkpoint["hydrogen_rhs_dln_a"]
    trhs[:START_J]=checkpoint["thermal_rhs_dln_a"]
    residual[:START_J]=checkpoint["matrix_residual"]
    tprev_after[:START_J]=checkpoint["thermal_prev_after"]
    tprev2_after[:START_J]=checkpoint["thermal_prev2_after"]
    tprev=boundary["thermal_prev"]; tprev2=boundary["thermal_prev2"]
    accepted=START_J; full_evals=0; samples=[]
    common_max={k:0. for k in ("rhs","thermal_rhs","virtual","average","lyman")}
    status="BOUNDED_INTERVAL_COMPLETE_BEFORE_RT"

    def emit(phase:str,failure=None):
        if checkpoint_callback is None: return
        n=accepted
        checkpoint_callback({"phase":phase,"accepted_extra":n-START_J,
            **{k:nodes[k][:n+1].copy() for k in node_names},
            "hydrogen_rhs_dln_a":rhs[:n].copy(),"thermal_rhs_dln_a":trhs[:n].copy(),
            "thermal_prev_after":tprev_after[:n].copy(),"thermal_prev2_after":tprev2_after[:n].copy(),
            "virtual_out":vout[:,:n].copy(),"average_virtual":avgout[:,:n].copy(),
            "lyman_out":lyout[:,:n].copy(),"matrix_residual":residual[:n].copy(),
            "thermal_prev":tprev,"thermal_prev2":tprev2,
            "full_evaluations":full_evals,"samples":tuple(samples),
            "common_max":dict(common_max),"failure":failure})

    emit("START")
    try:
        while accepted<ncap:
            j=accepted
            if j>=END_J: break
            iz=int(nodes["global_iz"][j]); z=float(nodes["z"][j]); xe=float(nodes["xe"][j]); tm=float(nodes["Tm_K"][j])
            tr=c.T0_K*(1+z); tr_rescaled=8.617343e-5*tr/(c.fsR*c.fsR*c.meR)
            if tr_rescaled<=.004 or tm/tr<=.1:
                status="HOLD_NEXT_STAGE_REQUIRED:THERMAL_TABLE_OR_RATIO_BOUNDARY"; break
            if not (0<xe<1 and 0<tm<=tr and float(nodes["xHeII"][j])==0. and
                    not bool(nodes["post_saha"][j])):
                raise FloatingPointError(f"U6_STATE_DOMAIN:j={j}")
            inc=causal_incoming_from_accepted_histories(
                energies_eV=table.energy_eV,virtual_history=vout[:,:j],lyman_history=lyout[:,:j],
                z_start=float(nodes["z"][0]),iz=j,z_face=z,dlna=SOURCE_DLNA,shear_q=0.)
            t=math.nextafter(tm,0.) if tm==tr else tm
            snap=populate_original_full_atomic(source,z=z,xHII=xe,xe=xe,Tm_K=t,
                incoming_virtual=inc.virtual_distortion[0],incoming_lyman=inc.lya_lyb_incoming_distortion[0])
            out=complete_original_full_atomic(snap); full_evals+=1
            if (not math.isfinite(out.dxHII_dln_a) or
                    not math.isfinite(out.normalized_matrix_residual) or
                    out.normalized_matrix_residual>2e-10):
                raise ArithmeticError(f"U6_FULL_SOURCE_NONFINITE_OR_SCHUR:j={j}")
            for name,val,shape in (("virtual",out.outgoing_virtual,(NVIRT,)),
                                   ("average",out.average_virtual,(NVIRT,)),
                                   ("lyman",out.outgoing_lyman,(3,))):
                if np.asarray(val).shape!=shape or not np.all(np.isfinite(val)):
                    raise ArithmeticError(f"U6_FULL_PHOTON_INVALID:j={j}:{name}")
            g=source_thermal_rhs(c,xe,t,z)
            if not math.isfinite(g): raise ArithmeticError(f"U6_THERMAL_RHS_NONFINITE:j={j}")
            if j in SAMPLE_J:
                ref=common_input_oracle(j,z,xe,0.,t,vout[:,:j],lyout[:,:j]); samples.append(j)
                hdiff=abs(out.dxHII_dln_a-float(ref["rhs"])) / max(1.,abs(float(ref["rhs"])))
                t_c=float(common_input_oracle.thermal_rhs(xe,t,z))
                tdiff=abs(g-t_c)/max(1.,abs(t_c))
                if not math.isfinite(hdiff) or hdiff>2e-10: raise ArithmeticError(f"U6_COMMON_H_RHS:j={j}")
                if not math.isfinite(tdiff) or tdiff>2e-10: raise ArithmeticError(f"U6_COMMON_T_RHS:j={j}")
                common_max["rhs"]=max(common_max["rhs"],hdiff)
                common_max["thermal_rhs"]=max(common_max["thermal_rhs"],tdiff)
                fbbv=1/np.expm1(table.energy_eV/(8.617343e-5*tr))
                fbbl=1/np.expm1(np.array((10.198714553953742,12.087365397278509,12.748393192442178))/(8.617343e-5*tr))
                for name,p,bb in (("virtual",out.outgoing_virtual,fbbv),
                                  ("average",out.average_virtual,fbbv),
                                  ("lyman",out.outgoing_lyman,fbbl)):
                    q=np.asarray(ref[name],dtype=float)
                    tol=1e-7*np.maximum(np.abs(p),np.abs(q))+1e-10*bb
                    ratio=np.abs(p-q)/tol
                    if q.shape!=p.shape or not np.all(np.isfinite(ratio)) or np.any(ratio>1):
                        raise ArithmeticError(f"U6_COMMON_PHOTON:j={j}:{name}")
                    common_max[name]=max(common_max[name],float(np.max(ratio)))
            rhs[j]=out.dxHII_dln_a; trhs[j]=g; residual[j]=out.normalized_matrix_residual
            vout[:,j]=out.outgoing_virtual; avgout[:,j]=out.average_virtual; lyout[:,j]=out.outgoing_lyman
            nextj=j+1; zn=c.redshift(iz+1)
            nodes["global_iz"][nextj]=iz+1; nodes["z"][nextj]=zn
            nodes["xe"][nextj]=xe+SOURCE_DLNA*(1.25*rhs[j]-.25*rhs[j-2])
            nodes["xHII"][nextj]=nodes["xe"][nextj]
            nodes["xH1s"][nextj]=1-nodes["xe"][nextj]
            nodes["xHeII"][nextj]=0.; nodes["post_saha"][nextj]=False
            nodes["Tm_K"][nextj]=tm+SOURCE_DLNA*(1.25*g-.25*tprev2)
            tprev2,tprev=tprev,g
            tprev_after[j]=tprev; tprev2_after[j]=tprev2
            if not (0<float(nodes["xe"][nextj])<1 and
                    0<float(nodes["Tm_K"][nextj])<=c.T0_K*(1+zn)):
                raise FloatingPointError(f"U6_ACCEPTED_STATE_DOMAIN:j={j}")
            accepted=nextj
            if (accepted-START_J)%512==0: emit(f"ACCEPTED_{accepted-START_J:04d}")
        if accepted==END_J:
            status="STOP_BEFORE_EMLA2S2P_RT_BOUNDARY"
        emit("STOP")
    except BaseException as exc:
        emit("EXCEPTION",{"type":type(exc).__name__,"message":str(exc),"last_accepted_j":accepted})
        raise
    n=accepted
    return {"status":status,"accepted_extra":n-START_J,"full_evaluations":full_evals,
        "samples":samples,"common_max":common_max,"thermal_prev":tprev,"thermal_prev2":tprev2,
        "nodes":{k:nodes[k][:n+1] for k in node_names},
        "hydrogen_rhs_dln_a":rhs[:n],"thermal_rhs_dln_a":trhs[:n],
        "thermal_prev_after":tprev_after[:n],"thermal_prev2_after":tprev2_after[:n],
        "virtual_out":vout[:,:n],"average_virtual":avgout[:,:n],"lyman_out":lyout[:,:n],
        "matrix_residual":residual[:n]}
