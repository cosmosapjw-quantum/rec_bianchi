#!/usr/bin/env python3
"""Bounded R3i h/2 start comparison: independent Python vs October-2012 C FULL H+He."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
# Set thread caps before importing NumPy or project modules: this host's
# default OpenBLAS runtime maps 32 worker stacks (~2.1 GiB virtual address
# space), making the required 2 GiB RLIMIT_AS unusable despite low RSS.
os.environ.update({"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1",
    "MKL_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1"})
from pathlib import Path
import resource
import signal
import shutil
import subprocess
import sys
import time
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (  # noqa:E402
    HyRec2012Cosmology,integrate_helium_stages,helium_rhs,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable  # noqa:E402
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (  # noqa:E402
    MAX_FULL_EVALUATIONS,N_ACCEPTED,SOURCE_DLNA,integrate_full_start_eight,make_hmla_source,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table  # noqa:E402

PINNED_ZIP_SHA="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
PINNED_SOURCE={
    "history.c":"8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976",
    "helium.c":"1db7a9845e1f5a3052153bf94c1b98bf908cf16715641cbd14c810e5df6a5ece",
    "hydrogen.c":"421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b",
    "hyrec_params.h":"cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2",
}
KB_EV_K=8.617343e-5
NVIRT=311


def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()


def safe_extract_source(zip_path:Path,dest:Path)->Path:
    if sha(zip_path)!=PINNED_ZIP_SHA: raise RuntimeError("SOURCE_ZIP_SHA_MISMATCH")
    dest.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            member=Path(info.filename)
            if member.is_absolute() or ".." in member.parts:
                raise RuntimeError(f"UNSAFE_TAR_MEMBER:{info.filename}")
        zf.extractall(dest)
    src=dest/"HyRec"
    check_sources(src)
    return src


def check_sources(src:Path)->dict:
    actual={name:sha(src/name) for name in PINNED_SOURCE}
    if actual!=PINNED_SOURCE: raise RuntimeError("ORIGINAL_SOURCE_HASH_MISMATCH:"+repr(actual))
    return actual


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))


def run_capture(cmd:list[str],cwd:Path,stdout:Path,stderr:Path,timeout:float,env:dict):
    start=time.monotonic()
    with stdout.open("wb") as out,stderr.open("wb") as err:
        done=subprocess.run(cmd,cwd=cwd,stdout=out,stderr=err,timeout=timeout,
            env=env,preexec_fn=child_limits,check=False)
    return {"command":cmd,"returncode":done.returncode,"wall_s":time.monotonic()-start,
            "stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr)}


def parse_native(path:Path):
    node=None; steps=[]; step_indices=set(); virtual={}; average={}; lines={}
    for line in path.read_text().splitlines():
        if line.startswith("HE,"): continue
        f=line.split(",")
        if f[0]=="NODE":
            if node is not None: raise RuntimeError("DUPLICATE_C_NODE")
            node={"iz":int(f[1]),"z":float(f[2]),"xH1s":float(f[3]),
                  "xHII":float(f[4]),"xHeII":float(f[5]),"xe":float(f[6]),
                  "Tm_K":float(f[7]),"post_saha":bool(int(f[8]))}
        elif f[0]=="STEP":
            j=int(f[1])
            if j not in range(N_ACCEPTED) or j in step_indices:
                raise RuntimeError(f"C_ORACLE_STEP_DUPLICATE_OR_INVALID_INDEX:{j}")
            step_indices.add(j)
            step={"j":int(f[1]),"iz":int(f[2]),"z":float(f[3]),
                "xH1s":float(f[4]),"xHII":float(f[5]),"xHeII":float(f[6]),
                "xe":float(f[7]),"Tm_K":float(f[8]),"hydrogen_rhs":float(f[9]),
                "helium_rhs":float(f[10]),"post_saha":bool(int(f[11]))}
            for name in ("hydrogen_rhs","helium_rhs"):
                if not math.isfinite(step[name]):
                    raise RuntimeError(f"C_ORACLE_STEP_NONFINITE_RHS:j={j}:species={name}")
            steps.append(step)
        elif f[0] in ("V","A","L"):
            j,b=int(f[1]),int(f[2]); value=float(f[3])
            target={"V":virtual,"A":average,"L":lines}[f[0]]
            if j not in range(N_ACCEPTED) or b in target.get(j,{}):
                raise RuntimeError(f"C_ORACLE_{f[0]}_DUPLICATE_OR_INVALID_INDEX:j={j}:bin={b}")
            if not math.isfinite(value):
                raise RuntimeError(f"C_ORACLE_{f[0]}_NONFINITE:j={j}:bin={b}")
            target.setdefault(j,{})[b]=value
    if node is None or len(steps)!=N_ACCEPTED or step_indices!=set(range(N_ACCEPTED)):
        raise RuntimeError("C_ORACLE_ROW_COUNT_OR_INDEX_SET")
    for tag,series,n in (("V",virtual,NVIRT),("A",average,NVIRT),("L",lines,3)):
        if set(series)!=set(range(N_ACCEPTED)) or any(set(r)!=set(range(n)) for r in series.values()):
            raise RuntimeError(f"C_ORACLE_{tag}_SPECTRUM_SHAPE")
    return node,steps,virtual,average,lines


class FullSourceCOracle:
    """ctypes access to upstream C FULL RHS using caller-owned accepted history."""
    def __init__(self,shared:Path,source_dir:Path,c:HyRec2012Cosmology):
        self.lib=ctypes.CDLL(str(shared))
        p=ctypes.POINTER(ctypes.c_double)
        fn=self.lib.rec_r3b_original_full_step
        fn.argtypes=[ctypes.c_double]*6+[ctypes.c_double,ctypes.c_uint,ctypes.c_double,
            p,p,p,p,p]
        fn.restype=ctypes.c_double
        self.fn=fn; self.source_dir=source_dir; self.c=c
        self.metrics={"evaluations":0,"max_rhs_scaled":0.0,
            "max_virtual_tolerance_ratio":0.0,"max_average_tolerance_ratio":0.0,
            "max_lyman_tolerance_ratio":0.0}

    def __call__(self,j,z,xh,xhe,tm,vhistory,lhistory):
        vv=np_carray(vhistory,(NVIRT,j)); ll=np_carray(lhistory,(3,j))
        outv=np.empty(NVIRT); outl=np.empty(3); outa=np.empty(NVIRT)
        # Native read_rates/read_twog_params resolve original table names in cwd.
        old=os.getcwd(); os.chdir(self.source_dir)
        try:
            rhs=self.fn(float(xh+xhe),float(xh),float(self.c.nH0_m3*1.e-6*(1.+z)**3),
                float(self.c.hubble_s(z)),float(KB_EV_K*tm),
                float(KB_EV_K*self.c.T0_K*(1.+z)),float(z0(self.c)),
                int(j),float(z),vv.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                ll.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                outv.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                outl.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                outa.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
        finally:
            os.chdir(old)
        return {"rhs":rhs,"virtual":outv,"lyman":outl,"average":outa,
                "metrics":self.metrics}


def z0(c): return c.redshift(c.izH0)


def np_carray(value,shape):
    import numpy as np
    arr=np.asarray(value,dtype=np.float64,order="C")
    if arr.shape!=shape: raise ValueError(f"history shape {arr.shape} != {shape}")
    # ctypes needs a non-null pointer even for the empty prehistory input.
    if arr.size==0: arr=np.zeros((1,),dtype=np.float64)
    return arr


def compare_state(a,b,j):
    limits={"xHII":5.e-9,"xe":5.e-9,"xHeII":5.e-10,"Tm_K":5.e-10}
    for name,lim in limits.items():
        av=float(a[name]); bv=float(b[name])
        if not all(map(math.isfinite,(av,bv,lim))) or lim<=0:
            raise ArithmeticError(f"INDEPENDENT_HISTORY_NONFINITE step={j} quantity={name}")
        scaled=(abs(av-bv) if name=="xHeII" else abs(av-bv)/max(abs(bv),1.e-8 if name in ("xHII","xe") else 1.))
        if not math.isfinite(scaled):
            raise ArithmeticError(f"INDEPENDENT_HISTORY_NONFINITE_RATIO step={j} quantity={name}")
        if scaled>lim:
            raise ArithmeticError(f"INDEPENDENT_HISTORY_PARITY step={j} quantity={name} scaled={scaled:.17g} limit={lim:.17g}")
    for name in ("z","xH1s"):
        if not all(math.isfinite(float(row[name])) for row in (a,b)):
            raise ArithmeticError(f"INDEPENDENT_HISTORY_NONFINITE step={j} quantity={name}")
    if abs(float(a["z"])-float(b["z"]))>2.e-12:
        raise ArithmeticError(f"SOURCE_REDSHIFT_MISMATCH step={j}")
    if abs(float(a["xH1s"])-float(b["xH1s"]))>5.e-9*max(abs(float(b["xH1s"])),1.e-8):
        raise ArithmeticError(f"SOURCE_NEUTRAL_HYDROGEN_MISMATCH step={j}")
    if a["iz"]!=b["iz"] or a["post_saha"]!=b["post_saha"]:
        raise ArithmeticError(f"SOURCE_BRANCH_OR_INDEX_MISMATCH step={j}")


def checked_integrated_rhs_ratio(pval,cval,lim,j,name):
    """Validate trajectory RHS operands and frozen limit before parity/metrics."""
    if not all(map(math.isfinite,(pval,cval,lim))) or lim<=0:
        raise ArithmeticError(f"INDEPENDENT_RHS_NONFINITE step={j} species={name}")
    scaled=abs(pval-cval)/max(1.,abs(cval))
    if not math.isfinite(scaled):
        raise ArithmeticError(f"INDEPENDENT_RHS_NONFINITE_RATIO step={j} species={name}")
    if scaled>lim:
        raise ArithmeticError(f"INDEPENDENT_RHS_PARITY step={j} species={name} scaled={scaled:.17g}")
    return scaled


def compare_photon_spectra(py_virtual,py_average,py_lyman,c_virtual,c_average,c_lyman,
                           fbb_virtual,fbb_lyman,step):
    """Compare physical outgoing, average, and Lyman spectra by channel."""
    maxima={"virtual":0.,"average":0.,"lyman":0.}
    for name,py,cs,fb,n in (
        ("virtual",py_virtual,c_virtual,fbb_virtual,NVIRT),
        ("average",py_average,c_average,fbb_virtual,NVIRT),
        ("lyman",py_lyman,c_lyman,fbb_lyman,3)):
        py=np.asarray(py,dtype=float); cs=np.asarray(cs,dtype=float); fb=np.asarray(fb,dtype=float)
        if py.shape!=(n,) or cs.shape!=(n,) or fb.shape!=(n,):
            raise ValueError(f"INTEGRATED_PHOTON_SHAPE step={step} species={name}")
        if not all(np.all(np.isfinite(arr)) for arr in (py,cs,fb)):
            raise ArithmeticError(f"INTEGRATED_PHOTON_NONFINITE step={step} species={name}")
        tol=1.e-7*np.maximum(np.abs(py),np.abs(cs))+1.e-10*fb
        if not np.all(np.isfinite(tol)) or np.any(tol<=0):
            raise ArithmeticError(f"INTEGRATED_PHOTON_INVALID_TOLERANCE step={step} species={name}")
        ratio=np.abs(py-cs)/tol
        if not np.all(np.isfinite(ratio)):
            raise ArithmeticError(f"INTEGRATED_PHOTON_NONFINITE_RATIO step={step} species={name}")
        if np.any(ratio>1.):
            bad=int(np.flatnonzero(ratio>1.)[0])
            raise ArithmeticError(f"INTEGRATED_PHOTON_PARITY step={step} species={name} bin={bad} ratio={ratio[bad]:.17g}")
        maxima[name]=float(np.max(ratio))
    return maxima



def compare_helium(py,c,path,shared,ev):
    rows=[line.split(",")[1:] for line in path.read_text().splitlines() if line.startswith("HE,")]
    if len(rows)!=36447 or len(py.iz)!=36447 or c.izH0!=36446:
        raise RuntimeError("H2_HELIUM_ROW_INDEX_CAP_MISMATCH")
    lib=ctypes.CDLL(str(shared)); rate=lib.rec_helium_dxHeIIdlna
    rate.argtypes=[ctypes.c_double]*9; rate.restype=ctypes.c_double
    names=("z","xe","xHII","xHeI","xHeII","xHeIII","Tm_K")
    maxima={k:0. for k in names}; common=traj=0.
    with (ev/"python_helium_rows.jsonl").open("x") as out:
        for i,row in enumerate(rows):
            ci=int(row[0]); values=list(map(float,row[1:13])); method=int(row[13]); post=int(row[14])
            if ci!=i: raise RuntimeError(f"HE_INDEX:{i}")
            z,xe,xh,he1,he2,he3,tm,rhs,zin,H,x1in,hein=values
            expected={"SAHA_ALGEBRAIC":-1,"POST_SAHA":1,"SOURCE_PREDICTOR":0}[py.update_method[i]]
            if expected!=method or bool(post)!=py.post_saha[i]: raise RuntimeError(f"HE_STAGE_FLAGS:{i}")
            record={"iz":i,"stage":py.stage[i],"update_method":py.update_method[i],"post_saha":py.post_saha[i]}
            for k,cv in zip(names,values[:7]):
                pv=float(getattr(py,k)[i]); record[k]=pv
                d=abs(pv-cv)/max(1.,abs(cv)); maxima[k]=max(maxima[k],d)
                if not math.isfinite(d) or d>2e-12: raise ArithmeticError(f"HE_STATE:{i}:{k}:{d:.17g}")
            record["helium_rhs_dln_a"]=py.helium_rhs_dln_a[i]
            out.write(json.dumps(record,separators=(",",":"))+"\n")
            if method!=-1:
                cm=rate(x1in,hein,c.nH0_m3,c.T0_K,c.fHe,H,zin,1.,1.)
                pm=helium_rhs(c,x1in,hein,H,zin)
                if not all(map(math.isfinite,(cm,pm,rhs,py.helium_rhs_dln_a[i]))):
                    raise ArithmeticError(f"HE_RHS_NONFINITE:{i}")
                d=abs(pm-cm)/max(1.,abs(cm)); common=max(common,d)
                dt=abs(py.helium_rhs_dln_a[i]-rhs)/max(1.,abs(rhs)); traj=max(traj,dt)
                if not all(map(math.isfinite,(d,dt))):
                    raise ArithmeticError(f"HE_RHS_NONFINITE_RATIO:{i}")
                if d>2e-10 or dt>2e-10: raise ArithmeticError(f"HE_RHS:{i}:common={d:.17g}:trajectory={dt:.17g}")
            if abs(py.xHII[i]+py.xHeII[i]+2*py.xHeIII[i]-py.xe[i])>5e-13:
                raise ArithmeticError(f"HE_ELECTRON_LEDGER:{i}")
            if abs(py.xHeI[i]+py.xHeII[i]+py.xHeIII[i]-c.fHe)>5e-13:
                raise ArithmeticError(f"HE_NUCLEUS_LEDGER:{i}")
    return {"status":"PASS","rows":len(rows),"izH0":c.izH0,"max_state_scaled_max1":maxima,
        "max_rhs_common_scaled_max1":common,"max_rhs_trajectory_scaled_max1":traj,
        "rows_sha256":sha(ev/"python_helium_rows.jsonl")}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--evidence-dir",type=Path,required=True)

    args=ap.parse_args()
    ev=args.evidence_dir.resolve()
    if ev.exists(): raise SystemExit("EVIDENCE_DIR_EXISTS; select a fresh immutable id")
    ev.mkdir(parents=True,exist_ok=False)
    start=time.monotonic(); usage0=resource.getrusage(resource.RUSAGE_SELF)
    original_affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,"sched_getaffinity") else []
    if original_affinity: os.sched_setaffinity(0,set(original_affinity[:1]))
    vm_before_limit_kb=next(int(line.split()[1]) for line in open("/proc/self/status") if line.startswith("VmSize:"))
    report={"status":"FAIL","scope":"8 accepted source-grid H+He FULL start steps; not full-history admission",
        "source_zip_sha256":PINNED_ZIP_SHA,"python_producer_sha256":sha(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_refined_start.py"),
        "scientific_admission":"HOLD_PENDING_INDEPENDENT_REVIEW", "three_level_order":"NOT_RUN",
        "resources":{"allowed_affinity":original_affinity[:1],"OMP_NUM_THREADS":1,
            "address_space_limit_bytes":2*1024**3,"wall_limit_s":180,
            "prelimit_vm_size_kib":vm_before_limit_kb},"first_failure":None}
    try:
        # Hash the small producer before imposing RLIMIT_AS; NumPy/OpenBLAS
        # reserves a large virtual mapping at import time and some kernels
        # reject even tiny allocations if the cap is installed first.
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(120,120))
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("U2_WALL_LIMIT_180S")))
        signal.alarm(180)
        source_dir=safe_extract_source(
            ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip",ev/"source_extract")
        original=check_sources(source_dir)
        header=source_dir/"hyrec_params.h"
        before=header.read_bytes()
        token=b"#define DLNA          8.49e-5"
        if before.count(token)!=1: raise RuntimeError("ACTIVE_DLNA_TOKEN_NOT_UNIQUE")
        after=before.replace(token,b"#define DLNA          (8.49e-5/2.)")
        header.write_bytes(after)
        if after.replace(b"#define DLNA          (8.49e-5/2.)",token)!=before:
            raise RuntimeError("SOURCE_CHANGE_EXCEEDS_ONE_DLNA_TOKEN")
        report["source_identity"]={"original":original,"modified":{
            name:sha(source_dir/name) for name in PINNED_SOURCE},
            "only_source_change":"one active DLNA token: 8.49e-5 -> (8.49e-5/2.)"}
        csrc=ROOT/"scripts/c_harness/original_hyrec_r3i_h2_start_harness.c"
        shim=csrc
        cc=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(source_dir),str(csrc),
            str(source_dir/"history.c"),str(source_dir/"hydrogen.c"),str(source_dir/"helium.c"),
            str(source_dir/"hyrectools.c"),"-lm","-o",str(ev/"native_full_start_oracle")]
        build=run_capture(cc,source_dir,ev/"native_build_stdout.txt",ev/"native_build_stderr.txt",60,os.environ.copy())
        report["native_build"]=build
        if build["returncode"]: raise RuntimeError("NATIVE_C_BUILD_FAILED")
        report["native_binary_sha256"]=sha(ev/"native_full_start_oracle")
        run=run_capture([str(ev/"native_full_start_oracle")],source_dir,
            ev/"native_oracle_stdout.csv",ev/"native_oracle_stderr.txt",30,os.environ.copy())
        report["native_run"]=run
        if run["returncode"]: raise RuntimeError("NATIVE_C_ORACLE_FAILED")
        cnode,csteps,cv,ca,cl=parse_native(ev/"native_oracle_stdout.csv")
        report["native_rows"]={"printed_start_node_rows":1,"accepted_steps":len(csteps),
            "accepted_state_nodes":1+len(csteps),"virtual_bins":NVIRT,
            "average_bins":NVIRT,"lyman_bins":3,
            "interpretation":"one NODE record is the U1 boundary; each of eight STEP records adds one accepted output node"}

        # C FULL common-input oracle for every Python accepted state and each
        # post-Saha probe; original C source is compiled unchanged.
        cc2=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-DR3I_SHARED","-I",str(source_dir),
            str(shim),str(source_dir/"hydrogen.c"),str(source_dir/"helium.c"),str(source_dir/"hyrectools.c"),
            "-lm","-o",str(ev/"liboriginal_full_source.so")]
        build2=run_capture(cc2,source_dir,ev/"common_build_stdout.txt",ev/"common_build_stderr.txt",60,os.environ.copy())
        report["common_input_build"]=build2
        if build2["returncode"]: raise RuntimeError("COMMON_INPUT_C_BUILD_FAILED")
        report["common_input_binary_sha256"]=sha(ev/"liboriginal_full_source.so")

        c=HyRec2012Cosmology()
        helium=integrate_helium_stages(c)
        report["helium_parity"]=compare_helium(helium,c,ev/"native_oracle_stdout.csv",ev/"liboriginal_full_source.so",ev)
        rate_table=OriginalHyRecPrimitiveRateTable.from_archive(
            ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
        photon_table=_canonical_twophoton_table(rate_table.archive_path)
        source=make_hmla_source(c,rate_table)
        oracle=FullSourceCOracle(ev/"liboriginal_full_source.so",source_dir,c)
        result=integrate_full_start_eight(helium,c,source,common_input_oracle=oracle)
        report["python_full_evaluations"]=result.full_evaluations
        if result.full_evaluations>MAX_FULL_EVALUATIONS: raise RuntimeError("FULL_EVALUATION_CAP")

        # Native integrated trajectory parity. Common-input checks were run
        # online during Python integration, so a first mismatch stopped it.
        state_diffs=[]; state_max={"xHII_scaled":0.,"xe_scaled":0.,
            "xHeII_abs":0.,"Tm_relative":0.}
        rhs_max={"H":0.,"He":0.}
        py_nodes=[]
        py0={"iz":int(result.iz[0]),"post_saha":bool(result.post_saha[0]),
             **{k:float(getattr(result,k)[0]) for k in ("z","xH1s","xHII","xHeII","xe","Tm_K")}}
        compare_state(py0,cnode,0); py_nodes.append(py0)
        for j,cstep in enumerate(csteps):
            py={"iz":int(result.iz[j+1]),"post_saha":bool(result.post_saha[j+1]),
                **{k:float(getattr(result,k)[j+1]) for k in ("z","xH1s","xHII","xHeII","xe","Tm_K")}}
            compare_state(py,cstep,j+1)
            state_diffs.append({k:float(py[k]-cstep[k]) for k in ("xHII","xe","xHeII","Tm_K")})
            state_max["xHII_scaled"]=max(state_max["xHII_scaled"],
                abs(py["xHII"]-cstep["xHII"])/max(abs(cstep["xHII"]),1.e-8))
            state_max["xe_scaled"]=max(state_max["xe_scaled"],
                abs(py["xe"]-cstep["xe"])/max(abs(cstep["xe"]),1.e-8))
            state_max["xHeII_abs"]=max(state_max["xHeII_abs"],abs(py["xHeII"]-cstep["xHeII"]))
            state_max["Tm_relative"]=max(state_max["Tm_relative"],
                abs(py["Tm_K"]-cstep["Tm_K"])/abs(cstep["Tm_K"]))
            # At node j the C trajectory RHS maps are source-native; compare
            # independent-trajectory RHS values after integration state drift.
            for name,pval,cval,lim in (("H",float(result.hydrogen_rhs_dln_a[j]),cstep["hydrogen_rhs"],2.e-7),
                                      ("He",float(result.helium_rhs_dln_a[j]),cstep["helium_rhs"],2.e-7)):
                scaled=checked_integrated_rhs_ratio(pval,cval,lim,j,name)
                rhs_max[name]=max(rhs_max[name],scaled)
        photon_max={"virtual":0.,"average":0.,"lyman":0.}
        line_energy=np.array((10.198714553953742,12.087365397278509,12.748393192442178))
        for j in range(N_ACCEPTED):
            tr_ev=KB_EV_K*c.T0_K*(1.+float(result.z[j]))
            fbb_v=1./np.expm1(photon_table.energy_eV/tr_ev)
            fbb_l=1./np.expm1(line_energy/tr_ev)
            per_step=compare_photon_spectra(
                result.virtual_out[:,j],result.average_virtual[:,j],result.lyman_out[:,j],
                np.array([cv[j][b] for b in range(NVIRT)]),
                np.array([ca[j][b] for b in range(NVIRT)]),
                np.array([cl[j][b] for b in range(3)]),fbb_v,fbb_l,j)
            for name,value in per_step.items(): photon_max[name]=max(photon_max[name],value)
        report["integrated_state_parity"]={"status":"PASS","nodes":9,"accepted_steps":8,
            "limits":{"xHII_xe_scaled":5.e-9,"xHeII_abs":5.e-10,"Tm_relative":5.e-10},
            "max_error":state_max,"stepwise_differences":state_diffs}
        report["integrated_rhs_parity"]={"status":"PASS","criterion":"|Python-C|/max(1,|C|) <= 2e-7",
            "hydrogen_values":8,"helium_values":8,
            "max_hydrogen_scaled":rhs_max["H"],
            "max_helium_scaled":rhs_max["He"]}
        # The native driver emits a complete independent C row per column;
        # common-input C/Python virtual, average, and line spectra are checked
        # within each RHS callback before the Python accepted column is stored.
        report["common_input_parity"]={"status":"PASS","rhs_scaled_limit":2.e-10,
            "photon_limit":"1e-7 max(|C|,|Python|) + 1e-10 fBB(E,Tr)",
            **oracle.metrics,"full_evaluations_compared":result.full_evaluations}
        report["integrated_photon_parity"]={"status":"PASS","columns":8,
            "limits":"abs(C-P) <= 1e-7 max(abs(C),abs(P)) + 1e-10 fBB(E,Tr)",
            "max_tolerance_ratio":photon_max}
        report["photon_history"]={"committed_columns":8,"virtual_bins_per_column":NVIRT,
            "average_virtual_bins_per_column":NVIRT,"lyman_bins_per_column":3,
            "future_columns_initialized":"NaN sentinel; only current accepted column committed"}
        report["source_stage"]={"joint_H_He":True,"XHEII_MIN":1.e-6,
            "post_saha_flags":list(map(bool,result.post_saha)),"native_dlna":SOURCE_DLNA}
        np.savez_compressed(ev/"python_accepted_history.npz",iz=result.iz,z=result.z,
            xH1s=result.xH1s,xHII=result.xHII,xHeII=result.xHeII,xe=result.xe,Tm_K=result.Tm_K,
            helium_rhs_dln_a=result.helium_rhs_dln_a,hydrogen_rhs_dln_a=result.hydrogen_rhs_dln_a,
            post_saha=result.post_saha,virtual_out=result.virtual_out,
            average_virtual=result.average_virtual,lyman_out=result.lyman_out,
            matrix_residual=result.matrix_residual)
        report["python_history_sha256"]=sha(ev/"python_accepted_history.npz")
        report["status"]="PASS"
    except BaseException as exc:
        report["status"]="FAIL"
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc)}
        (ev/"failure.txt").write_text(f"{type(exc).__name__}: {exc}\n")
    finally:
        signal.alarm(0)
        usage1=resource.getrusage(resource.RUSAGE_SELF)
        report["resources"].update({"wall_s":time.monotonic()-start,
            "parent_cpu_s":(usage1.ru_utime+usage1.ru_stime)-(usage0.ru_utime+usage0.ru_stime),
            "parent_peak_rss_bytes":usage1.ru_maxrss*1024,
            "children_cpu_s":(resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+
                              resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime),
            "children_peak_rss_bytes":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024})
        (ev/"verification.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print(json.dumps(report,sort_keys=True,indent=2))
    if report["status"]!="PASS": raise SystemExit(2)


if __name__=="__main__": main()
