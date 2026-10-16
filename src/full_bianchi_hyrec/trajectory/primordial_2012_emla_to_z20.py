"""Original-source EMLA2s2p H+Tm stage from reviewed RT stop to z=20 stencil.

The independent Python state is advanced on the original fixed ln(a) grid.
Accepted FULL photon history ends at the U6 boundary and is never read or
written here: source history.c selects EMLA2s2p at the first U7 input.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

START_J=10972
START_GLOBAL_IZ=29195
TARGET_Z=20.0
SOURCE_X0=-math.log(8001.0)
SOURCE_TARGET_X=-math.log(21.0)
SOURCE_STENCIL_I=math.floor((SOURCE_TARGET_X-SOURCE_X0)/SOURCE_DLNA)
END_GLOBAL_IZ=SOURCE_STENCIL_I+2
END_J=END_GLOBAL_IZ-18223
EXTRA_ACCEPTED=END_J-START_J
SAMPLE_J=(START_J,START_J+1,START_J+2)+tuple(START_J+2048*k for k in range(1,20))+(51773,51774,51775)
MAX_COMMON_SAMPLES=32
U6_STOP_NPZ_SHA256="417cd6ab5877708554c5672f0e437332c75899334515989835d9008d7d84d463"
U6_STOP_JSON_SHA256="bc6066283de4d13f78f79545199a438b14dd2808378f99a173fa2724a88adc12"
U6_VERIFICATION_SHA256="51ea46201dd17f6e6110fad623074d9adae49d1bb4390fef19fe11b4e908f2f1"
U6_C_STDOUT_SHA256="7e2b765f6899050d73cf5c4e67a1c6fe898e8d2bebe54f8d86470e270a14beaa"
U6_ADMISSION_SHA256="4356d9cc78970d7d6200421411bd69b1670eb99c0ed9dbddb02cbc1b6d276ac1"


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def source_cubic_weights(frac:float)->tuple[float,float,float,float]:
    """Exact algebraic weights of Oct-2012 hyrectools.c::rec_interp1d."""
    if not (math.isfinite(frac) and 0<=frac<=1):
        raise ValueError("SOURCE_CUBIC_FRACTION_DOMAIN")
    return (-frac*(1-frac)*(2-frac)/6,
            (1+frac)*(1-frac)*(2-frac)/2,
            (1+frac)*frac*(2-frac)/2,
            -(1+frac)*frac*(1-frac)/6)


def source_z20_cubic(values:np.ndarray)->dict:
    """Interpolate four independently integrated source-grid state nodes."""
    y=np.asarray(values,dtype=float)
    local_i=SOURCE_STENCIL_I-18223
    if y.shape!=(END_J+1,) or not np.all(np.isfinite(y[local_i-1:local_i+3])):
        raise ValueError("SOURCE_Z20_STENCIL_MISSING")
    raw=(SOURCE_TARGET_X-SOURCE_X0)/SOURCE_DLNA
    if math.floor(raw)!=SOURCE_STENCIL_I: raise ValueError("SOURCE_Z20_STENCIL_INDEX_DRIFT")
    frac=raw-SOURCE_STENCIL_I
    w=source_cubic_weights(frac)
    v=sum(weight*float(y[local_i-1+k]) for k,weight in enumerate(w))
    return {"value":v,"index":SOURCE_STENCIL_I,"fraction":frac,
            "weights":list(w),"source_globals":list(range(SOURCE_STENCIL_I-1,SOURCE_STENCIL_I+3))}


def load_admitted_u6_stop(npz:Path,sidecar:Path,verification:Path,c_stdout:Path,
                          admission:Path)->tuple[dict[str,np.ndarray],dict]:
    for path,want in ((npz,U6_STOP_NPZ_SHA256),(sidecar,U6_STOP_JSON_SHA256),
                      (verification,U6_VERIFICATION_SHA256),(c_stdout,U6_C_STDOUT_SHA256),
                      (admission,U6_ADMISSION_SHA256)):
        if sha256(path)!=want: raise ValueError(f"U6_PINNED_INPUT_SHA_MISMATCH:{Path(path).name}")
    meta=json.loads(Path(sidecar).read_text()); report=json.loads(Path(verification).read_text())
    review=json.loads(Path(admission).read_text())
    if (review.get("decision")!="SCOPED_PASS" or review.get("stop_npz_sha256")!=U6_STOP_NPZ_SHA256 or
            review.get("verification_sha256")!=U6_VERIFICATION_SHA256 or
            review.get("native_c_stdout_sha256")!=U6_C_STDOUT_SHA256 or
            review.get("historic_u5_original_status")!="FAIL" or
            review.get("historic_u5_average_gate")!="HOLD_ORIGINAL_TOLERANCE_NOT_MET"):
        raise ValueError("U6_SCOPED_ADMISSION_MISMATCH")
    if (meta.get("phase")!="STOP" or meta.get("accepted_extra")!=2604 or
            meta.get("npz_sha256")!=U6_STOP_NPZ_SHA256 or
            report.get("status")!="STOP_BEFORE_EMLA2S2P_RT_BOUNDARY" or
            report.get("accepted_extra")!=2604):
        raise ValueError("U6_STOP_SEMANTICS_MISMATCH")
    with np.load(npz,allow_pickle=False) as handle:
        a={k:np.array(handle[k],copy=True) for k in handle.files}
    nodes=("global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")
    for key in nodes:
        if key not in a or a[key].shape!=(START_J+1,):
            raise ValueError(f"U6_STATE_SHAPE:{key}")
    for key in ("hydrogen_rhs_dln_a","thermal_rhs_dln_a"):
        if key not in a or a[key].shape!=(START_J,) or not np.all(np.isfinite(a[key][-2:])):
            raise ValueError(f"U6_DERIVATIVE_MEMORY_SHAPE:{key}")
    if (int(a["global_iz"][-1])!=START_GLOBAL_IZ or
            float(a["xHeII"][-1])!=0. or bool(a["post_saha"][-1]) or
            not all(math.isfinite(float(a[key][-1])) for key in ("z","xe","Tm_K"))):
        raise ValueError("U6_STOP_STAGE_BOUNDARY_MISMATCH")
    boundary={"hydrogen_prev":float(a["hydrogen_rhs_dln_a"][-1]),
              "hydrogen_prev2":float(a["hydrogen_rhs_dln_a"][-2]),
              "thermal_prev":float(meta["thermal_prev"]),
              "thermal_prev2":float(meta["thermal_prev2"]),
              "u6_admission_sha256":U6_ADMISSION_SHA256}
    for key in boundary:
        if key!="u6_admission_sha256" and not math.isfinite(boundary[key]):
            raise ValueError(f"U6_MEMORY_NONFINITE:{key}")
    return a,boundary


def continue_emla_to_z20(checkpoint:dict[str,np.ndarray],boundary:dict,
                         c:HyRec2012Cosmology,source,*,common_input_oracle:Callable,
                         checkpoint_callback:Callable[[dict],None]|None=None,
                         max_extra_accepted:int=EXTRA_ACCEPTED)->dict:
    if not (1<=max_extra_accepted<=EXTRA_ACCEPTED):raise ValueError("U7_ACCEPTED_CAP_INVALID")
    if not callable(common_input_oracle) or not callable(getattr(common_input_oracle,"thermal_rhs",None)):
        raise ValueError("U7_COMMON_INPUT_C_ORACLE_REQUIRED")
    ncap=START_J+max_extra_accepted
    node_names=("global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")
    nodes={key:np.empty(ncap+1,dtype=checkpoint[key].dtype) for key in node_names}
    for key in node_names:nodes[key][:START_J+1]=checkpoint[key]
    h_rhs=np.full(ncap,np.nan);t_rhs=np.full(ncap,np.nan)
    h_rhs[:START_J]=checkpoint["hydrogen_rhs_dln_a"]
    t_rhs[:START_J]=checkpoint["thermal_rhs_dln_a"]
    h_prev=boundary["hydrogen_prev"];h_prev2=boundary["hydrogen_prev2"]
    t_prev=boundary["thermal_prev"];t_prev2=boundary["thermal_prev2"]
    accepted=START_J;attempted=0;samples=[];common_max={"hydrogen":0.,"thermal":0.}
    status="BOUNDED_EMLA_INTERVAL_COMPLETE_BEFORE_Z20_STENCIL"
    stop_failure=None

    def emit(phase:str,failure=None):
        if checkpoint_callback is None:return
        n=accepted
        checkpoint_callback({"phase":phase,"accepted_extra":n-START_J,
            "emla_evaluations_attempted":attempted,"status":status,
            **{key:nodes[key][:n+1].copy() for key in node_names},
            "hydrogen_rhs_dln_a":h_rhs[:n].copy(),"thermal_rhs_dln_a":t_rhs[:n].copy(),
            "hydrogen_prev":h_prev,"hydrogen_prev2":h_prev2,
            "thermal_prev":t_prev,"thermal_prev2":t_prev2,
            "common_input_sample_j":tuple(samples),"common_input_max":dict(common_max),
            "failure":failure})

    emit("START")
    try:
        while accepted<ncap:
            j=accepted;iz=int(nodes["global_iz"][j]);z=float(nodes["z"][j])
            xe=float(nodes["xe"][j]);tm=float(nodes["Tm_K"][j]);tr=c.T0_K*(1+z)
            if j<START_J or j>=END_J or iz!=j+18223:
                raise ValueError(f"U7_SOURCE_GRID_STAGE_INDEX:j={j}:iz={iz}")
            if not (0<xe<1 and 0<tm<=tr and float(nodes["xHeII"][j])==0. and
                    not bool(nodes["post_saha"][j])):
                status="HOLD_NEXT_STAGE_REQUIRED:EMLA_STATE_DOMAIN"
                stop_failure={"reason":status,"input_j":j,"last_accepted_j":accepted};break
            if not (8.617343e-5*tr/(c.fsR*c.fsR*c.meR)>.004 and tm/tr>.1):
                status="HOLD_NEXT_STAGE_REQUIRED:THERMAL_TABLE_OR_RATIO_BOUNDARY"
                stop_failure={"reason":status,"input_j":j,"last_accepted_j":accepted};break
            attempted+=1
            f=float(source.hydrogen_rhs_ln_a(z=z,x_HII=xe,x_e=xe,Tm_K=tm,fsR=c.fsR,meR=c.meR))
            g=float(source_thermal_rhs(c,xe,tm,z))
            if not math.isfinite(f) or not math.isfinite(g):
                raise ArithmeticError(f"U7_NONFINITE_EMLA_RHS:j={j}")
            if j in SAMPLE_J:
                if len(samples)>=MAX_COMMON_SAMPLES:raise RuntimeError("U7_COMMON_INPUT_CAP")
                c_f=float(common_input_oracle(j,z,xe,tm));c_g=float(common_input_oracle.thermal_rhs(xe,tm,z))
                h_err=abs(f-c_f)/max(abs(f),abs(c_f),1e-13)
                t_err=abs(g-c_g)/max(1.,abs(c_g))
                if not math.isfinite(h_err) or h_err>3e-10:
                    raise ArithmeticError(f"U7_COMMON_EMLA_H_RHS:j={j}:scaled={h_err}")
                if not math.isfinite(t_err) or t_err>2e-10:
                    raise ArithmeticError(f"U7_COMMON_EMLA_T_RHS:j={j}:scaled={t_err}")
                samples.append(j)
                common_max["hydrogen"]=max(common_max["hydrogen"],h_err)
                common_max["thermal"]=max(common_max["thermal"],t_err)
            nextj=j+1;zn=c.redshift(iz+1)
            nextxe=xe+SOURCE_DLNA*(1.25*f-.25*h_prev2)
            nexttm=tm+SOURCE_DLNA*(1.25*g-.25*t_prev2)
            if not (0<nextxe<1 and 0<nexttm<=c.T0_K*(1+zn)):
                status="HOLD_NEXT_STAGE_REQUIRED:EMLA_ACCEPTED_STATE_DOMAIN"
                stop_failure={"reason":status,"input_j":j,"candidate_j":nextj,
                    "candidate_xe":nextxe,"candidate_Tm_K":nexttm,
                    "last_accepted_j":accepted};break
            h_rhs[j]=f;t_rhs[j]=g
            nodes["global_iz"][nextj]=iz+1;nodes["z"][nextj]=zn
            nodes["xe"][nextj]=nextxe;nodes["xHII"][nextj]=nextxe
            nodes["xH1s"][nextj]=1-nextxe
            nodes["xHeII"][nextj]=0.;nodes["post_saha"][nextj]=False
            nodes["Tm_K"][nextj]=nexttm
            h_prev2,h_prev=h_prev,f;t_prev2,t_prev=t_prev,g
            accepted=nextj
            if accepted-START_J in (1,2) or (accepted-START_J)%4096==0:
                emit(f"ACCEPTED_{accepted-START_J:05d}")
        if accepted==END_J:status="STOP_AT_Z20_CUBIC_STENCIL"
        emit("STOP",stop_failure)
    except BaseException as exc:
        emit("EXCEPTION",{"type":type(exc).__name__,"message":str(exc),"last_accepted_j":accepted})
        raise
    n=accepted
    donor=None
    if n==END_J:
        donor={"z_ref":20.0,"xe":source_z20_cubic(nodes["xe"]),
               "Tm_K":source_z20_cubic(nodes["Tm_K"]),
               "source_model":"original Oct-2012 HyRec q=0 EMLA2s2p",
               "activation":False,"rei_initial_condition_replaced":False,
               "claim_ceiling":"candidate primordial q=0 donor; no REI production or optical-depth prediction"}
    return {"status":status,"failure":stop_failure,"accepted_extra":n-START_J,
        "emla_evaluations":attempted,
        "samples":samples,"common_max":common_max,"nodes":{k:nodes[k][:n+1] for k in node_names},
        "hydrogen_rhs_dln_a":h_rhs[:n],"thermal_rhs_dln_a":t_rhs[:n],
        "hydrogen_prev":h_prev,"hydrogen_prev2":h_prev2,
        "thermal_prev":t_prev,"thermal_prev2":t_prev2,"candidate_donor":donor}
