"""Original Oct-2012 HyRec EMLA-to-Peebles H+Tm continuation to z=0.

The source-grid state and both two-step derivative memories are carried from
the independently reviewed U7 STOP. Original C history.c switches once, at
the first failed effective-rate table guard, to PEEBLES with Fudge=1. No
photon history is read or written in this late-time source stage.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K,LYA_FACT_CM3,LAMBDA_2S1S_S_INV
from full_bianchi_hyrec.trajectory.primitive_rates import SAHA_COEFFICIENT_CGS,IONIZATION_ENERGY_EV
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

START_GLOBAL_IZ=69999
SOURCE_IZH0=18223
START_J=START_GLOBAL_IZ-SOURCE_IZH0
SOURCE_NZ=math.floor(2+math.log(8001.)/SOURCE_DLNA)
END_GLOBAL_IZ=SOURCE_NZ-1
END_J=END_GLOBAL_IZ-SOURCE_IZH0
EXTRA_ACCEPTED=END_J-START_J
SOURCE_X0=-math.log(8001.)
SOURCE_Z0_X=0.
SOURCE_Z0_RAW_INDEX=(SOURCE_Z0_X-SOURCE_X0)/SOURCE_DLNA
SOURCE_Z0_CLAMPED_INDEX=SOURCE_NZ-3
SOURCE_Z0_FRACTION=SOURCE_Z0_RAW_INDEX-SOURCE_Z0_CLAMPED_INDEX
FIXED_GLOBAL_SAMPLES=(START_GLOBAL_IZ,START_GLOBAL_IZ+1)+tuple(
    START_GLOBAL_IZ+2048*k for k in range(1,18))+(105855,105856,105857)
MAX_COMMON_SAMPLES=32
U7_STOP_NPZ_SHA256="f5a8c9f2adfd8217b964bc21c9a5c3a7822877be53240bc132c1205966fbfce8"
U7_STOP_JSON_SHA256="ec6478e81b444c51adb316570bde2469093801db455c50952893b19aa3ae699f"
U7_VERIFICATION_SHA256="203ed2182d986e12f78a9106fc86adc04ce639850cd96cad631162e40f570fa3"
U7_C_STDOUT_SHA256="7a7d8e56dd54ee286b5934935afc59579c4b990ccecf6b3af60c12644a604b55"
U7_ADMISSION_SHA256="b4368224b2a14858d99712d5276a08692d678d0ca7251109354a9cedade91a42"
U1_ACCEPTED_ROWS_SHA256="27785d0adfddfb960d007459a9969fb9ef4a74a38415e928238fc94a107177a4"
U1_VERIFICATION_SHA256="39f4c78d3cf78afd615b1a388f2988585c9724b9e7ae980a22632cdc2ede3ebb"


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def source_interp1d(values:np.ndarray,z_target:float)->dict:
    """Source hyrectools.c cubic with first/last index clamp, including z=0."""
    y=np.asarray(values,dtype=float)
    if y.shape!=(SOURCE_NZ,) or not math.isfinite(z_target) or not 0<=z_target<=8000:
        raise ValueError("U8_SOURCE_INTERPOLATION_DOMAIN")
    x=-math.log1p(z_target)
    raw=(x-SOURCE_X0)/SOURCE_DLNA
    ix=min(max(math.floor(raw),1),SOURCE_NZ-3)
    f=raw-ix
    if not np.all(np.isfinite(y[ix-1:ix+3])):raise ValueError("U8_SOURCE_STENCIL_NONFINITE")
    # Preserve native source's algebraic term order, without clipping frac.
    y0,y1,y2,y3=map(float,y[ix-1:ix+3])
    value=(-y0*f*(1-f)*(2-f)/6.
        +y1*(1+f)*(1-f)*(2-f)/2.
        +y2*(1+f)*f*(2-f)/2.
        -y3*(1+f)*f*(1-f)/6.)
    return {"value":value,"source_globals":list(range(ix-1,ix+3)),
            "raw_index":raw,"clamped_index":ix,
            "fraction":f}


def source_z0_clamped_cubic(values:np.ndarray)->dict:
    """z=0 interpolation from local hydrogen-start nodes including end clamp."""
    y=np.asarray(values,dtype=float)
    if y.shape!=(END_J+1,) or not np.all(np.isfinite(y[-4:])):
        raise ValueError("U8_Z0_SOURCE_STENCIL_MISSING")
    if not (math.floor(SOURCE_Z0_RAW_INDEX)==105857 and
            SOURCE_Z0_CLAMPED_INDEX==105856 and 1.<SOURCE_Z0_FRACTION<2.):
        raise ValueError("U8_Z0_SOURCE_CLAMP_DRIFT")
    # Local arrays begin at global 18223; the final stencil is identical.
    f=SOURCE_Z0_FRACTION;y0,y1,y2,y3=map(float,y[-4:])
    value=(-y0*f*(1-f)*(2-f)/6.
        +y1*(1+f)*(1-f)*(2-f)/2.
        +y2*(1+f)*f*(2-f)/2.
        -y3*(1+f)*f*(1-f)/6.)
    return {"value":value,"source_globals":[105855,105856,105857,105858],
            "raw_index":SOURCE_Z0_RAW_INDEX,"clamped_index":SOURCE_Z0_CLAMPED_INDEX,
            "fraction":f}


def assemble_full_source_grid(u1_rows:Path,u1_verification:Path,
                              hydrogen_nodes:dict[str,np.ndarray])->dict[str,np.ndarray]:
    """Join immutable U1 helium prefix and independently integrated H nodes."""
    if sha256(u1_rows)!=U1_ACCEPTED_ROWS_SHA256 or sha256(u1_verification)!=U1_VERIFICATION_SHA256:
        raise ValueError("U8_U1_PINNED_PREFIX_SHA_MISMATCH")
    receipt=json.loads(Path(u1_verification).read_text())
    if receipt.get("status")!="PASS" or receipt.get("rows")!=18224:
        raise ValueError("U8_U1_PREFIX_NOT_VERIFIED")
    prefix_x=np.empty(SOURCE_IZH0+1);prefix_t=np.empty(SOURCE_IZH0+1)
    count=0
    with Path(u1_rows).open() as stream:
        for line in stream:
            row=json.loads(line)
            if row.get("index")!=count or count>SOURCE_IZH0:
                raise ValueError("U8_U1_PREFIX_INDEX")
            prefix_x[count]=float(row["xe"]);prefix_t[count]=float(row["Tm_K"])
            count+=1
    if count!=SOURCE_IZH0+1:raise ValueError("U8_U1_PREFIX_ROW_COUNT")
    if (hydrogen_nodes["global_iz"].shape!=(END_J+1,) or
            not np.array_equal(hydrogen_nodes["global_iz"],np.arange(SOURCE_IZH0,SOURCE_NZ))):
        raise ValueError("U8_HYDROGEN_FULL_SOURCE_GRID_MISSING")
    for key,prefix in (("xe",prefix_x),("Tm_K",prefix_t)):
        got=float(hydrogen_nodes[key][0]);ref=float(prefix[-1])
        limit=5e-9 if key=="xe" else 5e-10
        if abs(got-ref)/max(abs(ref),1e-8 if key=="xe" else 1.)>limit:
            raise ArithmeticError(f"U8_U1_U8_DUPLICATE_18223:{key}")
    return {"xe":np.concatenate((prefix_x[:-1],hydrogen_nodes["xe"])),
            "Tm_K":np.concatenate((prefix_t[:-1],hydrogen_nodes["Tm_K"]))}


def source_emla_table_guard(c:HyRec2012Cosmology,z:float,tm_K:float)->tuple[bool,str|None]:
    """Exact history.c outer-loop left-to-right source guard."""
    tr=c.T0_K*(1.+z)
    if not (KB_NATIVE_EV_K*tr/c.fsR/c.fsR/c.meR>.004):
        return False,"TR_MIN"
    if not (tm_K/c.T0_K/(1.+z)>.1):
        return False,"TM_TR_MIN"
    return True,None


def peebles_rhs_ln_a(c:HyRec2012Cosmology,z:float,xe:float,tm_K:float)->float:
    """Direct Python translation of hydrogen.c::rec_TLA_dxHIIdlna, Fudge=1."""
    if not all(map(math.isfinite,(z,xe,tm_K))) or not (z>-1 and 0<xe<1 and tm_K>0):
        raise ValueError("U8_PEEBLES_STATE_DOMAIN")
    tr_K=c.T0_K*(1.+z)
    tm=KB_NATIVE_EV_K*tm_K/(c.fsR*c.fsR*c.meR)
    tr=KB_NATIVE_EV_K*tr_K/(c.fsR*c.fsR*c.meR)
    nH=1.e-6*c.nH0_m3*(1.+z)**3
    H=c.hubble_s(z)
    def alphaB(T):
        t4=T/KB_NATIVE_EV_K/1.e4
        return (c.fsR/c.meR)**2*4.309e-13*t4**(-.6166)/(1.+.6703*t4**.5300)
    rl=LYA_FACT_CM3*(c.fsR*c.fsR*c.meR)**3*H/nH/(1.-xe)
    a_tm=alphaB(tm);a_tr=alphaB(tr)
    sf=SAHA_COEFFICIENT_CGS*(c.fsR*c.meR)**3
    beta4=sf*tr*math.sqrt(tr)*math.exp(-.25*IONIZATION_ENERGY_EV/tr)*a_tr
    decay=LAMBDA_2S1S_S_INV*c.fsR**8*c.meR
    C=(3.*rl+decay)/(3.*rl+decay+beta4)
    s=sf*tr*math.sqrt(tr)*math.exp(-IONIZATION_ENERGY_EV/tr)/nH
    dxe2=xe*xe-s*(1.-xe)
    da=a_tm-a_tr
    rhs=-nH*(s*(1.-xe)*da+dxe2*a_tm)*C/H
    if not math.isfinite(rhs):raise ArithmeticError("U8_PEEBLES_NONFINITE_RHS")
    return float(rhs)


def load_admitted_u7_stop(npz:Path,sidecar:Path,verification:Path,c_stdout:Path,
                          admission:Path)->tuple[dict[str,np.ndarray],dict]:
    for path,want in ((npz,U7_STOP_NPZ_SHA256),(sidecar,U7_STOP_JSON_SHA256),
                      (verification,U7_VERIFICATION_SHA256),(c_stdout,U7_C_STDOUT_SHA256),
                      (admission,U7_ADMISSION_SHA256)):
        if sha256(path)!=want:raise ValueError(f"U7_PINNED_INPUT_SHA_MISMATCH:{Path(path).name}")
    meta=json.loads(Path(sidecar).read_text());report=json.loads(Path(verification).read_text())
    review=json.loads(Path(admission).read_text())
    if (review.get("decision")!="SCOPED_PASS" or review.get("stop_npz_sha256")!=U7_STOP_NPZ_SHA256 or
            review.get("verification_sha256")!=U7_VERIFICATION_SHA256 or
            review.get("native_c_stdout_sha256")!=U7_C_STDOUT_SHA256 or
            review.get("historic_u5_average_gate")!="HOLD_ORIGINAL_TOLERANCE_NOT_MET"):
        raise ValueError("U7_SCOPED_ADMISSION_MISMATCH")
    if (meta.get("phase")!="STOP" or meta.get("status")!="STOP_AT_Z20_CUBIC_STENCIL" or
            meta.get("accepted_extra")!=40804 or meta.get("npz_sha256")!=U7_STOP_NPZ_SHA256 or
            report.get("status")!="STOP_AT_Z20_CUBIC_STENCIL" or report.get("accepted_extra")!=40804):
        raise ValueError("U7_STOP_SEMANTICS_MISMATCH")
    with np.load(npz,allow_pickle=False) as handle:
        a={k:np.array(handle[k],copy=True) for k in handle.files}
    names=("global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")
    for key in names:
        if key not in a or a[key].shape!=(START_J+1,):raise ValueError(f"U7_STATE_SHAPE:{key}")
    for key in ("hydrogen_rhs_dln_a","thermal_rhs_dln_a"):
        if key not in a or a[key].shape!=(START_J,) or not np.all(np.isfinite(a[key][-2:])):
            raise ValueError(f"U7_MEMORY_SHAPE:{key}")
    if (int(a["global_iz"][-1])!=START_GLOBAL_IZ or float(a["xHeII"][-1])!=0. or
            bool(a["post_saha"][-1]) or not all(math.isfinite(float(a[k][-1])) for k in ("z","xe","Tm_K"))):
        raise ValueError("U7_STAGE_BOUNDARY_MISMATCH")
    boundary={"hydrogen_prev":float(meta["hydrogen_prev"]),
              "hydrogen_prev2":float(meta["hydrogen_prev2"]),
              "thermal_prev":float(meta["thermal_prev"]),
              "thermal_prev2":float(meta["thermal_prev2"]),
              "u7_admission_sha256":U7_ADMISSION_SHA256}
    for name in ("hydrogen_prev","hydrogen_prev2","thermal_prev","thermal_prev2"):
        if not math.isfinite(boundary[name]):raise ValueError(f"U7_MEMORY_NONFINITE:{name}")
    if (abs(boundary["hydrogen_prev"]-float(a["hydrogen_rhs_dln_a"][-1]))>1e-18 or
            abs(boundary["hydrogen_prev2"]-float(a["hydrogen_rhs_dln_a"][-2]))>1e-18):
        raise ValueError("U7_H_MEMORY_TAIL_MISMATCH")
    return a,boundary


def continue_low_z_to_end(checkpoint:dict[str,np.ndarray],boundary:dict,c:HyRec2012Cosmology,
                          emla_source,*,common_input_oracle:Callable,
                          checkpoint_callback:Callable[[dict],None]|None=None,
                          max_extra_accepted:int=EXTRA_ACCEPTED)->dict:
    if not 1<=max_extra_accepted<=EXTRA_ACCEPTED:raise ValueError("U8_ACCEPTED_CAP_INVALID")
    if not callable(common_input_oracle) or not callable(getattr(common_input_oracle,"thermal_rhs",None)):
        raise ValueError("U8_COMMON_INPUT_C_ORACLE_REQUIRED")
    ncap=START_J+max_extra_accepted
    node_names=("global_iz","z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")
    nodes={key:np.empty(ncap+1,dtype=checkpoint[key].dtype) for key in node_names}
    for key in node_names:nodes[key][:START_J+1]=checkpoint[key]
    hr=np.full(ncap,np.nan);gr=np.full(ncap,np.nan)
    hr[:START_J]=checkpoint["hydrogen_rhs_dln_a"]
    gr[:START_J]=checkpoint["thermal_rhs_dln_a"]
    hprev=boundary["hydrogen_prev"];hprev2=boundary["hydrogen_prev2"]
    tprev=boundary["thermal_prev"];tprev2=boundary["thermal_prev2"]
    accepted=START_J;attempted=0;event=None;models=[];sampled=[]
    common_max={"hydrogen":0.,"thermal":0.}
    status="BOUNDED_LOW_Z_INTERVAL_COMPLETE_BEFORE_SOURCE_END";stop_failure=None

    def emit(phase,failure=None):
        if checkpoint_callback is None:return
        n=accepted
        checkpoint_callback({"phase":phase,"accepted_extra":n-START_J,"attempted_evaluations":attempted,
            "status":status,"event":event,"models":tuple(models),
            **{key:nodes[key][:n+1].copy() for key in node_names},
            "hydrogen_rhs_dln_a":hr[:n].copy(),"thermal_rhs_dln_a":gr[:n].copy(),
            "hydrogen_prev":hprev,"hydrogen_prev2":hprev2,
            "thermal_prev":tprev,"thermal_prev2":tprev2,
            "failure":failure})

    emit("START")
    try:
        while accepted<ncap:
            j=accepted;iz=int(nodes["global_iz"][j]);z=float(nodes["z"][j])
            xe=float(nodes["xe"][j]);tm=float(nodes["Tm_K"][j]);tr=c.T0_K*(1+z)
            if iz!=j+SOURCE_IZH0 or not START_GLOBAL_IZ<=iz<END_GLOBAL_IZ:
                raise ValueError(f"U8_SOURCE_GRID_INPUT_INDEX:{j}:{iz}")
            if not (0<xe<1 and 0<tm<=tr and float(nodes["xHeII"][j])==0. and
                    not bool(nodes["post_saha"][j])):
                status="HOLD_NEXT_STAGE_REQUIRED:LOW_Z_INPUT_DOMAIN"
                stop_failure={"reason":status,"input_j":j,"last_accepted_j":accepted};break
            guard,reason=source_emla_table_guard(c,z,tm)
            if event is None and not guard:
                event={"j":j,"global_iz":iz,"z":z,"reason":reason}
                emit("PEEBLES_EVENT")
            model="EMLA2s2p" if event is None else "PEEBLES"
            attempted+=1
            f=float(emla_source.hydrogen_rhs_ln_a(z=z,x_HII=xe,x_e=xe,Tm_K=tm,
                fsR=c.fsR,meR=c.meR) if model=="EMLA2s2p" else peebles_rhs_ln_a(c,z,xe,tm))
            g=float(source_thermal_rhs(c,xe,tm,z))
            if not math.isfinite(f) or not math.isfinite(g):
                raise ArithmeticError(f"U8_NONFINITE_RHS:{j}:{model}")
            nextj=j+1;nextiz=iz+1;nextz=c.redshift(nextiz)
            nx=xe+SOURCE_DLNA*(1.25*f-.25*hprev2)
            nt=tm+SOURCE_DLNA*(1.25*g-.25*tprev2)
            if not (0<nx<1 and 0<nt<=c.T0_K*(1+nextz)):
                status="HOLD_NEXT_STAGE_REQUIRED:LOW_Z_ACCEPTED_STATE_DOMAIN"
                stop_failure={"reason":status,"input_j":j,"candidate_j":nextj,
                    "candidate_xe":nx,"candidate_Tm_K":nt,"last_accepted_j":accepted};break
            hr[j]=f;gr[j]=g
            nodes["global_iz"][nextj]=nextiz;nodes["z"][nextj]=nextz
            nodes["xe"][nextj]=nx;nodes["xHII"][nextj]=nx;nodes["xH1s"][nextj]=1-nx
            nodes["xHeII"][nextj]=0.;nodes["post_saha"][nextj]=False
            nodes["Tm_K"][nextj]=nt
            hprev2,hprev=hprev,f;tprev2,tprev=tprev,g
            models.append(model);accepted=nextj
            if accepted-START_J in (1,2) or (accepted-START_J)%4096==0 or (
                    event is not None and accepted in (event["j"]+1,event["j"]+2)):
                emit(f"ACCEPTED_{accepted-START_J:05d}")
        if accepted==END_J:status="STOP_AT_SOURCE_Z0_CUBIC_STENCIL"
        emit("STOP",stop_failure)
    except BaseException as exc:
        emit("EXCEPTION",{"type":type(exc).__name__,"message":str(exc),
                          "last_accepted_j":accepted,"attempted_evaluations":attempted})
        raise
    n=accepted
    if event is not None:
        samples=sorted((set(FIXED_GLOBAL_SAMPLES)|{event["global_iz"]-1,
              event["global_iz"],event["global_iz"]+1}) & set(range(START_GLOBAL_IZ,
              int(nodes["global_iz"][n]))))
    else:
        samples=sorted(set(FIXED_GLOBAL_SAMPLES) & set(range(START_GLOBAL_IZ,
              int(nodes["global_iz"][n]))))
    if len(samples)>MAX_COMMON_SAMPLES:raise RuntimeError("U8_COMMON_INPUT_SAMPLE_CAP")
    for iz in samples:
        j=iz-SOURCE_IZH0;model=models[j-START_J]
        z=float(nodes["z"][j]);xe=float(nodes["xe"][j]);tm=float(nodes["Tm_K"][j])
        cf=float(common_input_oracle(model,iz,z,xe,tm))
        cg=float(common_input_oracle.thermal_rhs(xe,tm,z))
        fh=float(hr[j]);fg=float(gr[j])
        dh=abs(fh-cf)/max(abs(fh),abs(cf),1e-13)
        dg=abs(fg-cg)/max(1.,abs(cg))
        if not math.isfinite(dh) or dh>3e-10:raise ArithmeticError(f"U8_COMMON_H_RHS:{j}:{dh}")
        if not math.isfinite(dg) or dg>2e-10:raise ArithmeticError(f"U8_COMMON_T_RHS:{j}:{dg}")
        sampled.append(iz);common_max["hydrogen"]=max(common_max["hydrogen"],dh)
        common_max["thermal"]=max(common_max["thermal"],dg)
    end=None
    if n==END_J:
        end={"xe":source_z0_clamped_cubic(nodes["xe"]),
             "Tm_K":source_z0_clamped_cubic(nodes["Tm_K"]),
             "rei_activation":False,"temporal_refinement":"NOT_RUN"}
    return {"status":status,"failure":stop_failure,"accepted_extra":n-START_J,
            "attempted_evaluations":attempted,"event":event,"models":models,
            "nodes":{key:nodes[key][:n+1] for key in node_names},
            "hydrogen_rhs_dln_a":hr[:n],"thermal_rhs_dln_a":gr[:n],
            "hydrogen_prev":hprev,"hydrogen_prev2":hprev2,
            "thermal_prev":tprev,"thermal_prev2":tprev2,
            "common_sample_globals":sampled,"common_max":common_max,"z0":end}
