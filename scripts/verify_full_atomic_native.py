"""Independent original-C HyRec2012 FULL one-step vs REC Python source physics.

The C oracle compiles *unmodified* Oct2012 source from SHA-pinned archive,
then calls its ORIGINAL populateTS, solve_real_virt and ORIGINAL
rec_HMLA_2photon_dxHIIdlna (with actual causal accepted history).

No native xe(z) or primordial FULL history integration is injected into REC.
"""
from __future__ import annotations

import ctypes
from contextlib import contextmanager
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    populate_original_full_atomic,complete_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.hmla_flrw import (
    HMLAFlrwSource,KB_NATIVE_EV_K,
)
from full_bianchi_hyrec.trajectory.primitive_rates import (
    OriginalHyRecPrimitiveRateTable,
)

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
WRAPPER=ROOT/"scripts/c_harness/original_hyrec_full_source_harness.c"
SOURCE_HASH="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
COSMO={
    "h":.6735837, "omega_cb":.31242079216478097,
    "omega_r_h2":4.1578740068818545e-5,
    "omega_de_h2":.3119234221656212,
    "omega_b_h2":.02242,"y_he_mass":.245,"tcmb0_K":2.7255,
}


@contextmanager
def _in_directory(p:Path):
    current=Path.cwd()
    try:
        os.chdir(p)
        yield
    finally:
        os.chdir(current)


def _compile_original(tmp:Path):
    with zipfile.ZipFile(ARCHIVE) as z:
        for name in ("hydrogen.c","hydrogen.h","hyrectools.c",
                     "hyrectools.h","hyrec_params.h","Alpha_inf.dat",
                     "R_inf.dat","two_photon_tables.dat"):
            z.extract("HyRec/"+name,tmp)
    native=tmp/"HyRec"
    so=tmp/"librec_atomic_r3b.so"
    cmd=["gcc","-std=gnu99","-O2","-shared","-fPIC",
         "-ffunction-sections","-fdata-sections",
         "-Wl,--gc-sections","-I",str(native),
         str(native/"hydrogen.c"),str(native/"hyrectools.c"),
         str(WRAPPER),"-lm","-o",str(so)]
    subprocess.run(cmd,check=True,text=True,capture_output=True)
    lib=ctypes.CDLL(str(so))
    dbl=ctypes.c_double
    ptr=ctypes.POINTER(dbl)
    pop=lib.rec_r3b_populate
    pop.argtypes=[dbl]*6+[ptr]*14
    pop.restype=None
    step=lib.rec_r3b_original_full_step
    # Native signature: 6 thermodynamic doubles, zstart, iz, z, 5 pointers.
    step.argtypes=[dbl]*7+[ctypes.c_uint,dbl]+[ptr]*5
    step.restype=dbl
    return native,pop,step


def _measured_pair(reference, actual):
    a=np.asarray(reference,dtype=float)
    b=np.asarray(actual,dtype=float)
    if a.shape!=b.shape:
        raise RuntimeError("native array shape mismatch")
    diff=np.abs(a-b)
    scale=max(float(np.max(np.abs(a))),float(np.max(np.abs(b))),1e-200)
    return {
        "max_abs":float(np.max(diff)),
        "max_relative_scaled":float(np.max(diff/np.maximum(
            np.maximum(np.abs(a),np.abs(b)),scale*1e-12))),
        "relative_global_infinity_norm":float(np.max(diff)/scale),
        "shapes":list(a.shape),
    }


def run():
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()!=SOURCE_HASH:
        raise ValueError("unverified original source archive")
    table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    hmla=HMLAFlrwSource(**COSMO,table=table)
    with zipfile.ZipFile(ARCHIVE) as zf:
        energy=np.ascontiguousarray(
            np.loadtxt(io.BytesIO(zf.read("HyRec/two_photon_tables.dat")))[:,0]
        )
    records=[]
    with tempfile.TemporaryDirectory(prefix="rec_r3b_original_") as d:
        folder=Path(d)
        native,pop,step=_compile_original(folder)
        def arr(shape):
            return np.empty(shape,dtype=np.float64)
        pt=ctypes.POINTER(ctypes.c_double)
        pointer=lambda a:a.ctypes.data_as(pt)
        # Independent physical source states; native histories are
        # manufactured accepted fminus arrays, NOT a C evolution output.
        for z,x,ratio,iz in (
            (650.,.002,.95,80),
            (900.,.04,.98,95),
            (1200.,.45,.999,170),
            (1450.,.97,.99999,200),
        ):
            tr=hmla.tcmb0_K*(1+z)
            tm=tr*ratio
            nH=hmla.cosmology(z)[1]*1e-6
            H=hmla.cosmology(z)[0]
            startz=math.expm1(math.log1p(z)+iz*SOURCE_DLNA)
            xx=np.arange(311)[:,None]
            ticks=np.arange(iz)[None,:]
            hist=np.ascontiguousarray(
                (1+xx/700)*(1+.1*np.sin(xx/17+ticks/11)+ticks/500)
                *4e-11
            )
            lyhist=np.ascontiguousarray(
                (1+np.arange(3)[:,None]/5)
                *(1+.1*np.cos(ticks/13+np.arange(3)[:,None]))*1e-11
            )
            inc=causal_incoming_from_accepted_histories(
                energies_eV=energy,virtual_history=hist,
                lyman_history=lyhist,z_start=startz,z_face=z,
                iz=iz,
            )
            s=populate_original_full_atomic(
                hmla,z=z,xHII=x,xe=x,Tm_K=tm,
                incoming_virtual=inc.virtual_distortion[0],
                incoming_lyman=inc.lya_lyb_incoming_distortion[0],
            )
            py=complete_original_full_atomic(s)
            outputs=[
                arr((2,2)),arr((2,311)),arr((2,311)),arr((3,311)),
                arr((2,)),arr((311,)),arr((311,)),
                arr((2,)),arr((2,)),arr((2,)),
                arr((2,)),arr((311,)),
            ]
            ov=arr((311,));ol=arr((3,));oa=arr((311,))
            with _in_directory(native):
                pop(float(x),float(x),float(nH),float(H),
                    float(KB_NATIVE_EV_K*tm),float(KB_NATIVE_EV_K*tr),
                    pointer(np.ascontiguousarray(inc.virtual_distortion[0])),
                    pointer(np.ascontiguousarray(inc.lya_lyb_incoming_distortion[0])),
                    *[pointer(v) for v in outputs])
                original=float(step(float(x),float(x),float(nH),float(H),
                    float(KB_NATIVE_EV_K*tm),float(KB_NATIVE_EV_K*tr),
                    float(startz),int(iz),float(z),
                    pointer(hist),pointer(lyhist),
                    pointer(ov),pointer(ol),pointer(oa)))
            names=("Trr","Trv","Tvr","Tvv","sr","sv","Dtau",
                   "Alpha_cgs","DAlpha_cgs","Beta_s_inv")
            arrays=tuple(getattr(s,n) for n in names)+(py.real_departures,
                    py.virtual_departures)
            compared={key:_measured_pair(native_array,p)
                      for key,native_array,p in zip(
                          names+("real_departures","virtual_departures"),
                          outputs,arrays)}
            compared.update({
                "outgoing_virtual":_measured_pair(ov,py.outgoing_virtual),
                "outgoing_lyman":_measured_pair(ol,py.outgoing_lyman),
                "average_virtual":_measured_pair(oa,py.average_virtual),
                "electron_rhs":_measured_pair(
                    np.array([original]),np.array([py.dxHII_dln_a])),
            })
            records.append({
                "z":z,"xHII":x,"Tm_over_Tr":ratio,"accepted_history":iz,
                "native_electron_rhs":original,
                "python_electron_rhs":float(py.dxHII_dln_a),
                "python_matrix_residual":float(py.normalized_matrix_residual),
                "field_comparisons":compared,
            })
    all_comp=[r["field_comparisons"][k]["max_relative_scaled"]
              for r in records for k in r["field_comparisons"]]
    worst=max(all_comp)
    return {
        "schema":"rec.r3b.original_full_hydrogen_instant_parity.v1",
        "source_archive_sha256":SOURCE_HASH,
        "C_owner":"unmodified hydrogen.c::populateTS_2photon,solve_real_virt,rec_HMLA_2photon_dxHIIdlna",
        "scoped_state":"manufactured accepted-history input; H-only original q0 FULL instantaneous atomic+virtual step",
        "source_state_count":len(records),
        "max_scaled_relative_across_fields":worst,
        "acceptance_threshold":1e-8,
        "status":"PASS_SOURCE_POINT_PARITY" if worst<1e-8 else "FAIL",
        "not_self_consistent_full_history":True,
        "samples":records,
    }


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    parsed=ap.parse_args()
    data=run()
    parsed.output.parent.mkdir(parents=True,exist_ok=True)
    parsed.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":data["status"],
        "max_scaled_relative_across_fields":data["max_scaled_relative_across_fields"],
        "samples":[{"z":r["z"],"native_rhs":r["native_electron_rhs"],
           "python_rhs":r["python_electron_rhs"],
           "matrix_residual":r["python_matrix_residual"],
           "max_block_scaled":max(v["max_relative_scaled"]
                                   for v in r["field_comparisons"].values())}
            for r in data["samples"]]
    },indent=2))
    if data["status"]!="PASS_SOURCE_POINT_PARITY":
        raise SystemExit(1)
