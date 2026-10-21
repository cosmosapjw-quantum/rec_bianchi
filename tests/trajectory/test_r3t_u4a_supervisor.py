"""Mock-only cgroup supervisor and native-frame regression tests."""
from __future__ import annotations
import sys
import itertools
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import run_r3t_u4a_supervised as sup


class FakePopen:
    def __init__(self,*_,**__): self.pid=42; self.done=False; self.killed=False; self.returncode=None
    def poll(self):
        if self.done:
            self.returncode=0
            return 0
        return None
    def communicate(self,timeout=None): self.done=True; self.returncode=0; return ("launcher out","launcher err")
    def kill(self): self.killed=True; self.done=True; self.returncode=-9


def _run_supervisor(monkeypatch,tmp_path,snaps,clock,worker_result=None,mode="u4a"):
    calls=[]; process=FakePopen()
    monkeypatch.setattr(sup.subprocess,"Popen",lambda *a,**k:process)
    def fake_show(unit):
        snap=snaps.pop(0) if snaps else {"ActiveState":"active","SubState":"exited","ControlGroup":"","InvocationID":"abc","CPUUsageNSec":"200000000","ExecMainCode":"1","ExecMainStatus":"0","Result":"success"}
        if snap.get("SubState")=="exited" or snap.get("ActiveState")=="failed": process.done=True
        return snap
    monkeypatch.setattr(sup,"show",fake_show)
    monkeypatch.setattr(sup.subprocess,"run",lambda args,**kw: calls.append(args) or SimpleNamespace(returncode=0,stdout="",stderr=""))
    monkeypatch.setattr(sup.time,"monotonic",lambda:next(clock))
    monkeypatch.setattr(sup.time,"sleep",lambda _:None)
    checkpoint=tmp_path/"cp.npz"; checkpoint.write_bytes(b"x")
    evidence=tmp_path/"evidence"; evidence.mkdir()
    if worker_result is not None:
        import json
        (evidence/"RESULT.json").write_text(json.dumps(worker_result))
    argv=["sup","--receipt-dir",str(tmp_path/"receipt"),"--checkpoint",str(checkpoint),"--evidence-dir",str(evidence),"--new-allocation-id","R3T_TEST"]
    if mode=="u4b": argv.extend(["--mode","u4b","--accepted-dir",str(evidence)])
    monkeypatch.setattr(sys,"argv",argv)
    try: sup.main()
    except SystemExit: pass
    return calls,process,(tmp_path/"receipt"/"RESULT.json").read_text()


def test_scope_is_polled_while_launcher_active_and_cpu_cap_kills_all(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"0","ActiveState":"active","SubState":"running","InvocationID":"abc"},{"CPUUsageNSec":"59000000000","ActiveState":"active","SubState":"running","InvocationID":"abc"},{"CPUUsageNSec":"59000000000","ActiveState":"failed","ControlGroup":"","InvocationID":"abc"},{"CPUUsageNSec":"59000000000","ActiveState":"failed","ControlGroup":"","InvocationID":"abc"}]
    calls,process,text=_run_supervisor(monkeypatch,tmp_path,snaps,iter([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.]))
    assert any(c[:4]==["systemctl","kill","--signal=KILL","--kill-whom=all"] for c in calls)
    assert process.done and '"status": "CAP_HOLD"' in text and '"kill_reason": "CPU"' in text


def test_launcher_registration_timeout_kills_and_reaps_client(monkeypatch):
    class TimeoutPopen(FakePopen):
        def communicate(self,timeout=None):
            if not self.done: raise sup.subprocess.TimeoutExpired("systemd-run",timeout)
            return ("","")
    process=TimeoutPopen()
    monkeypatch.setattr(sup.subprocess,"Popen",lambda *a,**k:process)
    with pytest.raises(RuntimeError,match="SYSTEMD_RUN_REGISTRATION_TIMEOUT"):
        sup.launch_registered_service(["systemd-run"])
    assert process.killed and process.done and process.poll()==0


def test_supervisor_exception_kills_scope_and_launcher(monkeypatch,tmp_path):
    snaps=[RuntimeError("show failed")]
    calls=[]; process=FakePopen()
    monkeypatch.setattr(sup.subprocess,"Popen",lambda *a,**k:process)
    def fail(_): raise snaps[0]
    monkeypatch.setattr(sup,"show",fail)
    monkeypatch.setattr(sup.subprocess,"run",lambda args,**kw: calls.append(args) or SimpleNamespace(returncode=0,stdout="",stderr=""))
    monkeypatch.setattr(sup.time,"monotonic",lambda:0.)
    checkpoint=tmp_path/"cp";checkpoint.write_bytes(b"x"); evidence=tmp_path/"ev";evidence.mkdir()
    monkeypatch.setattr(sys,"argv",["sup","--receipt-dir",str(tmp_path/"r"),"--checkpoint",str(checkpoint),"--evidence-dir",str(evidence),"--new-allocation-id","R3T_TEST"])
    with pytest.raises(SystemExit):sup.main()
    # The bounded launcher registration already completed before polling.  On
    # poll failure the owned systemd unit is killed; there is no live launcher
    # left to kill as a separate process.
    assert not process.killed and any(c[:4]==["systemctl","kill","--signal=KILL","--kill-whom=all"] for c in calls)
    import json
    result=json.loads((tmp_path/"r"/"RESULT.json").read_text())
    assert result["supervisor_exit_code"]==1
    assert result["resource_accounting_status"]=="UNRESOLVED"
    assert result["aggregate_cpu_s"] is None


def test_exception_terminal_service_is_stopped_after_readback(monkeypatch,tmp_path):
    process=FakePopen(); calls=[]; n=[0]
    monkeypatch.setattr(sup.subprocess,"Popen",lambda *a,**k:process)
    def one_failure(_):
        n[0]+=1
        if n[0]==1: raise RuntimeError("poll failed")
        return {"ActiveState":"failed","SubState":"failed","ControlGroup":"","InvocationID":"abc","CPUUsageNSec":"120000000","ExecMainCode":"2","ExecMainStatus":"9","Result":"signal"}
    monkeypatch.setattr(sup,"show",one_failure)
    monkeypatch.setattr(sup.subprocess,"run",lambda args,**kw: calls.append(args) or SimpleNamespace(returncode=0,stdout="",stderr=""))
    monkeypatch.setattr(sup.time,"monotonic",lambda:0.)
    checkpoint=tmp_path/"cp";checkpoint.write_bytes(b"x");evidence=tmp_path/"ev";evidence.mkdir()
    monkeypatch.setattr(sys,"argv",["sup","--receipt-dir",str(tmp_path/"r"),"--checkpoint",str(checkpoint),"--evidence-dir",str(evidence),"--new-allocation-id","R3T_TEST"])
    with pytest.raises(SystemExit): sup.main()
    import json
    result=json.loads((tmp_path/"r"/"RESULT.json").read_text())
    assert result["status"]=="SUPERVISOR_FAILURE_CLEANED"
    assert result["aggregate_cpu_s"] is None
    assert result["resource_accounting_status"]=="UNRESOLVED"
    assert result["supervisor_exit_code"]==1
    assert any(c[:2]==["systemctl","stop"] for c in calls)


def test_missing_final_cpu_counter_cannot_finish(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"0","ActiveState":"active","SubState":"running","InvocationID":"abc"}]+[{"ActiveState":"active","SubState":"exited","ControlGroup":"","InvocationID":"abc"}]*3
    _,_,text=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count())
    assert '"status": "CAP_HOLD"' in text


def test_stuck_scope_after_kill_is_unknown_active_run(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"0","ActiveState":"active","SubState":"running","InvocationID":"abc"},{"CPUUsageNSec":"59000000000","ActiveState":"active","SubState":"running","InvocationID":"abc"}]+[{"CPUUsageNSec":"59000000000","ActiveState":"deactivating","InvocationID":"abc"}]*102
    _,_,text=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count())
    assert '"status": "UNKNOWN_ACTIVE_RUN"' in text


def test_retained_service_uses_final_systemd_cpu_even_if_worker_snapshot_lower(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"100000000","ActiveState":"active","SubState":"running","InvocationID":"abc"},{"ActiveState":"active","SubState":"exited","ControlGroup":"","InvocationID":"abc","MemoryCurrent":"[not set]","MemoryPeak":"[not set]","CPUUsageNSec":"200000000","ExecMainCode":"1","ExecMainStatus":"0","Result":"success"},{"ActiveState":"active","SubState":"exited","ControlGroup":"","InvocationID":"abc","MemoryCurrent":"[not set]","MemoryPeak":"[not set]","CPUUsageNSec":"200000000","ExecMainCode":"1","ExecMainStatus":"0","Result":"success"}]
    worker={"status":"PASS_SCOPED_U4A_RESTART","resources_observed":{"process_tree_cpu_s":0.2}}
    _,_,receipt=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count(),worker)
    assert '"status": "FINISHED"' in receipt
    assert '"final_cpu_source": "retained_systemd_service_CPUUsageNSec"' in receipt
    assert '"aggregate_cpu_s": 0.2' in receipt
    assert '"memory_current_observation": "NOT_SET_BY_SYSTEMD"' in receipt


@pytest.mark.parametrize("worker",[
    None,
    {"status":"PASS_SCOPED_U4A_RESTART","resources_observed":{"process_tree_cpu_s":60.1}},
    {"status":"FAIL","resources_observed":{"process_tree_cpu_s":0.2}},
    {"status":"PASS_SCOPED_U4A_RESTART","resources_observed":{"process_tree_cpu_s":0.0}},
])
def test_missing_final_cpu_never_falls_back_to_worker_receipt(monkeypatch,tmp_path,worker):
    snaps=[{"CPUUsageNSec":"1000000000","ActiveState":"active","SubState":"running","InvocationID":"abc"}]+[{"ActiveState":"active","SubState":"exited","ControlGroup":"","InvocationID":"abc","CPUUsageNSec":"[not set]"}]*3
    _,_,receipt=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count(),worker)
    assert '"status": "FINISHED"' not in receipt
    assert '"aggregate_cpu_s": null' in receipt


def test_u4b_worker_status_and_accepted_dir_forwarded(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"0","ActiveState":"active","SubState":"running","InvocationID":"abc"}]+[{"ActiveState":"active","SubState":"exited","ControlGroup":"","InvocationID":"abc","CPUUsageNSec":"200000000","ExecMainCode":"1","ExecMainStatus":"0","Result":"success"}]*3
    _,_,receipt=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count(),{"status":"PASS_SCOPED_U4B_RESTART"},mode="u4b")
    import json
    data=json.loads(receipt)
    assert data["status"]=="FINISHED"
    assert data["supervisor_exit_code"]==0
    assert data["worker_terminal_status"]=="PASS_SCOPED_U4B_RESTART"
    assert data["worker_argv"][-4:-2]==["--mode","u4b"]
    assert data["worker_argv"][-2]=="--accepted-dir"


def test_missing_live_counter_kills_before_unbounded_cpu(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"[not set]","ActiveState":"active","SubState":"running","InvocationID":"abc"}]+[{"ActiveState":"failed","SubState":"failed","ControlGroup":"","InvocationID":"abc","CPUUsageNSec":"[not set]","ExecMainCode":"2","ExecMainStatus":"9","Result":"signal"}]*3
    calls,_,receipt=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count())
    import json
    data=json.loads(receipt)
    assert data["status"]=="CAP_HOLD"
    assert data["cap"]["kill_reason"]=="COUNTER_MISSING"
    assert data["aggregate_cpu_s"] is None
    assert any(c[:2]==["systemctl","kill"] for c in calls)
