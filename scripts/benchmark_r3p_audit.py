#!/usr/bin/env python3
"""Re-audit reviewed R3M saved outputs; never execute a physical trajectory.

One invocation is capped at 60 CPU / 180 wall seconds and 2 GiB. Restore,
hashing and setup are reported separately from the matched audit interval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"src"),str(ROOT/"scripts")]
import numpy as np
import scipy
import verify_r3i_h2_u6_rt_boundary as legacy
import r3p_stream_audit as cached
from r3p_rust_audit import PrefixAuditor, library_from_build, sha256
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u6_rt_boundary import U6RTResult, load_frozen_checkpoint

REVIEWED = {
    "python_u6_rt.npz":"5ceb99a7ed221f920460aa41188ce60a748332e854a75ee58362d3f10a360cd2",
    "native_oracle_stdout.csv":"57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38",
    "verification.json":"1d55f1ff90a9fad7174ddc6022bbf957aeb4f683b7831ecbb63acd854d925b4b",
}


def array_sha(a):
    return hashlib.sha256(memoryview(np.ascontiguousarray(a, dtype="<f8")).cast("B")).hexdigest()


class CaptureArrays:
    """Observe owned native arrays without editing the frozen reference source."""
    def __init__(self):
        self.arrays = []
    def __getattr__(self, name):
        return getattr(np,name)
    def full(self, *args, **kwargs):
        value = np.full(*args, **kwargs)
        self.arrays.append(value)
        return value


def load_inputs(raw, checkpoint):
    raw = Path(raw).resolve()
    for name,digest in REVIEWED.items():
        if sha256(raw/name) != digest:
            raise ValueError(f"R3P_REVIEWED_RAW_IDENTITY:{name}")
    receipt = json.loads((raw/"verification.json").read_text())
    if receipt["first_failure"] is not None or receipt["python_result"]["steps"] != 5210:
        raise ValueError("R3P_RAW_EXECUTION_NOT_COMPLETE")
    legacy.verify_source_closure(Path(checkpoint))
    cp = load_frozen_checkpoint(Path(checkpoint))
    event = dict(cp["event"])
    del cp
    with np.load(raw/"python_u6_rt.npz",allow_pickle=False) as d:
        states = tuple(json.loads(str(x)) for x in d["states_json"])
        steps = tuple(json.loads(str(x)) for x in d["steps_json"])
        arrays = [d[k] for k in ("virtual_out","average_virtual","lyman_out")]
    for a in arrays:
        if a.dtype != np.dtype("float64") or not np.all(np.isfinite(a)):
            raise ValueError("R3P_SAVED_ARRAY_CONTRACT")
        a.flags.writeable = False
    result = U6RTResult(states,steps,*arrays,event,5210,
        receipt["python_result"]["status"],receipt["python_result"]["rt_stop_iz"])
    c = legacy.HyRec2012Cosmology()
    rates = legacy.OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
    table = legacy._canonical_twophoton_table(rates.archive_path)
    source = legacy.make_hmla_source(c,rates)
    source_dir = raw/"source_extract/HyRec"
    for name,digest in receipt["modified_source_sha256"].items():
        if sha256(source_dir/name) != digest:
            raise ValueError(f"R3P_SAVED_SOURCE_CHANGED:{name}")
    lib = raw/"liboriginal_full_source.so"
    if sha256(lib) != receipt["common_binary_sha256"]:
        raise ValueError("R3P_SAVED_ORACLE_BINARY_CHANGED")
    oracle = legacy.CombinedOracle(lib,source_dir,c)
    return result,c,table,source,oracle,source_dir


def run(args):
    output = args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    available = sorted(os.sched_getaffinity(0))
    if args.cpus > len(available):
        raise ValueError("R3P_AFFINITY_TOO_SMALL")
    os.sched_setaffinity(0,set(available[:args.cpus]))
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU,(60,61))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("R3P_AUDIT_WALL_CAP")))
    signal.alarm(180)
    all_cpu,all_wall = time.process_time(),time.perf_counter()
    report = {"schema":"rec.r3p.saved-audit.v1","status":"FAILED","backend":args.backend,
              "threads":args.threads if args.backend=="rust" else 1,"new_physical_steps":0,
              "execution_location":"ChatGPT sandbox or explicitly recorded executor; see host",
              "host":platform.node(),"python":platform.python_version(),"numpy":np.__version__,
              "scipy":scipy.__version__,"affinity":sorted(os.sched_getaffinity(0)),
              "blas_threads":1,"cpu_cap_s":60,"wall_cap_s":180,"input_sha256":REVIEWED,
              "measurement":"Audit interval includes allocation, CSV reading, all predicates, maxima and forensic files. Setup/hashes separate."}
    prefix = None
    try:
        context = load_inputs(args.raw,args.checkpoint)
        result,c,table,source,oracle,source_dir = context
        module = legacy if args.backend=="legacy" else cached
        report["source_sha256"] = {str(Path(p).relative_to(ROOT)):sha256(p)
            for p in (Path(__file__),Path(cached.__file__),ROOT/"scripts/r3p_rust_audit.py")}
        if args.backend=="rust":
            if args.build is None: raise ValueError("R3P_RUST_BUILD_RECEIPT_REQUIRED")
            lib = library_from_build(args.build)
            t0, c0 = time.perf_counter(),time.process_time()
            prefix = PrefixAuditor(lib,threads=args.threads,block_columns=args.block_columns)
            report["pool_setup"]={"wall_s":time.perf_counter()-t0,"cpu_s":time.process_time()-c0}
            report["library_sha256"] = sha256(lib)
        capture, prior_np = CaptureArrays(),module.np
        report["setup_cpu_s"]=time.process_time()-all_cpu
        report["setup_wall_s"]=time.perf_counter()-all_wall
        guards = 0
        def guard(_):
            nonlocal guards
            guards += 1
            if time.process_time()-all_cpu > 57. or time.perf_counter()-all_wall > 177.:
                raise RuntimeError("R3P_AUDIT_BUDGET_WITH_RESERVE")
        module.np = capture
        t0,c0 = time.perf_counter(),time.process_time()
        try:
            extra = {"prefix_auditor":prefix} if prefix else {}
            verdict = module.compare_native_stream(args.raw/"native_oracle_stdout.csv",
                result,c,table,source,oracle,source_dir,output,guard,**extra)
        finally:
            module.np = prior_np
        report["audit_cpu_s"] = time.process_time()-c0
        report["audit_wall_s"] = time.perf_counter()-t0
        if len(capture.arrays)!=2:
            raise AssertionError("R3P_NATIVE_ARRAY_CAPTURE")
        report["native_array_sha256"] = [array_sha(a) for a in capture.arrays]
        report["verdict"] = verdict
        report["verdict_sha256"] = hashlib.sha256(json.dumps(verdict,sort_keys=True,allow_nan=False).encode()).hexdigest()
        report["diagnostic_sha256"]={name:sha256(output/name) for name in ("average_diagnostics.jsonl","average_raw_failures.jsonl")}
        report["guard_calls"] = guards
        if prefix: report["prefix_work"] = dict(prefix.stats)
        if args.ratio_fixture:
            cols = min(32,len(result.steps));p=legacy.PREFIX_COLUMNS
            py = np.ascontiguousarray(result.virtual_out[:,p:p+cols].T).ravel()
            native = np.ascontiguousarray(capture.arrays[0][:,p:p+cols].T).ravel()
            fbb = np.array([1./math.expm1(float(e)/(legacy.KB_EV_K*c.T0_K*(1.+result.states[i]["z"])))
                            for i in range(cols) for e in table.energy_eV])
            np.savez(output/"ratio_fixture.npz",py=py,native=native,fbb=fbb)
            report["ratio_fixture_sha256"] = sha256(output/"ratio_fixture.npz")
        for name,digest in REVIEWED.items():
            if sha256(args.raw/name)!=digest: raise ValueError("R3P_INPUT_MUTATED")
        guard("final")
        report["status"]="AUDIT_COMPLETED_PENDING_DIFFERENTIAL_REVIEW"
    except BaseException as exc:
        report["first_failure"]={"type":type(exc).__name__,"message":str(exc)}
    finally:
        if prefix: prefix.close()
        signal.alarm(0)
        report.update(total_cpu_s=time.process_time()-all_cpu,total_wall_s=time.perf_counter()-all_wall,
                      peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        with (output/"result.json").open("x") as f:
            json.dump(report,f,sort_keys=True,indent=2,allow_nan=False);f.write("\n");f.flush();os.fsync(f.fileno())
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--checkpoint",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--backend",choices=("legacy","cached","rust"),required=True)
    p.add_argument("--build",type=Path)
    p.add_argument("--threads",type=int,choices=(1,2,4),default=1)
    p.add_argument("--cpus",type=int,choices=(1,2,4),default=4)
    p.add_argument("--block-columns",type=int,choices=(1,8,16,32,64),default=32)
    p.add_argument("--ratio-fixture",action="store_true")
    args=p.parse_args();r=run(args)
    print(json.dumps({k:r.get(k) for k in ("status","backend","threads","audit_cpu_s","audit_wall_s","total_cpu_s","peak_rss_bytes","first_failure")},sort_keys=True))
    raise SystemExit(0 if r["status"]=="AUDIT_COMPLETED_PENDING_DIFFERENTIAL_REVIEW" else 2)


if __name__=="__main__":main()
