#!/usr/bin/env python3
"""Original October-2012 HyRec C HMLA2s2p RHS vs independent Python implementation.

Compiles ORIGINAL source hydrogen.c and hyrectools.c with a separate tiny C
driver. Runs many (x_HII, x_e, z, Tm/Tr) states. No native FULL gas-photon
evolution is invoked, and no reference x_e history is passed as a solver input.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile,math
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.hmla_flrw import HMLAFlrwSource,KB_NATIVE_EV_K

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
HARNESS=ROOT/"scripts/c_harness/original_hyrec_hmla_rhs_harness.c"
COSMOPARAMS={
    "h":0.6735837,"omega_cb":0.31242079216478097,
    "omega_r_h2":4.1578740068818545e-05,
    "omega_de_h2":0.3119234221656212,
    "omega_b_h2":0.022420000000000002,
    "y_he_mass":0.245,"tcmb0_K":2.7255
}
def source():
    return HMLAFlrwSource(
      **COSMOPARAMS,table=OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    )

def run()->dict:
    spec=source()
    outputs=[]
    with tempfile.TemporaryDirectory(prefix="rec_original_hmla_c_") as temp:
        root=Path(temp)
        c=spec.table.extract_source_tree(root)
        exe=root/"C_hmla_e2s2p"
        compile_cmd=[
          "gcc","-std=gnu11","-O2","-w","-I",str(c),
          str(HARNESS),str(c/"hydrogen.c"),str(c/"hyrectools.c"),
          "-lm","-o",str(exe),
        ]
        build=subprocess.run(compile_cmd,capture_output=True,text=True,timeout=30)
        if build.returncode:raise RuntimeError("gcc failed: "+build.stderr[-800:])
        for z in (650.,900.,1200.,1600.):
            H,nH=spec.cosmology(z)
            Tr_K=spec.tcmb0_K*(1+z)
            for xHII in (0.2,0.5,0.9,0.995):
                for frac in (0.,0.2):
                    xe=xHII+frac*spec.f_he
                    for ratio in (.82,.94,1.):
                        Tm_K=ratio*Tr_K
                        ref_args=[
                           str(exe),f"{xe:.17g}",f"{xHII:.17g}",
                           f"{nH*1e-6:.17g}",f"{H:.17g}",
                           f"{KB_NATIVE_EV_K*Tm_K:.17g}",
                           f"{KB_NATIVE_EV_K*Tr_K:.17g}","1","1",
                        ]
                        r=subprocess.run(ref_args,cwd=c,capture_output=True,text=True,timeout=10)
                        if r.returncode:raise RuntimeError("original HMLA C failed: "+r.stderr)
                        cref=float(r.stdout)
                        py=spec.hydrogen_rhs_ln_a(
                            z=z,x_HII=xHII,x_e=xe,Tm_K=Tm_K
                        )
                        if not (math.isfinite(cref) and math.isfinite(py)):
                            raise FloatingPointError("source HMLA invalid rate")
                        den=max(abs(cref),abs(py),1e-13)
                        diff=abs(py-cref)/den
                        if diff>3e-10:
                            raise AssertionError((z,xHII,frac,ratio,cref,py,diff))
                        outputs.append({
                          "z":z,"x_HII":xHII,"extra_electrons_from_HeII":frac*spec.f_he,
                          "matter_to_radiation_temperature":ratio,
                          "C_native_dx_HII_dln_a":cref,
                          "Python_dx_HII_dln_a":py,
                          "scaled_relative_difference":diff,
                        })
    return {
      "schema":"rec.hmla2s2p.original_C_vs_python.v1",
      "original_source_archive_sha256":hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
      "C_harness_sha256":hashlib.sha256(HARNESS.read_bytes()).hexdigest(),
      "scope":"Original HyRec 2012 EMLA2s2p hydrogen steady-state source, NOT FULL",
      "cosmology":COSMOPARAMS,"samples":len(outputs),
      "max_scaled_relative_difference":max(row["scaled_relative_difference"] for row in outputs),
      "test_gate":3e-10,
      "positive_Schur_denominator":"(betaS+Lambda)*(betaP+LyAlpha)+R*(betaS+Lambda+3betaP+3LyAlpha)",
      "rows":outputs,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    x=p.parse_args()
    if x.out.exists():p.error("output exists")
    ret=run()
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(ret,indent=2)+"\n")
    print(json.dumps({k:v for k,v in ret.items() if k!="rows"},indent=2))

if __name__=="__main__":
    main()
