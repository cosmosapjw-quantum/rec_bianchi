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
    def poll(self): return 0 if self.done else None
    def communicate(self,timeout=None): self.done=True; self.returncode=0; return ("launcher out","launcher err")
    def kill(self): self.killed=True; self.done=True; self.returncode=-9


def _run_supervisor(monkeypatch,tmp_path,snaps,clock,worker_result=None):
    calls=[]; process=FakePopen()
    monkeypatch.setattr(sup.subprocess,"Popen",lambda *a,**k:process)
    def fake_show(unit):
        snap=snaps.pop(0) if snaps else {"ActiveState":"inactive","ControlGroup":""}
        if snap.get("ActiveState")=="inactive": process.done=True
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
    monkeypatch.setattr(sys,"argv",["sup","--receipt-dir",str(tmp_path/"receipt"),"--checkpoint",str(checkpoint),"--evidence-dir",str(evidence),"--new-allocation-id","R3T_TEST"])
    try: sup.main()
    except SystemExit: pass
    return calls,process,(tmp_path/"receipt"/"RESULT.json").read_text()


def test_scope_is_polled_while_launcher_active_and_cpu_cap_kills_all(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"0","ActiveState":"active"},{"CPUUsageNSec":"59000000000","ActiveState":"active"},{"CPUUsageNSec":"59000000000","ActiveState":"inactive"},{"CPUUsageNSec":"59000000000","ActiveState":"inactive"}]
    calls,process,text=_run_supervisor(monkeypatch,tmp_path,snaps,iter([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.]))
    assert any(c[:4]==["systemctl","kill","--signal=KILL","--kill-whom=all"] for c in calls)
    assert process.done and '"status": "CAP_HOLD"' in text and '"kill_reason": "CPU"' in text


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
    assert process.killed and any(c[:4]==["systemctl","kill","--signal=KILL","--kill-whom=all"] for c in calls)


def test_missing_final_cpu_counter_cannot_finish(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"0","ActiveState":"active"},{"CPUUsageNSec":"59000000000","ActiveState":"active"},{"CPUUsageNSec":"59000000000","ActiveState":"inactive"},{"ActiveState":"inactive"}]
    _,_,text=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count())
    assert '"status": "CAP_HOLD"' in text


def test_stuck_scope_after_kill_is_unknown_active_run(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"0","ActiveState":"active"},{"CPUUsageNSec":"59000000000","ActiveState":"active"}]+[{"CPUUsageNSec":"59000000000","ActiveState":"deactivating"}]*102
    _,_,text=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count())
    assert '"status": "UNKNOWN_ACTIVE_RUN"' in text


def test_removed_scope_uses_finite_worker_process_tree_cpu_receipt(monkeypatch,tmp_path):
    snaps=[{"CPUUsageNSec":"100000000","ActiveState":"active"},{"ActiveState":"inactive","ControlGroup":"","MemoryCurrent":"[not set]","MemoryPeak":"[not set]","CPUUsageNSec":"[not set]"},{"ActiveState":"inactive","ControlGroup":"","MemoryCurrent":"[not set]","MemoryPeak":"[not set]","CPUUsageNSec":"[not set]"}]
    monkeypatch.setattr(sup,"cgroup_terminal_state",lambda snap,unit:"ACTIVE" if snap.get("ActiveState")=="active" else "REMOVED")
    worker={"status":"PASS_SCOPED_U4A_RESTART","resources_observed":{"process_tree_cpu_s":0.2}}
    _,_,receipt=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count(),worker)
    assert '"status": "FINISHED"' in receipt
    assert '"final_cpu_source": "worker_RUSAGE_process_tree_after_systemd_cgroup_removal"' in receipt
    assert '"memory_current_observation": "NOT_SET_BY_SYSTEMD"' in receipt


@pytest.mark.parametrize("worker",[
    None,
    {"status":"PASS_SCOPED_U4A_RESTART","resources_observed":{"process_tree_cpu_s":60.1}},
    {"status":"FAIL","resources_observed":{"process_tree_cpu_s":0.2}},
    {"status":"PASS_SCOPED_U4A_RESTART","resources_observed":{"process_tree_cpu_s":0.0}},
])
def test_removed_scope_missing_invalid_or_underreported_cpu_never_finishes(monkeypatch,tmp_path,worker):
    snaps=[{"CPUUsageNSec":"1000000000","ActiveState":"active"},{"ActiveState":"inactive","ControlGroup":""},{"ActiveState":"inactive","ControlGroup":""}]
    monkeypatch.setattr(sup,"cgroup_terminal_state",lambda snap,unit:"ACTIVE" if snap.get("ActiveState")=="active" else "REMOVED")
    _,_,receipt=_run_supervisor(monkeypatch,tmp_path,snaps,itertools.count(),worker)
    assert '"status": "FINISHED"' not in receipt
