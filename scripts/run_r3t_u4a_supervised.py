#!/usr/bin/env python3
"""Outer NCP cgroup supervisor for one bounded R3T-U4A worker invocation.

The controller stays outside the transient scope and records the cgroup's
aggregate CPU counter.  It creates no scientific input and is intentionally
separate from :mod:`verify_r3t_u4a` so it can kill every scoped descendant.
"""
from __future__ import annotations
import argparse, json, math, resource, subprocess, sys, time, uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def cgroup_terminal_state(snap, unit):
    """Return REMOVED only after the retained service has no live processes."""
    if snap.get("ActiveState")=="active" and snap.get("SubState")=="exited":
        pass
    elif snap.get("ActiveState")=="failed":
        pass
    elif snap.get("ActiveState") in ("active", "activating", "deactivating"):
        return "ACTIVE"
    else:
        return "UNKNOWN"
    cg=snap.get("ControlGroup","")
    root=Path("/sys/fs/cgroup").resolve()
    if not cg:
        return "REMOVED"
    path=(root/cg.lstrip("/")).resolve()
    if not path.is_relative_to(root) or path.name != unit:
        return "UNKNOWN"
    if not path.exists():
        return "REMOVED"
    try:
        events=path/"cgroup.events"
        populated=[line.split()[1] for line in events.read_text().splitlines() if line.startswith("populated ")]
        if len(populated)!=1: return "UNKNOWN"
        return "EMPTY" if populated[0]=="0" else "ACTIVE"
    except (OSError, IndexError):
        return "UNKNOWN"
def put_new(path, value):
    with path.open("x") as f: json.dump(value,f,sort_keys=True,indent=2);f.write("\n")
def controller_cpu_s():
    own=resource.getrusage(resource.RUSAGE_SELF)
    children=resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime+own.ru_stime+children.ru_utime+children.ru_stime
def show(unit):
    p=subprocess.run(["systemctl","show",unit,"--property=Id,InvocationID,ControlGroup,CPUUsageNSec,MemoryCurrent,MemoryPeak,MemoryMax,CPUQuotaPerSecUSec,ActiveState,SubState,Result,ExecMainCode,ExecMainStatus"],capture_output=True,text=True,check=False,timeout=1)
    if p.returncode: raise RuntimeError("SYSTEMCTL_SHOW_FAILED")
    data={k:v for k,v in (line.split("=",1) for line in p.stdout.splitlines() if "=" in line)}
    if "ActiveState" not in data: raise RuntimeError("SYSTEMCTL_SHOW_PROPERTY_MISSING")
    return data
def launch_registered_service(cmd):
    """Start one retained service and wait for the start job before polling it."""
    process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        stdout,stderr=process.communicate(timeout=5)
    except subprocess.TimeoutExpired as error:
        process.kill()
        try: process.communicate(timeout=1)
        except Exception: pass
        raise RuntimeError("SYSTEMD_RUN_REGISTRATION_TIMEOUT") from error
    return process, {"exit":process.returncode,"stdout":stdout,"stderr":stderr}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--receipt-dir",type=Path,required=True);ap.add_argument("--checkpoint",type=Path,required=True);ap.add_argument("--evidence-dir",type=Path,required=True);ap.add_argument("--new-allocation-id",required=True);ap.add_argument("--steps",choices=("16","32"),default="32");ap.add_argument("--mode",choices=("u4a","u4b"),default="u4a");ap.add_argument("--accepted-dir",type=Path);a=ap.parse_args()
    if a.mode=="u4b" and a.accepted_dir is None: ap.error("--accepted-dir is required for U4B")
    if a.mode=="u4a" and a.accepted_dir is not None: ap.error("--accepted-dir applies only to U4B")
    receipt=a.receipt_dir.resolve();receipt.mkdir(parents=True,exist_ok=False)
    unit="r3t-"+a.mode+"-"+uuid.uuid4().hex[:16]+".service"; started=time.monotonic(); controller_cpu_start=controller_cpu_s()
    worker=[sys.executable,str(ROOT/"scripts/verify_r3t_u4a.py"),"--checkpoint",str(a.checkpoint),"--evidence-dir",str(a.evidence_dir),"--new-allocation-id",a.new_allocation_id,"--steps",a.steps]
    if a.mode=="u4b": worker.extend(["--mode","u4b","--accepted-dir",str(a.accepted_dir)])
    rec={"status":"STARTED","unit":unit,"worker_argv":worker,"limits":{"process_tree_cpu_s":60,"kill_threshold_cpu_s":50,"wall_s":180,"kill_threshold_wall_s":150,"scope_memory_max":"2G","per_process_as_bytes":2*1024**3},"io_bytes":"NOT_MEASURED"};put_new(receipt/"STARTED.json",rec)
    cmd=["systemd-run","--no-block","--remain-after-exit","--unit="+unit,"--property=Type=exec","--property=CPUAccounting=yes","--property=CPUQuota=100%","--property=MemoryAccounting=yes","--property=MemoryMax=2G",*worker]
    try:
        # A retained transient service preserves its final cgroup CPU counter
        # after its worker exits.  Stop the exact unit only after readback.
        launched,launch_result=launch_registered_service(cmd)
        rec["launch"]={"argv":cmd,"launcher_pid":launched.pid}
        # Wait for systemd-run's start job to finish before the first unit
        # lookup. The service may already have exited; remain-after-exit keeps
        # it queryable while this bounded registration wait closes that race.
        rec["launch"].update(launch_result)
        if launched.returncode!=0: raise RuntimeError("SERVICE_LAUNCH_FAILED")
        invocation_id=None; max_memory_current=0
        while True:
            snap=show(unit); rec["last_scope"]=snap; wall=time.monotonic()-started
            if snap.get("Id") not in (None,"",unit): raise RuntimeError("UNIT_ID_MISMATCH")
            seen=snap.get("InvocationID")
            if seen:
                if invocation_id is not None and seen!=invocation_id: raise RuntimeError("UNIT_INVOCATION_CHANGED")
                invocation_id=seen
            raw_cpu=snap.get("CPUUsageNSec")
            cpu=float(raw_cpu)/1e9 if raw_cpu not in (None,"","[not set]") else None
            raw_memory=snap.get("MemoryCurrent")
            if raw_memory not in (None,"","[not set]"):
                try: max_memory_current=max(max_memory_current,int(raw_memory))
                except ValueError: rec.setdefault("memory_observation_errors",[]).append(str(raw_memory))
            else:
                rec["memory_current_observation"]="NOT_SET_BY_SYSTEMD"
            controller_now=controller_cpu_s()-controller_cpu_start
            allocation_cpu_now=cpu+controller_now if cpu is not None else None
            counter_missing=bool(invocation_id and cgroup_terminal_state(snap,unit)=="ACTIVE" and allocation_cpu_now is None)
            if (allocation_cpu_now is not None and allocation_cpu_now>=50.) or wall>=150. or counter_missing:
                reason="CPU" if allocation_cpu_now is not None and allocation_cpu_now>=50. else "COUNTER_MISSING" if counter_missing else "WALL"
                rec["status"]="CAP_HOLD";rec["cap"]={"service_cpu_s":cpu,"controller_cpu_s":controller_now,"allocation_accounted_cpu_s":allocation_cpu_now,"wall_s":wall,"kill_reason":reason}
                killed=subprocess.run(["systemctl","kill","--signal=KILL","--kill-whom=all",unit],capture_output=True,text=True,check=False,timeout=1)
                rec["kill"]={"argv":["systemctl","kill","--signal=KILL","--kill-whom=all",unit],"exit":killed.returncode,"stdout":killed.stdout,"stderr":killed.stderr}
                if killed.returncode: rec["status"]="UNKNOWN_ACTIVE_RUN"
                break
            if invocation_id and cgroup_terminal_state(snap,unit) in ("EMPTY","REMOVED") and launched.poll() is not None: break
            time.sleep(.2)
        # Preserve the retained unit while all descendants exit and before
        # systemctl stop discards CPUUsageNSec.
        cleanup_deadline=time.monotonic()+3.
        while time.monotonic()<cleanup_deadline:
            snap=show(unit); rec["last_scope"]=snap
            if cgroup_terminal_state(snap,unit) in ("EMPTY","REMOVED"): break
            time.sleep(.1)
        else:
            rec["status"]="UNKNOWN_ACTIVE_RUN"
        out,err=launched.communicate(timeout=1)
        rec["launch"].update(exit=launched.returncode,stdout=out,stderr=err)
        rec["final_scope"]=show(unit);rec["wall_s"]=time.monotonic()-started
        rec["invocation_id"]=invocation_id
        if not invocation_id or rec["final_scope"].get("InvocationID")!=invocation_id:
            rec["status"]="CAP_HOLD";rec["final_cpu_receipt_error"]="INVOCATION_ID_MISSING_OR_CHANGED"
        cstate=cgroup_terminal_state(rec["final_scope"],unit)
        rec["cgroup_terminal_state"]=cstate
        if cstate not in ("EMPTY","REMOVED"):
            rec["status"]="UNKNOWN_ACTIVE_RUN"
        final_counter=rec["final_scope"].get("CPUUsageNSec")
        try:
            if cstate not in ("EMPTY","REMOVED") or not invocation_id or rec["final_scope"].get("InvocationID")!=invocation_id:
                raise ValueError("TERMINAL_UNIT_OR_INVOCATION_UNRESOLVED")
            final_cpu=int(final_counter)/1e9
            if not math.isfinite(final_cpu) or final_cpu<0.: raise ValueError("FINAL_CPU_COUNTER_INVALID")
            rec["final_cpu_source"]="retained_systemd_service_CPUUsageNSec"
            rec["resource_accounting_status"]="OBSERVED"
        except (TypeError, ValueError) as cpu_error:
            if rec["status"]!="UNKNOWN_ACTIVE_RUN": rec["status"]="CAP_HOLD"
            rec["final_cpu_receipt_error"]=str(cpu_error);rec["resource_accounting_status"]="UNRESOLVED";final_cpu=None
        rec["aggregate_cpu_s"]=final_cpu
        rec["max_memory_current_bytes"]=max_memory_current;rec["memory_peak_bytes"]=rec["final_scope"].get("MemoryPeak","NOT_SUPPORTED")
        rec["worker_exit"]={"code_kind":rec["final_scope"].get("ExecMainCode"),"status_or_signal":rec["final_scope"].get("ExecMainStatus"),"unit_result":rec["final_scope"].get("Result")}
        if rec["status"]=="UNKNOWN_ACTIVE_RUN":
            pass
        elif final_cpu is None or final_cpu>60. or rec["wall_s"]>180.:
            rec["status"]="CAP_HOLD"
        elif rec.get("status")=="STARTED":
            worker_result=a.evidence_dir/"RESULT.json"
            if not worker_result.is_file(): rec["status"]="WORKER_TERMINAL_RECEIPT_MISSING"
            else:
                data=json.loads(worker_result.read_text())
                rec["worker_terminal_status"]=data.get("status")
                expected_worker="PASS_SCOPED_U4A_RESTART" if a.mode=="u4a" else "PASS_SCOPED_U4B_RESTART"
                rec["status"]="FINISHED" if data.get("status")==expected_worker and rec["launch"].get("exit")==0 and rec["worker_exit"]=={"code_kind":"1","status_or_signal":"0","unit_result":"success"} else "WORKER_HOLD"
        # This cleanup is after the final counter and exit readback.  Its CPU
        # is not part of the owned worker unit or its allocation accounting.
        stop=subprocess.run(["systemctl","stop",unit],capture_output=True,text=True,check=False,timeout=2)
        rec["unit_stop"]={"exit":stop.returncode,"stdout":stop.stdout,"stderr":stop.stderr}
        if stop.returncode and rec["status"]=="FINISHED": rec["status"]="SUPERVISOR_CLEANUP_HOLD"
    except Exception as e:
        rec["status"]="UNKNOWN_ACTIVE_RUN";rec["first_failure"]={"type":type(e).__name__,"message":str(e)}
        rec["aggregate_cpu_s"]=None;rec["resource_accounting_status"]="UNRESOLVED"
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
                stop=subprocess.run(["systemctl","stop",unit],capture_output=True,text=True,check=False,timeout=2)
                rec["unit_stop"]={"exit":stop.returncode,"stdout":stop.stdout,"stderr":stop.stderr}
                if stop.returncode: rec["status"]="SUPERVISOR_CLEANUP_HOLD"
        except Exception as cleanup_error:
            rec["exception_final_scope_error"]=f"{type(cleanup_error).__name__}: {cleanup_error}"
        rec["wall_s"]=time.monotonic()-started
    rec["controller_cpu_s"]=controller_cpu_s()-controller_cpu_start
    if rec.get("aggregate_cpu_s") is not None:
        rec["allocation_accounted_cpu_s"]=rec["aggregate_cpu_s"]+rec["controller_cpu_s"]
        if rec["allocation_accounted_cpu_s"]>60. and rec["status"]=="FINISHED": rec["status"]="CAP_HOLD"
    else: rec["allocation_accounted_cpu_s"]=None
    rec["supervisor_exit_code"]=0 if rec["status"]=="FINISHED" else 1
    put_new(receipt/"RESULT.json",rec)
    if rec["status"] not in ("FINISHED",):raise SystemExit(1)
if __name__=="__main__":main()
