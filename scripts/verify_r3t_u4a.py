#!/usr/bin/env python3
"""Supervised bounded R3T-U4A h/4 restart verification (16 or 32 steps)."""
from __future__ import annotations
import argparse, hashlib, json, os, resource, signal, subprocess, sys, time
from pathlib import Path
os.environ.update({"OMP_NUM_THREADS":"1", "OPENBLAS_NUM_THREADS":"1", "MKL_NUM_THREADS":"1", "NUMEXPR_NUM_THREADS":"1"})
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/"src"), str(ROOT/"scripts")]
from verify_r3i_h2_start import FullSourceCOracle, sha, compare_state
from verify_r3o_h4_start import prepare_source
from full_bianchi_hyrec.trajectory.primordial_2012_quarter_start import QuarterStartCosmology, make_hmla_source
from full_bianchi_hyrec.trajectory.primordial_2012_quarter_u4a import (CHECKPOINT_SHA256, SOURCE_INDEX_START, START_IZ, PREFIX_COLUMNS, U4B_START_IZ, U4B_PREFIX_COLUMNS, common_input_observer, integrate_u4a, load_reviewed_restart, load_u4b_restart, restart_checkpoint)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table

ZIP=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
HARNESS=ROOT/"scripts/c_harness/original_hyrec_r3q_h4_continuation_harness.c"
RESTART_HARNESS=ROOT/"scripts/c_harness/original_hyrec_r3t_u4a_restart.c"

def write_new(path: Path, obj: dict):
    with path.open("x") as f: json.dump(obj, f, indent=2, sort_keys=True); f.write("\n")

def compare_native_restart(path, result, table, c, initial_rhs_tail=None):
    """Compare native common-checkpoint restart output, never a C-history claim."""
    rows={"STEP":[],"RHS":[],"V":{},"A":{},"L":{}}
    expected_n=0; expected_tag="STEP"; expected_bin=0
    for line_no,line in enumerate(path.read_text().splitlines(),1):
        f=line.split(","); tag=f[0]
        if tag != expected_tag: raise ArithmeticError(f"NATIVE_RESTART_ORDER:{line_no}")
        if tag in ("STEP","RHS"):
            if len(f) != (8 if tag=="STEP" else 4): raise ArithmeticError("NATIVE_RESTART_FRAME")
            rows[tag].append(f[1:])
        elif tag in ("V","A","L"):
            if len(f)!=4: raise ArithmeticError("NATIVE_RESTART_FRAME")
            key=(int(f[1]),int(f[2]))
            if key in rows[tag]: raise ArithmeticError("NATIVE_RESTART_DUPLICATE")
            rows[tag][key]=float(f[3])
        else: raise ArithmeticError(f"NATIVE_RESTART_UNKNOWN_ROW:{line_no}")
        if tag=="STEP": expected_tag="RHS"
        elif tag=="RHS": expected_tag="V"; expected_bin=0
        elif tag in ("V","A","L"):
            bins={"V":311,"A":311,"L":3}[tag]
            if int(f[1])!=expected_n or int(f[2])!=expected_bin: raise ArithmeticError("NATIVE_RESTART_ORDER_INDEX")
            expected_bin+=1
            if expected_bin==bins:
                expected_tag={"V":"A","A":"L","L":"STEP"}[tag]; expected_bin=0
                if tag=="L": expected_n+=1
    if len(rows["STEP"]) != len(result.steps) or len(rows["RHS"]) != len(result.steps): raise ArithmeticError("NATIVE_RESTART_ROW_COUNT")
    if any(len(rows[tag]) != len(result.steps)*bins for tag,bins in (("V",311),("A",311),("L",3))): raise ArithmeticError("NATIVE_RESTART_PHOTON_ROW_COUNT")
    max_state=max_rhs=max_lane=0.
    for n,(state,step) in enumerate(zip(result.states[1:],result.steps)):
        r=rows["STEP"][n]
        if int(r[0]) != n or int(r[1]) != state["iz"] or bool(int(r[6])) != state["post_saha"]: raise ArithmeticError("NATIVE_RESTART_INDEX_OR_POST")
        if not np.isfinite(float(r[2])) or abs(float(r[2])-state["z"]) > 2e-12: raise ArithmeticError("NATIVE_RESTART_REDSHIFT")
        native={"iz":int(r[1]),"z":float(r[2]),"xH1s":float(r[3]),"xHII":float(r[4]),"xHeII":0.,"xe":float(r[4]),"Tm_K":float(r[5]),"post_saha":bool(int(r[6]))}
        compare_state(state,native,n)
        for key,val,lim,den in (("xH1s",float(r[3]),5e-9,max(abs(state["xH1s"]),1e-8)),("xHII",float(r[4]),5e-9,max(abs(state["xHII"]),1e-8)),("xe",float(r[4]),5e-9,max(abs(state["xe"]),1e-8)),("Tm_K",float(r[5]),5e-10,max(abs(state["Tm_K"]),1.))):
            if not np.isfinite(val): raise ArithmeticError("NATIVE_RESTART_NONFINITE_STATE:"+key)
            q=abs(state[key]-val)/den; max_state=max(max_state,q)
            if q>lim: raise ArithmeticError("NATIVE_RESTART_STATE_PARITY:"+key)
        rhsrow=rows["RHS"][n]
        if int(rhsrow[0]) != n: raise ArithmeticError("NATIVE_RESTART_RHS_INDEX")
        expected_prev=(result.steps[n-1]["hydrogen_rhs"] if n else initial_rhs_tail[1])
        if initial_rhs_tail is None or not np.isfinite(float(rhsrow[1])) or abs(float(rhsrow[1])-expected_prev)/max(1.,abs(expected_prev))>2e-7: raise ArithmeticError("NATIVE_RESTART_PREDICTOR_TAIL")
        pr=float(rhsrow[2]);
        if not np.isfinite(pr): raise ArithmeticError("NATIVE_RESTART_NONFINITE_RHS")
        q=abs(pr-step["hydrogen_rhs"])/max(1.,abs(pr)); max_rhs=max(max_rhs,q)
        if q>2e-7: raise ArithmeticError("NATIVE_RESTART_H_RHS")
        col=step["photon_col"]
        for tag,array,bins in (("V",result.virtual_out,311),("A",result.average_virtual,311),("L",result.lyman_out,3)):
            for b in range(bins):
                cv=rows[tag].get((n,b)); pv=float(array[b,col])
                if cv is None: raise ArithmeticError("NATIVE_RESTART_MISSING_COLUMN")
                energy=(np.array((10.198714553953742,12.087365397278509,12.748393192442178))[b] if tag=="L" else table.energy_eV[b])
                if not np.isfinite(cv) or not np.isfinite(pv): raise ArithmeticError("NATIVE_RESTART_NONFINITE_LANE")
                # Photon column is owned by the accepted input, not output.
                zin=c.redshift(step["input_iz"])
                fbb=1./np.expm1(energy/(8.617343e-5*c.T0_K*(1.+zin)))
                ratio=abs(pv-cv)/(1e-7*max(abs(pv),abs(cv))+1e-10*fbb); max_lane=max(max_lane,ratio)
                if not np.isfinite(ratio) or ratio>1.: raise ArithmeticError("NATIVE_RESTART_PHOTON_PARITY")
    return {"status":"PASS_COMMON_CHECKPOINT_NATIVE_RESTART", "max_state_scaled":max_state,"max_h_rhs_scaled":max_rhs,"max_lane_tolerance_ratio":max_lane}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--mode",choices=("u4a","u4b"),default="u4a"); p.add_argument("--checkpoint", type=Path, required=True); p.add_argument("--accepted-dir",type=Path); p.add_argument("--evidence-dir", type=Path, required=True); p.add_argument("--new-allocation-id", required=True); p.add_argument("--steps", type=int, choices=(16,32), default=32); a=p.parse_args()
    if a.mode=="u4b" and a.accepted_dir is None: p.error("--accepted-dir is required for U4B")
    if a.mode=="u4a" and a.accepted_dir is not None: p.error("--accepted-dir applies only to U4B")
    ev=a.evidence_dir.resolve(); ev.mkdir(parents=True, exist_ok=False)
    if not a.new_allocation_id.strip() or "CLOSED" in a.new_allocation_id.upper(): p.error("fresh allocation identifier required")
    started=time.monotonic(); ru0=resource.getrusage(resource.RUSAGE_SELF); child0=resource.getrusage(resource.RUSAGE_CHILDREN)
    report={"status":"FAIL", "mode":a.mode, "new_allocation_id":a.new_allocation_id, "argv":[sys.executable]+sys.argv, "checkpoint_sha256":CHECKPOINT_SHA256 if a.mode=="u4a" else None, "limits":{"cpu_s":60,"wall_s":180,"address_space_bytes":2*1024**3,"accepted_steps":a.steps,"single_trajectory_full_evaluations":4*a.steps}, "historical_budget":"CLOSED_HOLD_NOT_RESET", "old_U5_gate":"HOLD", "rei_activation":False}
    phases={}; report["phase_wall_s"]=phases
    write_new(ev/"STARTED.json", report)
    try:
        def tree_cpu():
            own=resource.getrusage(resource.RUSAGE_SELF); children=resource.getrusage(resource.RUSAGE_CHILDREN)
            return (own.ru_utime+own.ru_stime-ru0.ru_utime-ru0.ru_stime)+(children.ru_utime+children.ru_stime-child0.ru_utime-child0.ru_stime)
        def enforce_tree(where):
            used=tree_cpu()
            if used >= 60.: raise RuntimeError(f"PROCESS_TREE_CPU_CAP:{where}:{used:.6f}")
            return used
        resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
        used = resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime
        resource.setrlimit(resource.RLIMIT_CPU, (int(used)+60, int(used)+61))
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("R3T_U4A_WALL_CAP")))
        signal.alarm(180)
        aff=sorted(os.sched_getaffinity(0)); os.sched_setaffinity(0,{aff[0]}); report["affinity"]=[aff[0]]
        t=time.perf_counter(); cp=load_reviewed_restart(a.checkpoint) if a.mode=="u4a" else load_u4b_restart(a.checkpoint,a.accepted_dir); src=prepare_source(ZIP,ev/"source_extract")[0]; phases["setup_source_checkpoint"]=time.perf_counter()-t
        run_start=int(cp.get("run_start_iz",START_IZ)); prefix_cols=int(cp["state"]["iz"]-SOURCE_INDEX_START)
        if a.mode=="u4b" and (run_start!=U4B_START_IZ or prefix_cols!=U4B_PREFIX_COLUMNS): raise ValueError("U4B_NATIVE_INPUT_BINDING")
        lib=ev/"liboriginal_full_source.so"; flags=["gcc","-std=gnu99","-O2","-fno-fast-math","-shared","-fPIC","-DR3Q_SHARED","-I",str(src)]
        cmd=flags+[str(HARNESS)]+[str(src/f) for f in ("history.c","hydrogen.c","helium.c","hyrectools.c")]+["-lm","-o",str(lib)]
        def child_limits():
            resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
            resource.setrlimit(resource.RLIMIT_CPU, (55, 56))
        t=time.perf_counter(); build=subprocess.run(cmd,cwd=src,capture_output=True,text=True,timeout=60,check=False,preexec_fn=child_limits); phases["common_compile"]=time.perf_counter()-t
        (ev/"common_build_stdout.txt").write_text(build.stdout); (ev/"common_build_stderr.txt").write_text(build.stderr)
        if build.returncode: raise RuntimeError("COMMON_SOURCE_BUILD_FAILED")
        enforce_tree("after_common_build")
        c=QuarterStartCosmology(); rates=OriginalHyRecPrimitiveRateTable.from_archive(ZIP); source=make_hmla_source(c,rates); oracle=FullSourceCOracle(lib,src,c)
        metrics={}; table=_canonical_twophoton_table(rates.archive_path)
        # Create-only append-only accepted evidence; trial post-Saha calls are
        # deliberately absent.  Each accepted row owns one current V/A/L col.
        accepted=(ev/"accepted.jsonl").open("x")
        pv=(ev/"accepted_virtual_f64le.bin").open("xb"); pa=(ev/"accepted_average_f64le.bin").open("xb"); pl=(ev/"accepted_lyman_f64le.bin").open("xb")
        prev2, prev = cp["rhs_tail"]
        def on_accept(state, step, out):
            nonlocal prev2, prev
            clean=dict(step); clean["helium_rhs"]=None
            accepted.write(json.dumps({"state":state,"step":clean},sort_keys=True,separators=(",",":"))+"\n"); accepted.flush()
            for handle,array in ((pv,out.outgoing_virtual),(pa,out.average_virtual),(pl,out.outgoing_lyman)):
                handle.write(np.asarray(array,dtype="<f8").tobytes()); handle.flush()
            # Exact-once durable restart receipt for this accepted node.  The
            # complete causal prefix is the immutable checkpoint-prefix files
            # plus the flushed accepted-only column stream above.
            with (ev/f"accepted_checkpoint_{state['iz']}.npz").open("xb") as out_cp:
                np.savez_compressed(out_cp,state_json=np.array(json.dumps(state,sort_keys=True)),
                    predictor=np.array([cp["final_predictor"][0],[prev,step["hydrogen_rhs"]]]),
                    accepted_columns=np.array(state["iz"]-72892,dtype=np.int64))
            prev2, prev = prev, step["hydrogen_rhs"]
        try:
            t=time.perf_counter(); one=integrate_u4a(cp,c,source,accepted_steps=a.steps,max_full_evaluations=4*a.steps,observer=common_input_observer(oracle,table,metrics),on_accept=on_accept); phases["python_one_shot_integration"]=time.perf_counter()-t
        finally:
            for handle in (accepted,pv,pa,pl): handle.close()
        enforce_tree("after_python_restart")
        t=time.perf_counter(); half=a.steps//2
        first=integrate_u4a(cp,c,source,accepted_steps=half,max_full_evaluations=4*half)
        second=None
        if a.mode!="u4b" or first.status!="POST_SAHA_EXIT_WITHIN_BOUND":
            second=integrate_u4a(restart_checkpoint(first),c,source,accepted_steps=a.steps-half,max_full_evaluations=4*(a.steps-half))
        split_final=second if second is not None else first
        split_states=first.states + (second.states[1:] if second is not None else ())
        same=(one.states==split_states and (one.final_predictor==split_final.final_predictor).all() and (one.virtual_out==split_final.virtual_out).all() and (one.average_virtual==split_final.average_virtual).all() and (one.lyman_out==split_final.lyman_out).all())
        if not same: raise ArithmeticError("RESTART_SPLIT_IDENTITY")
        # Native continuation receives precisely the reviewed endpoint and
        # accepted prefix.  It is not an independent reconstruction of U1--U3.
        for name,array in (("checkpoint_prefix_virtual_f64le.bin",cp["virtual_out"]),("checkpoint_prefix_average_f64le.bin",cp["average_virtual"]),("checkpoint_prefix_lyman_f64le.bin",cp["lyman_out"])):
            with (ev/name).open("xb") as f: f.write(np.asarray(array,dtype="<f8",order="C").tobytes())
        native=ev/"native_restart"; ncmd=["gcc","-std=gnu99","-O2","-fno-fast-math","-I",str(src),str(RESTART_HARNESS)]+[str(src/f) for f in ("history.c","hydrogen.c","helium.c","hyrectools.c")]+["-lm","-o",str(native)]
        t=time.perf_counter(); nb=subprocess.run(ncmd,cwd=src,capture_output=True,text=True,timeout=60,check=False,preexec_fn=child_limits); phases["native_compile"]=time.perf_counter()-t
        (ev/"native_build_stdout.txt").write_text(nb.stdout); (ev/"native_build_stderr.txt").write_text(nb.stderr)
        if nb.returncode: raise RuntimeError("NATIVE_RESTART_BUILD_FAILED")
        enforce_tree("after_native_build")
        t=time.perf_counter(); nr=subprocess.run([str(native),str(len(one.steps)),repr(cp["state"]["xe"]),repr(cp["state"]["Tm_K"]),repr(cp["rhs_tail"][0]),repr(cp["rhs_tail"][1]),"1",str(run_start),str(prefix_cols),str(ev/"checkpoint_prefix_virtual_f64le.bin"),str(ev/"checkpoint_prefix_average_f64le.bin"),str(ev/"checkpoint_prefix_lyman_f64le.bin")],cwd=src,capture_output=True,text=True,timeout=120,check=False,preexec_fn=child_limits); phases["native_run"]=time.perf_counter()-t
        (ev/"native_restart_stdout.txt").write_text(nr.stdout); (ev/"native_restart_stderr.txt").write_text(nr.stderr)
        if nr.returncode: raise RuntimeError("NATIVE_RESTART_FAILED")
        enforce_tree("after_native_restart")
        t=time.perf_counter(); native_parity=compare_native_restart(ev/"native_restart_stdout.txt",one,table,c,cp["rhs_tail"]); phases["native_compare"]=time.perf_counter()-t
        with (ev/"final_checkpoint.npz").open("xb") as checkpoint_out:
            np.savez_compressed(checkpoint_out,
                states_json=np.array([json.dumps(s,sort_keys=True) for s in one.states]),
                steps_json=np.array([json.dumps({**s,"helium_rhs":None},sort_keys=True) for s in one.steps]),
                virtual_out=one.virtual_out,average_virtual=one.average_virtual,
                lyman_out=one.lyman_out,final_predictor=one.final_predictor,
                dlna=np.array(2.1225e-5),rei_activation=np.array(False))
        accepted_artifacts={name:sha(ev/name) for name in ("accepted.jsonl","accepted_virtual_f64le.bin","accepted_average_f64le.bin","accepted_lyman_f64le.bin","final_checkpoint.npz")}
        report.update(status="PASS_SCOPED_U4A_RESTART" if a.mode=="u4a" else "PASS_SCOPED_U4B_RESTART", accepted_end_global_index=one.states[-1]["iz"], accepted_steps=len(one.steps), requested_accepted_steps=a.steps, full_evaluations=one.full_evaluations, rt_stop_iz=one.rt_stop_iz, common_input=metrics, native_restart_parity=native_parity, restart_split={"one_shot_accepted":len(one.steps),"first_requested":half,"second_requested":0 if second is None else a.steps-half,"second_skipped_at_event":second is None and first.status=="POST_SAHA_EXIT_WITHIN_BOUND","status":"PASS_EXACT_VALUE_EQUALITY"}, event=one.status, accepted_artifacts=accepted_artifacts, source_zip_sha256=sha(ZIP), checkpoint_file_sha256=sha(a.checkpoint), producer_sha256=sha(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_quarter_u4a.py"))
    except Exception as e:
        report["first_failure"]={"type":type(e).__name__,"message":str(e)}
    finally:
        signal.alarm(0)
        ru=resource.getrusage(resource.RUSAGE_SELF); child=resource.getrusage(resource.RUSAGE_CHILDREN)
        report["resources_observed"]={"parent_cpu_s":ru.ru_utime+ru.ru_stime-ru0.ru_utime-ru0.ru_stime,"child_cpu_s":child.ru_utime+child.ru_stime-child0.ru_utime-child0.ru_stime,"process_tree_cpu_s":(ru.ru_utime+ru.ru_stime-ru0.ru_utime-ru0.ru_stime)+(child.ru_utime+child.ru_stime-child0.ru_utime-child0.ru_stime),"cpu_measurement_scope":"Python main after imports/resource baseline through worker finally; includes waited subprocess children; excludes module import/bootstrap CPU before baseline","wall_s":time.monotonic()-started,"max_rss_kib":ru.ru_maxrss}
        report["phase_wall_s"]["total_wall"]=report["resources_observed"]["wall_s"]
        report["evidence_manifest"]={p.name:sha(p) for p in sorted(ev.iterdir()) if p.is_file() and p.name not in ("RESULT.json","MANIFEST.json")}
        write_new(ev/"MANIFEST.json",report["evidence_manifest"])
        write_new(ev/"RESULT.json",report)
    expected_status="PASS_SCOPED_U4A_RESTART" if a.mode=="u4a" else "PASS_SCOPED_U4B_RESTART"
    if report["status"]!=expected_status: raise SystemExit(1)
if __name__=="__main__": main()
