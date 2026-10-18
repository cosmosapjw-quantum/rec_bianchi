"""Create-only owner-specific evidence for one new U5 average-photon failure.

The original tolerance decision and the bounded Decimal-80 shadow decision
are separate.  This routine never changes the accepted trajectory or gate.
"""
from __future__ import annotations

import ctypes
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    populate_original_full_atomic,complete_original_full_atomic)

U=2.**-53
KB_EV_K=8.617343e-5


def phi80(tau:float) -> Decimal:
    with localcontext() as ctx:
        ctx.prec=80
        t=Decimal.from_float(tau)
        return +(Decimal(1)-(Decimal(1)-(-t).exp())/t)


def numerical_gates(p:dict,c:dict,bb:float) -> dict:
    tol=1.e-7*max(abs(p["raw"]),abs(c["raw"]))+1.e-10*bb
    raw=abs(p["raw"]-c["raw"])
    original={"status":"PASS" if raw<=tol else "FAIL","absolute":raw,
              "tolerance":tol,"ratio":raw/tol}
    # Existing R3h roundoff certificate covers only the small-tau
    # cancellation domain.  Outside it the separate scientific gate is HOLD.
    if not (p["bin"]==c["bin"] and 0<=p["bin"]<100 and
            all(1.e-6<owner["tau"]<1.e-4 for owner in (p,c))):
        shadow={"status":"HOLD_OUTSIDE_DIAGNOSTIC_DOMAIN"}
    else:
        stable=abs(Decimal(p["A80"])-Decimal(c["A80"]))
        phi_ok=all(abs(owner["phi64"]-float(Decimal(owner["phi80"])))<=owner["phi_bound"]
                   for owner in (p,c))
        reconstruction_ok=all(owner["raw_reconstruction_absolute"]<=tol and
                              owner["source_reconstruction_absolute"]<=tol
                              for owner in (p,c))
        bound=(abs(p["Q"])*p["phi_bound"]+abs(c["Q"])*c["phi_bound"]+
               p["raw_reconstruction_absolute"]+c["raw_reconstruction_absolute"]+
               32*U*(abs(p["incoming"])+abs(p["phi64"]*p["Q"])+
                     abs(c["incoming"])+abs(c["phi64"]*c["Q"])))
        shadow={"status":"PASS" if phi_ok and reconstruction_ok and
                stable<=Decimal.from_float(tol) and raw<=tol+bound
                else "FAIL","stable_remainder_absolute":str(stable),
                "propagated_bound":bound,"raw_plus_bound_limit":tol+bound,
                "phi_error_bound_pass":phi_ok,"source_reconstruction_pass":reconstruction_ok}
    return {"original_gate":original,"decimal80_ieee_gate":shadow}


def _c_incoming(oracle,source_dir:Path,j:int,z:float,vh:np.ndarray,lh:np.ndarray):
    """Run original fplus_from_fminus on the saved accepted C columns."""
    fn=oracle.h.lib.rec_r3i_original_fplus
    dbl=ctypes.c_double;ptr=ctypes.POINTER(dbl)
    fn.argtypes=[ptr,ptr,ctypes.c_uint,dbl,dbl,dbl,ptr,ptr]
    fn.restype=None
    vv=np.ascontiguousarray(vh,dtype=np.float64)
    ll=np.ascontiguousarray(lh,dtype=np.float64)
    if vv.shape!=(311,j) or ll.shape!=(3,j):
        raise ValueError("C_OWNER_ACCEPTED_HISTORY_SHAPE")
    out=np.empty(311,dtype=np.float64)
    lines=np.empty(2,dtype=np.float64)
    point=lambda x:x.ctypes.data_as(ptr)
    c=oracle.c
    tr=KB_EV_K*c.T0_K*(1.+z)
    old=os.getcwd();os.chdir(source_dir)
    try:
        fn(point(vv),point(ll),j,tr,c.redshift(c.izH0),z,point(out),point(lines))
    finally:os.chdir(old)
    if not np.all(np.isfinite(out)) or not np.all(np.isfinite(lines)):
        raise ArithmeticError("C_OWNER_NATIVE_FPLUS_NONFINITE")
    return out,lines


def _c_populate(oracle,source_dir:Path,state:dict,incoming:np.ndarray,ly:np.ndarray):
    lib=oracle.h.lib
    fn=lib.rec_r3b_populate
    dbl=ctypes.c_double;ptr=ctypes.POINTER(dbl)
    fn.argtypes=[dbl]*6+[ptr]*14;fn.restype=None
    arrays=[np.empty(shape,dtype=np.float64) for shape in
            ((2,2),(2,311),(2,311),(3,311),(2,),(311,),(311,),
             (2,),(2,),(2,),(2,),(311,))]
    incoming=np.ascontiguousarray(incoming,dtype=np.float64)
    ly=np.ascontiguousarray(ly,dtype=np.float64)
    point=lambda x:x.ctypes.data_as(ptr)
    c=oracle.c;z=state["z"];xe=state["xe"];tm=state["Tm_K"]
    a=1.+z
    n_h=1.e-6*c.nH0_m3*a*a*a
    old=os.getcwd();os.chdir(source_dir)
    try:
        fn(xe,xe,n_h,c.hubble_s(z),KB_EV_K*tm,
           KB_EV_K*c.T0_K*(1.+z),point(incoming),point(ly),
           *[point(a) for a in arrays])
    finally:os.chdir(old)
    return arrays


def _owner(owner:str,state:dict,vh:np.ndarray,lh:np.ndarray,raw:float,
           *,j:int,b:int,c,source,table,oracle,source_dir:Path) -> dict:
    if owner=="C":
        fin,lin=_c_incoming(oracle,source_dir,j,state["z"],vh,lh)
        interpolation_owner="original_C_fplus_from_fminus"
    else:
        inc=causal_incoming_from_accepted_histories(
            energies_eV=table.energy_eV,virtual_history=vh,lyman_history=lh,
            z_start=c.redshift(c.izH0),iz=j,z_face=state["z"],
            dlna=4.245e-5,shear_q=0.)
        fin=inc.virtual_distortion[0]
        lin=inc.lya_lyb_incoming_distortion[0]
        interpolation_owner="independent_Python_source_links"
    tr=c.T0_K*(1.+state["z"])
    tm=math.nextafter(state["Tm_K"],0.) if state["Tm_K"]==tr else state["Tm_K"]
    if owner=="Python":
        snap=populate_original_full_atomic(source,z=state["z"],xHII=state["xe"],
            xe=state["xe"],Tm_K=tm,incoming_virtual=fin,incoming_lyman=lin)
        real=snap.instantaneous_schur_solution()[0]
        tau=float(snap.Dtau[b]);rv=snap.Trv;vr=snap.Tvr
        reconstructed=float(complete_original_full_atomic(snap).average_virtual[b])
    else:
        arrays=_c_populate(oracle,source_dir,
            {**state,"Tm_K":tm},fin,lin)
        tau=float(arrays[6][b]);rv=arrays[1];vr=arrays[2];real=arrays[10]
        reconstructed=float(oracle(j,state["z"],state["xe"],0.,tm,vh,lh)["average"][b])
    x1s=1.-state["xe"]
    gamma=-float(rv[0,b]+rv[1,b])
    f=float(fin[b])
    q=-(real[0]*vr[0,b]+real[1]*vr[1,b])/(x1s*gamma)-f
    p64=1.-(1.-math.exp(-tau))/tau
    p80=phi80(tau)
    with localcontext() as ctx:
        ctx.prec=80
        a80=Decimal.from_float(f)+p80*Decimal.from_float(q)
    a64=f+p64*q
    return {"owner":owner,"interpolation_owner":interpolation_owner,
            "bin":b,"state":state,"tau":tau,"Q":q,"incoming":f,
            "phi64":p64,"phi80":str(p80),"A64":a64,"A80":str(a80),
            "raw":raw,"recomputed_full_average":reconstructed,
            "raw_reconstruction_absolute":abs(a64-raw),
            "source_reconstruction_absolute":abs(reconstructed-raw),
            "phi_bound":U/tau+4*U,"history_shape":[list(vh.shape),list(lh.shape)]}


def preserve_failure(ev:Path,*,j:int,b:int,python_state:dict,c_state:dict,
                     py_vh:np.ndarray,py_lh:np.ndarray,c_vh:np.ndarray,c_lh:np.ndarray,
                     py_raw:float,c_raw:float,c,source,table,oracle,source_dir:Path,
                     source_identities:dict) -> dict:
    """Write exact accepted owner histories before any diagnostic can fail."""
    folder=ev/"average_first_failure"
    folder.mkdir(parents=True,exist_ok=False)
    history_hashes={}
    for name,array in (("python_virtual",py_vh),("python_lyman",py_lh),
                       ("c_virtual",c_vh),("c_lyman",c_lh)):
        path=folder/f"{name}.npy"
        with path.open("xb") as stream:
            np.save(stream,np.ascontiguousarray(array,dtype=np.float64),allow_pickle=False)
        history_hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    base={"j":j,"bin":b,"global_input_iz":c.izH0+j,
          "source_identities":source_identities,
          "accepted_history_sha256":history_hashes,
          "python_state":python_state,"c_state":c_state,
          "python_raw_average":py_raw,"c_raw_average":c_raw,
          "status":"FORENSIC_IN_PROGRESS"}
    with (folder/"forensic_input.json").open("x") as stream:
        stream.write(json.dumps(base,sort_keys=True,indent=2)+"\n")
    try:
        p=_owner("Python",python_state,py_vh,py_lh,py_raw,j=j,b=b,
                 c=c,source=source,table=table,oracle=oracle,source_dir=source_dir)
        n=_owner("C",c_state,c_vh,c_lh,c_raw,j=j,b=b,
                 c=c,source=source,table=table,oracle=oracle,source_dir=source_dir)
        tr=KB_EV_K*c.T0_K*(1.+python_state["z"])
        bb=1./math.expm1(float(table.energy_eV[b])/tr)
        base.update({"owners":[p,n],**numerical_gates(p,n,bb),"status":"DIAGNOSTIC_COMPLETE"})
    except BaseException as exc:
        base.update({"status":"DIAGNOSTIC_ERROR","diagnostic_error":
                     {"type":type(exc).__name__,"message":str(exc)}})
    with (folder/"forensic_result.json").open("x") as stream:
        stream.write(json.dumps(base,sort_keys=True,indent=2)+"\n")
    return base
