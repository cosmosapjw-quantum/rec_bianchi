#!/usr/bin/env python3
"""Outer NCP cgroup supervisor for one bounded R3T-U4A worker invocation.

The controller stays outside the transient scope and records the cgroup's
aggregate CPU counter.  It creates no scientific input and is intentionally
separate from :mod:`verify_r3t_u4a` so it can kill every scoped descendant.
"""
from __future__ import annotations
import argparse, json, math, subprocess, sys, time, uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def cgroup_terminal_state(snap, unit):
    """Return EMPTY, REMOVED, ACTIVE, or UNKNOWN for this owned scope."""
    if snap.get("ActiveState") in ("active", "activating", "deactivating"):
        return "ACTIVE"
    cg=snap.get("ControlGroup","")
    root=Path("/sys/fs/cgroup").resolve()
    if not cg:
        # On this NCP systemd removes a transient scope's cgroup and clears
        # ControlGroup after it is inactive.  The empty unit cgroup is then
        # systemd's terminal proof; final CPU comes from the worker receipt.
        return "REMOVED" if snap.get("ActiveState")=="inactive" else "UNKNOWN"
    path=(root/cg.lstrip("/")).resolve()
    if not path.is_relative_to(root) or path.name != unit:
        return "UNKNOWN"
    if not path.exists():
        return "REMOVED" if snap.get("ActiveState")=="inactive" else "UNKNOWN"
    try:
        events=path/"cgroup.events"
        populated=[line.split()[1] for line in events.read_text().splitlines() if line.startswith("populated ")]
        if len(populated)!=1: return "UNKNOWN"
        return "EMPTY" if populated[0]=="0" else "ACTIVE"
    except (OSError, IndexError):
        return "UNKNOWN"
def put_new(path, value):
    with path.open("x") as f: json.dump(value,f,sort_keys=True,indent=2);f.write("\n")
def show(unit):
    p=subprocess.run(["systemctl","show",unit,"--property=ControlGroup,CPUUsageNSec,MemoryCurrent,MemoryPeak,MemoryMax,CPUQuotaPerSecUSec,ActiveState"],capture_output=True,text=True,check=False,timeout=1)
    if p.returncode: raise RuntimeError("SYSTEMCTL_SHOW_FAILED")
    data={k:v for k,v in (line.split("=",1) for line in p.stdout.splitlines() if "=" in line)}
    if "ActiveState" not in data: raise RuntimeError("SYSTEMCTL_SHOW_PROPERTY_MISSING")
    return data
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--receipt-dir",type=Path,required=True);ap.add_argument("--checkpoint",type=Path,required=True);ap.add_argument("--evidence-dir",type=Path,required=True);ap.add_argument("--new-allocation-id",required=True);ap.add_argument("--steps",choices=("16","32"),default="32");a=ap.parse_args()
    receipt=a.receipt_dir.resolve();receipt.mkdir(parents=True,exist_ok=False)
    unit="r3t-u4a-"+uuid.uuid4().hex[:16]+".scope"; started=time.monotonic()
    worker=[sys.executable,str(ROOT/"scripts/verify_r3t_u4a.py"),"--checkpoint",str(a.checkpoint),"--evidence-dir",str(a.evidence_dir),"--new-allocation-id",a.new_allocation_id,"--steps",a.steps]
    rec={"status":"STARTED","unit":unit,"worker_argv":worker,"limits":{"process_tree_cpu_s":60,"kill_threshold_cpu_s":50,"wall_s":180,"kill_threshold_wall_s":150,"scope_memory_max":"2G","per_process_as_bytes":2*1024**3},"io_bytes":"NOT_MEASURED"};put_new(receipt/"STARTED.json",rec)
    cmd=["systemd-run","--scope","--no-block","--unit="+unit,"--property=CPUAccounting=yes","--property=CPUQuota=100%","--property=MemoryAccounting=yes","--property=MemoryMax=2G",*worker]
    try:
        # systemd-run --scope can wait for the command lifetime.  Popen keeps
        # this controller outside the scope and lets it poll cgroup counters.
        launched=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        rec["launch"]={"argv":cmd,"launcher_pid":launched.pid}
        observed_cpu=False; last_active_cpu_s=None; max_memory_current=0
        while True:
            snap=show(unit); rec["last_scope"]=snap; wall=time.monotonic()-started
            raw_cpu=snap.get("CPUUsageNSec")
            cpu=float(raw_cpu)/1e9 if raw_cpu not in (None,"","[not set]") else None
            if cpu is not None and cpu==cpu:
                observed_cpu=True
                if cgroup_terminal_state(snap,unit) in ("ACTIVE","EMPTY"):
                    last_active_cpu_s=cpu
            raw_memory=snap.get("MemoryCurrent")
            if raw_memory not in (None,"","[not set]"):
                try: max_memory_current=max(max_memory_current,int(raw_memory))
                except ValueError: rec.setdefault("memory_observation_errors",[]).append(str(raw_memory))
            else:
                rec["memory_current_observation"]="NOT_SET_BY_SYSTEMD"
            if (cpu is not None and cpu>=50.) or wall>=150.:
                rec["status"]="CAP_HOLD";rec["cap"]={"cpu_s":cpu,"wall_s":wall,"kill_reason":"CPU" if cpu is not None and cpu>=50. else "WALL"}
                killed=subprocess.run(["systemctl","kill","--signal=KILL","--kill-whom=all",unit],capture_output=True,text=True,check=False,timeout=1)
                rec["kill"]={"argv":["systemctl","kill","--signal=KILL","--kill-whom=all",unit],"exit":killed.returncode,"stdout":killed.stdout,"stderr":killed.stderr}
                if killed.returncode: rec["status"]="UNKNOWN_ACTIVE_RUN"
                break
            if snap.get("ActiveState") not in ("active","activating") and launched.poll() is not None: break
            time.sleep(.2)
        # Scope can remain in deactivating briefly; the final counter is read
        # only after its children are no longer active.
        cleanup_deadline=time.monotonic()+3.
        while time.monotonic()<cleanup_deadline:
            snap=show(unit); rec["last_scope"]=snap
            if snap.get("ActiveState") not in ("active","activating","deactivating"): break
            time.sleep(.1)
        else:
            rec["status"]="UNKNOWN_ACTIVE_RUN"
        out,err=launched.communicate(timeout=1)
        rec["launch"].update(exit=launched.returncode,stdout=out,stderr=err)
        rec["final_scope"]=show(unit);rec["wall_s"]=time.monotonic()-started
        cstate=cgroup_terminal_state(rec["final_scope"],unit)
        rec["cgroup_terminal_state"]=cstate
        if cstate not in ("EMPTY","REMOVED"):
            rec["status"]="UNKNOWN_ACTIVE_RUN"
        final_counter=rec["final_scope"].get("CPUUsageNSec")
        if final_counter not in (None,"","[not set]"):
            final_cpu=float(final_counter)/1e9;rec["final_cpu_source"]="systemd_cgroup_CPUUsageNSec"
        elif cstate=="REMOVED":
            worker_result=a.evidence_dir/"RESULT.json"
            try:
                data=json.loads(worker_result.read_text())
                final_cpu=float(data["resources_observed"]["process_tree_cpu_s"])
                if data.get("status")!="PASS_SCOPED_U4A_RESTART" or not math.isfinite(final_cpu) or final_cpu<0.:
                    raise ValueError("worker terminal/CPU receipt invalid")
                if last_active_cpu_s is not None and last_active_cpu_s > final_cpu + .25:
                    raise ValueError("worker CPU below active cgroup observation")
                rec["final_cpu_source"]="worker_RUSAGE_process_tree_after_systemd_cgroup_removal"
            except Exception as cpu_error:
                rec["status"]="CAP_HOLD";rec["final_cpu_receipt_error"]=str(cpu_error);final_cpu=float("nan")
        else:
            rec["status"]="CAP_HOLD";final_cpu=float("nan")
        rec["aggregate_cpu_s"]=final_cpu
        rec["max_memory_current_bytes"]=max_memory_current;rec["memory_peak_bytes"]=rec["final_scope"].get("MemoryPeak","NOT_SUPPORTED")
        if not math.isfinite(final_cpu) or final_cpu>60. or rec["wall_s"]>180.:
            rec["status"]="CAP_HOLD"
        elif rec.get("status")=="STARTED":
            worker_result=a.evidence_dir/"RESULT.json"
            if not worker_result.is_file(): rec["status"]="WORKER_TERMINAL_RECEIPT_MISSING"
            else:
                data=json.loads(worker_result.read_text())
                rec["worker_terminal_status"]=data.get("status")
                rec["status"]="FINISHED" if data.get("status")=="PASS_SCOPED_U4A_RESTART" and rec["launch"].get("exit")==0 else "WORKER_HOLD"
    except Exception as e:
        rec["status"]="UNKNOWN_ACTIVE_RUN";rec["first_failure"]={"type":type(e).__name__,"message":str(e)}
        try:
            killed=subprocess.run(["systemctl","kill","--signal=KILL","--kill-whom=all",unit],capture_output=True,text=True,check=False,timeout=1)
            rec["exception_cleanup_kill"]={"exit":killed.returncode,"stdout":killed.stdout,"stderr":killed.stderr}
        except Exception as cleanup_error:
            rec["exception_cleanup_kill"]={"error":f"{type(cleanup_error).__name__}: {cleanup_error}"}
        if 'launched' in locals() and launched.poll() is None:
            launched.kill()
            try: launched.communicate(timeout=1)
            except Exception: pass
        try:
            final=show(unit); rec["exception_final_scope"]=final
            rec["exception_cgroup_terminal_state"]=cgroup_terminal_state(final,unit)
            if rec["exception_cgroup_terminal_state"] in ("EMPTY","REMOVED"):
                rec["status"]="SUPERVISOR_FAILURE_CLEANED"
        except Exception as cleanup_error:
            rec["exception_final_scope_error"]=f"{type(cleanup_error).__name__}: {cleanup_error}"
        rec["wall_s"]=time.monotonic()-started
    put_new(receipt/"RESULT.json",rec)
    if rec["status"] not in ("FINISHED",):raise SystemExit(1)
if __name__=="__main__":main()
