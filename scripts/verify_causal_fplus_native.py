"""Original HyRec Oct2012 FULL fplus source vs REC causal incoming source.

Executable scientific parity receipt, not a FULL recombination run.
Raw source archive is unchanged and compiled in an isolated temporary dir.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import tempfile
import zipfile

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, causal_incoming_from_accepted_histories,
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
WRAPPER=ROOT/"scripts/c_harness/original_hyrec_causal_fplus_harness.c"
FILES=("hydrogen.c","hydrogen.h","hyrectools.c",
       "hyrectools.h","hyrec_params.h")


def run():
    archive_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="rec_raw_hyrec_native_fplus_") as tmp:
        tmp=Path(tmp)
        with zipfile.ZipFile(SOURCE) as zf:
            en=np.ascontiguousarray(
                np.loadtxt(io.BytesIO(zf.read("HyRec/two_photon_tables.dat")))[:,0]
            )
            for fn in FILES:
                zf.extract("HyRec/"+fn,tmp)
        base=tmp/"HyRec"
        so=tmp/"libhyrec_causal.so"
        args=["gcc","-std=gnu99","-O2","-shared","-fPIC",
              "-ffunction-sections","-fdata-sections",
              "-fvisibility=hidden","-Wl,--gc-sections",
              "-I",str(base),str(base/"hydrogen.c"),
              str(base/"hyrectools.c"),str(WRAPPER),
              "-lm","-o",str(so)]
        subprocess.run(args,check=True,capture_output=True,text=True)
        fn=ctypes.CDLL(str(so)).rec_r3_native_fplus
        pointer=ctypes.POINTER(ctypes.c_double)
        fn.argtypes=[pointer,pointer,pointer,ctypes.c_uint,
                     ctypes.c_double,ctypes.c_double,
                     pointer,pointer]
        fn.restype=None
        ptr=lambda a:a.ctypes.data_as(pointer)
        results=[]
        for iz in (2,40,200,640):
            # Multiple distinct nonconstant bin/time source values.
            t=np.arange(iz)[None,:]
            b=np.arange(311)[:,None]
            virtual=np.ascontiguousarray(
                1e-7*(1+b/250)*(1+t/1300+.08*np.sin(t/13+b/20))
            )
            lyman=np.ascontiguousarray(
                1e-8*(1+np.arange(3)[:,None]/5) *
                (1-t/1700+.03*np.cos(t/17+np.arange(3)[:,None]))
            )
            zstart=1600.
            z=math.expm1(math.log1p(zstart)-iz*SOURCE_DLNA)
            py=causal_incoming_from_accepted_histories(
                energies_eV=en,virtual_history=virtual,
                lyman_history=lyman,z_start=zstart,
                z_face=z,iz=iz)
            c_virt=np.empty(311)
            c_lya=np.empty(2)
            fn(ptr(en),ptr(virtual),ptr(lyman),iz,zstart,z,
               ptr(c_virt),ptr(c_lya))
            oracle=np.r_[c_virt,c_lya]
            observed=np.r_[py.virtual_distortion[0],
                            py.lya_lyb_incoming_distortion[0]]
            err=np.abs(observed-oracle)
            rel=err/np.maximum(np.abs(oracle),1e-12)
            results.append({
                "accepted_steps":iz,
                "photons_compared":int(err.size),
                "max_absolute_difference":float(err.max()),
                "max_scaled_relative_difference":float(rel.max()),
            })
    maxerr=max(v["max_scaled_relative_difference"] for v in results)
    return {
        "schema":"rec.native_causal_fplus_parity.v1",
        "source_archive_sha256":archive_sha,
        "C_owner":"October-2012 original hydrogen.c::fplus_from_fminus",
        "source_wrapper_sha256":hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),
        "source_virtual_energy_table":"HyRec/two_photon_tables.dat",
        "source_virtual_bins":311,
        "incoming_lyman_faces":2,
        "native_C_compiler":"gcc -std=gnu99 -O2 shared raw source",
        "comparisons":results,
        "global_max_scaled_relative_difference":maxerr,
        "acceptance_threshold":2e-11,
        "status":"PASS_SCOPED_C_NATIVE_PARITY" if maxerr<2e-11 else "FAIL",
        "not_full_solver":True,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    data=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(json.dumps(data,indent=2))
    if data["status"]!="PASS_SCOPED_C_NATIVE_PARITY":
        raise SystemExit(1)
