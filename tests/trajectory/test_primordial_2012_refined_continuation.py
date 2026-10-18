"""Bounded R3i continuation tests; never claim a full primordial history."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory import primordial_2012_refined_continuation as mod
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    HyRec2012Cosmology,make_hmla_source,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from verify_r3i_h2_continuation import (  # noqa:E402
    checked_cpu_budget,compare_native_stream,enforce_final_cpu_gate,
    select_event_sample_calls,serializable_step,
    verify_capsule_source_closure,
)

ROOT=Path(__file__).resolve().parents[2]
CHECKPOINT=(ROOT/"research/rec_r3i_time_refinement_20261016/h2_start_001"
            /"run_003/python_accepted_history.npz")
ZIP=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def test_frozen_checkpoint_rejects_mutated_bytes(tmp_path):
    if not CHECKPOINT.is_file(): pytest.skip("reviewed h2-start checkpoint is not installed")
    raw=CHECKPOINT.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==mod.CHECKPOINT_SHA256
    damaged=tmp_path/"altered.npz"
    damaged.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
    with pytest.raises(ValueError,match="FROZEN_H2_CHECKPOINT_SHA_MISMATCH"):
        mod.load_frozen_start(damaged)


def test_next_uncommitted_column_is_not_a_checkpoint_source():
    if not CHECKPOINT.is_file() or not ZIP.is_file():
        pytest.skip("reviewed h2-start checkpoint or original source ZIP is not installed")
    cp=mod.load_frozen_start(CHECKPOINT)
    c=HyRec2012Cosmology()
    rates=OriginalHyRecPrimitiveRateTable.from_archive(ZIP)
    source=make_hmla_source(c,rates)
    accepted=[]
    result=mod.integrate_continuation(
        cp,c,source,max_extra_accepted=1,max_full_evaluations=4,
        on_accept=lambda state,step,out: accepted.append((state,step)))
    assert result.status=="CAP_BEFORE_EVENT_PLUS_TWO"
    assert result.full_evaluations==4
    assert result.states[0]["iz"]==36454 and result.states[-1]["iz"]==36455
    assert result.steps[0]["photon_col"]==8
    assert result.virtual_out.shape==(311,9)
    assert np.array_equal(result.virtual_out[:,:8],cp["virtual_out"])
    assert len(accepted)==1
    assert result.steps[0]["schur_residual"]<2e-10


def test_hard_caps_refuse_expansion_before_source_evaluation():
    if not CHECKPOINT.is_file(): pytest.skip("reviewed h2-start checkpoint is not installed")
    cp=mod.load_frozen_start(CHECKPOINT)
    with pytest.raises(ValueError,match="EXTRA_ACCEPTED_CAP"):
        mod.integrate_continuation(cp,HyRec2012Cosmology(),None,
                                   max_extra_accepted=mod.MAX_EXTRA_ACCEPTED+1)
    with pytest.raises(ValueError,match="FULL_EVALUATION_CAP"):
        mod.integrate_continuation(cp,HyRec2012Cosmology(),None,
                                   max_full_evaluations=mod.MAX_FULL_EVALUATIONS+1)


@pytest.mark.parametrize("bad",[math.nan,math.inf,-1.e-12])
def test_bad_schur_residual_stops_before_accept(monkeypatch,bad):
    if not CHECKPOINT.is_file() or not ZIP.is_file(): pytest.skip("physical source unavailable")
    cp=mod.load_frozen_start(CHECKPOINT)
    c=HyRec2012Cosmology()
    source=make_hmla_source(c,OriginalHyRecPrimitiveRateTable.from_archive(ZIP))
    accepted=[]
    monkeypatch.setattr(mod,"complete_original_full_atomic",lambda _:
        SimpleNamespace(dxHII_dln_a=0.,normalized_matrix_residual=bad))
    with pytest.raises(ArithmeticError,match="FULL_SOURCE_OR_SCHUR"):
        mod.integrate_continuation(cp,c,source,max_extra_accepted=1,
                                   on_accept=lambda *_: accepted.append(1))
    assert accepted==[]


def test_negative_or_nonfinite_species_ledger_stops_before_source():
    if not CHECKPOINT.is_file(): pytest.skip("reviewed checkpoint unavailable")
    cp=mod.load_frozen_start(CHECKPOINT)
    cp["xHeII"][-1]=-1.e-4
    with pytest.raises(ArithmeticError,match="NEGATIVE_OR_SUPERUNITY_SPECIES"):
        mod.integrate_continuation(cp,HyRec2012Cosmology(),None,max_extra_accepted=1)
    cp=mod.load_frozen_start(CHECKPOINT)
    cp["xe"][-1]=math.nan
    with pytest.raises(ArithmeticError,match="NONFINITE_SPECIES_LEDGER"):
        mod.integrate_continuation(cp,HyRec2012Cosmology(),None,max_extra_accepted=1)


def test_h_only_sentinel_is_only_allowed_nonfinite_step_field():
    assert serializable_step({"branch":"H_ONLY","helium_rhs":math.nan,
                              "hydrogen_rhs":1.})["helium_rhs"] is None
    with pytest.raises(ArithmeticError,match="NONFINITE_ACCEPTED_STEP"):
        serializable_step({"branch":"H_HE","helium_rhs":math.nan})
    with pytest.raises(ArithmeticError,match="H_ONLY_HELIUM_RHS_SENTINEL"):
        serializable_step({"branch":"H_ONLY","helium_rhs":0.})


def test_event_neighborhood_counts_calls_including_regular_samples():
    tail=[(i,100+i//4) for i in range(1,257)]
    online={4:101,128:132,252:163}
    chosen,report=select_event_sample_calls(tail,online,event_g=163)
    assert report["total_calls"]==64
    assert report["online_calls"]==3
    assert report["new_calls"]==61
    assert len({r[0] for r in chosen}&set(online))==0
    assert len(chosen)+report["online_calls"]<=64


def test_cumulative_cpu_watchdog_and_capsule_closure(monkeypatch):
    import verify_r3i_h2_continuation as verifier
    monkeypatch.setattr(verifier,"total_process_tree_cpu_s",lambda:601.)
    with pytest.raises(RuntimeError,match="CUMULATIVE_CPU_CAP"):
        checked_cpu_budget(0.,"synthetic_overrun")
    if not CHECKPOINT.is_file(): pytest.skip("reviewed checkpoint unavailable")
    result=verify_capsule_source_closure(ROOT,CHECKPOINT)
    assert result["checkpoint_sha256"]==mod.CHECKPOINT_SHA256
    assert result["verified_files"]>=15


def test_streaming_cpu_guard_fires_before_native_row_parse_completes(tmp_path):
    # The long HE prefix of the original native stdout is enough to cross a
    # periodic boundary; no spectrum or physical evolution is rerun.
    path=tmp_path/"native.csv"
    path.write_text("HE\n"*4096)
    calls=[]
    def guard(stage):
        calls.append(stage)
        raise RuntimeError("CUMULATIVE_CPU_CAP:synthetic_stream")
    with pytest.raises(RuntimeError,match="synthetic_stream"):
        compare_native_stream(path,None,None,None,None,cpu_guard=guard)
    assert calls==["native_stdout_stream"]


def test_final_cpu_cap_boundary_and_first_failure_preservation():
    under={"status":"PASS_PENDING_INDEPENDENT_REVIEW","first_failure":None}
    assert enforce_final_cpu_gate(under,599.999)["status"]=="PASS_PENDING_INDEPENDENT_REVIEW"
    at={"status":"PASS_PENDING_INDEPENDENT_REVIEW","first_failure":None}
    result=enforce_final_cpu_gate(at,600.)
    assert result["status"]=="FAIL_CPU_CAP"
    assert result["first_failure"]["type"]=="CPU_CAP"
    prior={"status":"FAIL","first_failure":{"type":"SCIENTIFIC_PARITY","message":"first"}}
    result=enforce_final_cpu_gate(prior,600.001)
    assert result["status"]=="FAIL_CPU_CAP"
    assert result["first_failure"]["type"]=="SCIENTIFIC_PARITY"
    assert result["cpu_cap_failure"]["type"]=="CPU_CAP"
